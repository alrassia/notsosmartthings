from pysmartthings.device import DeviceEntity as OriginalDeviceEntity



class DeviceEntity(OriginalDeviceEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = self.Status()

    @property
    def disabled_components(self) -> []:
        """Get the list of disabled components for this device."""
        if self._attributes.get("disabledComponents"):
            return self._attributes["disabledComponents"].value
        return []