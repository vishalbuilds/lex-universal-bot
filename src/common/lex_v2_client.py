import boto3


def lex_v2_client(region_name: str = "us-east-1"):
    """
    arg:
        region_name: AWS region name (default:us-east-1 )
    Return:
         amazon lex V2 client
    """
    return boto3.client("lexv2-models", region_name=region_name)
