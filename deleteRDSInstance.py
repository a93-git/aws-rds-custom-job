""" Delte the given RDS instance after creating its snapshot 

    Usage: python3 deleteRDSSnapshot.py <region> <dbId>"""

def deleteRDSInstance(client, dbId, snapName):
    """ Delete the given RDS instance (dbId) after creating its snapshot

    Params: client - an interface with RDS service
            dbId - DB Instance identifier of the RDS to delete
            snapName - Name of the snapshot to be created
    Return: 

    Note: This WILL NOT work with db clusters
    """

    try:
        response = client.delete_db_instance(
            DBInstanceIdentifier=dbId,
            SkipFinalSnapshot=True,
            FinalDBSnapshotIdentifier=snapName
            )
    
        return response
    
    except:
        return 'Error'

if __name__=='__main__':
    import boto3
    import datetime
    import sys

    region = sys.argv[1]
    dbId = sys.argv[2]

    snapName = dbId + '-' + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H-%M') + '-boto'

    client = boto3. client('rds', region_name=region)
    
    message['DBIdentifier'] = dbId
    message['DBStatus'] = deleteRDSInstance(client, dbId, snapName)

    print(message)
