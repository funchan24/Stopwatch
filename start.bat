@echo off

cd /d %~dp0
setlocal enabledelayedexpansion

if not exist .venv\scripts\python.exe (
    python -m venv .venv 1>nul 2>nul

    if not exist .venv\scripts\python.exe (
        echo Install Python...
        set temp_file=!Temp!\python-3.7.6.exe

        set url="https://oss.npmmirror.com/dist/python/3.7.6/python-3.7.6.exe"
        certutil -urlcache -split -f !url! !temp_file! 1>nul 2>nul

        if !errorlevel! NEQ 0 (
            set url="https://www.python.org/ftp/python/3.7.6/python-3.7.6.exe"
            certutil -urlcache -split -f !url! !temp_file! 1>nul 2>nul

            if !errorlevel! NEQ 0 (
                echo Error: Failed to download Python, Check the network!
                pause >nul
                exit
            )
        )

        if "!PROCESSOR_ARCHITECTURE!"=="AMD64" (
            set python_dir=!LocalAppData!\Programs\Python37-32
        ) else (
            set python_dir=!LocalAppData!\Programs\Python37
        )

        !temp_file! /passive /quiet PrependPath=1 TargetDir=!python_dir!
        !python_dir!\python.exe -m venv .venv 1>nul 2>nul
    )
)

.venv\scripts\python.exe launch.py