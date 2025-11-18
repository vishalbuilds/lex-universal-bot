from bot_engine.builder.bot_base import BotBase


class CreatBotIntent(BotBase):
    def __init__(
        self,
        intent_name,
        locale_id,
        bot_hook: list = None,
    ):

        self.intent_name = intent_name
        self.locale_id = locale_id
        self.bot_hook = bot_hook

    def create_bot_intent(
        self,
        utterances: list[str],
        slots: list[dict],  # [{'name':..., 'slotType':...}]
    ):
        try:
            # Slots mapping
            slot_list = []
            for s in slots:
                slot_list.append(
                    {
                        "slotName": s["name"],
                        "slotTypeId": s["slotType"],
                        "valueElicitationSetting": {"slotConstraint": "Optional"},
                    }
                )

            intent_definition = {
                "intentName": self.intent_name,
                "description": f"intent name: {self.intent_name} for bot_id: {self.bot_id} with locale_id: {self.locale_id}",
                "sampleUtterances": [{"utterance": u} for u in utterances],
            }

            if "fulfillmentCodeHook" in self.bot_hook or self.bot_hook == None:
                intent_definition["fulfillmentCodeHook"] = {
                    "enabled": True,
                    "active": True,
                }

            if "intentConfirmationSetting" in self.bot_hook:
                intent_definition["intentConfirmationSetting"] = {"enabled": True}

            response = self.lex_client.create_intent(
                botId=BotBase.BOT_NAME,
                botVersion=self.bot_version,
                localeId=self.locale_id,
                slots=slot_list,
                **intent_definition,
            )
            return response["intentId"]
        except Exception as e:
            raise
