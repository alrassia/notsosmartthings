from __future__ import annotations

from typing import Any, NamedTuple, Literal
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
class NumberMap(NamedTuple):
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
        NumberMap(
            attribute=Attribute.cooling_setpoint,
            name="Cooling Setpoint",
            command="set_cooling_setpoint",
            default_unit=UnitOfTemperature.CELSIUS,
            device_class=NumberDeviceClass.TEMPERATURE,
            min_value=-460,
            max_value=10000,
            step=1,
            mode=NumberMode.AUTO,
            entity_category=None,
        ),
        NumberMap(
            attribute=Attribute.cooling_setpoint_range,
            name="Cooling Setpoint Range",
            command=None,
            default_unit=None,
            device_class=None,
            min_value=None,
            max_value=None,
            step=None,
            mode=None,
            entity_category=None,
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
        for component_id, component_info in device_components.items():
            _LOGGER.debug(f"Adding numbers of component_id: {component_id} with {device_components[component_id]}")
            entities.extend(
                _get_device_number_entities(broker, device, component_id, component_info)
            )
    async_add_entities(entities)

def _get_device_number_entities(
    broker: Any, 
    device: DeviceEntity, 
    component_id: str | None, 
    component_info: dict[str, Any],
) -> list[NumberEntity]:
    entities: list[NumberEntity] = []
    component_attributes = component_info["attributes"]
    disabled_capabilities = component_info["disabled_capabilities"]
    
    for capability in broker.get_assigned(device.device_id, Platform.NUMBER):
        if capability in disabled_capabilities:
            _LOGGER.debug(f"Number: Skipping disabled capability: {capability}")
            continue

        if capability == Capability.thermostat_cooling_setpoint:
            _LOGGER.debug(f"Adding thermostat cooling setpoint capability: {capability}")
            if Attribute.cooling_setpoint_range in component_attributes:
                cooling_setpoint_range_attr = component_attributes[Attribute.cooling_setpoint_range]
                cooling_setpoint_range = cooling_setpoint_range_attr.value
                min_value = cooling_setpoint_range.get("minimum")
                max_value = cooling_setpoint_range.get("maximum")
                step = cooling_setpoint_range.get("step")
                entities.append(
                    SmartThingsNumber(
                        device,
                        Attribute.cooling_setpoint,
                        "Cooling Setpoint",
                        "set_cooling_setpoint",
                        UnitOfTemperature.CELSIUS,
                        NumberDeviceClass.TEMPERATURE,
                        min_value,
                        max_value,
                        step,
                        NumberMode.AUTO,
                        None,
                        component_id,
                    )
                )
            else:
                _LOGGER.warning(f"Cooling setpoint range not found in component attributes for device {device.label}")
        else:
            maps = CAPABILITY_TO_NUMBER[capability]
            _LOGGER.debug(f"Number: {component_id} Adding number entity: {m.name}")
            for m in maps:
                if m.attribute not in component_attributes:
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
        self._command = command
       
        self._attr_name = format_component_name(device.label, name, component_id)
        self._attr_unique_id = format_component_name(
            device.device_id, attribute, component_id, "."
        )
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_mode = mode
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
        return self._attr_native_step

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

