from pysmartthings.device import DeviceEntity as OriginalDeviceEntity
from typing import List



class DeviceEntity(OriginalDeviceEntity):
    @property
    def disabled_components(self) -> List[str]:
        """Get the list of disabled components for this device."""
        if hasattr(self._status, '_attributes') and self._status._attributes.get("disabledComponents"):
            return self._status._attributes["disabledComponents"].value
        return []