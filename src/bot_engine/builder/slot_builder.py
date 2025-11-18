from typing import Literal, Optional
from common.lex_v2_client import lex_v2_client


class CreateBotSlotDefinitions:
    def __init__(self, region_name):
        self.lex_client = lex_v2_client(region_name)

    def create_bot_slot_type(
        self,
        slot_type_name,
        description,
        bot_id,
        bot_version,
        locale_id,
        resolutionStrategy: Literal[
            "OriginalValue", "TopResolution", "Concatenation"
        ] = "OriginalValue",
    ):
        try:
            response = self.lex_client.create_slot_type(
                slotTypeName=f"LEX_{slot_type_name}",
                botId=bot_id,
                botVersion=bot_version,
                localeId=locale_id,
                description=description,
                valueSelectionSetting={"resolutionStrategy": resolutionStrategy},
            )
            return response

        except Exception as e:
            raise

    def create_bot_slot_type_extended(
        self,
        slot_type_name,
        description,
        bot_id,
        bot_version,
        locale_id,
        parent_slot_type_signature: str = "AMAZON.AlphaNumeric",
        regex_pattern: Optional[str] = None,
        resolutionStrategy: Literal[
            "OriginalValue", "TopResolution", "Concatenation"
        ] = "OriginalValue",
    ):
        try:
            request = {
                "slotTypeName": f"LEX_{slot_type_name}",
                "botId": bot_id,
                "botVersion": bot_version,
                "localeId": locale_id,
                "description": description,
            }

            if parent_slot_type_signature:
                request["parentSlotTypeSignature"] = parent_slot_type_signature

            value_selection = {"resolutionStrategy": resolutionStrategy}
            if regex_pattern:
                value_selection["regexFilter"] = {"pattern": regex_pattern}

            request["valueSelectionSetting"] = value_selection

            response = self.lex_client.create_slot_type(**request)
            return response

        except Exception as e:
            raise
