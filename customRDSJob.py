""" Start the job and send notification once it is complete 

    Usage: python3 customRDSJob.py <region> <db1Name> <db2Name> <topicArn>"""

import boto3
import sys
import datetime
import os

import restoreRDSInstance
import deleteRDSInstance
import createRDSSnapshot
import sendSNSMessage

region = sys.argv[1]
# DB to create snapshot of and restore the second db from
db1 = sys.argv[2]
# DB to delete
db2 = sys.argv[3]
# SNS topic to send notification to
topicArn = sys.argv[4]

# Create RDS client
client_rds = boto3.client('rds', region_name=region)
client_sns = boto3.client('sns', region_name=region)

message = {}

# 1. Take snapshot of db1
snapName1 = db1 + '-' + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H-%M') + '-boto'
db1_resp = createRDSSnapshot.createRDSSnapshot(client_rds, db1, snapName1)

if db1_resp[0] == 'Error':
    message['DB1Snapshot'] = 'Unable to take snapshot of ' + db1
    sendSNSMessage(client, str(message), topicArn)
    os._exit(0) # Exit the program if the snapshot creation for db1 couldn't be initiated
else:
    # 2. Confirm that the snapshot of db1 is complete
    waiter1 = client_rds.get_waiter('db_snapshot_available')
    count = 0
    while True:
        try:
            ret = waiter1.wait(
                DBSnapshotIdentifier=snapName1,
                WaiterConfig={
                    'Delay': 30,
                    'MaxAttempts': 60
                }
            )
    
            if ret is None:
                break
        except:
            count += 1
            if count >=4:
                message['DBSnapshot'] = 'DB Snapshot unavailable for 2 hours'
                sendSNSMessage(client, str(message), topicArn)
                os._exit(0) # Exit the program if snapshot not available for 2 hours
            pass
    
# Retrieve the information about db2
db2_data = client_rds.describe_db_instances(
    DBInstanceIdentifier=db2
    )

dbInfo = {}

dbInfo['DBInstanceIdentifier'] = db2_data['DBInstances'][0]['DBInstanceIdentifier']
dbInfo['DBInstanceClass'] = db2_data['DBInstances'][0]['DBInstanceClass']
dbInfo['AvailabilityZone'] = db2_data['DBInstances'][0]['AvailabilityZone']
dbInfo['DBSubnetGroupName'] = db2_data['DBInstances'][0]['DBSubnetGroup']['DBSubnetGroupName']
dbInfo['MultiAZ'] = db2_data['DBInstances'][0]['MultiAZ']
dbInfo['PubliclyAccessible'] = db2_data['DBInstances'][0]['PubliclyAccessible']
dbInfo['AutoMinorVersionUpgrade'] = db2_data['DBInstances'][0]['AutoMinorVersionUpgrade']
dbInfo['LicenseModel'] = db2_data['DBInstances'][0]['LicenseModel']
dbInfo['Engine'] = db2_data['DBInstances'][0]['Engine']
dbInfo['OptionGroupName'] = db2_data['DBInstances'][0]['OptionGroupMemberships'][0]['OptionGroupName']
dbInfo['StorageType'] = db2_data['DBInstances'][0]['StorageType']
dbInfo['CopyTagsToSnapshot'] = db2_data['DBInstances'][0]['CopyTagsToSnapshot']
dbInfo['Port'] = db2_data['DBInstances'][0]['Endpoint']['Port']

# 3. Take snapshot of and delete db2
snapName2 = db2 + '-' + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H-%M') + '-boto'
db2_resp = deleteRDSInstance.deleteRDSInstance(client_rds, db2, snapName2)

if db2_resp == 'Error':
    message['DB2Delete'] = 'Error in deleting ' + db2
    sendSNSMessage(client, str(message), topicArn)
    os._exit(0) # Exit the program if db2 deletion can't be initiated
else:
    # Wait for db2 to be deleted
    waiter2 = client_rds.get_waiter('db_instance_deleted')
    count = 0
    while True:
        ret = waiter2.wait(
            DBInstanceIdentifier=db2,
            WaiterConfig={
                'Delay': 30,
                'MaxAttempts': 60
            }
        )
        if ret is None:
            message['DB2Delete'] = 'Successfully deleted ' + db2
            break
        else:
            count += 1
            if count >=4:
                message['DBInstanceDelete'] = 'DB Instance couldn\'t be deleted for 2 hours'
                sendSNSMessage(client, str(message), topicArn)
                os._exit(0) # Exit the program if db not deleted for 2 hours

# 4. Restore db2 from snapshot of db1
db2_restore_resp = restoreRDSInstance.restoreRDSInstance(client_rds, snapName1, dbInfo)

if db2_restore_resp is 'Error':
    message['DBRestore'] = 'DB Snapshot restore failed'
else:
    message['DBRestore'] = 'DB restore in progress; current status is: ' + str(db2_restore_resp)
sendSNSMessage(client_sns, str(message), topicArn)
