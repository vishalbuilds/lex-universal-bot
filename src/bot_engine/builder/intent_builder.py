from bot_engine.builder.bot_base import BotBase


class CreatBotIntent(BotBase):
    def __init__(self, bot_version, locale_id, bot_id):
        self.bot_version = bot_version
        self.locale_id = locale_id
        self.bot_id = bot_id

    def create_bot_intent(
        self,
        intent_name,
        description,
        utterances: list[str],
        intent_hook: list,
    ):
        try:

            intent_definition = {}

            if "fulfillmentCodeHook" in intent_hook:
                intent_definition["fulfillmentCodeHook"] = {
                    "enabled": True,
                    "active": True,
                }

            if "intentConfirmationSetting" in intent_hook:
                intent_definition["intentConfirmationSetting"] = {
                    "active": True,
                    "promptSpecification": {
                        "messageGroups": [
                            {
                                "message": {
                                    "plainTextMessage": {"value": "Please confirm"}
                                }
                            }
                        ],
                        "maxRetries": 2,
                    },
                }

            response = self.LEX_CLIENT.create_intent(
                intentName=intent_name,
                description=description,
                botId=self.bot_id,
                botVersion=self.bot_version,
                sampleUtterances=[{"utterance": u} for u in utterances],
                localeId=self.locale_id,
                **intent_definition,
            )
            return response["intentId"]
        except Exception as e:
            raise

    def Create_slot_in_intent(
        self,
        slot_name,
        slot_type_id,
        intent_id,
        slot_constraint="Optional",
    ):
        try:
            response = self.LEX_CLIENT.create_slot(
                botId=self.bot_id,
                botVersion=self.bot_version,
                localeId=self.locale_id,
                intentId=intent_id,
                slotName=slot_name,
                slotTypeId=slot_type_id,
                valueElicitationSetting={
                    "slotConstraint": slot_constraint,
                },
            )
            return response
        except Exception as e:
            raise
