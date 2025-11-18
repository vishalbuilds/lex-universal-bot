from common.lex_v2_client import lex_v2_client


class CreateBotAlias:
    def __init__(
        self,
        bot_id,
        alias_name,
        bot_version,
        region_name,
        Alias_Locale_Settings_list: list[dict],  # [{'Locale':..., 'Lambda_arn':...}]
    ):
        self.bot_id = bot_id
        self.alias_name = alias_name
        self.bot_version = bot_version
        self.lex_client = lex_v2_client(region_name)
        self.Alias_Locale_Settings_list = Alias_Locale_Settings_list

    def create_bot_alias(self):
        try:
            Alias_Locale_Settings = {}
            for Alias_Locale in self.Alias_Locale_Settings_list:
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

            response = self.lex_client.create_bot_alias(
                botAliasName=self.alias_name,
                botId=self.bot_id,
                description=f"bot_id: {self.bot_id}, alias_name: {self.alias_name}",
                botVersion=self.bot_version,
                botAliasLocaleSettings=Alias_Locale_Settings,
            )
            return response
        except Exception as e:
            raise
