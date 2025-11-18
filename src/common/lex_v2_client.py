import boto3


def lex_v2_client(region_name: str = "us-east-1"):
    """
    arg:
        region_name: AWS region name (default:us-east-1 )
    Return:
         amazon lex V2 client
    """
    return boto3.client("lexv2-models", region_name=region_name)


region = "us-east-1"  # use the region where your bot exists
bot_id = "4LEWMR7I5F"

client = boto3.client("lexv2-models", region_name=region)

# Create an alias pointing to the DRAFT version
response = client.build_bot_locale(
    botId="YOZ7FRJCOQ",
    botVersion="DRAFT",
    localeId="en_US",
)

print(response)
