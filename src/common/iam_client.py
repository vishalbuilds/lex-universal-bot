import boto3


def iam_client():
    """
    arg:
        region_name: AWS region name (default:us-east-1 )
    Return:
         amazon iam client
    """
    return boto3.client("iam")
