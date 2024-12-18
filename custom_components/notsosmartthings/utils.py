"""Shared functionality to serve multiple HA components."""

from typing import Any
from pysmartthings import DeviceStatusBase

def format_component_name(
    prefix: str, suffix: str, component_id: str | None, delimiter: str = " "
) -> str:
    """Format component name according to convention."""
    parts = [prefix]

    if component_id is not None and not "main":
        parts.append(component_id)

    parts.append(suffix)

    component_name = delimiter.join(parts)

    return component_name


def get_device_status(device, component_id: str | None) -> DeviceStatusBase:
    """Choose the status object based on device and component id."""
    status = device.status

    if component_id == "main":
        status = device.status
    elif component_id is not None:
        status = status.components[component_id]

    return status


def get_device_components(device) -> dict[str | None, list[str, Any]]:
    """Construct list of components related to a device."""
    result: dict[str | None, dict[str, Any]] = {}
    device_components_keys = list(device.status.components.keys())

    components_keys = [None]

    if len(device_components_keys) > 1:
        components_keys.extend(device_components_keys)

    disabled_components = device.status.attributes["disabledComponents"].value
    
    for component_key in components_keys:
        if component_key is not None and component_key in disabled_components:
            continue

        component_id = None
        component_attributes: dict[str, Any] = {}
        component_capabilities = None
        disabled_capabilities = []

        if component_key is not None:
            component = device.status.components[component_key]
            component_id = component.component_id
            component_attributes = {attr_name: attr for attr_name, attr in component.attributes.items()}
            #component_capabilities = list(component.capabilities.keys())
            if "disabledCapabilities" in component.attributes:
                disabled_capabilities = component.attributes["disabledCapabilities"].value
        else:
            component_id = "main"
            component_attributes = {attr_name: attr for attr_name, attr in device.status.attributes.items()}
            #component_capabilities = device.capabilities
            if "disabledCapabilities" in component_attributes:
                disabled_capabilities = device.status.attributes["disabledCapabilities"].value
                
        result[component_id] = {
            "attributes": component_attributes,
            "disabled_capabilities": disabled_capabilities,
            #"capabilities": component_capabilities,
        }

    return result
