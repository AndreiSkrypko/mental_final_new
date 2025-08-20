@echo off
cd /d "D:\Cursor\mental_arifmetic"
git add README.md
git commit -m "Restore README.md without token"
git push origin main
echo README.md восстановлен и отправлен в репозиторий
pause
