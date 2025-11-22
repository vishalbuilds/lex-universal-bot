import logging
from datetime import datetime
from typing import Dict

from common.lex_v2_client import lex_v2_client


logger = logging.getLogger(__name__)


class BotBase:
    """Base class for bot builders with shared AWS Lex client and configuration"""

    BOT_NAME: str = ""
    DESCRIPTION: str = ""
    LEX_CLIENT = None
    BOT_TAGS: Dict[str, str] = {}

    @classmethod
    def set_base(cls, bot_name: str, description: str, region_name: str) -> None:
        """Initialize base configuration and AWS clients"""
        try:
            logger.info(
                f"Initializing BotBase with name: {bot_name}, region: {region_name}"
            )
            cls.BOT_NAME = bot_name
            cls.DESCRIPTION = description
            cls.LEX_CLIENT = lex_v2_client(region_name)
            cls.BOT_TAGS = {
                "name": bot_name,
                "created_time": datetime.now().isoformat(),
            }
            logger.info("BotBase initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize BotBase: {e}")
            raise
