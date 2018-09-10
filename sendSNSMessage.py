""" Send SNS message for a given topic in the given region"""

def sendSNSMessage(client, message, topicArn):
    """ Sends string message to sns topics with Email endpoints

    Arguments: topicArn - arn of sns topic to which the message is published
               message - message to publish
               client - sns client with region information
    Returns: Returns 0 on success and 1 on failure
    """

    try:
        response = client.publish(TopicArn=topicArn,
            Message=message)
    except:
        raise

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return 0
    else:
        return 1
