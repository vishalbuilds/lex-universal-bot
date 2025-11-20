from bot_engine.builder.bot_base import BotBase
import logging
import time
from typing import Dict, List


logger = logging.getLogger(__name__)


class BotCreationException(Exception):
    """Base exception for bot creation failures"""

    pass


class ConfigurationException(BotCreationException):
    """Exception for configuration-related errors"""

    pass


class CreateBotAlias(BotBase):
    """Handles bot alias creation and configuration"""

    def __init__(self, bot_id: str, alias_name: str, description: str):
        self.bot_id = bot_id
        self.alias_name = alias_name
        self.description = description

    def create_bot_alias(self) -> str:
        """
        Create a new bot alias.

        Returns:
            Alias ID

        Raises:
            BotCreationException: If creation fails
        """
        try:
            logger.info(f"Creating bot alias: {self.alias_name}")

            response = self.LEX_CLIENT.create_bot_alias(
                botId=self.bot_id,
                botAliasName=self.alias_name,
                description=self.description,
            )

            alias_id = response.get("botAliasId")
            logger.info(f"Bot alias created: {self.alias_name} ({alias_id})")
            logger.debug("Waiting 10 seconds for AWS Lex to process...")
            time.sleep(10)
            return alias_id

        except Exception as e:
            logger.error(f"Failed to create bot alias {self.alias_name}: {e}")
            raise BotCreationException(f"Alias creation failed: {e}") from e

    def update_bot_alias(
        self,
        bot_alias_id: str,
        bot_version: str,
        alias_locale_settings_list: List[Dict[str, str]],
    ) -> Dict:
        """
        Update bot alias with locale settings and code hooks.

        Args:
            bot_alias_id: Alias ID to update
            bot_version: Bot version to link
            alias_locale_settings_list: List of locale settings

        Returns:
            API response

        Raises:
            BotCreationException: If update fails
        """
        try:
            logger.info(f"Updating bot alias: {bot_alias_id}")

            if not alias_locale_settings_list:
                raise ValueError("Alias locale settings list cannot be empty")

            # Build locale settings
            alias_locale_settings = self._build_locale_settings(
                alias_locale_settings_list
            )

            response = self.LEX_CLIENT.update_bot_alias(
                botAliasName=self.alias_name,
                botId=self.bot_id,
                botVersion=bot_version,
                botAliasId=bot_alias_id,
                botAliasLocaleSettings=alias_locale_settings,
            )

            logger.info(f"Bot alias updated: {bot_alias_id}")
            logger.debug("Waiting 10 seconds for AWS Lex to process...")
            time.sleep(10)
            return response

        except Exception as e:
            logger.error(f"Failed to update bot alias {bot_alias_id}: {e}")
            raise BotCreationException(f"Alias update failed: {e}") from e

    @staticmethod
    def _build_locale_settings(
        alias_locale_settings_list: List[Dict[str, str]],
    ) -> Dict:
        """Transform locale settings list to API format"""
        alias_locale_settings = {}

        for locale_setting in alias_locale_settings_list:
            locale_id = locale_setting.get("Locale")
            lambda_arn = locale_setting.get("Lambda_arn")
            code_hook_version = locale_setting.get("codeHookInterfaceVersion")

            if not all([locale_id, lambda_arn, code_hook_version]):
                raise ConfigurationException(
                    f"Invalid locale setting: missing required fields. Got {locale_setting}"
                )

            alias_locale_settings[locale_id] = {
                "enabled": True,
                "codeHookSpecification": {
                    "lambdaCodeHook": {
                        "lambdaARN": lambda_arn,
                        "codeHookInterfaceVersion": code_hook_version,
                    }
                },
            }

        return alias_locale_settings
