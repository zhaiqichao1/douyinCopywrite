@echo off
taskkill /F /IM chrome.exe /T
timeout /t 2
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%~dp0chrome-data" 