#!/bin/bash

# Build script for Wigor Viewer CLI executable
# Creates a single-file executable using PyInstaller

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="wigor-viewer"
SPEC_FILE="wigor.spec"
DIST_DIR="dist"
BUILD_DIR="build"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    Wigor Viewer Build Script                    ║"
    echo "║              Building CLI executable with PyInstaller           ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_requirements() {
    log_info "Checking build requirements..."
    
    # Check Python
    if ! command -v python &> /dev/null; then
        log_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip &> /dev/null; then
        log_error "pip is not installed or not in PATH"
        exit 1
    fi
    
    # Check project files
    if [ ! -f "$SPEC_FILE" ]; then
        log_error "PyInstaller spec file not found: $SPEC_FILE"
        exit 1
    fi
    
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt not found"
        exit 1
    fi
    
    if [ ! -f "requirements-dev.txt" ]; then
        log_error "requirements-dev.txt not found"
        exit 1
    fi
    
    log_success "All requirements check passed"
}

install_dependencies() {
    log_info "Installing dependencies..."
    
    # Upgrade pip first
    python -m pip install --upgrade pip
    
    # Install production dependencies
    log_info "Installing production dependencies..."
    pip install -r requirements.txt
    
    # Install development dependencies
    log_info "Installing development dependencies..."
    pip install -r requirements-dev.txt
    
    # Ensure PyInstaller is available
    log_info "Ensuring PyInstaller is installed..."
    pip install pyinstaller>=5.13.0
    
    log_success "Dependencies installed successfully"
}

run_tests() {
    log_info "Running tests and quality checks..."
    
    # Run lint checks
    log_info "Running lint checks..."
    if command -v flake8 &> /dev/null; then
        flake8 src/ tests/ test_regression.py || {
            log_error "Lint checks failed"
            exit 1
        }
    else
        log_warning "flake8 not available, skipping lint checks"
    fi
    
    # Run format checks
    log_info "Running format checks..."
    if command -v black &> /dev/null; then
        black --check --diff src/ tests/ test_regression.py || {
            log_error "Format checks failed - run 'black src/ tests/ test_regression.py' to fix"
            exit 1
        }
    else
        log_warning "black not available, skipping format checks"
    fi
    
    # Run import sorting checks
    if command -v isort &> /dev/null; then
        isort --check-only --diff src/ tests/ test_regression.py || {
            log_error "Import sorting failed - run 'isort src/ tests/ test_regression.py' to fix"
            exit 1
        }
    else
        log_warning "isort not available, skipping import checks"
    fi
    
    # Run tests
    log_info "Running tests..."
    if command -v pytest &> /dev/null; then
        pytest test_regression.py -v --tb=short || {
            log_error "Tests failed"
            exit 1
        }
    else
        log_warning "pytest not available, skipping tests"
    fi
    
    # Run CLI smoke test
    log_info "Running CLI smoke test..."
    python -m src.cli --check || {
        log_error "CLI smoke test failed"
        exit 1
    }
    
    log_success "All tests and quality checks passed"
}

clean_previous_builds() {
    log_info "Cleaning previous builds..."
    
    # Remove dist directory
    if [ -d "$DIST_DIR" ]; then
        rm -rf "$DIST_DIR"
        log_info "Removed $DIST_DIR directory"
    fi
    
    # Remove build directory
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
        log_info "Removed $BUILD_DIR directory"
    fi
    
    # Remove PyInstaller cache
    if [ -d "__pycache__" ]; then
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        log_info "Removed Python cache files"
    fi
    
    log_success "Build directories cleaned"
}

build_executable() {
    log_info "Building executable with PyInstaller..."
    
    # Check PyInstaller
    if ! command -v pyinstaller &> /dev/null; then
        log_error "PyInstaller not found in PATH"
        exit 1
    fi
    
    # Build executable
    log_info "Running PyInstaller with spec file: $SPEC_FILE"
    pyinstaller "$SPEC_FILE" --clean --noconfirm || {
        log_error "PyInstaller build failed"
        exit 1
    }
    
    log_success "Executable built successfully"
}

verify_build() {
    log_info "Verifying build..."
    
    # Check if executable exists
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        EXECUTABLE="$DIST_DIR/${PROJECT_NAME}.exe"
    else
        EXECUTABLE="$DIST_DIR/$PROJECT_NAME"
    fi
    
    if [ ! -f "$EXECUTABLE" ]; then
        log_error "Executable not found: $EXECUTABLE"
        exit 1
    fi
    
    # Check executable size
    FILESIZE=$(stat -c%s "$EXECUTABLE" 2>/dev/null || stat -f%z "$EXECUTABLE" 2>/dev/null || echo "unknown")
    log_info "Executable size: $(numfmt --to=iec $FILESIZE 2>/dev/null || echo "$FILESIZE bytes")"
    
    # Test executable
    log_info "Testing executable..."
    
    # Test --version
    "$EXECUTABLE" --version || {
        log_error "Executable --version test failed"
        exit 1
    }
    
    # Test --check
    "$EXECUTABLE" --check || {
        log_error "Executable --check test failed"
        exit 1
    }
    
    log_success "Executable verification completed successfully"
}

show_build_summary() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                        Build Summary                             ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        EXECUTABLE="$DIST_DIR/${PROJECT_NAME}.exe"
    else
        EXECUTABLE="$DIST_DIR/$PROJECT_NAME"
    fi
    
    echo -e "${BLUE}📦 Executable:${NC} $(realpath "$EXECUTABLE")"
    echo -e "${BLUE}📏 Size:${NC} $(stat -c%s "$EXECUTABLE" 2>/dev/null || stat -f%z "$EXECUTABLE" 2>/dev/null || echo "unknown") bytes"
    echo -e "${BLUE}🎯 Type:${NC} Single-file CLI executable"
    echo -e "${BLUE}🖥️  Platform:${NC} $(uname -s) $(uname -m)"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ${EXECUTABLE} --version"
    echo -e "  ${EXECUTABLE} --check"
    echo -e "  ${EXECUTABLE} --help"
    echo ""
    echo -e "${GREEN}✨ Build completed successfully!${NC}"
}

# Main execution
main() {
    print_banner
    
    # Parse command line arguments
    SKIP_TESTS=false
    SKIP_DEPS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-tests)
                SKIP_TESTS=true
                log_warning "Skipping tests as requested"
                shift
                ;;
            --skip-deps)
                SKIP_DEPS=true
                log_warning "Skipping dependency installation as requested"
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-tests    Skip running tests and lint checks"
                echo "  --skip-deps     Skip dependency installation"
                echo "  -h, --help      Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Execute build steps
    check_requirements
    
    if [ "$SKIP_DEPS" = false ]; then
        install_dependencies
    fi
    
    if [ "$SKIP_TESTS" = false ]; then
        run_tests
    fi
    
    clean_previous_builds
    build_executable
    verify_build
    show_build_summary
}

# Run main function
main "$@"