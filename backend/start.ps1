# Modernes PowerShell-Startskript für Python-Anwendungen

# Dieses Skript automatisiert die Einrichtung einer virtuellen Python-Umgebung,
# die Installation von Abhängigkeiten und das Ausführen einer Flask-Anwendung.
# Es bietet farbige Status-Updates für eine moderne Benutzererfahrung.
#
# ANLEITUNG:
# 1. Speichern Sie diese Datei als `start.ps1` im selben Verzeichnis wie Ihre `app.py`.
# 2. Klicken Sie mit der rechten Maustaste auf `start.ps1` und wählen Sie "Mit PowerShell ausführen".
# 3. Wenn ein Fehler bezüglich der Ausführungsrichtlinien auftritt, öffnen Sie PowerShell als
#    Administrator und führen Sie folgenden Befehl aus:
#    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#    Versuchen Sie danach erneut, das Skript auszuführen.

# --- Konfiguration ---
$pythonExecutable = "python.exe"
$venvDir = "venv"
$appScript = "app.py"
$requiredPackages = "flask" # Fügen Sie bei Bedarf weitere Pakete hinzu, z.B. "flask numpy pandas"

# --- Funktionen für eine saubere Ausgabe ---
function Write-Step { param([string]$message)
    Write-Host "`n--------------------------------------------------" -ForegroundColor Cyan
    Write-Host "➡️  $message" -ForegroundColor Cyan
    Write-Host "--------------------------------------------------" -ForegroundColor Cyan
}

function Write-Info { param([string]$message); Write-Host "[INFO] $message" -ForegroundColor Gray }
function Write-Success { param([string]$message); Write-Host "✅ $message" -ForegroundColor Green }
function Write-Error { param([string]$message); Write-Host "❌ $message" -ForegroundColor Red }

function Run-Command {
    param([scriptblock]$command)
    try {
        & $command
        if ($LASTEXITCODE -ne 0) { Throw "Der letzte Befehl ist mit Exit-Code $LASTEXITCODE fehlgeschlagen." }
    } catch {
        Write-Error "Ein Fehler ist aufgetreten: $_"
        Write-Host "Das Skript wird beendet."
        Read-Host "Drücken Sie Enter, um das Fenster zu schließen."
        exit 1
    }
}

# --- Hauptskript ---
Clear-Host
Write-Host "🚀 Modern Python App Launcher wird gestartet..." -ForegroundColor Yellow

# Schritt 1: Globales Pip aktualisieren (optional, war im Originalskript)
Write-Step "Aktualisiere globales Pip-Paket..."
Run-Command { & $pythonExecutable -m pip install --upgrade pip }
Write-Success "Pip wurde erfolgreich aktualisiert."

# Schritt 2: Alte virtuelle Umgebung löschen
Write-Step "Lösche alte virtuelle Umgebung..."
if (Test-Path -Path $venvDir) {
    Write-Info "Verzeichnis '$venvDir' gefunden. Es wird gelöscht..."
    Run-Command { Remove-Item -Path $venvDir -Recurse -Force }
    Start-Sleep -Seconds 1
    Write-Success "Alte virtuelle Umgebung wurde gelöscht."
} else {
    Write-Info "Keine alte virtuelle Umgebung ('$venvDir') gefunden. Überspringe."
}

# Schritt 3: Neue virtuelle Umgebung erstellen
Write-Step "Erstelle neue virtuelle Umgebung..."
Write-Info "Führe aus: $pythonExecutable -m venv $venvDir"
Run-Command { & $pythonExecutable -m venv $venvDir }
Start-Sleep -Seconds 2
Write-Success "Neue virtuelle Umgebung '$venvDir' wurde erstellt."

# Schritt 4: Pakete in der virtuellen Umgebung installieren
Write-Step "Installiere benötigte Pakete in '$venvDir'..."
$venvPython = Join-Path -Path (Get-Location) -ChildPath "$venvDir\Scripts\python.exe"

if (-not (Test-Path -Path $venvPython)) {
    Write-Error "Konnte die Python-Executable in der venv nicht finden: $venvPython"
    Read-Host "Drücken Sie Enter, um das Fenster zu schließen."
    exit 1
}

Write-Info "Aktualisiere pip in venv..."
Run-Command { & $venvPython -m pip install --upgrade pip }
Write-Success "pip in venv wurde aktualisiert."

Write-Info "Installiere Pakete: $requiredPackages..."
Run-Command { & $venvPython -m pip install $requiredPackages }
Write-Success "Alle Pakete wurden erfolgreich installiert."

# Schritt 5: Anwendung in neuem Fenster starten
Write-Step "Starte die Anwendung in einem neuen Fenster..."
Write-Info "Die App '$appScript' wird jetzt gestartet..."

$activateScript = Join-Path -Path (Get-Location) -ChildPath "$venvDir\Scripts\activate.bat"
$runCommand = "python $appScript"
$finalCommand = "$activateScript && $runCommand"

Start-Process cmd -ArgumentList "/k", $finalCommand

Write-Host ""
Write-Success "Startbefehl wurde an ein neues Fenster gesendet."
Write-Host "Dieses Launcher-Fenster kann jetzt geschlossen werden." -ForegroundColor Gray
Read-Host "Drücken Sie Enter zum Beenden..."
