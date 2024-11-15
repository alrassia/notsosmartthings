import logging

from pysmartthings.device import DeviceEntity as OriginalDeviceEntity
from typing import List

_LOGGER = logging.getLogger(__name__)

class DeviceEntity(OriginalDeviceEntity):
    @property
    def disabled_components(self) -> List[str]:
        """Get the list of disabled components for this device.."""
        _LOGGER.debug("Disabled components: %s", self._status._attributes["disabledComponents"].value)
        _LOGGER.debug("DisabledComponents: %s", self._status._attributes.get("disabledComponents"))
        
        if self._status._attributes.get("disabledComponents"):
            return self._status._attributes["disabledComponents"].value
        return []