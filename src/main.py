from config import Config
from asyncua import Client
import asyncio

async def main(): 
    config = Config()

    async with Client(config.server_url) as client:
        print(await client.nodes.objects.get_children())

if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())