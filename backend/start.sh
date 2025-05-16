#!/bin/bash

echo "Lade Updates..."
python3 -m pip install --upgrade pip

echo "Warte 10 Sekunden..."
sleep 10

echo "Alte virtuelle Umgebung wird gelöscht..."
# Prüfen, ob das 'venv'-Verzeichnis existiert, bevor es gelöscht wird
if [ -d "venv" ]; then
    rm -rf venv
else
    echo "Virtuelle Umgebung 'venv' nicht gefunden. Überspringe das Löschen."
fi

echo "Warte 2 Sekunden..."
sleep 2

echo "Neue virtuelle Umgebung wird erstellt..."
python3 -m venv venv

echo "Warte 5 Sekunden für venv-Erstellung..."
sleep 5

echo "venv wurde installiert."

# Neue Konsole mit aktivierter venv und Start von app.py
# Für Linux gibt es keine direkte Entsprechung von 'start cmd /k' für eine neue, persistente Terminal-Session,
# die den Kontext behält. Stattdessen wird hier der venv-Befehl direkt in der aktuellen Shell ausgeführt.
# Wenn Sie eine neue, separate Terminalsitzung benötigen, müssten Sie eine Terminal-Emulator-Befehl wie 'gnome-terminal', 'konsole' oder 'xterm' verwenden.
# Die meisten Server haben jedoch keine grafische Oberfläche, daher ist das Starten im aktuellen Terminal die Standardvorgehensweise.

echo "Aktiviere virtuelle Umgebung und installiere Abhängigkeiten..."
source venv/bin/activate
pip install --upgrade pip
pip install flask

echo "Starte Flask-Anwendung..."
# Führen Sie 'app.py' aus. Beachten Sie, dass diese Zeile den Skriptfluss blockiert,
# solange die Flask-App läuft. Um es im Hintergrund laufen zu lassen,
# müssten Sie Tools wie 'nohup' oder 'screen' verwenden oder es als Systemd-Dienst konfigurieren.
python app.py
