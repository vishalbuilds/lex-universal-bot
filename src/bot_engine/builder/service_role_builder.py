from common.iam_client import iam_client


def create_bot_service_role_arn(role_name):
    response = iam_client().create_service_linked_role(
        AWSServiceName="lex.amazonaws.com",
        Description=f"iam service linked role: {role_name} for lex V2 to create bot",
    )
    return response["Role"]["Arn"]
