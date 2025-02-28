import asyncio
import websockets
import json
from classes.wrappers.RobotWrapper import RobotWrapper
from classes.wrappers.QrCodeWrapper import QrCodeWrapper
class WebSocketWrapper:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.qr = QrCodeWrapper()
        self.clients = set()

    async def handler(self, websocket, path):
        # Register every new client connection
        self.clients.add(websocket)
        try:
            async for message in websocket:
                print(f"Message from WebSocket: {message}")
                data = json.loads(message)
                target = data.get('target')
                action = data.get('action')
                
                # Use Python's match-case to handle different targets
                match target.upper():
                    case 'QRCODE':
                        print('Target: QRCODE')
                        # Directly call the QRCode service action
                        await self.qr.handle_action(action)
                        pass
                    # case 'ROBOT':
                    #     print('Target: ROBOT')
                    #     # Directly call the Robot service action
                    #     await self.robot.handle_action(action)
                    #     pass
                    case 'FRONTEND':
                        print('Broadcasting to Frontend.')
                        # Broadcast message to all connected clients
                        await self.broadcast(json.dumps(data))
                    case _:
                        print(f"Unknown target: {target}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON received: {e}")
            await websocket.send("Error: Invalid JSON format")
        finally:
            # Unregister the client on disconnect
            self.clients.remove(websocket)

    async def broadcast(self, message):
        # Broadcast a message to all connected clients
        for client in self.clients:
            await client.send(message)

    async def start(self):
        async with websockets.serve(self.handler, self.host, self.port): # type: ignore
            print(f"WebSocket Server started at ws://{self.host}:{self.port}")
            await asyncio.Future()  # Keep the server running indefinitely