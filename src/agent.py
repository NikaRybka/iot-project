from asyncio import create_task
from asyncua.ua import Variant, VariantType
from azure.iot.device import IoTHubDeviceClient, Message, MethodRequest, MethodResponse
from typing import Literal
import json
from datetime import datetime


class Agent:
    def __init__(self, device, connection_string):
        self.device = device
        self.client = IoTHubDeviceClient.create_from_connection_string(connection_string)
        self.client.connect()

        self.client.on_method_request_received = self.method_request_handler
        self.client.on_twin_desired_properties_patch_received = self.twin_desired_patch_handler

        self.tasks = []

    @classmethod
    def create(cls, device, connection_string):
        return cls(device, connection_string)

    def get_tasks(self):
        tasks = [create_task(task) for task in self.tasks] + [create_task(self.send_telemetry())]
        self.tasks = []
        return tasks

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

    def method_request_handler(self, method_request: MethodRequest):
        if method_request.name == 'EmergencyStop':
            print('Wywołanie metody EmergencyStop')
            self.tasks.append(self.device.call_method('EmergencyStop'))
        elif method_request.name == 'ResetErrorStatus':
            print('Wywołanie metody ResetErrorStatus')
            self.tasks.append(self.device.call_method('ResetErrorStatus'))
        elif method_request.name == 'MaintenanceDone':
            print('Wywołanie metody MaintenanceDone')
            self.client.patch_twin_reported_properties({"LastMaintenanceDate": datetime.now().isoformat()})
        else:
            print('Nieznana metoda: ', method_request.name)

        self.client.send_method_response(MethodResponse(
            request_id=method_request.request_id,
            status=200,
            payload='OK'
        ))

    def twin_desired_patch_handler(self, patch):
        if 'ProductionRate' in patch:
            print('Ustawienie ProductionRate na ', patch['ProductionRate'])
            self.tasks.append(self.device.set_property_value(
                name='ProductionRate',
                value=Variant(patch['ProductionRate'], VariantType.Int32)
            ))
