from bot_engine.builder.bot_base import BotBase
import logging
import time

from typing import Dict, List, Optional


logger = logging.getLogger(__name__)


class BotCreationException(Exception):
    """Base exception for bot creation failures"""

    pass


class CreateBotIntent(BotBase):
    """Handles intent and slot management"""

    def __init__(self, bot_version: str, locale_id: str, bot_id: str):
        self.bot_version = bot_version
        self.locale_id = locale_id
        self.bot_id = bot_id

    def create_bot_intent(
        self,
        intent_name: str,
        description: str,
        utterances: List[str],
        intent_hooks: Optional[List[str]] = None,
    ) -> str:
        """
        Create a new intent with sample utterances.

        Args:
            intent_name: Intent name
            description: Intent description
            utterances: Sample utterances
            intent_hooks: List of hook types to enable

        Returns:
            Intent ID

        Raises:
            BotCreationException: If creation fails
        """
        try:
            logger.info(f"Creating intent: {intent_name}")

            intent_definition = self._build_intent_definition(intent_hooks or [])

            response = self.LEX_CLIENT.create_intent(
                intentName=intent_name,
                description=description,
                botId=self.bot_id,
                botVersion=self.bot_version,
                sampleUtterances=[{"utterance": u} for u in utterances],
                localeId=self.locale_id,
                **intent_definition,
            )

            intent_id = response.get("intentId")
            logger.info(f"Intent created: {intent_name} ({intent_id})")
            logger.debug("Waiting 10 seconds for AWS Lex to process...")
            time.sleep(10)
            return intent_id

        except Exception as e:
            logger.error(f"Failed to create intent {intent_name}: {e}")
            raise BotCreationException(f"Intent creation failed: {e}") from e

    def create_slot_in_intent(
        self,
        slot_name: str,
        slot_type_id: str,
        intent_id: str,
        slot_constraint: str = "Optional",
    ) -> str:
        """
        Add a slot to an intent.

        Args:
            slot_name: Slot name
            slot_type_id: Slot type ID
            intent_id: Intent ID to add slot to
            slot_constraint: Required or Optional

        Returns:
            Slot ID

        Raises:
            BotCreationException: If creation fails
        """
        try:
            logger.info(f"Creating slot {slot_name} in intent {intent_id}")

            response = self.LEX_CLIENT.create_slot(
                botId=self.bot_id,
                botVersion=self.bot_version,
                localeId=self.locale_id,
                intentId=intent_id,
                slotName=slot_name,
                slotTypeId=slot_type_id,
                valueElicitationSetting={"slotConstraint": slot_constraint},
            )

            slot_id = response.get("slotId")
            logger.info(f"Slot created: {slot_name} ({slot_id})")
            logger.debug("Waiting 10 seconds for AWS Lex to process...")
            time.sleep(10)
            return slot_id

        except Exception as e:
            logger.error(f"Failed to create slot {slot_name}: {e}")
            raise BotCreationException(f"Slot creation failed: {e}") from e

    def update_intent_slot_priority(
        self,
        intent_id: str,
        intent_name: str,
        slot_priorities_list: List[Dict[str, any]],
    ) -> Dict:
        """
        Update slot priorities for an intent.

        Args:
            intent_id: Intent ID to update
            intent_name: Intent name (required by AWS Lex API)
            slot_priorities_list: List of {slotId, priority}

        Returns:
            API response

        Raises:
            BotCreationException: If update fails
        """
        try:
            logger.info(f"Updating slot priorities for intent {intent_id}")

            slot_priorities = [
                {
                    "slotId": slot_dict["slotId"],
                    "priority": slot_dict["priority"],
                }
                for slot_dict in slot_priorities_list
            ]

            response = self.LEX_CLIENT.update_intent(
                intentId=intent_id,
                intentName=intent_name,
                botId=self.bot_id,
                botVersion=self.bot_version,
                localeId=self.locale_id,
                slotPriorities=slot_priorities,
            )

            logger.info(f"Slot priorities updated for intent {intent_id}")
            logger.debug("Waiting 10 seconds for AWS Lex to process...")
            time.sleep(10)
            return response

        except Exception as e:
            logger.error(f"Failed to update slot priorities: {e}")
            raise BotCreationException(f"Slot priority update failed: {e}") from e

    def update_intent(
        self,
        intent_id: str,
        intent_name: str,
        description: Optional[str] = None,
        utterances: Optional[List[str]] = None,
        intent_hooks: Optional[List[str]] = None,
        slot_priorities_list: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Update intent properties.

        Args:
            intent_id: Intent ID to update
            intent_name: New intent name
            description: Optional new description
            utterances: Optional new utterances
            intent_hooks: Optional hooks to enable
            slot_priorities_list: Optional slot priorities

        Returns:
            API response

        Raises:
            BotCreationException: If update fails
        """
        try:
            logger.info(f"Updating intent: {intent_name}")

            update_params = {
                "intentId": intent_id,
                "intentName": intent_name,
                "botId": self.bot_id,
                "botVersion": self.bot_version,
                "localeId": self.locale_id,
            }

            if description:
                update_params["description"] = description

            if utterances:
                update_params["sampleUtterances"] = [
                    {"utterance": u} for u in utterances
                ]

            if intent_hooks:
                update_params.update(self._build_intent_definition(intent_hooks))

            if slot_priorities_list:
                update_params["slotPriorities"] = [
                    {
                        "slotId": slot_dict["slotId"],
                        "priority": slot_dict["priority"],
                    }
                    for slot_dict in slot_priorities_list
                ]

            response = self.LEX_CLIENT.update_intent(**update_params)
            logger.info(f"Intent updated: {intent_name}")
            logger.debug("Waiting 10 seconds for AWS Lex to process...")
            time.sleep(10)
            return response

        except Exception as e:
            logger.error(f"Failed to update intent {intent_name}: {e}")
            raise BotCreationException(f"Intent update failed: {e}") from e

    @staticmethod
    def _build_intent_definition(intent_hooks: List[str]) -> Dict:
        """Build intent definition from hook list"""
        intent_definition = {}

        if "fulfillmentCodeHook" in intent_hooks:
            intent_definition["fulfillmentCodeHook"] = {
                "enabled": True,
                "active": True,
            }

        if "intentConfirmationSetting" in intent_hooks:
            intent_definition["intentConfirmationSetting"] = {
                "active": True,
                "promptSpecification": {
                    "messageGroups": [
                        {"message": {"plainTextMessage": {"value": "Please confirm"}}}
                    ],
                    "maxRetries": 2,
                },
            }

        return intent_definition
