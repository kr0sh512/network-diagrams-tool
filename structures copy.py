class Wire:
    def __init__(self, from_device, to_device):
        self.from_device = from_device
        self.to_device = to_device


class Device:
    def __init__(self, name, model, properties):
        self.name = name
        self.model = model
        self.properties = properties


class Switch(Device):
    pass


class Router(Device):
    pass


class Host(Device):
    pass
