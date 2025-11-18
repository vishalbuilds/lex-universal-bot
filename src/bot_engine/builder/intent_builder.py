from common.lex_v2_client import lex_v2_client


class CreatBotIntent:
    def __init__(self, bot_id, intent_name, locale_id, bot_version, region_name):
        self.bot_id = bot_id
        self.intent_name = intent_name
        self.locale_id = locale_id
        self.bot_version = bot_version
        self.lex_client = lex_v2_client(region_name)

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
                "fulfillmentCodeHook": {"enabled": True, "active": True},
            }
            response = self.lex_client.create_intent(
                botId=self.bot_id,
                botVersion=self.bot_version,
                localeId=self.locale_id,
                slots=slot_list,
                **intent_definition,
            )
            return response
        except Exception as e:
            raise
