@echo off
title MagxxicVOT SMS
if exist venv\Scripts\activate (
    call venv\Scripts\activate
)
python app.py
pause
