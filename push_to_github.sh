#!/bin/bash

# Voxtral Project - GitHub Push Automation Script
# This script helps you push your code to GitHub

set -e  # Exit on error

echo "================================================"
echo "  Voxtral Project - GitHub Push Script"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git first."
    exit 1
fi

print_success "Git is installed"

# Check if we're in a git repository
if [ ! -d .git ]; then
    print_warning "Not a git repository. Initializing..."
    git init
    print_success "Git repository initialized"
else
    print_info "Already a git repository"
fi

# Get repository information
echo ""
print_info "Please provide your GitHub repository information:"
echo ""

# Check if remote already exists
if git remote get-url origin &> /dev/null; then
    CURRENT_REMOTE=$(git remote get-url origin)
    print_info "Current remote: $CURRENT_REMOTE"
    read -p "Do you want to use this remote? (y/n): " USE_CURRENT
    
    if [ "$USE_CURRENT" != "y" ] && [ "$USE_CURRENT" != "Y" ]; then
        read -p "Enter your GitHub username: " GITHUB_USERNAME
        read -p "Enter your repository name: " REPO_NAME
        REPO_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
        
        print_info "Updating remote origin to: $REPO_URL"
        git remote set-url origin "$REPO_URL"
    fi
else
    read -p "Enter your GitHub username: " GITHUB_USERNAME
    read -p "Enter your repository name: " REPO_NAME
    REPO_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    
    print_info "Adding remote origin: $REPO_URL"
    git remote add origin "$REPO_URL"
fi

print_success "Remote configured"

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
if [ -z "$CURRENT_BRANCH" ]; then
    CURRENT_BRANCH="main"
    print_info "Creating initial branch: $CURRENT_BRANCH"
fi

# Add all files
echo ""
print_info "Adding files to git..."
git add .

# Show status
echo ""
print_info "Git status:"
git status --short

# Get commit message
echo ""
read -p "Enter commit message (or press Enter for default): " COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Initial commit: Voxtral Realtime Transcription App

- Web-based UI for real-time speech transcription
- GPU version using Voxtral-Mini-4B-Realtime-2602
- CPU version using Vosk (no GPU required)
- Audio visualization and statistics
- Multi-language support
- Comprehensive documentation"
fi

# Commit changes
print_info "Committing changes..."
git commit -m "$COMMIT_MSG"
print_success "Changes committed"

# Push to GitHub
echo ""
print_info "Pushing to GitHub..."
read -p "Push to branch '$CURRENT_BRANCH'? (y/n): " CONFIRM_PUSH

if [ "$CONFIRM_PUSH" = "y" ] || [ "$CONFIRM_PUSH" = "Y" ]; then
    # Check if branch exists on remote
    if git ls-remote --heads origin "$CURRENT_BRANCH" | grep -q "$CURRENT_BRANCH"; then
        git push origin "$CURRENT_BRANCH"
    else
        print_info "Branch doesn't exist on remote. Creating..."
        git push -u origin "$CURRENT_BRANCH"
    fi
    
    print_success "Code pushed to GitHub successfully!"
    echo ""
    print_info "Your repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
else
    print_warning "Push cancelled. You can push manually later with:"
    echo "  git push origin $CURRENT_BRANCH"
fi

echo ""
print_success "Done!"
echo ""
print_info "Next steps:"
echo "  1. Visit your repository on GitHub"
echo "  2. Add a description and topics"
echo "  3. Enable GitHub Pages (optional)"
echo "  4. Share your project!"
echo ""

# Made with Bob
