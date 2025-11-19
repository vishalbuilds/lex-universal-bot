from bot_engine.builder.bot_base import BotBase
import time


class CreateBotVersion(BotBase):
    def __init__(self, bot_id):
        self.bot_id = bot_id

    def create_bot_version(
        self, description, bot_version_locale_specification: list[dict]
    ):

        locale_spec = {}
        for locale_dict in bot_version_locale_specification:
            for locale_id, base_version in locale_dict.items():
                locale_spec[locale_id] = {"sourceBotVersion": base_version}

        response = self.LEX_CLIENT.create_bot_version(
            botId=self.bot_id,
            description=description,
            botVersionLocaleSpecification=locale_spec,
        )

        bot_version = response["botVersion"]

        while True:
            time.sleep(5)
            version_status = self.LEX_CLIENT.describe_bot_version(
                botId=self.bot_id, botVersion=bot_version
            )

            if version_status["botStatus"] == "Available":
                break
            elif version_status["botStatus"] == "Failed":
                raise Exception(
                    f"Bot version creation failed: {version_status.get('failureReasons', [])}"
                )

        return bot_version
