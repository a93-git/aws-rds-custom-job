""" Create the snapshot of the given RDS identifier """

def createRDSSnapshot(client, dbId, snapName):
    """ Create snapshot of the given db instance

    Snapshot name should be snapName
    
    Parameters: client - interface to AWS' RDS service
                dbId - DB Instance identifier of the RDS isntance to create the
                snapshot
                snapName - Name of the snapshot
    Return:

    Note: 1. It won't create snapshot of Aurora systems
          2. Tags can't be specified, need to add them manually
    """

    try:
        response = client.create_db_snapshot(
            DBSnapshotIdentifier=snapName,
            DBInstanceIdentifier=dbId
            )
    
        return response['DBSnapshot']['Status']
    except:
        return 'Error creating snapshot of dbId: ' + dbId

if __name__=='__main__':
    import sys
    import boto3
    import datetime

    region = sys.argv[1]
    dbId = sys.argv[2]

    snapName = dbId + '-' + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H-%M') + '-boto'
    client = boto3.client('rds', region_name=region)

    message = []

    message['DBIdentifier'] = dbId

    try:
        message['SnapStatus'] = createRDSSnapshot(client, dbId, snapName)
    except:
        message['SnapStatus'] = 'Error creating snapshot'
    
    # Do something with message: either print it out to console or send a
    # message to an SNS topic

    print(message)


