from bot_engine.builder.bot_base import BotBase
from common.iam_client import iam_client
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class BotCreationException(Exception):
    """Base exception for bot creation failures"""

    pass


def create_bot_service_role_arn(role_name: str) -> str:
    """Create IAM service-linked role for Lex V2"""
    try:
        logger.info(f"Creating service-linked role for Lex: {role_name}")
        response = iam_client().create_service_linked_role(
            AWSServiceName="lex.amazonaws.com",
            Description=f"IAM service linked role: {role_name} for Lex V2",
        )
        arn = response["Role"]["Arn"]
        logger.info(f"Service-linked role created: {arn}")
        return arn
    except Exception as e:
        logger.error(f"Failed to create service-linked role: {e}")
        raise BotCreationException(f"Service role creation failed: {e}") from e


class CreateBotInstance(BotBase):
    """Handles bot instance creation and updates"""

    def create_bot_instance(
        self,
        idle_session_ttl_in_seconds: int = 300,
        child_directed: bool = False,
        role_arn: Optional[str] = None,
    ) -> str:
        """
        Create a new Lex V2 bot instance.

        Args:
            idle_session_ttl_in_seconds: Session timeout in seconds
            child_directed: Whether bot is directed at children
            role_arn: Optional IAM role ARN (auto-created if not provided)

        Returns:
            Bot ID

        Raises:
            BotCreationException: If bot creation fails
        """
        try:
            logger.info(f"Creating bot instance: {self.BOT_NAME}")

            # Use provided role or create new one
            final_role_arn = role_arn or create_bot_service_role_arn(self.BOT_NAME)

            response = self.LEX_CLIENT.create_bot(
                botName=self.BOT_NAME,
                description=self.DESCRIPTION,
                roleArn=final_role_arn,
                idleSessionTTLInSeconds=idle_session_ttl_in_seconds,
                dataPrivacy={"childDirected": child_directed},
                botTags=self.BOT_TAGS,
                testBotAliasTags={"TestAliasName": f"{self.BOT_NAME}-test-alias"},
                botType="Bot",
            )

            bot_id = response.get("botId")
            if not bot_id:
                raise ValueError("Bot creation response missing botId")

            logger.info(f"Bot instance created successfully: {bot_id}")
            logger.debug("Waiting 10 seconds for AWS Lex to process...")
            time.sleep(10)
            return bot_id

        except Exception as e:
            logger.error(f"Failed to create bot instance: {e}")
            raise BotCreationException(f"Bot instance creation failed: {e}") from e

    def update_bot_instance(
        self,
        bot_id: str,
        idle_session_ttl_in_seconds: Optional[int] = None,
        description: Optional[str] = None,
    ) -> str:
        """
        Update an existing bot instance properties.

        Args:
            bot_id: Bot ID to update
            idle_session_ttl_in_seconds: Optional new session timeout
            description: Optional new description

        Returns:
            Updated bot ID

        Raises:
            BotCreationException: If update fails
        """
        try:
            logger.info(f"Updating bot instance: {bot_id}")

            # Fetch current bot configuration
            current_bot = self.LEX_CLIENT.describe_bot(botId=bot_id)

            update_params = {
                "botId": bot_id,
                "botName": self.BOT_NAME,
                "roleArn": current_bot["roleArn"],
                "dataPrivacy": current_bot["dataPrivacy"],
                "description": description or self.DESCRIPTION,
                "idleSessionTTLInSeconds": (
                    idle_session_ttl_in_seconds
                    or current_bot["idleSessionTTLInSeconds"]
                ),
            }

            response = self.LEX_CLIENT.update_bot(**update_params)
            updated_bot_id = response.get("botId")

            logger.info(f"Bot instance updated: {updated_bot_id}")
            logger.debug("Waiting 10 seconds for AWS Lex to process...")
            time.sleep(10)
            return updated_bot_id

        except Exception as e:
            logger.error(f"Failed to update bot instance: {e}")
            raise BotCreationException(f"Bot update failed: {e}") from e
