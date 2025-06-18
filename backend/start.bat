@echo off
REM =================================================================
REM ==  GUI Control Center Starter                                 ==
REM =================================================================
REM
REM  Dieses Skript startet das Python Control Center (main_gui.py).
REM  Das Python-Skript wird sich selbstständig um die Erstellung
REM  der virtuellen Umgebung und die Installation aller
REM  notwendigen Pakete kümmern.

echo.
echo ===================================
echo  Starte das Control Center...
echo ===================================
echo.

REM WICHTIG: Stellen Sie sicher, dass Ihr Python-Skript "main_gui.py" heisst.
REM Wenn Sie es anders genannt haben, passen Sie den Befehl unten entsprechend an.
python main_gui.py

pause
exit
