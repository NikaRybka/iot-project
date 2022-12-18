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
        self.errors = []

    @classmethod
    def create(cls, device, connection_string):
        return cls(device, connection_string)

    def get_tasks(self):
        tasks = [create_task(task) for task in self.tasks] + [create_task(self.send_telemetry())]
        self.tasks = []
        return tasks

    async def get_subscribed_properties(self):
        return [
            await self.device.get_property('ProductionRate'),
            await self.device.get_property('DeviceError')
        ]

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

    async def datachange_notification(self, node, val, _):
        prop_name = await node.read_browse_name()

        if prop_name.Name == 'DeviceError':
            self.errors.clear()
            errors = {
                1: 'Emergency Stop',
                2: 'Power Failure',
                4: 'Sensor Failure',
                8: 'Unknown'
            }

            for err_value, error in errors.items():
                if val & err_value:
                    if error not in self.errors:
                        self.errors.append(error)
                        self.send_message({'DeviceError': error}, 'event')
                        self.client.patch_twin_reported_properties({"LastErrorDate": datetime.now().isoformat()})
            self.client.patch_twin_reported_properties({"device_error": self.errors})

        elif prop_name.Name == 'ProductionRate':
            self.client.patch_twin_reported_properties({"ProductionRate": val})
