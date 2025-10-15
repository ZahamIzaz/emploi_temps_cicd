# Scripts PowerShell pour Windows (équivalent du Makefile)

# Variables globales
$PROJECT_NAME = "wigor-viewer"
$SRC_DIR = "src"
$TEST_DIR = "tests"
$PYTHON = "python"

function Show-Help {
    Write-Host "Scripts de développement Wigor Viewer" -ForegroundColor Green
    Write-Host "=======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installation :" -ForegroundColor Yellow
    Write-Host "  .\dev.ps1 install      - Installation des dépendances"
    Write-Host "  .\dev.ps1 install-dev  - Installation des dépendances de dev"
    Write-Host ""
    Write-Host "Tests :" -ForegroundColor Yellow
    Write-Host "  .\dev.ps1 test         - Tous les tests"
    Write-Host "  .\dev.ps1 test-unit    - Tests unitaires uniquement"
    Write-Host "  .\dev.ps1 test-integration - Tests d'intégration"
    Write-Host "  .\dev.ps1 coverage     - Rapport de couverture"
    Write-Host ""
    Write-Host "Qualité de code :" -ForegroundColor Yellow
    Write-Host "  .\dev.ps1 lint         - Vérification PEP8"
    Write-Host "  .\dev.ps1 format       - Formatage automatique"
    Write-Host "  .\dev.ps1 type-check   - Vérification des types"
    Write-Host "  .\dev.ps1 security     - Analyse de sécurité"
    Write-Host "  .\dev.ps1 quality      - Toutes les vérifications"
    Write-Host ""
    Write-Host "Build :" -ForegroundColor Yellow
    Write-Host "  .\dev.ps1 build        - Construction exécutable"
    Write-Host "  .\dev.ps1 docker-build - Construction image Docker"
    Write-Host ""
    Write-Host "Utilitaires :" -ForegroundColor Yellow
    Write-Host "  .\dev.ps1 clean        - Nettoyage"
    Write-Host "  .\dev.ps1 run          - Lancement application"
    Write-Host "  .\dev.ps1 ci-local     - Simulation CI/CD local"
}

function Install-Dependencies {
    Write-Host "📦 Installation des dépendances..." -ForegroundColor Blue
    & $PYTHON -m pip install --upgrade pip
    & $PYTHON -m pip install -r requirements.txt
    Write-Host "✅ Dépendances installées" -ForegroundColor Green
}

function Install-DevDependencies {
    Install-Dependencies
    Write-Host "🔧 Installation des dépendances de développement..." -ForegroundColor Blue
    & $PYTHON -m pip install pytest pytest-cov pytest-html pytest-xdist
    & $PYTHON -m pip install black isort flake8 mypy bandit safety
    & $PYTHON -m pip install pyinstaller
    Write-Host "✅ Environnement de développement configuré" -ForegroundColor Green
}

function Run-Tests {
    Write-Host "🧪 Lancement des tests..." -ForegroundColor Blue
    & $PYTHON -m pytest $TEST_DIR/ -v --tb=short --cov=$SRC_DIR --cov-report=html --cov-report=term-missing --cov-report=xml
}

function Run-UnitTests {
    Write-Host "🧪 Tests unitaires..." -ForegroundColor Blue
    & $PYTHON -m pytest $TEST_DIR/ -v -m "unit" --tb=short
}

function Run-IntegrationTests {
    Write-Host "🧪 Tests d'intégration..." -ForegroundColor Blue
    & $PYTHON -m pytest $TEST_DIR/ -v -m "integration" --tb=short
}

function Run-Coverage {
    Write-Host "📊 Génération du rapport de couverture..." -ForegroundColor Blue
    & $PYTHON -m pytest $TEST_DIR/ --cov=$SRC_DIR --cov-report=html --cov-report=term --cov-report=xml --cov-fail-under=70
    Write-Host "✅ Rapport généré dans htmlcov/" -ForegroundColor Green
}

function Run-Lint {
    Write-Host "🔍 Vérification PEP8..." -ForegroundColor Blue
    & $PYTHON -m flake8 $SRC_DIR/ $TEST_DIR/ --max-line-length=88 --extend-ignore=E203,W503
}

function Run-Format {
    Write-Host "🎨 Formatage du code..." -ForegroundColor Blue
    & $PYTHON -m black $SRC_DIR/ $TEST_DIR/
    & $PYTHON -m isort $SRC_DIR/ $TEST_DIR/
    Write-Host "✅ Code formaté" -ForegroundColor Green
}

function Run-FormatCheck {
    Write-Host "🎨 Vérification du formatage..." -ForegroundColor Blue
    & $PYTHON -m black --check --diff $SRC_DIR/ $TEST_DIR/
    & $PYTHON -m isort --check-only --diff $SRC_DIR/ $TEST_DIR/
}

function Run-TypeCheck {
    Write-Host "🔍 Vérification des types..." -ForegroundColor Blue
    & $PYTHON -m mypy $SRC_DIR/ --ignore-missing-imports
}

function Run-Security {
    Write-Host "🔒 Analyse de sécurité..." -ForegroundColor Blue
    & $PYTHON -m bandit -r $SRC_DIR/ -f json -o bandit-report.json
    & $PYTHON -m safety check --json --output safety-report.json
}

function Run-Quality {
    Write-Host "✨ Vérifications qualité complètes..." -ForegroundColor Blue
    Run-FormatCheck
    Run-Lint
    Run-TypeCheck
    Run-Security
    Write-Host "✅ Toutes les vérifications passées" -ForegroundColor Green
}

function Build-Executable {
    Write-Host "🏗️  Construction de l'exécutable..." -ForegroundColor Blue
    & pyinstaller --onefile --windowed --name=WigorViewer.exe `
        --add-data "assets;assets" `
        --hidden-import=tkinter `
        --hidden-import=requests `
        --hidden-import=bs4 `
        run.py
    Write-Host "✅ Exécutable créé dans dist/" -ForegroundColor Green
}

function Build-Docker {
    Write-Host "🐳 Construction de l'image Docker..." -ForegroundColor Blue
    docker build -t $PROJECT_NAME":latest" .
    Write-Host "✅ Image Docker créée" -ForegroundColor Green
}

function Clean-All {
    Write-Host "🧹 Nettoyage..." -ForegroundColor Blue
    Get-ChildItem -Path . -Recurse -Name "*.pyc" | Remove-Item -Force
    Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }
    if (Test-Path ".coverage") { Remove-Item -Force ".coverage" }
    if (Test-Path "htmlcov") { Remove-Item -Recurse -Force "htmlcov" }
    if (Test-Path ".mypy_cache") { Remove-Item -Recurse -Force ".mypy_cache" }
    Write-Host "✅ Nettoyage terminé" -ForegroundColor Green
}

function Run-Application {
    Write-Host "🚀 Lancement de l'application..." -ForegroundColor Blue
    & $PYTHON run.py
}

function Run-LocalCI {
    Write-Host "🚀 Simulation du pipeline CI/CD en local..." -ForegroundColor Blue
    Clean-All
    Install-DevDependencies
    Run-Quality
    Run-Tests
    Build-Executable
    Write-Host "✅ Pipeline CI/CD simulé avec succès !" -ForegroundColor Green
}

# Point d'entrée principal
param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install" { Install-Dependencies }
    "install-dev" { Install-DevDependencies }
    "test" { Run-Tests }
    "test-unit" { Run-UnitTests }
    "test-integration" { Run-IntegrationTests }
    "coverage" { Run-Coverage }
    "lint" { Run-Lint }
    "format" { Run-Format }
    "format-check" { Run-FormatCheck }
    "type-check" { Run-TypeCheck }
    "security" { Run-Security }
    "quality" { Run-Quality }
    "build" { Build-Executable }
    "docker-build" { Build-Docker }
    "clean" { Clean-All }
    "run" { Run-Application }
    "ci-local" { Run-LocalCI }
    default { 
        Write-Host "❌ Commande inconnue: $Command" -ForegroundColor Red
        Show-Help
    }
}