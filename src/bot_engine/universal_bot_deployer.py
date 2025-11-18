from bot_engine.utils.yaml_loader import bot_config
from bot_engine.builder.instance_builder import CreatebotInstance
from bot_engine.builder.locale_builder import CreateBuildBotLocale
from bot_engine.builder.intent_builder import CreatBotIntent
from bot_engine.builder.slots_type_builder import CreateBotSlotsType
from bot_engine.builder.alias_builder import CreateBotAlias
from bot_engine.builder.bot_base import BotBase


class CreateUniversalBot:
    def __init__(self):

        BotBase.set_base(
            bot_config.name,
            bot_config.description,
            "1.0.0",
            bot_config.region,
        )
        self.bot_id = self._init_bot()
        self._init_language()

    # create bot instance
    def _init_bot(self):
        try:
            return CreatebotInstance.create_bot_instance(
                bot_config.idleSessionTTLInSeconds, bot_config.dataPrivacy.childDirected
            )
        except Exception as e:
            raise

    # add lang, add intent, add utterance, add slots, add slotstype, build locale
    def _init_language(
        self,
    ):
        try:
            for i in len(bot_config.locale):

                locale = bot_config.locale[i]
                # create lang
                BotLocaleDefinitions_obj = CreateBuildBotLocale(
                    self.bot_id, locale.locale_id
                )
                BotLocaleDefinitions_obj.create_bot_locale(
                    self.locale.nluIntentConfidenceThreshold,
                    self.locale.voiceSettings.voiceId,
                    self.locale.voiceSettings.engine,
                )
                # create slot type

                # create intent
                self.intent_id = CreatBotIntent(
                    locale.name, locale.locale_id, locale.fulfillmentCodeHook
                ).create_bot_intent

        except Exception as e:
            raise

    # def _init_alias(self):
