"""
Utilities for Amazon Lex V2 operations used by the strategies package.

This class provides low-level, descriptive methods for common and advanced Amazon Lex V2 operations,
including bot creation, intent management, slot type handling, versioning, and publishing.
It also supports runtime interactions for sending user input and retrieving responses.

All methods include logging and error handling for robust production use.
"""

import datetime
from common.lex_v2_client import lex_v2_client
from bot_infra.lex_service_role_creator import lex_service_role_arn
import os
from typing import Literal


region_name = os.environ.get("REGION_NAME")


class CreateInstance:
    def __init__(self, bot_name: str, description: str):
        self.bot_name = bot_name
        self.description = description
        self.lex_client = lex_v2_client(region_name)

    def create_instance(
        self,
        role_arn: str = None,
        idle_session_ttl_in_seconds: int = 300,
    ):
        """
        Create aws lexV2 bot.

        Args:
            role_arn: lexV2 role arn to exicute process.
            idle_session_ttl_in_seconds: session timeout wait time
        Returns:
                bot id

        Raises:

        """
        try:
            response = self.lex_client.create_bot(
                botName=self.bot_name,
                description=self.description,
                roleArn=role_arn if role_arn else lex_service_role_arn(self.bot_name),
                idleSessionTTLInSeconds=idle_session_ttl_in_seconds,
                dataPrivacy={"childDirected": False},
                botTags={
                    "name": self.bot_name,
                    "created_time": datetime.datetime.now().isoformat(),
                },
                testBotAliasTags={"TestAliasName": f"{self.bot_name}-test-alias"},
                botType="Bot",
            )
            return response.get("botId")
        except Exception as e:
            raise
