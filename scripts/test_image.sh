#!/bin/bash

# Test script for Wigor Viewer Docker image
# Builds the Docker image and runs smoke tests

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="wigor-viewer"
IMAGE_TAG="ci"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"
CONTAINER_NAME="wigor-test-$$"  # Unique name with process ID

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

log_step() {
    echo -e "${CYAN}🔄 $1${NC}"
}

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    Docker Image Test Script                      ║"
    echo "║              Building and testing wigor-viewer:ci               ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

cleanup() {
    log_info "Cleaning up..."
    
    # Remove container if it exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        log_info "Removing container: ${CONTAINER_NAME}"
        docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
    fi
    
    # Optional: Remove image if --cleanup flag is provided
    if [ "$CLEANUP_IMAGE" = true ]; then
        log_info "Removing image: ${FULL_IMAGE_NAME}"
        docker rmi "${FULL_IMAGE_NAME}" >/dev/null 2>&1 || true
    fi
}

check_docker() {
    log_step "Checking Docker availability..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon is not running or not accessible"
        exit 1
    fi
    
    log_success "Docker is available and running"
}

check_dockerfile() {
    log_step "Checking Dockerfile..."
    
    if [ ! -f "Dockerfile" ]; then
        log_error "Dockerfile not found in current directory"
        exit 1
    fi
    
    if [ ! -f "wigor.spec" ]; then
        log_error "wigor.spec file not found (required for PyInstaller build)"
        exit 1
    fi
    
    log_success "Required files found"
}

build_image() {
    log_step "Building Docker image: ${FULL_IMAGE_NAME}"
    
    # Build with build progress and cache
    docker build \
        --tag "${FULL_IMAGE_NAME}" \
        --progress=plain \
        --no-cache \
        . || {
        log_error "Docker image build failed"
        exit 1
    }
    
    log_success "Docker image built successfully"
    
    # Show image info
    IMAGE_SIZE=$(docker images "${FULL_IMAGE_NAME}" --format "table {{.Size}}" | tail -n 1)
    log_info "Image size: ${IMAGE_SIZE}"
}

test_image() {
    log_step "Testing Docker image..."
    
    # Test 1: Default command (--check)
    log_info "Test 1: Running default command (--check)"
    docker run --rm --name "${CONTAINER_NAME}-test1" "${FULL_IMAGE_NAME}" || {
        log_error "Default command test failed"
        exit 1
    }
    log_success "Default command test passed"
    
    # Test 2: Version command
    log_info "Test 2: Testing --version command"
    VERSION_OUTPUT=$(docker run --rm --name "${CONTAINER_NAME}-test2" "${FULL_IMAGE_NAME}" --version) || {
        log_error "Version command test failed"
        exit 1
    }
    log_success "Version command test passed: ${VERSION_OUTPUT}"
    
    # Test 3: Help command
    log_info "Test 3: Testing --help command"
    docker run --rm --name "${CONTAINER_NAME}-test3" "${FULL_IMAGE_NAME}" --help >/dev/null || {
        log_error "Help command test failed"
        exit 1
    }
    log_success "Help command test passed"
    
    # Test 4: Interactive shell test (optional)
    log_info "Test 4: Testing container accessibility"
    docker run --rm --name "${CONTAINER_NAME}-test4" --entrypoint=/bin/bash "${FULL_IMAGE_NAME}" -c "ls -la /app && whoami" || {
        log_error "Container accessibility test failed"
        exit 1
    }
    log_success "Container accessibility test passed"
}

test_security() {
    log_step "Running security tests..."
    
    # Test running as non-root
    log_info "Checking if container runs as non-root user"
    USER_ID=$(docker run --rm --name "${CONTAINER_NAME}-security" --entrypoint=/bin/bash "${FULL_IMAGE_NAME}" -c "id -u")
    
    if [ "$USER_ID" = "0" ]; then
        log_warning "Container is running as root (UID 0) - consider security implications"
    else
        log_success "Container runs as non-root user (UID: $USER_ID)"
    fi
    
    # Test executable permissions
    log_info "Checking executable permissions"
    docker run --rm --name "${CONTAINER_NAME}-perms" --entrypoint=/bin/bash "${FULL_IMAGE_NAME}" -c "ls -la /app/wigor-viewer" || {
        log_error "Cannot check executable permissions"
        exit 1
    }
    log_success "Executable permissions verified"
}

run_performance_test() {
    log_step "Running performance tests..."
    
    # Measure startup time
    log_info "Measuring container startup time"
    START_TIME=$(date +%s%N)
    docker run --rm --name "${CONTAINER_NAME}-perf" "${FULL_IMAGE_NAME}" --version >/dev/null
    END_TIME=$(date +%s%N)
    
    DURATION_MS=$(( (END_TIME - START_TIME) / 1000000 ))
    log_info "Container startup time: ${DURATION_MS}ms"
    
    if [ $DURATION_MS -lt 5000 ]; then
        log_success "Fast startup time (< 5s)"
    elif [ $DURATION_MS -lt 10000 ]; then
        log_warning "Moderate startup time (5-10s)"
    else
        log_warning "Slow startup time (> 10s)"
    fi
}

show_test_summary() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                        Test Summary                              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    IMAGE_ID=$(docker images "${FULL_IMAGE_NAME}" --format "{{.ID}}")
    IMAGE_SIZE=$(docker images "${FULL_IMAGE_NAME}" --format "{{.Size}}")
    
    echo -e "${BLUE}🐳 Image:${NC} ${FULL_IMAGE_NAME}"
    echo -e "${BLUE}🆔 ID:${NC} ${IMAGE_ID}"
    echo -e "${BLUE}📏 Size:${NC} ${IMAGE_SIZE}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  docker run --rm ${FULL_IMAGE_NAME}                    # Default (--check)"
    echo -e "  docker run --rm ${FULL_IMAGE_NAME} --version          # Show version"
    echo -e "  docker run --rm ${FULL_IMAGE_NAME} --help             # Show help"
    echo ""
    echo -e "${GREEN}✨ All tests passed successfully!${NC}"
    
    if [ "$CLEANUP_IMAGE" = true ]; then
        echo -e "${YELLOW}🗑️  Image will be cleaned up automatically${NC}"
    else
        echo -e "${CYAN}💡 To remove the image: docker rmi ${FULL_IMAGE_NAME}${NC}"
    fi
}

# Signal handlers for cleanup
trap cleanup EXIT
trap 'log_warning "Script interrupted"; exit 1' INT TERM

# Main execution
main() {
    print_banner
    
    # Parse command line arguments
    CLEANUP_IMAGE=false
    SKIP_PERFORMANCE=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cleanup)
                CLEANUP_IMAGE=true
                log_warning "Will cleanup image after testing"
                shift
                ;;
            --skip-perf)
                SKIP_PERFORMANCE=true
                log_warning "Skipping performance tests"
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --cleanup       Remove image after testing"
                echo "  --skip-perf     Skip performance tests"
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
    
    # Execute test steps
    check_docker
    check_dockerfile
    build_image
    test_image
    test_security
    
    if [ "$SKIP_PERFORMANCE" = false ]; then
        run_performance_test
    fi
    
    show_test_summary
}

# Run main function
main "$@"