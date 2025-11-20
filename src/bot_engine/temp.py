import logging
import time
from typing import Dict, List, Optional
from bot_engine.builder.bot_base import BotBase


logger = logging.getLogger(__name__)

from bot_engine.utils.yaml_loader import bot_config
from bot_engine.builder.instance_builder import CreateBotInstance
from bot_engine.builder.locale_builder import CreateBuildBotLocale
from bot_engine.builder.intent_builder import CreateBotIntent
from bot_engine.builder.slots_type_builder import CreateBotSlotsType
from bot_engine.builder.alias_builder import CreateBotAlias
from bot_engine.builder.bot_health_checker import BotHealthChecker
from bot_engine.builder.version_builder import CreateBotVersion


class BotCreationException(Exception):
    """Base exception for bot creation failures"""

    pass


class BotStatusException(BotCreationException):
    """Exception for bot status check failures"""

    pass


class ConfigurationException(BotCreationException):
    """Exception for configuration-related errors"""

    pass


class CreateUniversalBot:
    """Main orchestrator for bot creation workflow"""

    MAX_STATUS_RETRIES = 24  # 2 minutes with 5-second intervals
    RETRY_DELAY = 5

    def __init__(self):
        self.bot_id: Optional[str] = None
        self.bot_version: Optional[str] = None
        self.do_operation()

    def __str__(self) -> str:
        return f"Bot(id={self.bot_id}, version={self.bot_version})"

    def _wait_for_status(
        self,
        check_func,
        status_name: str = "Status",
        max_retries: int = MAX_STATUS_RETRIES,
    ) -> None:
        """
        Generic method to poll for a status with timeout.

        Args:
            check_func: Callable that returns True when status is ready
            status_name: Name of status for logging
            max_retries: Maximum number of retry attempts

        Raises:
            BotStatusException: If status check times out
        """
        for attempt in range(max_retries):
            try:
                if check_func():
                    logger.info(f"{status_name} check passed")
                    return
            except Exception as e:
                logger.warning(f"{status_name} check attempt {attempt + 1} failed: {e}")

            if attempt < max_retries - 1:
                time.sleep(self.RETRY_DELAY)

        raise BotStatusException(
            f"{status_name} check failed after {max_retries} attempts "
            f"({max_retries * self.RETRY_DELAY} seconds)"
        )

    def _init_bot(self) -> str:
        """
        Create bot instance and return bot ID.

        Returns:
            Bot ID

        Raises:
            BotCreationException: If bot creation fails
        """
        try:
            logger.info("Initializing bot instance...")
            bot_id = CreateBotInstance().create_bot_instance(
                bot_config.idleSessionTTLInSeconds,
                bot_config.dataPrivacy.childDirected,
                bot_config.roleArn,
            )
            logger.info(f"Bot instance initialized: {bot_id}")
            return bot_id
        except Exception as e:
            logger.error(f"Failed to initialize bot instance: {e}")
            raise

    def _check_bot_status(self) -> bool:
        """
        Check if bot status is Available.

        Returns:
            True if available

        Raises:
            BotStatusException: If status check fails
        """
        bot_status = BotHealthChecker().get_bot_status(self.bot_id)
        return bot_status == "Available"

    def _check_bot_locale_status(self, locale_id: str) -> bool:
        """
        Check if bot locale status is NotBuilt.

        Args:
            locale_id: Locale to check

        Returns:
            True if NotBuilt

        Raises:
            BotStatusException: If status check fails
        """
        locale_status = BotHealthChecker().get_bot_locale_status(
            self.bot_id, "DRAFT", locale_id
        )
        return locale_status == "NotBuilt"

    def _create_slot_types(
        self,
        locale_id: str,
        slot_definitions: List,
    ) -> Dict[str, str]:
        """
        Create custom and extended slot types.

        Args:
            locale_id: Locale ID
            slot_definitions: Slot definitions from config

        Returns:
            Mapping of slot name to slot type ID

        Raises:
            BotCreationException: If slot type creation fails
        """
        slots_type_id_set = {}

        try:
            logger.info(f"Creating slot types for locale {locale_id}")
            slots_type_obj = CreateBotSlotsType(self.bot_id, locale_id, "DRAFT")

            for slot in slot_definitions:
                try:
                    if slot.type == "Custom":
                        logger.debug(f"Creating custom slot type: {slot.name}")
                        slot_type_values = [
                            {val.sampleValue: val.synonyms}
                            for val in slot.slotType.slotTypeValues
                        ]
                        slot_type_id = slots_type_obj.create_bot_slot_type_custom(
                            slot.name,
                            slot.description,
                            slot_type_values,
                            slot.slotType.resolutionStrategy,
                        )
                        slots_type_id_set[slot.name] = slot_type_id

                    elif slot.type == "Extended":
                        logger.debug(f"Creating extended slot type: {slot.name}")
                        slot_type_id = slots_type_obj.create_bot_slot_type_extended(
                            slot.name,
                            slot.description,
                            slot.slotType.parentSlotTypeSignature,
                            slot.slotType.regexPattern,
                            slot.slotType.resolutionStrategy,
                        )
                        slots_type_id_set[slot.name] = slot_type_id

                except Exception as e:
                    logger.error(f"Failed to create slot type {slot.name}: {e}")
                    raise

            logger.info(f"Successfully created {len(slots_type_id_set)} slot types")
            return slots_type_id_set

        except Exception as e:
            logger.error(f"Failed to create slot types for locale {locale_id}: {e}")
            raise

    def _create_intents(
        self,
        locale_id: str,
        intents_config: List,
    ) -> Dict[str, str]:
        """
        Create intents.

        Args:
            locale_id: Locale ID
            intents_config: Intent configurations from config

        Returns:
            Mapping of intent name to intent ID

        Raises:
            BotCreationException: If intent creation fails
        """
        intent_id_set = {}

        try:
            logger.info(f"Creating intents for locale {locale_id}")
            intent_obj = CreateBotIntent("DRAFT", locale_id, self.bot_id)

            for intent in intents_config:
                try:
                    logger.debug(f"Creating intent: {intent.name}")
                    intent_id = intent_obj.create_bot_intent(
                        intent.name,
                        intent.description,
                        intent.sampleUtterances,
                        intent.codeHook,
                    )
                    intent_id_set[intent.name] = intent_id
                except Exception as e:
                    logger.error(f"Failed to create intent {intent.name}: {e}")
                    raise

            logger.info(f"Successfully created {len(intent_id_set)} intents")
            return intent_id_set

        except Exception as e:
            logger.error(f"Failed to create intents for locale {locale_id}: {e}")
            raise

    def _add_slots_to_intents(
        self,
        locale_id: str,
        slot_definitions: List,
        intent_id_set: Dict[str, str],
        slots_type_id_set: Dict[str, str],
    ) -> None:
        """
        Add slots to intents with proper priority ordering.

        Args:
            locale_id: Locale ID
            slot_definitions: Slot definitions from config
            intent_id_set: Mapping of intent names to IDs
            slots_type_id_set: Mapping of slot names to type IDs

        Raises:
            BotCreationException: If slot binding fails
        """
        try:
            logger.info(f"Adding slots to intents for locale {locale_id}")
            intent_obj = CreateBotIntent("DRAFT", locale_id, self.bot_id)
            intent_slot_priorities = {}

            for slot in slot_definitions:
                intent_name = slot.intent
                target_intent_id = intent_id_set.get(intent_name)

                if target_intent_id is None:
                    logger.warning(
                        f"Slot '{slot.name}' references non-existent intent '{intent_name}'. "
                        "Skipping."
                    )
                    continue

                if target_intent_id not in intent_slot_priorities:
                    intent_slot_priorities[target_intent_id] = []

                try:
                    if slot.type in ("Custom", "Extended"):
                        if slot.name not in slots_type_id_set:
                            raise ConfigurationException(
                                f"Slot type '{slot.name}' not found in created slot types"
                            )
                        logger.debug(
                            f"Adding {slot.type} slot '{slot.name}' to intent '{intent_name}'"
                        )
                        slot_id = intent_obj.create_slot_in_intent(
                            slot.slotPhraseName,
                            slots_type_id_set[slot.name],
                            target_intent_id,
                            slot.slotConstraint,
                        )

                    elif slot.type == "BuiltIn":
                        logger.debug(
                            f"Adding BuiltIn slot '{slot.name}' to intent '{intent_name}'"
                        )
                        slot_id = intent_obj.create_slot_in_intent(
                            slot.slotPhraseName,
                            slot.slotTypeId,
                            target_intent_id,
                            slot.slotConstraint,
                        )
                    else:
                        logger.warning(f"Unknown slot type: {slot.type}. Skipping.")
                        continue

                    intent_slot_priorities[target_intent_id].append(
                        {"slotId": slot_id, "priority": slot.priority}
                    )

                except Exception as e:
                    logger.error(f"Failed to add slot {slot.name} to intent: {e}")
                    raise

            # Update intent slot priorities
            for intent_id, slot_priorities_list in intent_slot_priorities.items():
                if slot_priorities_list:
                    logger.debug(
                        f"Updating slot priorities for intent {intent_id}: "
                        f"{len(slot_priorities_list)} slots"
                    )
                    intent_obj.update_intent_slot_priority(
                        intent_id, slot_priorities_list
                    )

            logger.info("All slots added to intents successfully")

        except Exception as e:
            logger.error(f"Failed to add slots to intents: {e}")
            raise

    def _init_language_intent_slots(self) -> None:
        """
        Initialize locales with intents and slots.

        Raises:
            BotCreationException: If initialization fails
        """
        try:
            for locale in bot_config.locale:
                logger.info(f"Initializing locale: {locale.localeId}")

                # Create locale
                locale_builder = CreateBuildBotLocale(self.bot_id, locale.localeId)
                locale_builder.create_bot_locale(
                    locale.nluIntentConfidenceThreshold,
                    locale.voiceSettings.voiceId,
                    locale.voiceSettings.engine,
                )

                # Wait for locale to be ready
                logger.info(f"Waiting for locale {locale.localeId} to be ready...")
                self._wait_for_status(
                    lambda loc_id=locale.localeId: self._check_bot_locale_status(
                        loc_id
                    ),
                    f"Locale {locale.localeId}",
                )

                # Create slot types
                slots_type_id_set = self._create_slot_types(
                    locale.localeId, locale.slotDefinitions
                )

                # Create intents
                intent_id_set = self._create_intents(locale.localeId, locale.intents)

                # Add slots to intents
                self._add_slots_to_intents(
                    locale.localeId,
                    locale.slotDefinitions,
                    intent_id_set,
                    slots_type_id_set,
                )

                logger.info(f"Locale {locale.localeId} initialization complete")

        except Exception as e:
            logger.error(f"Failed to initialize language, intents, and slots: {e}")
            raise

    def _build_bot_locales(self) -> None:
        """
        Build all bot locales.

        Raises:
            BotCreationException: If build fails
        """
        try:
            logger.info("Building bot locales...")
            for locale in bot_config.locale:
                logger.info(f"Building locale: {locale.localeId}")
                response = CreateBuildBotLocale(
                    self.bot_id, locale.localeId
                ).build_bot_locale("DRAFT")
                logger.debug(f"Build response for {locale.localeId}: {response}")

            logger.info("All locales built successfully")

        except Exception as e:
            logger.error(f"Failed to build bot locales: {e}")
            raise

    def _init_version(self) -> str:
        """
        Create a new bot version.

        Returns:
            Bot version string

        Raises:
            BotCreationException: If version creation fails
        """
        try:
            logger.info("Creating bot version...")
            bot_version_locale_spec = [
                {locale.localeId: "DRAFT"} for locale in bot_config.locale
            ]

            version_builder = CreateBotVersion(self.bot_id)
            bot_version = version_builder.create_bot_version(
                "First bot version 1 based on DRAFT",
                bot_version_locale_spec,
            )
            logger.info(f"Bot version created: {bot_version}")
            return bot_version

        except Exception as e:
            logger.error(f"Failed to create bot version: {e}")
            raise

    def _init_alias(self) -> None:
        """
        Create and configure bot alias.

        Raises:
            BotCreationException: If alias creation/config fails
        """
        try:
            logger.info("Creating and configuring bot alias...")
            alias_builder = CreateBotAlias(
                self.bot_id,
                bot_config.alias.name,
                bot_config.alias.description,
            )
            bot_alias_id = alias_builder.create_bot_alias()
            logger.info(f"Bot alias created: {bot_alias_id}")

            # Configure alias with locale settings
            alias_locale_settings = [
                {
                    "Locale": locale.localeId,
                    "Lambda_arn": locale.lambdaHooks.arn,
                    "codeHookInterfaceVersion": locale.lambdaHooks.codeHookInterfaceVersion,
                }
                for locale in bot_config.locale
            ]

            if self.bot_version is None:
                raise ValueError("Bot version not set before alias configuration")

            alias_builder.update_bot_alias(
                bot_alias_id, self.bot_version, alias_locale_settings
            )
            logger.info("Bot alias configuration complete")

        except Exception as e:
            logger.error(f"Failed to create/configure bot alias: {e}")
            raise

    def do_operation(self) -> None:
        """
        Main orchestration method for complete bot creation workflow.

        Raises:
            BotCreationException: If any step fails
        """
        try:
            logger.info("=" * 60)
            logger.info("Starting universal bot creation process...")
            logger.info("=" * 60)

            # Set base configuration
            BotBase.set_base(
                bot_config.name,
                bot_config.description,
                bot_config.region,
            )

            # Create bot instance
            self.bot_id = self._init_bot()

            # Wait for bot to be available
            logger.info("Waiting for bot to be available...")
            self._wait_for_status(
                self._check_bot_status,
                "Bot availability",
            )

            # Initialize locales, intents, and slots
            self._init_language_intent_slots()

            # Build bot locales
            self._build_bot_locales()

            # Create version
            self.bot_version = self._init_version()

            # Setup alias
            self._init_alias()

            logger.info("=" * 60)
            logger.info("Bot creation process completed successfully!")
            logger.info(f"Bot ID: {self.bot_id}")
            logger.info(f"Bot Version: {self.bot_version}")
            logger.info("=" * 60)

        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"Bot creation process failed: {e}")
            logger.error("=" * 60)
            raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    try:
        bot = CreateUniversalBot()
        print(f"✓ {bot}")
    except BotCreationException as e:
        logger.error(f"Bot creation failed: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)
