#!/usr/bin/env python3
"""
CPU-Compatible Realtime Transcription Server using Vosk
Works on CPU without GPU requirements
"""

import argparse
import asyncio
import base64
import json
import logging
import os
import struct
from typing import Optional

import websockets
from websockets.server import WebSocketServerProtocol

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    print("⚠️  Vosk not installed. Install with: pip install vosk")
    print("⚠️  Download a model from: https://alphacephei.com/vosk/models")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VoskTranscriptionServer:
    def __init__(self, model_path: str):
        if not VOSK_AVAILABLE:
            raise ImportError("Vosk is not installed. Run: pip install vosk")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}\n"
                f"Download from: https://alphacephei.com/vosk/models\n"
                f"Example: vosk-model-small-en-us-0.15"
            )
        
        logger.info(f"Loading Vosk model from {model_path}")
        self.model = Model(model_path)
        logger.info("Model loaded successfully")
        
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle incoming client WebSocket connection"""
        client_id = id(websocket)
        logger.info(f"Client {client_id} connected from {websocket.remote_address}")
        
        # Create recognizer for this session
        recognizer = KaldiRecognizer(self.model, 16000)
        recognizer.SetWords(True)
        
        session_id = f"vosk-session-{client_id}"
        
        try:
            # Send session.created
            await websocket.send(json.dumps({
                'type': 'session.created',
                'id': session_id,
                'model': 'vosk-cpu',
                'object': 'realtime.session'
            }))
            
            logger.info(f"Session created: {session_id}")
            
            audio_buffer = bytearray()
            is_recording = False
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type', 'unknown')
                    
                    logger.debug(f"Client {client_id}: {msg_type}")
                    
                    if msg_type == 'session.update':
                        # Acknowledge session update
                        await websocket.send(json.dumps({
                            'type': 'session.updated',
                            'session': {
                                'id': session_id,
                                'model': 'vosk-cpu'
                            }
                        }))
                        
                    elif msg_type == 'input_audio_buffer.commit':
                        is_recording = True
                        if data.get('final', False):
                            # Process final audio
                            if recognizer.AcceptWaveform(bytes(audio_buffer)):
                                result = json.loads(recognizer.Result())
                                text = result.get('text', '')
                                
                                if text:
                                    await websocket.send(json.dumps({
                                        'type': 'transcription.done',
                                        'text': text,
                                        'object': 'realtime.transcription'
                                    }))
                                    logger.info(f"Final transcription: {text}")
                            
                            # Get any remaining text
                            final_result = json.loads(recognizer.FinalResult())
                            final_text = final_result.get('text', '')
                            if final_text:
                                await websocket.send(json.dumps({
                                    'type': 'transcription.done',
                                    'text': final_text,
                                    'object': 'realtime.transcription'
                                }))
                            
                            # Reset for next session
                            audio_buffer.clear()
                            recognizer = KaldiRecognizer(self.model, 16000)
                            recognizer.SetWords(True)
                            is_recording = False
                        
                    elif msg_type == 'input_audio_buffer.append':
                        if is_recording:
                            # Decode base64 audio
                            audio_b64 = data.get('audio', '')
                            audio_bytes = base64.b64decode(audio_b64)
                            
                            # Add to buffer
                            audio_buffer.extend(audio_bytes)
                            
                            # Process in chunks
                            if len(audio_buffer) >= 8192:  # Process every 8KB
                                chunk = bytes(audio_buffer[:8192])
                                audio_buffer = audio_buffer[8192:]
                                
                                if recognizer.AcceptWaveform(chunk):
                                    result = json.loads(recognizer.Result())
                                    text = result.get('text', '')
                                    
                                    if text:
                                        # Send partial result
                                        await websocket.send(json.dumps({
                                            'type': 'transcription.delta',
                                            'delta': text + ' ',
                                            'object': 'realtime.transcription.delta'
                                        }))
                                        logger.info(f"Partial transcription: {text}")
                                else:
                                    # Send partial result
                                    partial = json.loads(recognizer.PartialResult())
                                    partial_text = partial.get('partial', '')
                                    
                                    if partial_text:
                                        await websocket.send(json.dumps({
                                            'type': 'transcription.delta',
                                            'delta': partial_text,
                                            'object': 'realtime.transcription.delta'
                                        }))
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from client {client_id}: {e}")
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'error': f'Invalid JSON: {str(e)}'
                    }))
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'error': f'Processing error: {str(e)}'
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} connection closed")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}", exc_info=True)
        finally:
            logger.info(f"Client {client_id} disconnected")
    
    async def start(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the WebSocket server"""
        logger.info(f"Starting Vosk transcription server on {host}:{port}")
        logger.info("This server runs on CPU - no GPU required!")
        
        async with websockets.serve(self.handle_client, host, port):
            logger.info(f"Server ready and listening on ws://{host}:{port}")
            await asyncio.Future()  # Run forever


def main():
    parser = argparse.ArgumentParser(
        description="CPU-Compatible Realtime Transcription Server using Vosk"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind the server (default: 8080)"
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Path to Vosk model directory (e.g., vosk-model-small-en-us-0.15)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not VOSK_AVAILABLE:
        print("\n❌ Vosk is not installed!")
        print("\nInstall with:")
        print("  pip install vosk")
        print("\nDownload a model from:")
        print("  https://alphacephei.com/vosk/models")
        print("\nExample models:")
        print("  - vosk-model-small-en-us-0.15 (40MB, fast)")
        print("  - vosk-model-en-us-0.22 (1.8GB, accurate)")
        return 1
    
    try:
        server = VoskTranscriptionServer(model_path=args.model)
        asyncio.run(server.start(host=args.host, port=args.port))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

# Made with Bob
