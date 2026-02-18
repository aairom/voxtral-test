# 🎤 Voxtral Realtime Speech Transcription

A web-based application for testing the **Mistral AI Voxtral-Mini-4B-Realtime-2602** model for real-time speech transcription. This application provides a user-friendly interface to capture audio from your microphone and receive live transcriptions with low latency (<500ms).

**🖥️ CPU-Only Version Available!** Don't have a GPU? Check out [`QUICKSTART_CPU.md`](QUICKSTART_CPU.md) for a CPU-compatible version using Vosk.

![Voxtral UI](https://img.shields.io/badge/Status-Ready-green) ![Python](https://img.shields.io/badge/Python-3.9+-blue) ![License](https://img.shields.io/badge/License-MIT-yellow) ![CPU](https://img.shields.io/badge/CPU-Compatible-orange)

## 🌟 Features

- **Real-time Speech Transcription**: Low-latency transcription with <500ms delay
- **Audio Visualization**: Live waveform visualization of audio input
- **Multiple Audio Sources**: Select from available microphone devices
- **Statistics Dashboard**: Monitor chunks sent, responses received, latency, and duration
- **Transcript Management**: Copy, download, and clear transcriptions
- **System Logs**: Detailed logging for debugging and monitoring
- **Modern UI**: Beautiful, responsive dark-themed interface
- **WebSocket Communication**: Efficient bidirectional streaming

## 📋 Prerequisites

### Two Setup Options Available:

#### Option 1: GPU Setup (Original Voxtral)
**Hardware Requirements:**
- **NVIDIA GPU with 16GB+ VRAM** (for running the vLLM server)
- Microphone or audio input device

**Software Requirements:**
- **Python 3.9+** with websockets and numpy
- **Podman** (or Docker) for running the vLLM server
- Modern web browser with WebSocket and Web Audio API support (Chrome, Firefox, Edge)

#### Option 2: CPU-Only Setup (Vosk Alternative) ⭐ Recommended for Testing
**Hardware Requirements:**
- Any modern CPU (no GPU required!)
- Microphone or audio input device

**Software Requirements:**
- **Python 3.9+** with websockets and vosk
- Modern web browser with WebSocket and Web Audio API support (Chrome, Firefox, Edge)

**👉 For CPU-only setup, see [`QUICKSTART_CPU.md`](QUICKSTART_CPU.md) for a 5-minute setup guide!**

## 🚀 Quick Start

### Step 1: Clone or Download

```bash
# If you have this as a git repository
git clone <repository-url>
cd voxtral-test

# Or simply navigate to the directory where you extracted the files
cd voxtral-test
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Start the vLLM Server

The vLLM server runs the Voxtral model. You can use either the RHAII Preview Image or download the model directly.

#### Option A: Using RHAII Preview Image (Recommended)

```bash
podman run --rm \
  --device nvidia.com/gpu=0 \
  --security-opt=label=disable \
  --shm-size=4g \
  -p 8000:8000 \
  -v ~/.cache/huggingface:/hf:Z \
  -e HF_HUB_OFFLINE=1 \
  -e VLLM_DISABLE_COMPILE_CACHE=1 \
  -e HF_HOME=/hf \
  registry.redhat.io/rhaiis-preview/vllm-cuda-rhel9:voxtral-realtime \
  --model mistralai/Voxtral-Mini-4B-Realtime-2602 \
  --tokenizer-mode mistral \
  --config-format mistral \
  --load-format mistral \
  --trust-remote-code \
  --compilation-config '{"cudagraph_mode":"PIECEWISE"}' \
  --tensor-parallel-size 1 \
  --max-model-len 45000 \
  --max-num-batched-tokens 8192 \
  --max-num-seqs 16 \
  --gpu-memory-utilization 0.90 \
  --host 0.0.0.0 --port 8000
```

#### Option B: Download Model First

```bash
# Download the model
huggingface-cli download mistralai/Voxtral-Mini-4B-Realtime-2602

# Then run with the downloaded model
podman run --rm \
  --device nvidia.com/gpu=0 \
  --security-opt=label=disable \
  --shm-size=4g \
  -p 8000:8000 \
  -v ~/.cache/huggingface:/hf:Z \
  -e HF_HOME=/hf \
  registry.redhat.io/rhaiis-preview/vllm-cuda-rhel9:voxtral-realtime \
  --model mistralai/Voxtral-Mini-4B-Realtime-2602 \
  --tokenizer-mode mistral \
  --config-format mistral \
  --load-format mistral \
  --trust-remote-code \
  --compilation-config '{"cudagraph_mode":"PIECEWISE"}' \
  --tensor-parallel-size 1 \
  --max-model-len 45000 \
  --max-num-batched-tokens 8192 \
  --max-num-seqs 16 \
  --gpu-memory-utilization 0.90 \
  --host 0.0.0.0 --port 8000
```

**Note**: The vLLM server will be available at `ws://127.0.0.1:8000/v1/realtime`

### Step 4: Start the Proxy Server

The proxy server bridges the web client and the vLLM server:

```bash
python server.py
```

By default, the proxy server runs on `http://0.0.0.0:8080`. You can customize this:

```bash
# Custom host and port
python server.py --host 0.0.0.0 --port 8080

# Connect to remote vLLM server
python server.py --vllm-host 192.168.1.100 --vllm-port 8000

# Enable debug logging
python server.py --debug
```

### Step 5: Open the Web Interface

Open `index.html` in your web browser:

```bash
# On macOS
open index.html

# On Linux
xdg-open index.html

# On Windows
start index.html

# Or use a simple HTTP server
python -m http.server 3000
# Then visit http://localhost:3000
```

## 🎮 Usage

1. **Select Audio Source**: Choose your microphone from the dropdown
2. **Connect to Server**: Click "Connect to Server" to establish WebSocket connection
3. **Start Recording**: Click "Start Recording" to begin capturing audio
4. **View Transcription**: Watch real-time transcription appear in the transcript panel
5. **Monitor Stats**: Check latency, chunks sent, and other statistics
6. **Stop Recording**: Click "Stop Recording" when done
7. **Manage Transcript**: Copy or download your transcription

## 📁 Project Structure

```
voxtral-test/
├── index.html          # Main web interface
├── style.css           # Styling and theme
├── app.js              # Client-side JavaScript (WebSocket, audio handling)
├── server.py           # Python proxy server
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🔧 Configuration

### Client Configuration (in browser)
- **Server Host**: Default `127.0.0.1`
- **Server Port**: Default `8000`
- **Model**: `mistralai/Voxtral-Mini-4B-Realtime-2602`

### Server Configuration (command line)
```bash
python server.py --help

Options:
  --host HOST           Host to bind the proxy server (default: 0.0.0.0)
  --port PORT           Port to bind the proxy server (default: 8080)
  --vllm-host HOST      vLLM server host (default: 127.0.0.1)
  --vllm-port PORT      vLLM server port (default: 8000)
  --debug               Enable debug logging
```

## 🎯 Technical Details

### Audio Processing
- **Sample Rate**: 16kHz
- **Channels**: Mono (1 channel)
- **Format**: PCM16 (16-bit signed integer)
- **Chunk Size**: 4096 samples
- **Encoding**: Base64 for transmission

### WebSocket Protocol
The application uses WebSocket for bidirectional communication:

**Client → Server Messages:**
- `session.update`: Initialize session with model
- `input_audio_buffer.append`: Send audio chunks
- `input_audio_buffer.commit`: Signal audio completion

**Server → Client Messages:**
- `session.created`: Session initialization confirmation
- `transcription.delta`: Incremental transcription updates
- `transcription.done`: Final transcription result
- `error`: Error messages

### Architecture
```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │ ◄─────► │ Proxy Server │ ◄─────► │ vLLM Server │
│  (Client)   │  WS     │  (Python)    │  WS     │  (Voxtral)  │
└─────────────┘         └──────────────┘         └─────────────┘
```

## 🐛 Troubleshooting

### Connection Issues
- Ensure vLLM server is running and accessible
- Check firewall settings for ports 8000 and 8080
- Verify WebSocket URLs in browser console

### Audio Issues
- Grant microphone permissions in browser
- Check audio device selection
- Verify audio levels in visualization

### Performance Issues
- Ensure GPU has sufficient VRAM (16GB+)
- Monitor GPU utilization
- Check network latency between components

### Common Errors

**"Connection refused"**
- vLLM server not running or wrong host/port
- Solution: Start vLLM server and verify connection settings

**"No audio devices found"**
- Microphone not connected or permissions denied
- Solution: Connect microphone and grant browser permissions

**"Session creation failed"**
- vLLM server not ready or model not loaded
- Solution: Wait for vLLM server to fully initialize

## 📊 Performance

- **Latency**: <500ms typical
- **Accuracy**: Comparable to offline systems
- **Languages**: Supports 13 languages
- **GPU Memory**: ~4-6GB VRAM usage

## 🔗 Resources

- [Voxtral Model Card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602)
- [vLLM Documentation](https://docs.vllm.ai/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)

## 📝 License

This project is provided as-is for testing and evaluation purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## ⚠️ Notes

- This is a testing/demo application
- Requires NVIDIA GPU for vLLM server
- Audio is processed in real-time and not stored
- Transcriptions are client-side only (not saved to server)

## 🎉 Acknowledgments

- Mistral AI for the Voxtral model
- vLLM team for the inference engine
- Red Hat AI for the container images