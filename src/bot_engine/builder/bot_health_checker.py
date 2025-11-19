from bot_engine.builder.bot_base import BotBase


class BotHealthChecker(BotBase):

    def get_bot_status(self, bot_id):
        try:
            response = self.LEX_CLIENT.describe_bot(botId=bot_id)
            return response["botStatus"]
        except Exception as e:
            raise

    def get_bot_locale_status(self, bot_id, bot_version, locale_id):
        try:
            response = self.LEX_CLIENT.describe_bot_locale(
                botId=bot_id, botVersion=bot_version, localeId=locale_id
            )
            return response["botLocaleStatus"]
        except Exception as e:
            raise

    # def get_bot_locale_status(self, bot_id, bot_version, locale_id, intent_id):
    #     try:
    #         response = self.LEX_CLIENT.describe_intent(
    #             intentId=intent_id,
    #             botId=bot_id,
    #             botVersion=bot_version,
    #             localeId=locale_id,
    #         )
    #         return response["botLocaleStatus"]
    #     except Exception as e:
    #         raise
