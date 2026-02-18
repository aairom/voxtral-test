# 🏗️ Architecture Documentation

This document provides a comprehensive overview of the Voxtral Realtime Transcription application architecture, including system components, data flows, and implementation details.

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagrams](#architecture-diagrams)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Deployment Options](#deployment-options)

---

## System Overview

The Voxtral Realtime Transcription application is a web-based system that enables real-time speech-to-text transcription using AI models. It supports two deployment modes:

1. **GPU Mode**: Uses Mistral AI's Voxtral-Mini-4B-Realtime-2602 model via vLLM
2. **CPU Mode**: Uses Vosk for CPU-compatible real-time transcription

---

## Architecture Diagrams

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Web Browser UI]
        MIC[Microphone Input]
        VIZ[Audio Visualizer]
        TRANS[Transcript Display]
    end
    
    subgraph "Application Layer"
        WS[WebSocket Client]
        AUDIO[Audio Processor]
        STATE[State Manager]
    end
    
    subgraph "Server Layer - GPU"
        PROXY1[Proxy Server<br/>server.py]
        VLLM[vLLM Server<br/>Voxtral Model]
    end
    
    subgraph "Server Layer - CPU"
        VOSK[Vosk Server<br/>server_vosk.py]
        MODEL[Vosk Model]
    end
    
    MIC --> AUDIO
    AUDIO --> WS
    WS --> UI
    UI --> VIZ
    UI --> TRANS
    
    WS <-->|WebSocket| PROXY1
    PROXY1 <-->|WebSocket| VLLM
    
    WS <-->|WebSocket| VOSK
    VOSK --> MODEL
    
    style UI fill:#6366f1,stroke:#4f46e5,color:#fff
    style VLLM fill:#10b981,stroke:#059669,color:#fff
    style VOSK fill:#f59e0b,stroke:#d97706,color:#fff
```

### GPU Mode - Detailed Architecture

```mermaid
graph LR
    subgraph "Browser"
        A[User Interface<br/>index.html]
        B[Audio Capture<br/>Web Audio API]
        C[WebSocket Client<br/>app.js]
        D[Visualizer<br/>Canvas API]
    end
    
    subgraph "Proxy Server"
        E[WebSocket Handler<br/>server.py]
        F[Message Router]
        G[Session Manager]
    end
    
    subgraph "vLLM Server"
        H[WebSocket Endpoint<br/>/v1/realtime]
        I[Voxtral Model<br/>4B Parameters]
        J[Audio Processor]
        K[Transcription Engine]
    end
    
    subgraph "Infrastructure"
        L[NVIDIA GPU<br/>16GB+ VRAM]
        M[CUDA Runtime]
        N[Model Cache]
    end
    
    B -->|PCM16 Audio| C
    C <-->|WS Messages| E
    E <-->|WS Messages| H
    H --> J
    J --> I
    I --> K
    K -->|Transcription| H
    H -->|Response| E
    E -->|Response| C
    C --> A
    C --> D
    
    I -.->|Uses| L
    I -.->|Uses| M
    I -.->|Loads from| N
    
    style A fill:#6366f1,stroke:#4f46e5,color:#fff
    style I fill:#10b981,stroke:#059669,color:#fff
    style L fill:#ef4444,stroke:#dc2626,color:#fff
```

### CPU Mode - Detailed Architecture

```mermaid
graph LR
    subgraph "Browser"
        A[User Interface<br/>index.html]
        B[Audio Capture<br/>Web Audio API]
        C[WebSocket Client<br/>app.js]
        D[Visualizer<br/>Canvas API]
    end
    
    subgraph "Vosk Server"
        E[WebSocket Handler<br/>server_vosk.py]
        F[Session Manager]
        G[Audio Buffer]
        H[Vosk Recognizer]
        I[Vosk Model<br/>40MB-1.8GB]
    end
    
    subgraph "Infrastructure"
        J[CPU<br/>Any Modern CPU]
        K[RAM<br/>2-4GB]
    end
    
    B -->|PCM16 Audio| C
    C <-->|WS Messages| E
    E --> F
    F --> G
    G --> H
    H --> I
    I -->|Transcription| H
    H -->|Response| E
    E -->|Response| C
    C --> A
    C --> D
    
    H -.->|Uses| J
    I -.->|Loads to| K
    
    style A fill:#6366f1,stroke:#4f46e5,color:#fff
    style I fill:#f59e0b,stroke:#d97706,color:#fff
    style J fill:#10b981,stroke:#059669,color:#fff
```

### WebSocket Communication Flow

```mermaid
sequenceDiagram
    participant Browser
    participant Client as WebSocket Client
    participant Server as Proxy/Vosk Server
    participant Model as AI Model
    
    Browser->>Client: User clicks "Connect"
    Client->>Server: WebSocket Connect
    Server->>Client: session.created
    Client->>Browser: Update UI (Connected)
    
    Browser->>Client: User clicks "Start Recording"
    Client->>Browser: Request Microphone Access
    Browser->>Client: Microphone Stream
    
    Client->>Server: session.update (model info)
    Server->>Client: session.updated
    
    Client->>Server: input_audio_buffer.commit
    
    loop Audio Streaming
        Browser->>Client: Audio Chunk (PCM16)
        Client->>Client: Convert to Base64
        Client->>Server: input_audio_buffer.append
        Server->>Model: Process Audio
        Model->>Server: Partial Transcription
        Server->>Client: transcription.delta
        Client->>Browser: Update Transcript
    end
    
    Browser->>Client: User clicks "Stop"
    Client->>Server: input_audio_buffer.commit (final)
    Server->>Model: Process Final Audio
    Model->>Server: Final Transcription
    Server->>Client: transcription.done
    Client->>Browser: Display Final Transcript
    
    Browser->>Client: User clicks "Disconnect"
    Client->>Server: WebSocket Close
    Server->>Client: Connection Closed
```

### Audio Processing Pipeline

```mermaid
graph TB
    subgraph "Audio Capture"
        A[Microphone] --> B[MediaStream API]
        B --> C[AudioContext<br/>16kHz Sample Rate]
    end
    
    subgraph "Audio Processing"
        C --> D[ScriptProcessor<br/>4096 samples]
        D --> E[Float32Array<br/>Audio Data]
        E --> F[Convert to Int16<br/>PCM16 Format]
        F --> G[Base64 Encode]
    end
    
    subgraph "Visualization"
        C --> H[AnalyserNode]
        H --> I[FFT Analysis]
        I --> J[Canvas Rendering<br/>Waveform]
    end
    
    subgraph "Transmission"
        G --> K[WebSocket Send]
        K --> L[Server Processing]
    end
    
    subgraph "Feedback"
        L --> M[Transcription Result]
        M --> N[UI Update]
        H --> O[Audio Level Display]
    end
    
    style A fill:#6366f1,stroke:#4f46e5,color:#fff
    style L fill:#10b981,stroke:#059669,color:#fff
    style J fill:#f59e0b,stroke:#d97706,color:#fff
```

### Message Protocol Flow

```mermaid
stateDiagram-v2
    [*] --> Disconnected
    Disconnected --> Connecting: Connect Button
    Connecting --> Connected: session.created
    Connecting --> Error: Connection Failed
    Error --> Disconnected: Retry
    
    Connected --> Idle: Ready
    Idle --> Recording: Start Recording
    Recording --> Processing: Audio Chunks
    Processing --> Recording: Continue
    Processing --> Finalizing: Stop Recording
    Finalizing --> Idle: transcription.done
    
    Idle --> Disconnected: Disconnect
    Recording --> Disconnected: Connection Lost
    Processing --> Disconnected: Connection Lost
    
    state Recording {
        [*] --> Capturing
        Capturing --> Encoding: Audio Data
        Encoding --> Sending: Base64
        Sending --> Capturing: Next Chunk
    }
    
    state Processing {
        [*] --> Receiving
        Receiving --> Decoding: transcription.delta
        Decoding --> Displaying: Update UI
        Displaying --> Receiving: Next Delta
    }
```

### Deployment Architecture - GPU Mode

```mermaid
graph TB
    subgraph "User's Machine"
        BROWSER[Web Browser]
    end
    
    subgraph "Server Infrastructure"
        subgraph "Container Runtime"
            PODMAN[Podman/Docker]
            VLLM_CONTAINER[vLLM Container<br/>CUDA + Voxtral]
        end
        
        subgraph "Python Environment"
            PROXY[Proxy Server<br/>Python + WebSockets]
        end
        
        subgraph "Hardware"
            GPU[NVIDIA GPU<br/>16GB+ VRAM]
            CPU[CPU]
            RAM[RAM 32GB+]
        end
    end
    
    subgraph "External Services"
        HF[Hugging Face<br/>Model Repository]
    end
    
    BROWSER <-->|HTTPS/WSS| PROXY
    PROXY <-->|WebSocket| VLLM_CONTAINER
    VLLM_CONTAINER -.->|Uses| GPU
    PROXY -.->|Uses| CPU
    VLLM_CONTAINER -.->|Downloads| HF
    
    style BROWSER fill:#6366f1,stroke:#4f46e5,color:#fff
    style GPU fill:#ef4444,stroke:#dc2626,color:#fff
    style VLLM_CONTAINER fill:#10b981,stroke:#059669,color:#fff
```

### Deployment Architecture - CPU Mode

```mermaid
graph TB
    subgraph "User's Machine"
        BROWSER[Web Browser]
    end
    
    subgraph "Server Infrastructure"
        subgraph "Python Environment"
            VOSK_SERVER[Vosk Server<br/>Python + WebSockets]
            VOSK_LIB[Vosk Library]
        end
        
        subgraph "Models"
            SMALL[Small Model<br/>40MB]
            LARGE[Large Model<br/>1.8GB]
        end
        
        subgraph "Hardware"
            CPU[CPU<br/>Any Modern CPU]
            RAM[RAM 2-4GB]
        end
    end
    
    subgraph "External Services"
        ALPHACEPHEI[AlphaCephei<br/>Model Repository]
    end
    
    BROWSER <-->|HTTPS/WSS| VOSK_SERVER
    VOSK_SERVER --> VOSK_LIB
    VOSK_LIB --> SMALL
    VOSK_LIB --> LARGE
    VOSK_SERVER -.->|Uses| CPU
    VOSK_LIB -.->|Loads to| RAM
    SMALL -.->|Downloads| ALPHACEPHEI
    LARGE -.->|Downloads| ALPHACEPHEI
    
    style BROWSER fill:#6366f1,stroke:#4f46e5,color:#fff
    style CPU fill:#10b981,stroke:#059669,color:#fff
    style VOSK_SERVER fill:#f59e0b,stroke:#d97706,color:#fff
```

---

## Component Details

### Frontend Components

#### 1. User Interface (`index.html`)
- **Purpose**: Main application interface
- **Features**:
  - Connection settings panel
  - Audio source selection
  - Control buttons (Connect, Start, Stop, Clear)
  - Real-time transcription display
  - Statistics dashboard
  - System logs viewer
- **Technologies**: HTML5, Semantic markup

#### 2. Styling (`style.css`)
- **Purpose**: Visual design and theming
- **Features**:
  - Dark theme with gradient backgrounds
  - Responsive grid layout
  - Animated status indicators
  - Custom scrollbars
  - Button hover effects
- **Technologies**: CSS3, Flexbox, Grid

#### 3. Client Application (`app.js`)
- **Purpose**: Client-side logic and WebSocket communication
- **Key Classes**:
  - `VoxtralClient`: Main application controller
- **Responsibilities**:
  - WebSocket connection management
  - Audio capture and processing
  - Real-time visualization
  - UI state management
  - Statistics tracking
- **Technologies**: JavaScript ES6+, Web Audio API, WebSocket API

### Backend Components

#### 1. GPU Proxy Server (`server.py`)
- **Purpose**: Bridge between web client and vLLM server
- **Key Classes**:
  - `VoxtralServer`: WebSocket proxy handler
- **Responsibilities**:
  - Client connection management
  - Message forwarding (bidirectional)
  - Session tracking
  - Error handling
- **Technologies**: Python 3.9+, websockets, asyncio

#### 2. CPU Vosk Server (`server_vosk.py`)
- **Purpose**: Direct transcription using Vosk
- **Key Classes**:
  - `VoskTranscriptionServer`: WebSocket handler with Vosk integration
- **Responsibilities**:
  - Audio buffer management
  - Real-time recognition
  - Partial result streaming
  - Session management
- **Technologies**: Python 3.9+, websockets, vosk, asyncio

#### 3. vLLM Server (External)
- **Purpose**: Run Voxtral model for transcription
- **Deployment**: Podman/Docker container
- **Requirements**: NVIDIA GPU, CUDA
- **Endpoint**: `/v1/realtime` (WebSocket)

---

## Data Flow

### Audio Data Flow

```mermaid
graph LR
    A[Microphone] -->|Raw Audio| B[Web Audio API]
    B -->|Float32Array| C[Audio Processor]
    C -->|Int16Array PCM16| D[Base64 Encoder]
    D -->|String| E[WebSocket]
    E -->|Network| F[Server]
    F -->|Decode| G[Audio Buffer]
    G -->|Process| H[AI Model]
    H -->|Text| I[Response]
    I -->|Network| E
    E -->|JSON| J[Client]
    J -->|Display| K[UI]
    
    style A fill:#6366f1,stroke:#4f46e5,color:#fff
    style H fill:#10b981,stroke:#059669,color:#fff
    style K fill:#f59e0b,stroke:#d97706,color:#fff
```

### Message Types

#### Client → Server

1. **session.update**
   ```json
   {
     "type": "session.update",
     "model": "mistralai/Voxtral-Mini-4B-Realtime-2602"
   }
   ```

2. **input_audio_buffer.append**
   ```json
   {
     "type": "input_audio_buffer.append",
     "audio": "base64_encoded_pcm16_data"
   }
   ```

3. **input_audio_buffer.commit**
   ```json
   {
     "type": "input_audio_buffer.commit",
     "final": true
   }
   ```

#### Server → Client

1. **session.created**
   ```json
   {
     "type": "session.created",
     "id": "session-12345",
     "model": "voxtral-mini-4b",
     "object": "realtime.session"
   }
   ```

2. **transcription.delta**
   ```json
   {
     "type": "transcription.delta",
     "delta": "partial transcription text",
     "object": "realtime.transcription.delta"
   }
   ```

3. **transcription.done**
   ```json
   {
     "type": "transcription.done",
     "text": "complete transcription text",
     "usage": {
       "tokens": 150,
       "duration": 5.2
     }
   }
   ```

---

## Technology Stack

### Frontend Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| UI Framework | Vanilla HTML5 | - | Structure |
| Styling | CSS3 | - | Design |
| Client Logic | JavaScript ES6+ | - | Functionality |
| Audio API | Web Audio API | - | Audio capture |
| Communication | WebSocket API | - | Real-time messaging |
| Visualization | Canvas API | - | Waveform display |

### Backend Stack - GPU Mode

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.9+ | Server logic |
| WebSocket | websockets | 12.0+ | Communication |
| Async | asyncio | Built-in | Concurrency |
| Model Server | vLLM | Latest | Model inference |
| Container | Podman/Docker | Latest | Deployment |
| GPU Runtime | CUDA | 11.8+ | GPU acceleration |

### Backend Stack - CPU Mode

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.9+ | Server logic |
| WebSocket | websockets | 12.0+ | Communication |
| ASR Engine | Vosk | 0.3.45+ | Speech recognition |
| Async | asyncio | Built-in | Concurrency |

---

## Deployment Options

### Option 1: Local Development

```mermaid
graph LR
    A[Developer Machine] --> B[Browser]
    A --> C[Python Server]
    A --> D[vLLM/Vosk]
    
    B <--> C
    C <--> D
    
    style A fill:#6366f1,stroke:#4f46e5,color:#fff
```

### Option 2: Client-Server Split

```mermaid
graph LR
    A[User's Browser] <-->|Internet| B[Server]
    B --> C[Python Proxy]
    B --> D[vLLM/Vosk]
    
    style A fill:#6366f1,stroke:#4f46e5,color:#fff
    style B fill:#10b981,stroke:#059669,color:#fff
```

### Option 3: Cloud Deployment

```mermaid
graph TB
    A[Users] <-->|HTTPS/WSS| B[Load Balancer]
    B --> C[Server 1]
    B --> D[Server 2]
    B --> E[Server N]
    
    C --> F[GPU Pool]
    D --> F
    E --> F
    
    style A fill:#6366f1,stroke:#4f46e5,color:#fff
    style B fill:#10b981,stroke:#059669,color:#fff
    style F fill:#ef4444,stroke:#dc2626,color:#fff
```

---

## Performance Characteristics

### GPU Mode (Voxtral)

| Metric | Value | Notes |
|--------|-------|-------|
| Latency | <500ms | End-to-end |
| Throughput | Real-time | 1x audio speed |
| Accuracy | 95-98% | English |
| GPU Memory | 4-6GB | VRAM usage |
| Languages | 13 | Multilingual |

### CPU Mode (Vosk)

| Metric | Value | Notes |
|--------|-------|-------|
| Latency | 500ms-2s | End-to-end |
| Throughput | Real-time | 1x audio speed |
| Accuracy | 85-95% | Depends on model |
| CPU Usage | 20-40% | Modern CPUs |
| Languages | 20+ | Multiple models |

---

## Security Considerations

1. **WebSocket Security**: Use WSS (WebSocket Secure) in production
2. **Authentication**: Implement token-based auth for production
3. **Rate Limiting**: Prevent abuse with request throttling
4. **Input Validation**: Sanitize all client inputs
5. **CORS**: Configure appropriate CORS policies
6. **Data Privacy**: Audio is not stored by default

---

## Scalability

### Horizontal Scaling

```mermaid
graph TB
    LB[Load Balancer] --> S1[Server Instance 1]
    LB --> S2[Server Instance 2]
    LB --> S3[Server Instance N]
    
    S1 --> G1[GPU 1]
    S2 --> G2[GPU 2]
    S3 --> G3[GPU N]
    
    style LB fill:#6366f1,stroke:#4f46e5,color:#fff
    style G1 fill:#ef4444,stroke:#dc2626,color:#fff
    style G2 fill:#ef4444,stroke:#dc2626,color:#fff
    style G3 fill:#ef4444,stroke:#dc2626,color:#fff
```

### Vertical Scaling

- Increase GPU memory for larger models
- Add more CPU cores for Vosk
- Increase RAM for model caching

---

## Future Enhancements

1. **Multi-user Support**: Session management for multiple concurrent users
2. **Recording Storage**: Optional audio/transcript storage
3. **Language Detection**: Automatic language identification
4. **Speaker Diarization**: Identify different speakers
5. **Punctuation**: Automatic punctuation insertion
6. **Custom Vocabulary**: Domain-specific word lists
7. **Real-time Translation**: Multi-language translation
8. **API Integration**: RESTful API for programmatic access

---

## References

- [Voxtral Model Card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602)
- [vLLM Documentation](https://docs.vllm.ai/)
- [Vosk Documentation](https://alphacephei.com/vosk/)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)