# 🚀 Quick Start Guide - CPU Only

This guide will help you run the Voxtral transcription UI on a CPU-only system using Vosk.

## ⚡ Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
pip install -r requirements_cpu.txt
```

### Step 2: Download Vosk Model

Choose a model based on your needs:

**Small Model (Recommended for testing - 40MB)**
```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

**Large Model (Better accuracy - 1.8GB)**
```bash
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip
```

**Other Languages:**
- French: `vosk-model-fr-0.22`
- German: `vosk-model-de-0.21`
- Spanish: `vosk-model-es-0.42`
- See all: https://alphacephei.com/vosk/models

### Step 3: Start the Server

```bash
python3 server_vosk.py --model vosk-model-small-en-us-0.15
```

Or with the large model:
```bash
python3 server_vosk.py --model vosk-model-en-us-0.22
```

### Step 4: Open the UI

```bash
open index.html
```

Or use a simple HTTP server:
```bash
python3 -m http.server 3000
# Then visit http://localhost:3000
```

### Step 5: Use the Application

1. Click "Connect to Server"
2. Select your microphone
3. Click "Start Recording"
4. Speak into your microphone
5. Watch real-time transcription appear!

## 🎯 What to Expect

### Performance on CPU
- **Latency**: ~500ms - 2s (depending on CPU)
- **Real-time**: Yes, works in real-time on most modern CPUs
- **Accuracy**: Good (85-90% for small model, 90-95% for large model)
- **CPU Usage**: 20-40% on modern CPUs

### Comparison with GPU Voxtral
| Feature | Vosk (CPU) | Voxtral (GPU) |
|---------|-----------|---------------|
| Hardware | Any CPU | NVIDIA GPU 16GB+ |
| Latency | 0.5-2s | <500ms |
| Accuracy | 85-95% | 95-98% |
| Setup | Easy | Complex |
| Cost | Free | GPU required |

## 🔧 Troubleshooting

### "Model not found"
Make sure you've downloaded and extracted the model in the same directory as the server script.

### "Vosk not installed"
```bash
pip install vosk
```

### "Connection refused"
Make sure the server is running on port 8080. Check with:
```bash
lsof -i :8080
```

### Poor transcription quality
- Use the larger model (`vosk-model-en-us-0.22`)
- Speak clearly and at a moderate pace
- Reduce background noise
- Use a good quality microphone

## 📊 Model Comparison

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| small-en-us-0.15 | 40MB | Fast | Good | Testing, demos |
| en-us-0.22 | 1.8GB | Medium | Excellent | Production |
| en-us-0.22-lgraph | 128MB | Fast | Very Good | Balance |

## 🌍 Multi-Language Support

Vosk supports many languages. Download the appropriate model:

```bash
# French
wget https://alphacephei.com/vosk/models/vosk-model-fr-0.22.zip

# German  
wget https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip

# Spanish
wget https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip

# Chinese
wget https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip
```

Then start the server with the appropriate model:
```bash
python3 server_vosk.py --model vosk-model-fr-0.22
```

## 💡 Tips for Best Results

1. **Use a good microphone**: Built-in laptop mics work, but external USB mics are better
2. **Reduce background noise**: Close windows, turn off fans
3. **Speak clearly**: Moderate pace, clear pronunciation
4. **Use the large model**: If you have disk space, use `vosk-model-en-us-0.22`
5. **Check audio levels**: Use the visualizer to ensure audio is being captured

## 🎉 Success!

You now have a working real-time speech transcription system running entirely on CPU!

## 📚 Next Steps

- Try different Vosk models for better accuracy
- Experiment with different languages
- Customize the UI in `index.html` and `style.css`
- Check out the full documentation in `README.md`

## ❓ Need Help?

- Vosk Documentation: https://alphacephei.com/vosk/
- Vosk Models: https://alphacephei.com/vosk/models
- GitHub Issues: Report problems in the repository

---

**Note**: This CPU version uses Vosk instead of Voxtral. While it has slightly lower accuracy, it runs in real-time on any modern CPU without requiring a GPU!