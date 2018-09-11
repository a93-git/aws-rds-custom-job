""" Restore an RDS instance from a snapshot

    Usage: python3 restoreRDSInstance.py <snapName> <dbInfo>

    dbInfo is a dictionary containing the following information:
    
    -DBInstanceIdentifier
    -DBInstanceClass
    -AvailabilityZone
    -DBSubnetGroupName
    -MultiAZ
    -PubliclyAccessible
    -AutoMinorVersionUpgrade
    -LicenseModel
    -Engine
    -OptionGroupName
    -StorageType
    -CopyTagsToSnapshot
    -Port 
    """

def restoreRDSInstance(client, snapId, dbInfo):
    """ Restore RDS Instance from the given snapshot ID

    Parmeters: client: Interface to AWS RDS service
               snapId - ID of the RDS snapshot to restore from
               dbInfo - Dictionary with RDS instance info for restoration
    Return: Returns the current status of restored db

    Note: Doesn't apply to Aurora db
    """

    try:
        response = client.restore_db_instance_from_db_snapshot(
            DBInstanceIdentifier=dbInfo['DBInstanceIdentifier'],
            DBSnapshotIdentifier=snapId,
            DBInstanceClass=dbInfo['DBInstanceClass'],
            Port=dbInfo['Port'],
            AvailabilityZone=dbInfo['AvailabilityZone'],
            DBSubnetGroupName=dbInfo['DBSubnetGroupName'],
            MultiAZ=dbInfo['MultiAZ'],
            PubliclyAccessible=dbInfo['PubliclyAccessible'],
            AutoMinorVersionUpgrade=dbInfo['AutoMinorVersionUpgrade'],
            LicenseModel=dbInfo['LicenseModel'],
            Engine=dbInfo['Engine'],
            OptionGroupName=dbInfo['OptionGroupName'],
            StorageType=dbInfo['StorageType'],
            CopyTagsToSnapshot=True #dbInfo['CopyTagsToSnapshot'],
            )

        return response['DBInstance']['DBInstanceStatus']
    except:
        return 'Error'

if __name__=='__main__':
    import boto3
    import sys

    region = sys.argv[1]
    dbInfo = sys.argv[2]
    client = boto3.client('rds', region_name=region)

    
