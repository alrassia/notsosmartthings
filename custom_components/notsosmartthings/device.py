import logging

from pysmartthings.device import DeviceEntity as OriginalDeviceEntity
from typing import List

_LOGGER = logging.getLogger(__name__)

class DeviceEntity(OriginalDeviceEntity):
    @property
    def disabled_components(self) -> List[str]:
        """Get the list of disabled components for this device.."""
        if hasattr(self._status, '_attributes') and self._status._attributes.get("disabledComponents"):
            disabled_components = self._status._attributes["disabledComponents"].value
            if disabled_components is not None:
                _LOGGER.debug("Disabled components: %s", disabled_components)
                return disabled_components
        return []