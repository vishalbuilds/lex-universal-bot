from typing import Literal, Optional
from bot_engine.builder.bot_base import BotBase


class CreateBotSlotsType(BotBase):
    def __init__(self, bot_id, locale_id, bot_version):
        self.bot_id = bot_id
        self.locale_id = locale_id
        self.bot_version = bot_version

    def create_bot_slot_type_custom(
        self,
        slot_type_name,
        description,
        slot_type_values_list_row: list[
            dict
        ],  # [{sampleValue1:[synonyms1,synonyms2....]},{sampleValue2:[synonyms11,synonyms21....]}]
        resolutionStrategy: Literal[
            "OriginalValue", "TopResolution", "Concatenation"
        ] = "OriginalValue",
    ):
        try:
            slot_type_values_list = []
            for slot_type in slot_type_values_list_row:
                for sample_value, synonyms in slot_type.items():
                    slot_type_values_list.append(
                        {
                            "sampleValue": {"value": sample_value},
                            "synonyms": [{"value": synonym} for synonym in synonyms],
                        }
                    )

            response = self.LEX_CLIENT.create_slot_type(
                slotTypeName=slot_type_name,
                slotTypeValues=slot_type_values_list,
                botId=self.bot_id,
                botVersion=self.bot_version,
                localeId=self.locale_id,
                description=description,
                valueSelectionSetting={"resolutionStrategy": resolutionStrategy},
            )
            return response["slotTypeId"]

        except Exception as e:
            raise

    def create_bot_slot_type_extended(
        self,
        slot_type_name,
        description,
        parent_slot_type_signature: str = "AMAZON.AlphaNumeric",
        regex_pattern: Optional[str] = None,
        resolutionStrategy: Literal[
            "OriginalValue", "TopResolution", "Concatenation"
        ] = "OriginalValue",
    ):
        try:
            request = {
                "slotTypeName": slot_type_name,
                "botId": self.bot_id,
                "botVersion": self.bot_version,
                "localeId": self.locale_id,
                "description": description,
            }

            if parent_slot_type_signature:
                request["parentSlotTypeSignature"] = parent_slot_type_signature

            value_selection = {"resolutionStrategy": resolutionStrategy}
            if regex_pattern:
                value_selection["regexFilter"] = {"pattern": regex_pattern}

            request["valueSelectionSetting"] = value_selection

            response = self.LEX_CLIENT.create_slot_type(**request)
            return response["slotTypeId"]

        except Exception as e:
            raise
