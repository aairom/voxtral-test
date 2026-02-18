@echo off
REM Voxtral Project - GitHub Push Automation Script (Windows)
REM This script helps you push your code to GitHub

setlocal enabledelayedexpansion

echo ================================================
echo   Voxtral Project - GitHub Push Script
echo ================================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed. Please install git first.
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [OK] Git is installed
echo.

REM Check if we're in a git repository
if not exist .git (
    echo [INFO] Not a git repository. Initializing...
    git init
    echo [OK] Git repository initialized
) else (
    echo [INFO] Already a git repository
)

REM Get repository information
echo.
echo [INFO] Please provide your GitHub repository information:
echo.

REM Check if remote already exists
git remote get-url origin >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%i in ('git remote get-url origin') do set CURRENT_REMOTE=%%i
    echo [INFO] Current remote: !CURRENT_REMOTE!
    set /p USE_CURRENT="Do you want to use this remote? (y/n): "
    
    if /i not "!USE_CURRENT!"=="y" (
        set /p GITHUB_USERNAME="Enter your GitHub username: "
        set /p REPO_NAME="Enter your repository name: "
        set REPO_URL=https://github.com/!GITHUB_USERNAME!/!REPO_NAME!.git
        
        echo [INFO] Updating remote origin to: !REPO_URL!
        git remote set-url origin "!REPO_URL!"
    )
) else (
    set /p GITHUB_USERNAME="Enter your GitHub username: "
    set /p REPO_NAME="Enter your repository name: "
    set REPO_URL=https://github.com/!GITHUB_USERNAME!/!REPO_NAME!.git
    
    echo [INFO] Adding remote origin: !REPO_URL!
    git remote add origin "!REPO_URL!"
)

echo [OK] Remote configured
echo.

REM Check current branch
for /f "delims=" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
if "!CURRENT_BRANCH!"=="" set CURRENT_BRANCH=main

REM Add all files
echo [INFO] Adding files to git...
git add .

REM Show status
echo.
echo [INFO] Git status:
git status --short

REM Get commit message
echo.
set /p COMMIT_MSG="Enter commit message (or press Enter for default): "

if "!COMMIT_MSG!"=="" (
    set COMMIT_MSG=Initial commit: Voxtral Realtime Transcription App
)

REM Commit changes
echo [INFO] Committing changes...
git commit -m "!COMMIT_MSG!"
echo [OK] Changes committed

REM Push to GitHub
echo.
echo [INFO] Pushing to GitHub...
set /p CONFIRM_PUSH="Push to branch '!CURRENT_BRANCH!'? (y/n): "

if /i "!CONFIRM_PUSH!"=="y" (
    REM Check if branch exists on remote
    git ls-remote --heads origin !CURRENT_BRANCH! | findstr !CURRENT_BRANCH! >nul 2>&1
    if not errorlevel 1 (
        git push origin !CURRENT_BRANCH!
    ) else (
        echo [INFO] Branch doesn't exist on remote. Creating...
        git push -u origin !CURRENT_BRANCH!
    )
    
    echo [OK] Code pushed to GitHub successfully!
    echo.
    echo [INFO] Your repository: https://github.com/!GITHUB_USERNAME!/!REPO_NAME!
) else (
    echo [WARNING] Push cancelled. You can push manually later with:
    echo   git push origin !CURRENT_BRANCH!
)

echo.
echo [OK] Done!
echo.
echo [INFO] Next steps:
echo   1. Visit your repository on GitHub
echo   2. Add a description and topics
echo   3. Enable GitHub Pages (optional)
echo   4. Share your project!
echo.

pause

@REM Made with Bob
