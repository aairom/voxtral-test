#!/usr/bin/env python3
"""
Voxtral Realtime Transcription Server
Connects to vLLM server running Voxtral-Mini-4B-Realtime-2602
"""

import argparse
import asyncio
import base64
import json
import logging
import time
from typing import Optional

import numpy as np
import websockets
from websockets.server import WebSocketServerProtocol

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VoxtralServer:
    def __init__(self, vllm_host: str = "127.0.0.1", vllm_port: int = 8000):
        self.vllm_host = vllm_host
        self.vllm_port = vllm_port
        self.vllm_url = f"ws://{vllm_host}:{vllm_port}/v1/realtime"
        self.sessions = {}
        
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle incoming client WebSocket connection"""
        client_id = id(websocket)
        logger.info(f"Client {client_id} connected from {websocket.remote_address}")
        
        vllm_ws = None
        
        try:
            # Connect to vLLM server
            logger.info(f"Connecting to vLLM server at {self.vllm_url}")
            vllm_ws = await websockets.connect(self.vllm_url)
            logger.info(f"Connected to vLLM server for client {client_id}")
            
            # Wait for session.created from vLLM
            session_response = await vllm_ws.recv()
            session_data = json.loads(session_response)
            
            if session_data.get('type') == 'session.created':
                logger.info(f"Session created: {session_data.get('id')}")
                # Forward session.created to client
                await websocket.send(session_response)
            
            # Create tasks for bidirectional communication
            client_to_vllm = asyncio.create_task(
                self.forward_client_to_vllm(websocket, vllm_ws, client_id)
            )
            vllm_to_client = asyncio.create_task(
                self.forward_vllm_to_client(vllm_ws, websocket, client_id)
            )
            
            # Wait for either task to complete
            done, pending = await asyncio.wait(
                [client_to_vllm, vllm_to_client],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
        except websockets.exceptions.WebSocketException as e:
            logger.error(f"WebSocket error for client {client_id}: {e}")
            try:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'error': f'Connection error: {str(e)}'
                }))
            except:
                pass
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}", exc_info=True)
            try:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'error': f'Server error: {str(e)}'
                }))
            except:
                pass
        finally:
            if vllm_ws:
                await vllm_ws.close()
            logger.info(f"Client {client_id} disconnected")
    
    async def forward_client_to_vllm(
        self, 
        client_ws: WebSocketServerProtocol, 
        vllm_ws, 
        client_id: int
    ):
        """Forward messages from client to vLLM server"""
        try:
            async for message in client_ws:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type', 'unknown')
                    
                    logger.debug(f"Client {client_id} -> vLLM: {msg_type}")
                    
                    # Forward to vLLM
                    await vllm_ws.send(message)
                    
                    # Log audio chunks
                    if msg_type == 'input_audio_buffer.append':
                        audio_len = len(data.get('audio', ''))
                        logger.debug(f"Forwarded audio chunk ({audio_len} bytes)")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from client {client_id}: {e}")
                except Exception as e:
                    logger.error(f"Error forwarding client message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} connection closed")
        except Exception as e:
            logger.error(f"Error in client->vLLM forwarding: {e}")
    
    async def forward_vllm_to_client(
        self, 
        vllm_ws, 
        client_ws: WebSocketServerProtocol, 
        client_id: int
    ):
        """Forward messages from vLLM server to client"""
        try:
            async for message in vllm_ws:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type', 'unknown')
                    
                    logger.debug(f"vLLM -> Client {client_id}: {msg_type}")
                    
                    # Forward to client
                    await client_ws.send(message)
                    
                    # Log transcription results
                    if msg_type == 'transcription.delta':
                        delta = data.get('delta', '')
                        logger.info(f"Transcription delta: {delta}")
                    elif msg_type == 'transcription.done':
                        text = data.get('text', '')
                        logger.info(f"Transcription complete: {text}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from vLLM: {e}")
                except Exception as e:
                    logger.error(f"Error forwarding vLLM message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"vLLM connection closed for client {client_id}")
        except Exception as e:
            logger.error(f"Error in vLLM->client forwarding: {e}")
    
    async def start(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the WebSocket server"""
        logger.info(f"Starting Voxtral proxy server on {host}:{port}")
        logger.info(f"Proxying to vLLM server at {self.vllm_url}")
        
        async with websockets.serve(self.handle_client, host, port):
            logger.info(f"Server ready and listening on ws://{host}:{port}")
            await asyncio.Future()  # Run forever


def main():
    parser = argparse.ArgumentParser(
        description="Voxtral Realtime Transcription Proxy Server"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the proxy server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind the proxy server (default: 8080)"
    )
    parser.add_argument(
        "--vllm-host",
        type=str,
        default="127.0.0.1",
        help="vLLM server host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--vllm-port",
        type=int,
        default=8000,
        help="vLLM server port (default: 8000)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    server = VoxtralServer(vllm_host=args.vllm_host, vllm_port=args.vllm_port)
    
    try:
        asyncio.run(server.start(host=args.host, port=args.port))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)


if __name__ == "__main__":
    main()

# Made with Bob
