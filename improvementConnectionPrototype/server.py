import asyncio, logging, websockets
from websockets import WebSocketServerProtocol

logging.basicConfig(level=logging.INFO)

class Server:
	clients = set()

	async def connect(self, ws: WebSocketServerProtocol) -> None:
		self.clients.add(ws)
		logging.info(f"{ws.remote_address} connects.")

	async def disconnect(self, ws:WebSocketServerProtocol) -> None:
		self.clients.remove(ws)
		logging.info(f"{ws.remote_address} disconnects.")

	async def send_to_clients(self, message:str) -> None:
		if self.clients:
			await asyncio.wait([client.send(message) for client in self.clients])

	async def ws_handler(self, ws:WebSocketServerProtocol, url:str) -> None:
		await self.register(ws)
		try:
			await self.distribute(ws)
		finally:
			await self.disconnect(ws)

	async def distribute(self, ws:WebSocketServerProtocol) -> None:
		async for message in ws:
			await self.send_to_clients(message)