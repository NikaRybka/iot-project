from asyncua.common.node import Node
from asyncua.ua import Variant
from typing import Literal


class Device:
    def __init__(self, node: Node):
        self.node = node

    @classmethod
    def create(cls, node: Node):
        return cls(node)

    @property
    def name(self):
        return self.node.get_display_name().Text

    async def get_property(self, name: str):
        children = await self.node.get_children()
        for child in children:
            if (await child.read_display_name()).Text == name:
                return child

    async def get_property_value(self, name: str):
        prop = await self.get_property(name)
        return await prop.read_value()

    async def set_property_value(self, name: str, value: Variant):
        await (await self.get_property(name)).write_value(value)

    async def call_method(self, method_name: Literal['EmergencyStop', 'ResetErrorStatus', 'MaintenanceDone']):
        await self.node.call_method(method_name)
