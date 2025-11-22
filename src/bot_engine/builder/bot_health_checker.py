import logging

from bot_engine.builder.bot_base import BotBase


logger = logging.getLogger(__name__)


class BotCreationException(Exception):
    """Base exception for bot creation failures"""

    pass


class BotStatusException(BotCreationException):
    """Exception for bot status check failures"""

    pass


class BotHealthChecker(BotBase):
    """Handles bot and bot locale health checks"""

    def get_bot_status(self, bot_id: str) -> str:
        """
        Get current bot status.

        Args:
            bot_id: Bot ID to check

        Returns:
            Bot status string

        Raises:
            BotStatusException: If status check fails
        """
        try:
            logger.debug(f"Checking bot status: {bot_id}")
            response = self.LEX_CLIENT.describe_bot(botId=bot_id)
            status = response.get("botStatus", "Unknown")
            logger.debug(f"Bot {bot_id} status: {status}")
            return status
        except Exception as e:
            logger.error(f"Failed to get bot status for {bot_id}: {e}")
            raise BotStatusException(f"Bot status check failed: {e}") from e

    def get_bot_locale_status(
        self, bot_id: str, bot_version: str, locale_id: str
    ) -> str:
        """
        Get current bot locale status.

        Args:
            bot_id: Bot ID
            bot_version: Bot version (e.g., "DRAFT")
            locale_id: Locale ID to check

        Returns:
            Locale status string

        Raises:
            BotStatusException: If status check fails
        """
        try:
            logger.debug(f"Checking locale status - Bot: {bot_id}, Locale: {locale_id}")
            response = self.LEX_CLIENT.describe_bot_locale(
                botId=bot_id,
                botVersion=bot_version,
                localeId=locale_id,
            )
            status = response.get("botLocaleStatus", "Unknown")
            logger.debug(f"Locale {locale_id} status: {status}")
            return status
        except Exception as e:
            logger.error(f"Failed to get locale status for {locale_id}: {e}")
            raise BotStatusException(f"Locale status check failed: {e}") from e
