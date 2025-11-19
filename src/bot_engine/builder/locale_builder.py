from bot_engine.builder.bot_base import BotBase
from typing import Literal


class CreateBuildBotLocale(BotBase):
    def __init__(self, bot_id, locale_id):
        self.bot_id = bot_id
        self.locale_id = locale_id

    def create_bot_locale(
        self,
        nlu_intent_confidence_threshold: float = 0.4,
        voice_id: str = "Joanna",
        engine: Literal["standard", "neural"] = "neural",
    ):
        """create lexV2 locale.

        Args:
            bot_version: The version of the bot to build. This can only be the draft version of the bot.
            locale_id: The locale to build either en_US or en_IN. Default is en_US.

        Returns:
                api response

        Raises:

        """
        try:
            response = self.LEX_CLIENT.create_bot_locale(
                botId=self.bot_id,
                localeId=self.locale_id,
                description=f"bot_id: {self.bot_id}, locale_id: {self.locale_id}",
                botVersion="DRAFT",
                nluIntentConfidenceThreshold=nlu_intent_confidence_threshold,
                voiceSettings={
                    "voiceId": voice_id,
                    "engine": engine,
                },
            )
            return response["botVersion"]
        except Exception as e:
            raise

    def build_bot_locale(self):
        """build lexV2 locale.

        Args:
            bot_version: The version of the bot to build. This can only be the draft version of the bot.
            locale_id: The locale to build either en_US or en_IN. Default is en_US.

        Returns:
                api response

        Raises:

        """
        try:
            response = self.LEX_CLIENT.build_bot_locale(
                botId=self.bot_id,
                localeId=self.locale_id,
                botVersion="DRAFT",
            )
            return response
        except Exception as e:
            raise
