from bot_engine.utils.yaml_loader import bot_config
from bot_engine.builder.instance_builder import CreatebotInstance
from bot_engine.builder.locale_builder import CreateBuildBotLocale
from bot_engine.builder.intent_builder import CreatBotIntent
from bot_engine.builder.slots_type_builder import CreateBotSlotsType
from bot_engine.builder.alias_builder import CreateBotAlias
from bot_engine.builder.bot_health_checker import BotHealthChecker
from bot_engine.builder.bot_base import BotBase
import time


class CreateUniversalBot:
    def __init__(self):
        self.do_operation()

    # create bot instance
    def _init_bot(self):
        try:
            return CreatebotInstance().create_bot_instance(
                bot_config.idleSessionTTLInSeconds,
                bot_config.dataPrivacy.childDirected,
                bot_config.roleArn,
            )
        except Exception as e:
            raise

    def _check_bot_status(self):
        try:
            bot_staus = BotHealthChecker().get_bot_status(self.bot_id)
            if bot_staus == "Available":
                return True
        except Exception as e:
            raise

    def _check_bot_locale_status(self, locale_id):
        try:
            bot_status = BotHealthChecker().get_bot_locale_status(
                self.bot_id, "DRAFT", locale_id
            )
            if bot_status == "NotBuilt":
                return True
        except Exception as e:
            raise

    # add lang, add intent, add utterance, add slots, add slotstype, build locale
    def _init_language_intent_slots(
        self,
    ):

        try:
            for locale in bot_config.locale:

                slots_type_id_set = {}
                intent_id_set = {}
                # create lang based on per locale
                CreateBuildBotLocale_obj = CreateBuildBotLocale(
                    self.bot_id, locale.localeId
                )
                CreateBuildBotLocale_obj.create_bot_locale(
                    locale.nluIntentConfidenceThreshold,
                    locale.voiceSettings.voiceId,
                    locale.voiceSettings.engine,
                )

                while True:
                    if self._check_bot_locale_status(locale.localeId):
                        break
                    time.sleep(5)

                # create slot type
                CreateBotSlotsType_obj = CreateBotSlotsType(
                    self.bot_id, locale.localeId, "DRAFT"
                )
                for slots in locale.slotDefinitions:
                    if slots.type == "Custom":
                        print(f"start cust slot {slots.name} ")
                        #  [{sampleValue1:[synonyms1,synonyms2....]},{sampleValue2:[synonyms11,synonyms21....]}]
                        slot_type_values_list_row = [
                            {Values.sampleValue: Values.synonyms}
                            for Values in slots.slotType.slotTypeValues
                        ]

                        slot_type_id = (
                            CreateBotSlotsType_obj.create_bot_slot_type_custom(
                                slots.name,
                                slots.description,
                                slot_type_values_list_row,
                                slots.slotType.resolutionStrategy,
                            )
                        )

                        slots_type_id_set[slots.name] = slot_type_id

                    if slots.type == "Extended":
                        print(f"start ex slot {slots.name} ")

                        slot_type_id = (
                            CreateBotSlotsType_obj.create_bot_slot_type_extended(
                                slots.name,
                                slots.description,
                                slots.slotType.parentSlotTypeSignature,
                                slots.slotType.regexPattern,
                                slots.slotType.resolutionStrategy,
                            )
                        )
                        slots_type_id_set[slots.name] = slot_type_id

                # create intent
                CreatBotIntent_obj = CreatBotIntent(
                    "DRAFT", locale.localeId, self.bot_id
                )
                for intent in locale.intents:

                    intent_id = CreatBotIntent_obj.create_bot_intent(
                        intent.name,
                        intent.description,
                        intent.sampleUtterances,
                        intent.codeHook,
                    )
                    intent_id_set[intent.name] = intent_id
                # add slot in intent
                for slot in locale.slotDefinitions:
                    # Get the intent_id for this slot
                    target_intent_id = intent_id_set.get(slot.intent)
                    print(target_intent_id)

                    if target_intent_id is None:
                        print(
                            f"WARNING: Slot '{slot.name}' references intent '{slot.intent}' which doesn't exist. Skipping."
                        )
                        continue

                    if slot.type == "Custom" or slot.type == "Extended":
                        print(
                            f"start slot cust and ext add in intent {slot.name} to intent {slot.intent}"
                        )
                        CreatBotIntent_obj.Create_slot_in_intent(
                            slot.name,
                            slots_type_id_set.get(slot.name, "AMAZON.AlphaNumeric"),
                            target_intent_id,
                            slot.slotConstraint,
                        )
                    elif slot.type == "BuiltIn":
                        print(
                            f"start slot builtin add in intent {slot.name} to intent {slot.intent}"
                        )
                        CreatBotIntent_obj.Create_slot_in_intent(
                            slot.name,
                            slot.slotTypeId,
                            target_intent_id,
                            slot.slotConstraint,
                        )

        except Exception as e:
            raise

    def _init_alias(self):
        try:
            # create alias
            CreateBotAlias_obj = CreateBotAlias(
                self.bot_id, bot_config.name, bot_config.description
            )
            bot_alias_id = CreateBotAlias_obj.create_bot_alias()

        except Exception as e:
            raise

    def do_operation(self):

        BotBase.set_base(
            bot_config.name,
            bot_config.description,
            bot_config.region,
        )

        self.bot_id = self._init_bot()

        while True:
            if self._check_bot_status():
                break
            time.sleep(5)
        self._init_language_intent_slots()


if __name__ == "__main__":
    c = CreateUniversalBot()
    print(c)
