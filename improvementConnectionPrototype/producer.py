import asyncio, websockets
from server import Server

async def produce(message: str, host: str, port: int) -> None:
	async with websockets.connect(f"ws://{host}:{port}") as ws:
		await ws.send(message)
		await ws.recv()

server = Server()
start_server = websockets.serve(server.ws_handler, 'localhst', 4000)
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.run_forever()