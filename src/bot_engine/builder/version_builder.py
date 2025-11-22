import logging
import time
from typing import Dict, List
from bot_engine.builder.bot_base import BotBase


logger = logging.getLogger(__name__)


class BotCreationException(Exception):
    """Base exception for bot creation failures"""

    pass


class CreateBotVersion(BotBase):
    """Handles bot version creation and monitoring"""

    MAX_RETRIES = 24  # 2 minutes with 5-second intervals
    RETRY_DELAY = 5

    def __init__(self, bot_id: str):
        self.bot_id = bot_id

    def create_bot_version(
        self,
        description: str,
        bot_version_locale_specification: List[Dict[str, str]],
    ) -> str:
        """
        Create a new bot version from DRAFT.

        Args:
            description: Version description
            bot_version_locale_specification: List of locale specifications

        Returns:
            Bot version string

        Raises:
            BotCreationException: If creation fails
        """
        try:
            logger.info("Creating bot version")

            # Transform locale specifications
            locale_spec = {}
            for locale_dict in bot_version_locale_specification:
                for locale_id, base_version in locale_dict.items():
                    locale_spec[locale_id] = {"sourceBotVersion": base_version}

            response = self.LEX_CLIENT.create_bot_version(
                botId=self.bot_id,
                description=description,
                botVersionLocaleSpecification=locale_spec,
            )

            bot_version = response.get("botVersion")
            if not bot_version:
                raise ValueError("Bot version creation response missing version")

            logger.info(
                f"Bot version created: {bot_version}, waiting for completion..."
            )

            # Wait for version to be available
            self._wait_for_version_availability(bot_version)

            logger.info(f"Bot version ready: {bot_version}")
            logger.debug("Waiting 10 seconds for AWS Lex to process...")
            time.sleep(10)
            return bot_version

        except Exception as e:
            logger.error(f"Failed to create bot version: {e}")
            raise BotCreationException(f"Bot version creation failed: {e}") from e

    def _wait_for_version_availability(self, bot_version: str) -> None:
        """
        Poll for bot version to become available.

        Args:
            bot_version: Bot version to monitor

        Raises:
            BotCreationException: If version fails or times out
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                time.sleep(self.RETRY_DELAY)

                version_status = self.LEX_CLIENT.describe_bot_version(
                    botId=self.bot_id,
                    botVersion=bot_version,
                )

                status = version_status.get("botStatus", "Unknown")
                logger.debug(
                    f"Version {bot_version} status: {status} (attempt {attempt + 1})"
                )

                if status == "Available":
                    logger.info(f"Bot version {bot_version} is available")
                    return

                elif status == "Failed":
                    failure_reasons = version_status.get("failureReasons", [])
                    raise BotCreationException(
                        f"Bot version creation failed: {failure_reasons}"
                    )

            except Exception as e:
                if isinstance(e, BotCreationException):
                    raise
                logger.warning(f"Status check attempt {attempt + 1} failed: {e}")

        raise BotCreationException(
            f"Bot version {bot_version} failed to reach Available status "
            f"after {self.MAX_RETRIES} attempts"
        )
