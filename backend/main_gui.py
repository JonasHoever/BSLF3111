import sys
import os
import subprocess
import shutil
import webbrowser
import threading

# --- BOOTSTRAP: Self-contained environment setup ---
# Dieser Abschnitt stellt sicher, dass das Skript in einer virtuellen Umgebung
# läuft und alle Abhängigkeiten, einschließlich PyQt6, dort installiert sind.
# Dies vermeidet Windows MAX_PATH-Fehler und Berechtigungsprobleme.
VENV_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "venv"))
PYTHON_IN_VENV = os.path.join(VENV_DIR, "Scripts", "python.exe") if os.name == 'nt' else os.path.join(VENV_DIR, "bin", "python")
is_in_venv = sys.prefix == VENV_DIR

if not is_in_venv:
    print("--- Initialisiere Launcher: Richte virtuelle Umgebung ein ---")
    try:
        if not os.path.exists(PYTHON_IN_VENV):
            print(f"Erstelle virtuelle Umgebung in '{VENV_DIR}'...")
            # FIX: Verwende --upgrade-deps, um die venv zu erstellen und pip/setuptools atomar zu aktualisieren.
            # Dies ist robuster, als die Umgebung zu erstellen und pip danach manuell zu aktualisieren.
            subprocess.run([sys.executable, "-m", "venv", "--upgrade-deps", VENV_DIR], check=True, capture_output=True)
            print("✅ Virtuelle Umgebung erstellt und Abhängigkeiten aktualisiert.")
        
        # Installiere die GUI-Abhängigkeiten
        print("Installiere GUI-Abhängigkeiten (PyQt6)...")
        # Der --upgrade-deps-Flag sollte ein funktionierendes pip erstellt haben. Wir müssen es hier nicht mehr separat aktualisieren.
        subprocess.run([PYTHON_IN_VENV, "-m", "pip", "install", "PyQt6"], check=True, capture_output=True)
        print("✅ GUI-Abhängigkeiten installiert.")

    except subprocess.CalledProcessError as e:
        print("\n--- FEHLER BEI DER INSTALLATION ---")
        print(f"Befehl '{' '.join(e.cmd)}' ist fehlgeschlagen mit Code {e.returncode}")
        # Gib die detaillierte Ausgabe von stdout und stderr aus, um die Fehlersuche zu erleichtern
        print("\n--- STDOUT ---")
        print(e.stdout.decode(errors='ignore'))
        print("\n--- STDERR ---")
        print(e.stderr.decode(errors='ignore'))
        input("Drücken Sie Enter, um das Fenster zu schließen...")
        sys.exit(1)
    
    print("--- Starte im virtuellen Modus neu ---")
    os.execv(PYTHON_IN_VENV, [PYTHON_IN_VENV, __file__] + sys.argv[1:])

# --- MAIN APPLICATION ---
import PyQt6 # Importieren, um den Pfad zu finden
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                             QWidget, QTextEdit, QHBoxLayout, QLabel)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QObject, QProcess, QThread, QCoreApplication

# --- Configuration ---
APP_SCRIPT = "app.py"
FLASK_PACKAGES = ["flask"]
FLASK_URL = "http://127.0.0.1:3000"

# Worker class for handling background tasks to avoid GUI freeze
class Worker(QObject):
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    setup_complete = pyqtSignal()
    finished = pyqtSignal()

    def run(self):
        try:
            self.progress.emit("--- Starte Setup-Prozess ---")
            self.progress.emit("Hinweis: Für einen kompletten Reset, löschen Sie den 'venv' Ordner manuell, bevor Sie starten.")
            
            # Step 1: Check/Create virtual environment (no deletion)
            if not os.path.exists(PYTHON_IN_VENV):
                 self.progress.emit(f"Keine virtuelle Umgebung gefunden. Erstelle sie in '{VENV_DIR}'...")
                 self.run_command([sys.executable, "-m", "venv", "--upgrade-deps", VENV_DIR], "Erstelle venv...")
                 self.progress.emit("✅ Neue virtuelle Umgebung erstellt.")
            else:
                self.progress.emit("✅ Vorhandene virtuelle Umgebung wird verwendet.")

            # Step 2: Install/Update packages in venv
            self.progress.emit("Installiere/Aktualisiere Pakete in venv...")
            self.run_command([PYTHON_IN_VENV, "-m", "pip", "install", "--upgrade", "pip"], "Aktualisiere pip in venv...")
            self.run_command([PYTHON_IN_VENV, "-m", "pip", "install"] + FLASK_PACKAGES, "Installiere Flask...")
            self.progress.emit("✅ Alle Pakete wurden erfolgreich installiert.")
            
            # Signal that the setup is complete and the main thread can start the server
            self.setup_complete.emit()
            
        except Exception as e:
            self.error.emit(f"Ein kritischer Fehler ist im Setup aufgetreten: {e}")
        finally:
            # Signal that the worker thread's job is done
            self.finished.emit()
            
    def run_command(self, command, description):
        self.progress.emit(f"\n> {description}")
        # Use Popen to capture live output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='ignore', shell=False)
        for line in iter(process.stdout.readline, ''):
            self.progress.emit(line.strip())
        process.wait() # Wait for the command to complete
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)


class ControlCenter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.process = None
        self.worker_thread = None
        self.worker = None
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.setWindowTitle("Python/Flask Control Center")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Status Bar
        status_layout = QHBoxLayout()
        self.status_indicator = QLabel("●")
        self.status_text = QLabel("Gestoppt")
        status_layout.addWidget(QLabel("Status:"))
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        main_layout.addLayout(status_layout)

        # Terminal Output
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setFont(QFont("Fira Code", 10))
        self.terminal_output.setPlaceholderText("Willkommen! Klicken Sie auf 'Starten'...")
        main_layout.addWidget(self.terminal_output)

        # Button Bar
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("▶ Starten & Setup ausführen")
        self.stop_button = QPushButton("■ Stoppen")
        self.open_browser_button = QPushButton("🌐 Im Browser öffnen")
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.open_browser_button)
        main_layout.addLayout(button_layout)
        
        self.setup_styles()
        self.update_status("stopped")

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #111827; color: #e5e7eb; }
            QTextEdit { background-color: #1f2937; border: 1px solid #374151; border-radius: 8px; color: #d1d5db; padding: 5px; }
            QPushButton { border: none; border-radius: 8px; font-size: 14px; font-weight: bold; padding: 12px; }
            QPushButton:disabled { background-color: #374151; color: #6b7280; }
            QLabel { font-size: 14px; }
        """)
        self.start_button.setStyleSheet("background-color: #16a34a;")
        self.stop_button.setStyleSheet("background-color: #dc2626;")
        self.open_browser_button.setStyleSheet("background-color: #2563eb;")

    def connect_signals(self):
        self.start_button.clicked.connect(self.start_worker)
        self.stop_button.clicked.connect(self.stop_process)
        self.open_browser_button.clicked.connect(self.open_in_browser)
        
    @pyqtSlot(str)
    def append_to_terminal(self, text):
        self.terminal_output.append(text)

    def update_status(self, status):
        if status == "setup":
            self.status_indicator.setStyleSheet("color: #f59e0b;")
            self.status_text.setText("Setup läuft...")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.open_browser_button.setEnabled(False)
        elif status == "running":
            self.status_indicator.setStyleSheet("color: #22c55e;")
            self.status_text.setText("Laufend")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.open_browser_button.setEnabled(True)
        elif status == "stopped":
            self.status_indicator.setStyleSheet("color: #ef4444;")
            self.status_text.setText("Gestoppt")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.open_browser_button.setEnabled(False)
        elif status == "error":
            self.status_indicator.setStyleSheet("color: #ef4444;")
            self.status_text.setText("Fehler im Setup")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.open_browser_button.setEnabled(False)

    def closeEvent(self, event):
        self.stop_process()
        event.accept()

    def start_worker(self):
        self.terminal_output.clear()
        self.update_status("setup")
        
        self.worker_thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.worker_thread)
        
        self.worker.progress.connect(self.append_to_terminal)
        self.worker.error.connect(self.on_worker_error)
        self.worker.setup_complete.connect(self.launch_flask_server)
        
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()
        
    def on_worker_error(self, message):
        self.append_to_terminal(message)
        self.update_status("error")
        
    def launch_flask_server(self):
        self.append_to_terminal("\n--- Setup abgeschlossen. Starte Flask-Server... ---")
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.finished.connect(self.process_finished)
        self.process.start(PYTHON_IN_VENV, [APP_SCRIPT])

    def stop_process(self):
        """
        Stoppt den Flask-Prozess und alle seine untergeordneten Prozesse.
        Diese Methode ist jetzt robuster für Windows-Systeme.
        """
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.append_to_terminal("--- Beende Flask-Server... ---")
            
            pid = self.process.processId()
            
            # Für Windows verwenden wir taskkill, um den gesamten Prozessbaum zu beenden.
            if os.name == 'nt':
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], capture_output=True)
                self.append_to_terminal(f"Prozessbaum mit PID {pid} wurde beendet.")
            else: # Für Linux/macOS
                self.process.kill()

            self.process.waitForFinished(1000) # Warte kurz
            self.process = None
            
        self.update_status("stopped")

    def open_in_browser(self):
        webbrowser.open(FLASK_URL)
        
    def handle_stdout(self):
        if self.process:
            data = self.process.readAllStandardOutput().data().decode('utf-8', errors='ignore').strip()
            self.append_to_terminal(data)
            # Check if flask is running and update status
            if "Running on" in data:
                self.update_status("running")

    def process_finished(self):
        self.append_to_terminal("--- Flask-Prozess wurde beendet. ---")
        self.update_status("stopped")
        self.process = None

if __name__ == "__main__":
    if not os.path.exists(APP_SCRIPT):
        with open(APP_SCRIPT, "w") as f:
            f.write("""
from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello_world():
    return '<h1>Hallo von Flask!</h1><p>Die App läuft.</p>'
if __name__ == '__main__':
    # use_reloader=False is important for this setup
    app.run(debug=True, use_reloader=False) 
""")
    
    # FIX for Qt platform plugin error
    # Fügt den Pfad zu den Qt-Plugins explizit hinzu, bevor die App gestartet wird.
    # Dies ist notwendig, damit die App weiß, wo sie die DLLs zum Zeichnen von Fenstern findet.
    pyqt_path = os.path.dirname(PyQt6.__file__)
    plugin_path = os.path.join(pyqt_path, "Qt6", "plugins")
    QCoreApplication.addLibraryPath(plugin_path)

    app = QApplication(sys.argv)
    window = ControlCenter()
    window.show()
    sys.exit(app.exec())
