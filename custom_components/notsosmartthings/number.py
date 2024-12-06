from __future__ import annotations

from typing import NamedTuple, Literal
from collections.abc import Sequence
import logging

import asyncio


from pysmartthings import Capability, Attribute

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from homeassistant.components.number import NumberEntity, NumberMode, NumberDeviceClass, DEFAULT_MAX_VALUE, DEFAULT_MIN_VALUE
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, PERCENTAGE, Platform, EntityCategory, UnitOfTemperature

from .const import DOMAIN, DATA_BROKERS
from .entity import SmartThingsEntity
from .utils import format_component_name, get_device_components, get_device_status
from .device import DeviceEntity

_LOGGER = logging.getLogger(__name__)

# Define the namedtuple for capabilities
class Map(NamedTuple):
    """Tuple for mapping Smartthings capabilities to Home Assistant sensors."""

    attribute: str
    name: str
    command: str
    default_unit: str | None
    device_class: NumberDeviceClass | None
    min_value: float | None
    max_value: float | None
    step: float | None
    mode: NumberMode | None
    entity_category: EntityCategory | None

# Example capabilities
CAPABILITY_TO_NUMBER = {
    Capability.thermostat_cooling_setpoint: [
        Map(
            Attribute.cooling_setpoint,
            "Cooling Setpoint",
            "set_cooling_setpoint",
            UnitOfTemperature.CELSIUS,
            NumberDeviceClass.TEMPERATURE,
            -460,
            10000,
            1,
            NumberMode.AUTO,
            None,
        ),
    ],
}

UNITS = {
    "C": UnitOfTemperature.CELSIUS,
    "F": UnitOfTemperature.FAHRENHEIT,
}

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    broker = hass.data[DOMAIN][DATA_BROKERS][config_entry.entry_id]
    entities: list[NumberEntity] = []

    for device in broker.devices.values():
        _LOGGER.debug(f"Adding numbers for device: {device.label}")
        device_components = get_device_components(device)
        for component_id in list(device_components.keys()):
            _LOGGER.debug(f"Adding numbers of component_id: {component_id} in {device_components}")
            attributes = device_components[component_id]["attributes"]
            _LOGGER.debug(f"Attributes: {attributes}")
            disabled_capabilities = device_components[component_id]["disabled_capabilities"]
            entities.extend(
                _get_device_number_entities(broker, device, component_id, attributes, disabled_capabilities)
            )
    async_add_entities(entities)

"""TODO: make min, max and step dynamic based on the device's capabilities"""
def _get_device_number_entities(
    broker, device, component_id: str | None, component_attributes: list[str] | None, disabled_capabilities: list[str] | None
) -> list[NumberEntity]:
    entities: list[NumberEntity] = []
    for capability in broker.get_assigned(device.device_id, Platform.NUMBER):
        if capability in disabled_capabilities:
            _LOGGER.debug(f"Skipping disabled capability: {capability}")
            continue
        if capability == Capability.thermostat_cooling_setpoint:
            _LOGGER.debug(f"Adding thermostat cooling setpoint capability: {capability}")
            entities.extend(
                [
                    SmartThingsNumber(
                        device,
                        Attribute.cooling_setpoint,
                        "Cooling Setpoint",
                        "set_cooling_setpoint",
                        UnitOfTemperature.CELSIUS,
                        NumberDeviceClass.TEMPERATURE,
                        1, 
                        7, 
                        1, 
                        NumberMode.AUTO,
                        None,
                        component_id,
                    ),
                ]
            )
        else:
            maps = CAPABILITY_TO_NUMBER[capability]
            _LOGGER.debug(f"adding number capability: {maps}")
            for m in maps:
                if (
                    component_attributes is not None
                    and m.attribute not in component_attributes
                ):
                    continue
                    
                if component_id is None and m.attribute in [
                    Attribute.cooling_setpoint,
                ]:
                    continue
                entity = SmartThingsNumber(
                    device,
                    m.attribute,
                    m.name,
                    m.command,
                    m.default_unit,
                    m.device_class,
                    m.min_value,
                    m.max_value,
                    m.step,
                    m.mode,
                    m.entity_category,
                    component_id,
                )
            entities.append(entity)
    return entities

def get_capabilities(capabilities: Sequence[str]) -> Sequence[str] | None:
    """Return all capabilities supported if minimum required are present."""
    return [
        capability for capability in CAPABILITY_TO_NUMBER if capability in capabilities
    ]

class SmartThingsNumber(SmartThingsEntity, NumberEntity):
    """Representation of a custom number entity."""

    def __init__(
        self,
        device: DeviceEntity,
        attribute: str,
        name: str,
        command: str,
        default_unit: str | None,
        device_class: NumberDeviceClass | None,
        min_value: str | None,
        max_value: str | None,
        step: str | None,
        mode: NumberMode | None,
        entity_category: EntityCategory | None,
        component_id: str | None = None,

    ) -> None:
        """Initialize the entity."""	
        super().__init__(device)
        self._component_id = component_id
        self._attribute = attribute
        
        self._attr_name = format_component_name(device.label, name, component_id)
        self._attr_unique_id = format_component_name(
            device.device_id, attribute, component_id, "."
        )
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_mode = mode
        self._attr_command = command
        self._attr_entity_category = entity_category
        self._attr_native_unit_of_measurement = default_unit
        self._attr_device_class = device_class

    @property
    def native_min_value(self):
        """Return the minimum value."""
        return self._attr_native_min_value

    @property
    def natrive_max_value(self):
        """Return the maximum value."""
        return self._attr_native_max_value

    @property
    def native_step(self):
        """Return the step value."""
        return self._attr_step

    @property
    def native_unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        status = get_device_status(self._device, self._component_id)
        unit = status.attributes[self._attribute].unit
        return UNITS.get(unit, unit) if unit else self._attr_native_unit_of_measurement
    
    @property
    def mode(self) -> Literal["auto", "slider", "box"]:
        """Return the representation mode of the number."""
        return self._attr_mode

    @property
    def native_value(self) -> float:
        """Return the state of the number."""
        status = get_device_status(self._device, self._component_id)
        return status.attributes[self._attribute].value

    async def async_set_native_value(self, value: float) -> None:
        """Set the number value."""
        await getattr(self.device, self._command)(int(value), set_status=True)
        self.async_write_ha_state()

