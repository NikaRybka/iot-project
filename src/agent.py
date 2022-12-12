from azure.iot.device import IoTHubDeviceClient, Message
from typing import Literal
import json


class Agent:
    def __init__(self, device, connection_string):
        self.device = device
        self.client = IoTHubDeviceClient.create_from_connection_string(connection_string)
        self.client.connect()

    @classmethod
    def create(cls, device, connection_string):
        return cls(device, connection_string)

    async def send_telemetry(self):
        data = {
            "WorkorderId": await self.device.get_property_value('WorkorderId'),
            "ProductionStatus": await self.device.get_property_value('ProductionStatus'),
            "GoodCount": await self.device.get_property_value('GoodCount'),
            "BadCount": await self.device.get_property_value('BadCount'),
            "Temperature": await self.device.get_property_value('Temperature')
        }

        print(data)
        self.send_message(data, 'telemetry')

    def send_message(self, data: dict, message_type: Literal['telemetry', 'event']):
        data['message_type'] = message_type
        message = Message(
            data=json.dumps(data),
            content_encoding='utf-8',
            content_type='application/json'
        )

        self.client.send_message(message)
