from config import Config
from asyncua import Client
from agent import Agent
from device import Device
import asyncio


async def main():
    config = Config()
    agents = []

    async with Client(config.server_url) as client:
        server_node = client.get_server_node()
        for device in await client.nodes.objects.get_children():
            if device != server_node:
                device_name = (await device.read_display_name()).Text
                connection_string = config.get_device_connection_string(device_name)

                agent = Agent.create(Device.create(device), connection_string)
                agents.append(agent)

        if not len(agents):
            print('Nie znaleziono żadnych urządzeń')
            return

        while True:
            for agent in agents:
                await asyncio.gather(*agent.get_tasks())
            await asyncio.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
