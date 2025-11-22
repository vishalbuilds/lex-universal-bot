from typing import Dict, List, Optional, Literal
from bot_engine.builder.bot_base import BotBase
import logging
import time

logger = logging.getLogger(__name__)


class BotCreationException(Exception):
    """Base exception for bot creation failures"""

    pass


class CreateBotSlotsType(BotBase):
    """Handles slot type creation and management"""

    def __init__(self, bot_id: str, locale_id: str, bot_version: str):
        self.bot_id = bot_id
        self.locale_id = locale_id
        self.bot_version = bot_version

    def create_bot_slot_type_custom(
        self,
        slot_type_name: str,
        description: str,
        slot_type_values_list: List[Dict[str, List[str]]],
        resolution_strategy: Literal[
            "OriginalValue", "TopResolution", "Concatenation"
        ] = "OriginalValue",
    ) -> str:
        """
        Create a custom slot type with sample values and synonyms.

        Args:
            slot_type_name: Name of the slot type
            description: Slot type description
            slot_type_values_list: List of {sampleValue: [synonyms]}
            resolution_strategy: How to handle multiple matches

        Returns:
            Slot type ID

        Raises:
            BotCreationException: If creation fails
        """
        try:
            logger.info(f"Creating custom slot type: {slot_type_name}")

            # Transform input format to API format
            slot_type_values = []
            for slot_dict in slot_type_values_list:
                for sample_value, synonyms in slot_dict.items():
                    slot_type_values.append(
                        {
                            "sampleValue": {"value": sample_value},
                            "synonyms": [{"value": syn} for syn in (synonyms or [])],
                        }
                    )

            response = self.LEX_CLIENT.create_slot_type(
                slotTypeName=slot_type_name,
                slotTypeValues=slot_type_values,
                botId=self.bot_id,
                botVersion=self.bot_version,
                localeId=self.locale_id,
                description=description,
                valueSelectionSetting={"resolutionStrategy": resolution_strategy},
            )

            slot_type_id = response.get("slotTypeId")
            logger.info(f"Custom slot type created: {slot_type_name} ({slot_type_id})")
            logger.debug("Waiting 10 seconds for AWS Lex to process...")
            time.sleep(10)
            return slot_type_id

        except Exception as e:
            logger.error(f"Failed to create custom slot type {slot_type_name}: {e}")
            raise BotCreationException(f"Custom slot type creation failed: {e}") from e

    def create_bot_slot_type_extended(
        self,
        slot_type_name: str,
        description: str,
        parent_slot_type_signature: str = "AMAZON.AlphaNumeric",
        regex_pattern: Optional[str] = None,
        resolution_strategy: Literal[
            "OriginalValue", "TopResolution", "Concatenation"
        ] = "OriginalValue",
    ) -> str:
        """
        Create an extended slot type based on a parent slot type.

        Args:
            slot_type_name: Name of the slot type
            description: Slot type description
            parent_slot_type_signature: Parent slot type to extend
            regex_pattern: Optional regex filter
            resolution_strategy: How to handle multiple matches

        Returns:
            Slot type ID

        Raises:
            BotCreationException: If creation fails
        """
        try:
            logger.info(f"Creating extended slot type: {slot_type_name}")

            request_params = {
                "slotTypeName": slot_type_name,
                "botId": self.bot_id,
                "botVersion": self.bot_version,
                "localeId": self.locale_id,
                "description": description,
            }

            if parent_slot_type_signature:
                request_params["parentSlotTypeSignature"] = parent_slot_type_signature

            # Build value selection settings
            value_selection = {"resolutionStrategy": resolution_strategy}
            if regex_pattern:
                value_selection["regexFilter"] = {"pattern": regex_pattern}

            request_params["valueSelectionSetting"] = value_selection

            response = self.LEX_CLIENT.create_slot_type(**request_params)

            slot_type_id = response.get("slotTypeId")
            logger.info(
                f"Extended slot type created: {slot_type_name} ({slot_type_id})"
            )
            logger.debug("Waiting 10 seconds for AWS Lex to process...")
            time.sleep(10)
            return slot_type_id

        except Exception as e:
            logger.error(f"Failed to create extended slot type {slot_type_name}: {e}")
            raise BotCreationException(
                f"Extended slot type creation failed: {e}"
            ) from e
