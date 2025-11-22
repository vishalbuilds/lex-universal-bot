import logging
import time

from typing import Dict, Literal
from bot_engine.builder.bot_base import BotBase


logger = logging.getLogger(__name__)


class BotCreationException(Exception):
    """Base exception for bot creation failures"""

    pass


class CreateBuildBotLocale(BotBase):
    """Handles bot locale creation and building"""

    def __init__(self, bot_id: str, locale_id: str):
        self.bot_id = bot_id
        self.locale_id = locale_id

    def create_bot_locale(
        self,
        nlu_intent_confidence_threshold: float = 0.4,
        voice_id: str = "Joanna",
        engine: Literal["standard", "neural"] = "neural",
    ) -> str:
        """
        Create a new locale for the bot.

        Args:
            nlu_intent_confidence_threshold: NLU confidence threshold (0-1)
            voice_id: Voice ID for text-to-speech
            engine: Voice engine (standard or neural)

        Returns:
            Bot version

        Raises:
            BotCreationException: If locale creation fails
        """
        try:
            logger.info(f"Creating locale {self.locale_id} for bot {self.bot_id}")

            response = self.LEX_CLIENT.create_bot_locale(
                botId=self.bot_id,
                localeId=self.locale_id,
                description=f"Bot: {self.bot_id}, Locale: {self.locale_id}",
                botVersion="DRAFT",
                nluIntentConfidenceThreshold=nlu_intent_confidence_threshold,
                voiceSettings={
                    "voiceId": voice_id,
                    "engine": engine,
                },
            )

            bot_version = response.get("botVersion")
            logger.info(f"Locale created: {self.locale_id}, version: {bot_version}")
            logger.debug("Waiting 10 seconds for AWS Lex to process...")
            time.sleep(10)
            return bot_version

        except Exception as e:
            logger.error(f"Failed to create locale {self.locale_id}: {e}")
            raise BotCreationException(f"Locale creation failed: {e}") from e

    def build_bot_locale(self, bot_version: str = "DRAFT") -> Dict:
        """
        Build a bot locale to apply all changes.

        Args:
            bot_version: Bot version to build

        Returns:
            API response

        Raises:
            BotCreationException: If build fails
        """
        try:
            logger.info(f"Building locale {self.locale_id} for version {bot_version}")

            response = self.LEX_CLIENT.build_bot_locale(
                botId=self.bot_id,
                localeId=self.locale_id,
                botVersion=bot_version,
            )

            logger.info(f"Locale build initiated: {self.locale_id}")
            logger.debug("Waiting 10 seconds for AWS Lex to process...")
            time.sleep(10)
            return response

        except Exception as e:
            logger.error(f"Failed to build locale {self.locale_id}: {e}")
            raise BotCreationException(f"Locale build failed: {e}") from e
