from pysmartthings.device import DeviceEntity as OriginalDeviceEntity
from typing import List



class DeviceEntity(OriginalDeviceEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = self.Status()

    @property
    def disabled_components(self) -> List:
        """Get the list of disabled components for this device."""
        if self._attributes.get("disabledComponents"):
            return self._attributes["disabledComponents"].value
        return List