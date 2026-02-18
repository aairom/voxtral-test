# 🚀 GitHub Setup Guide

This guide will help you push your Voxtral project to GitHub.

## 📋 Prerequisites

1. **Git installed** on your system
   - macOS: `brew install git` or download from [git-scm.com](https://git-scm.com)
   - Linux: `sudo apt install git` or `sudo yum install git`
   - Windows: Download from [git-scm.com](https://git-scm.com/download/win)

2. **GitHub account**
   - Create one at [github.com](https://github.com/signup)

3. **GitHub repository created**
   - Go to [github.com/new](https://github.com/new)
   - Create a new repository (e.g., "voxtral-transcription")
   - Don't initialize with README (we already have one)

## 🎯 Quick Start - Automated Push

### Option 1: Using the Automation Script (Recommended)

#### On macOS/Linux:
```bash
./push_to_github.sh
```

#### On Windows:
```cmd
push_to_github.bat
```

The script will:
1. ✅ Check if git is installed
2. ✅ Initialize git repository (if needed)
3. ✅ Ask for your GitHub username and repository name
4. ✅ Configure the remote origin
5. ✅ Add all files
6. ✅ Create a commit with a descriptive message
7. ✅ Push to GitHub

### Option 2: Manual Setup

If you prefer to do it manually:

```bash
# 1. Initialize git repository
git init

# 2. Add all files
git add .

# 3. Create initial commit
git commit -m "Initial commit: Voxtral Realtime Transcription App"

# 4. Add your GitHub repository as remote
# Replace YOUR_USERNAME and YOUR_REPO with your actual values
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 5. Push to GitHub
git branch -M main
git push -u origin main
```

## 🔐 Authentication

### Using HTTPS (Recommended for beginners)

When pushing, GitHub will ask for credentials:
- **Username**: Your GitHub username
- **Password**: Use a Personal Access Token (PAT), not your password

**To create a PAT:**
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name (e.g., "Voxtral Project")
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)
7. Use this token as your password when pushing

### Using SSH (Advanced)

If you prefer SSH:

```bash
# 1. Generate SSH key (if you don't have one)
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. Add SSH key to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 3. Copy public key
cat ~/.ssh/id_ed25519.pub

# 4. Add to GitHub: Settings → SSH and GPG keys → New SSH key

# 5. Use SSH URL instead of HTTPS
git remote set-url origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
```

## 📝 What Gets Pushed

The following files will be pushed to GitHub:

```
voxtral-test/
├── index.html              # Web interface
├── style.css               # Styling
├── app.js                  # Client JavaScript
├── server.py               # GPU server (Voxtral)
├── server_vosk.py          # CPU server (Vosk)
├── requirements.txt        # Python deps (GPU)
├── requirements_cpu.txt    # Python deps (CPU)
├── test_setup.py           # Setup verification
├── README.md               # Main documentation
├── QUICKSTART_CPU.md       # CPU quick start
├── CPU_SETUP.md            # CPU alternatives
├── GITHUB_SETUP.md         # This file
├── .gitignore              # Git ignore rules
├── push_to_github.sh       # Push script (Unix)
└── push_to_github.bat      # Push script (Windows)
```

**Note**: Vosk models (large files) are excluded via `.gitignore`

## 🎨 Customizing Your Repository

After pushing, enhance your GitHub repository:

### 1. Add Repository Description
- Go to your repository on GitHub
- Click the ⚙️ icon next to "About"
- Add description: "Real-time speech transcription with Voxtral AI - GPU and CPU versions available"
- Add topics: `speech-recognition`, `voxtral`, `transcription`, `websocket`, `real-time`, `ai`, `mistral-ai`

### 2. Enable GitHub Pages (Optional)
To host the web interface:
1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main`, folder: `/ (root)`
4. Save
5. Your app will be available at: `https://YOUR_USERNAME.github.io/YOUR_REPO/`

**Note**: The server won't work on GitHub Pages (it's client-side only), but users can see the UI.

### 3. Add a License
1. Click "Add file" → "Create new file"
2. Name it `LICENSE`
3. Click "Choose a license template"
4. Select MIT License (or your preference)
5. Commit

### 4. Create a Nice README Badge
Add to the top of README.md:
```markdown
![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/YOUR_REPO)
![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/YOUR_REPO)
![GitHub issues](https://img.shields.io/github/issues/YOUR_USERNAME/YOUR_REPO)
```

## 🔄 Updating Your Repository

After making changes:

```bash
# 1. Check what changed
git status

# 2. Add changes
git add .

# 3. Commit with a message
git commit -m "Description of changes"

# 4. Push to GitHub
git push origin main
```

Or simply run the automation script again:
```bash
./push_to_github.sh
```

## 🌟 Making Your Project Stand Out

### Add Screenshots
1. Take screenshots of your app
2. Create a `screenshots/` folder
3. Add images to README.md:
```markdown
![Voxtral UI](screenshots/main-interface.png)
```

### Add a Demo Video
1. Record a short demo (30-60 seconds)
2. Upload to YouTube or GitHub
3. Add to README.md:
```markdown
[![Demo Video](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)
```

### Create a Project Website
Use GitHub Pages to create a landing page:
1. Create `docs/` folder
2. Add `docs/index.html` with project info
3. Enable GitHub Pages from `docs/` folder

## 🐛 Troubleshooting

### "Permission denied (publickey)"
- You need to set up SSH keys or use HTTPS with a PAT
- See Authentication section above

### "Repository not found"
- Check the repository URL
- Make sure the repository exists on GitHub
- Verify you have access to the repository

### "Failed to push some refs"
- Someone else pushed changes
- Pull first: `git pull origin main`
- Then push: `git push origin main`

### "Large files detected"
- Vosk models are too large for GitHub
- They're already in `.gitignore`
- If you accidentally added them: `git rm --cached vosk-model*`

## 📚 Additional Resources

- [GitHub Docs](https://docs.github.com)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [GitHub Desktop](https://desktop.github.com) - GUI alternative
- [VS Code Git Integration](https://code.visualstudio.com/docs/editor/versioncontrol)

## 🎉 Success!

Once pushed, share your project:
- Tweet about it with #VoxtralAI #SpeechRecognition
- Post on Reddit (r/MachineLearning, r/Python)
- Share on LinkedIn
- Add to Awesome Lists

Your repository URL will be:
```
https://github.com/YOUR_USERNAME/YOUR_REPO
```

Happy coding! 🚀