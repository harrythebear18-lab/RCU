@echo off
title Homelab Tools System Audit
color 0A
echo ========================================
echo Homelab Tools - Chunked System Audit
echo ========================================
echo.
echo This will run the system audit in this window
echo so you can see the progress in real-time.
echo.
echo Press any key to start the audit...
pause > nul
echo.
echo Starting chunked audit...
echo.

py chunked_system_audit.py

echo.
echo.
echo ========================================
echo Audit completed!
echo ========================================
echo.
echo Results saved to: comprehensive_system_audit_results.json
echo.
echo Press any key to close this window...
pause > nul
