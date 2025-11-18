from bot_engine.builder.bot_base import BotBase


class CreateBotAlias(BotBase):
    def __init__(self, bot_id, alias_name, description):
        self.bot_id = bot_id
        self.alias_name = alias_name
        self.description = description

    def create_bot_alias(self):
        try:
            response = self.lex_client.create_bot_alias(
                botAliasName=self.alias_name,
                botId=self.bot_id,
                description=self.description,
            )
            return response["botAliasId"]
        except Exception as e:
            raise

    def update_bot_alias(
        self, bot_alias_id, Alias_Locale_Settings_list: list[dict]
    ):  # [{'Locale':..., 'Lambda_arn':...}]s)
        try:
            Alias_Locale_Settings = {}
            for Alias_Locale in Alias_Locale_Settings_list:
                Alias_Locale_Settings.update(
                    {
                        Alias_Locale["Locale"]: {
                            "enabled": True,
                            "codeHookSpecification": {
                                "lambdaCodeHook": {
                                    "lambdaARN": Alias_Locale["Lambda_arn"],
                                    "codeHookInterfaceVersion": "1.0",
                                }
                            },
                        }
                    }
                )

            response = self.lex_client.update_bot_alias(
                botAliasName=self.alias_name,
                botId=self.bot_id,
                botAliasId=bot_alias_id
                botAliasLocaleSettings=Alias_Locale_Settings,
            )
            return response
        except Exception as e:
            raise
