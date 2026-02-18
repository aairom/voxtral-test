// Voxtral Realtime Transcription Client
class VoxtralClient {
    constructor() {
        this.ws = null;
        this.audioContext = null;
        this.mediaStream = null;
        this.audioWorkletNode = null;
        this.isRecording = false;
        this.isConnected = false;
        this.sessionId = null;
        
        // Statistics
        this.stats = {
            startTime: null,
            chunksSent: 0,
            responsesReceived: 0,
            lastLatency: 0
        };
        
        // UI Elements
        this.elements = {
            serverHost: document.getElementById('serverHost'),
            serverPort: document.getElementById('serverPort'),
            audioSource: document.getElementById('audioSource'),
            connectBtn: document.getElementById('connectBtn'),
            startBtn: document.getElementById('startBtn'),
            stopBtn: document.getElementById('stopBtn'),
            clearBtn: document.getElementById('clearBtn'),
            copyBtn: document.getElementById('copyBtn'),
            downloadBtn: document.getElementById('downloadBtn'),
            clearLogsBtn: document.getElementById('clearLogsBtn'),
            autoScrollLogs: document.getElementById('autoScrollLogs'),
            connectionStatus: document.getElementById('connectionStatus'),
            recordingStatus: document.getElementById('recordingStatus'),
            audioStatus: document.getElementById('audioStatus'),
            audioLevel: document.getElementById('audioLevel'),
            transcriptOutput: document.getElementById('transcriptOutput'),
            logsOutput: document.getElementById('logsOutput'),
            wordCount: document.getElementById('wordCount'),
            duration: document.getElementById('duration'),
            chunksSent: document.getElementById('chunksSent'),
            responsesReceived: document.getElementById('responsesReceived'),
            latency: document.getElementById('latency'),
            visualizer: document.getElementById('visualizer')
        };
        
        this.canvasContext = this.elements.visualizer.getContext('2d');
        this.initializeUI();
        this.setupEventListeners();
        this.enumerateAudioDevices();
    }
    
    initializeUI() {
        this.updateConnectionStatus(false);
        this.updateRecordingStatus(false);
        this.log('Application initialized', 'info');
    }
    
    setupEventListeners() {
        this.elements.connectBtn.addEventListener('click', () => this.toggleConnection());
        this.elements.startBtn.addEventListener('click', () => this.startRecording());
        this.elements.stopBtn.addEventListener('click', () => this.stopRecording());
        this.elements.clearBtn.addEventListener('click', () => this.clearTranscript());
        this.elements.copyBtn.addEventListener('click', () => this.copyTranscript());
        this.elements.downloadBtn.addEventListener('click', () => this.downloadTranscript());
        this.elements.clearLogsBtn.addEventListener('click', () => this.clearLogs());
    }
    
    async enumerateAudioDevices() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const audioInputs = devices.filter(device => device.kind === 'audioinput');
            
            this.elements.audioSource.innerHTML = '<option value="">Select microphone...</option>';
            audioInputs.forEach(device => {
                const option = document.createElement('option');
                option.value = device.deviceId;
                option.textContent = device.label || `Microphone ${audioInputs.indexOf(device) + 1}`;
                this.elements.audioSource.appendChild(option);
            });
            
            if (audioInputs.length > 0) {
                this.elements.audioSource.selectedIndex = 1;
            }
            
            this.log(`Found ${audioInputs.length} audio input device(s)`, 'info');
        } catch (error) {
            this.log(`Error enumerating devices: ${error.message}`, 'error');
        }
    }
    
    async toggleConnection() {
        if (this.isConnected) {
            this.disconnect();
        } else {
            await this.connect();
        }
    }
    
    async connect() {
        const host = this.elements.serverHost.value;
        const port = this.elements.serverPort.value;
        const wsUrl = `ws://${host}:${port}/v1/realtime`;
        
        this.log(`Connecting to ${wsUrl}...`, 'info');
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.elements.connectBtn.innerHTML = '<span class="btn-icon">🔌</span> Disconnect';
                this.elements.startBtn.disabled = false;
                this.log('Connected to server', 'success');
            };
            
            this.ws.onmessage = (event) => {
                this.handleServerMessage(event.data);
            };
            
            this.ws.onerror = (error) => {
                this.log(`WebSocket error: ${error.message || 'Connection failed'}`, 'error');
            };
            
            this.ws.onclose = () => {
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.elements.connectBtn.innerHTML = '<span class="btn-icon">🔌</span> Connect to Server';
                this.elements.startBtn.disabled = true;
                this.log('Disconnected from server', 'warning');
                
                if (this.isRecording) {
                    this.stopRecording();
                }
            };
        } catch (error) {
            this.log(`Connection error: ${error.message}`, 'error');
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
    
    async startRecording() {
        if (!this.isConnected) {
            this.log('Not connected to server', 'error');
            return;
        }
        
        const deviceId = this.elements.audioSource.value;
        if (!deviceId) {
            this.log('Please select an audio input device', 'error');
            return;
        }
        
        try {
            this.log('Starting audio capture...', 'info');
            
            // Get audio stream
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    deviceId: deviceId,
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            // Create audio context
            this.audioContext = new AudioContext({ sampleRate: 16000 });
            const source = this.audioContext.createMediaStreamSource(this.mediaStream);
            
            // Create analyzer for visualization
            this.analyzer = this.audioContext.createAnalyser();
            this.analyzer.fftSize = 2048;
            source.connect(this.analyzer);
            
            // Create script processor for audio data
            this.scriptProcessor = this.audioContext.createScriptProcessor(4096, 1, 1);
            source.connect(this.scriptProcessor);
            this.scriptProcessor.connect(this.audioContext.destination);
            
            this.scriptProcessor.onaudioprocess = (e) => {
                if (this.isRecording && this.ws && this.ws.readyState === WebSocket.OPEN) {
                    const inputData = e.inputBuffer.getChannelData(0);
                    this.sendAudioChunk(inputData);
                }
            };
            
            // Send session.update with model
            this.sendMessage({
                type: 'session.update',
                model: 'mistralai/Voxtral-Mini-4B-Realtime-2602'
            });
            
            // Signal ready to start
            this.sendMessage({
                type: 'input_audio_buffer.commit'
            });
            
            this.isRecording = true;
            this.stats.startTime = Date.now();
            this.stats.chunksSent = 0;
            this.stats.responsesReceived = 0;
            
            this.updateRecordingStatus(true);
            this.elements.startBtn.disabled = true;
            this.elements.stopBtn.disabled = false;
            this.elements.audioStatus.textContent = '🔴 Recording';
            
            this.startVisualization();
            this.startDurationTimer();
            
            this.log('Recording started', 'success');
        } catch (error) {
            this.log(`Error starting recording: ${error.message}`, 'error');
        }
    }
    
    stopRecording() {
        if (!this.isRecording) return;
        
        this.isRecording = false;
        
        // Send final commit
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.sendMessage({
                type: 'input_audio_buffer.commit',
                final: true
            });
        }
        
        // Stop audio processing
        if (this.scriptProcessor) {
            this.scriptProcessor.disconnect();
            this.scriptProcessor = null;
        }
        
        if (this.analyzer) {
            this.analyzer.disconnect();
            this.analyzer = null;
        }
        
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.mediaStream = null;
        }
        
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        
        if (this.durationInterval) {
            clearInterval(this.durationInterval);
            this.durationInterval = null;
        }
        
        this.updateRecordingStatus(false);
        this.elements.startBtn.disabled = false;
        this.elements.stopBtn.disabled = true;
        this.elements.audioStatus.textContent = '🔴 Not Recording';
        this.elements.audioLevel.textContent = 'Level: 0%';
        
        this.clearVisualization();
        
        this.log('Recording stopped', 'info');
    }
    
    sendAudioChunk(audioData) {
        // Convert Float32Array to Int16Array (PCM16)
        const pcm16 = new Int16Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
            const s = Math.max(-1, Math.min(1, audioData[i]));
            pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        
        // Convert to base64
        const base64Audio = this.arrayBufferToBase64(pcm16.buffer);
        
        // Send to server
        this.sendMessage({
            type: 'input_audio_buffer.append',
            audio: base64Audio
        });
        
        this.stats.chunksSent++;
        this.elements.chunksSent.textContent = this.stats.chunksSent;
    }
    
    sendMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }
    
    handleServerMessage(data) {
        try {
            const message = JSON.parse(data);
            
            if (message.type === 'session.created') {
                this.sessionId = message.id;
                this.log(`Session created: ${this.sessionId}`, 'success');
            } else if (message.type === 'transcription.delta') {
                this.appendTranscript(message.delta);
                this.stats.responsesReceived++;
                this.elements.responsesReceived.textContent = this.stats.responsesReceived;
            } else if (message.type === 'transcription.done') {
                if (message.text) {
                    this.appendTranscript('\n\n' + message.text);
                }
                this.log('Transcription completed', 'success');
                if (message.usage) {
                    this.log(`Usage: ${JSON.stringify(message.usage)}`, 'info');
                }
            } else if (message.type === 'error') {
                this.log(`Server error: ${message.error}`, 'error');
            }
            
            // Update latency
            if (this.stats.startTime) {
                this.stats.lastLatency = Date.now() - this.stats.startTime;
                this.elements.latency.textContent = `${this.stats.lastLatency}ms`;
            }
        } catch (error) {
            this.log(`Error parsing server message: ${error.message}`, 'error');
        }
    }
    
    appendTranscript(text) {
        const output = this.elements.transcriptOutput;
        
        // Remove placeholder if present
        const placeholder = output.querySelector('.placeholder');
        if (placeholder) {
            placeholder.remove();
        }
        
        // Append text
        output.textContent += text;
        
        // Update word count
        const words = output.textContent.trim().split(/\s+/).filter(w => w.length > 0);
        this.elements.wordCount.textContent = `Words: ${words.length}`;
        
        // Auto-scroll
        output.scrollTop = output.scrollHeight;
    }
    
    clearTranscript() {
        this.elements.transcriptOutput.innerHTML = '<p class="placeholder">Transcription will appear here...</p>';
        this.elements.wordCount.textContent = 'Words: 0';
        this.log('Transcript cleared', 'info');
    }
    
    copyTranscript() {
        const text = this.elements.transcriptOutput.textContent;
        if (text && !text.includes('Transcription will appear here')) {
            navigator.clipboard.writeText(text).then(() => {
                this.log('Transcript copied to clipboard', 'success');
            }).catch(err => {
                this.log(`Error copying transcript: ${err.message}`, 'error');
            });
        }
    }
    
    downloadTranscript() {
        const text = this.elements.transcriptOutput.textContent;
        if (text && !text.includes('Transcription will appear here')) {
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `voxtral-transcript-${Date.now()}.txt`;
            a.click();
            URL.revokeObjectURL(url);
            this.log('Transcript downloaded', 'success');
        }
    }
    
    startVisualization() {
        const draw = () => {
            if (!this.isRecording || !this.analyzer) return;
            
            requestAnimationFrame(draw);
            
            const bufferLength = this.analyzer.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            this.analyzer.getByteTimeDomainData(dataArray);
            
            const canvas = this.elements.visualizer;
            const ctx = this.canvasContext;
            const width = canvas.width;
            const height = canvas.height;
            
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(0, 0, width, height);
            
            ctx.lineWidth = 2;
            ctx.strokeStyle = '#6366f1';
            ctx.beginPath();
            
            const sliceWidth = width / bufferLength;
            let x = 0;
            
            for (let i = 0; i < bufferLength; i++) {
                const v = dataArray[i] / 128.0;
                const y = v * height / 2;
                
                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
                
                x += sliceWidth;
            }
            
            ctx.lineTo(width, height / 2);
            ctx.stroke();
            
            // Calculate and display audio level
            const sum = dataArray.reduce((a, b) => a + Math.abs(b - 128), 0);
            const average = sum / bufferLength;
            const level = Math.round((average / 128) * 100);
            this.elements.audioLevel.textContent = `Level: ${level}%`;
        };
        
        draw();
    }
    
    clearVisualization() {
        const canvas = this.elements.visualizer;
        const ctx = this.canvasContext;
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    
    startDurationTimer() {
        this.durationInterval = setInterval(() => {
            if (this.stats.startTime) {
                const elapsed = Math.floor((Date.now() - this.stats.startTime) / 1000);
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
                this.elements.duration.textContent = 
                    `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            }
        }, 1000);
    }
    
    updateConnectionStatus(connected) {
        this.isConnected = connected;
        if (connected) {
            this.elements.connectionStatus.textContent = 'Connected';
            this.elements.connectionStatus.className = 'status-badge status-connected';
        } else {
            this.elements.connectionStatus.textContent = 'Disconnected';
            this.elements.connectionStatus.className = 'status-badge status-disconnected';
        }
    }
    
    updateRecordingStatus(recording) {
        if (recording) {
            this.elements.recordingStatus.textContent = 'Recording';
            this.elements.recordingStatus.className = 'status-badge status-recording';
        } else {
            this.elements.recordingStatus.textContent = 'Idle';
            this.elements.recordingStatus.className = 'status-badge status-idle';
        }
    }
    
    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        logEntry.innerHTML = `<span class="log-timestamp">[${timestamp}]</span> ${message}`;
        
        this.elements.logsOutput.appendChild(logEntry);
        
        if (this.elements.autoScrollLogs.checked) {
            this.elements.logsOutput.scrollTop = this.elements.logsOutput.scrollHeight;
        }
    }
    
    clearLogs() {
        this.elements.logsOutput.innerHTML = '';
        this.log('Logs cleared', 'info');
    }
    
    arrayBufferToBase64(buffer) {
        let binary = '';
        const bytes = new Uint8Array(buffer);
        const len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    const client = new VoxtralClient();
});

// Made with Bob
