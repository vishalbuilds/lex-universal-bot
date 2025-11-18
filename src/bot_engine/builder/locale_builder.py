from common.lex_v2_client import lex_v2_client
from typing import Literal


class BotLocaleDefinitions:
    def __init__(
        self,
        bot_id: str,
        bot_version: str,
        region_name: str,
        locale_id: Literal["en_IN", "en_US"] = "en_US",
    ):
        self.bot_id = bot_id
        self.bot_version = bot_version
        self.locale_id = locale_id
        self.lex_client = lex_v2_client(region_name)

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
            response = self.lex_client.create_bot_locale(
                description=f"bot_id: {self.bot_id}, locale_id: {self.locale_id}",
                nluIntentConfidenceThreshold=nlu_intent_confidence_threshold,
                voiceSettings={
                    "voiceId": voice_id,
                    "engine": engine,
                },
            )
            return response
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
            response = self.lex_client.build_bot_locale(
                botId=self.bot_id, botVersion=self.bot_version, localeId=self.locale_id
            )
            return response
        except Exception as e:
            raise
