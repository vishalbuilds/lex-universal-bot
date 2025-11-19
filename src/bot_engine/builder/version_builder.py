from bot_engine.builder.bot_base import BotBase
import time


class CreateBotVersion(BotBase):
    def __init__(self, bot_id):
        self.bot_id = bot_id

    def create_bot_version(self, description, locale_id, base_version):
        response = self.LEX_CLIENT.create_bot_version(
            botId=self.bot_id,
            description=description,
            botVersionLocaleSpecification={
                locale_id: {"sourceBotVersion": base_version}
            },
        )
        while True:
            if response["botStatus"] == "Available":
                break
            time.sleep(5)
        return
