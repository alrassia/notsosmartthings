from pysmartthings.device import DeviceEntity as OriginalDeviceEntity
from typing import List



class DeviceEntity(OriginalDeviceEntity):
    @property
    def disabled_components(self) -> List[str]:
        """Get the list of disabled components for this device."""
        if self._attributes.get("disabledComponents"):
            return self._attributes["disabledComponents"].value
        return []