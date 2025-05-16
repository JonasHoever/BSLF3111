#!/bin/bash

# Skript zum Bereitstellen/Aktualisieren einer Flask-Anwendung mit Gunicorn

set -e # Skriptabbruch bei Fehlern

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

echo "Aktiviere virtuelle Umgebung und installiere Abhängigkeiten..."
source venv/bin/activate
pip install --upgrade pip
pip install flask gunicorn  # Gunicorn wird jetzt auch installiert

echo "Starte Flask-Anwendung mit Gunicorn..."
#  Startet die Flask-Anwendung mit Gunicorn.
#  --bind 0.0.0.0:3000: Bindet an alle verfügbaren Netzwerkschnittstellen auf Port 3000.
#  wsgi:app:  Nimmt an, dass Ihre Flask-App in der 'app'-Variable der 'wsgi.py'-Datei definiert ist.
#  Wenn Ihre Flask-App anders heißt oder in einer anderen Datei ist, passen Sie dies an.
gunicorn --bind 0.0.0.0:3000 wsgi:app

#  Wichtig: gunicorn läuft im Vordergrund und blockiert das Terminal.  Das ist
#  normal für einen direkten Start.  Für den Hintergrundbetrieb in der Produktion
#  sollten Sie Systemd oder ein ähnliches System verwenden.
