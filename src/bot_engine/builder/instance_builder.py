"""
Utilities for Amazon Lex V2 operations used by the strategies package.

This class provides low-level, descriptive methods for common and advanced Amazon Lex V2 operations,
including bot creation, intent management, slot type handling, versioning, and publishing.
It also supports runtime interactions for sending user input and retrieving responses.

All methods include logging and error handling for robust production use.
"""

from bot_engine.builder.bot_base import BotBase
from bot_engine.builder.service_role_builder import create_bot_service_role_arn


class CreatebotInstance(BotBase):

    def create_bot_instance(
        self,
        idle_session_ttl_in_seconds: int = 300,
        childDirected: str = False,
        role_arn: str = None,
    ):
        """
        Create aws lexV2 bot.

        Args:
            role_arn: lexV2 role arn to execute process. if none will create auto
            idle_session_ttl_in_seconds: session timeout wait time
        Returns:
                bot id

        Raises:

        """
        try:
            response = self.LEX_CLIENT.create_bot(
                botName=self.BOT_NAME,
                description=self.DESCRIPTION,
                roleArn=(
                    role_arn if role_arn else create_bot_service_role_arn(self.BOT_NAME)
                ),
                idleSessionTTLInSeconds=idle_session_ttl_in_seconds,
                dataPrivacy={"childDirected": childDirected},
                botTags=self.BOT_TAGS,
                testBotAliasTags={"TestAliasName": f"{self.BOT_NAME}-test-alias"},
                botType="Bot",
            )
            return response.get("botId")

        except Exception as e:
            raise
