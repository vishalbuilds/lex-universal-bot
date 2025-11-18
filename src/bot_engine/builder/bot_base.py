from common.lex_v2_client import lex_v2_client
import datetime


class BotBase:

    # Class variables shared across all children
    BOT_NAME = ""
    DESCRIPTION = ""
    LEX_CLIENT = None
    BOT_TAGS = {}

    @classmethod
    def set_base(cls, bot_name, description, bot_version, region_name):

        cls.BOT_NAME = bot_name
        cls.DESCRIPTION = description
        cls.LEX_CLIENT = lex_v2_client(region_name)
        cls.BOT_TAGS = {
            "name": bot_name,
            "created_time": datetime.datetime.now().isoformat(),
        }
