@echo off
chcp 65001 >nul
title Ulvar - install
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
