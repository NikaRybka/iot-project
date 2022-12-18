import os

import azure.functions as func
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Brak danych", status_code=500)

    registry_manager = IoTHubRegistryManager(os.environ["ConnectionString"])
    for device in filter(lambda d: d["errors"] > 3, req_body):
        registry_manager.invoke_device_method(
            device["ConnectionDeviceId"],
            CloudToDeviceMethod(method_name="EmergencyStop")
        )
    return func.HttpResponse("Ok", status_code=200)
