#!/bin/bash
# docker_build.sh: helper script to build and test manuskript inside docker.
set -e

# Change directory to the repository root
cd "$(dirname "$0")/.."

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: docker is not installed. Please install Docker first."
    exit 1
fi

# Print usage
print_usage() {
    echo "Usage: $0 [action]"
    echo "Actions:"
    echo "  test         Run tests using pytest inside docker"
    echo "  pyinstaller  Build standalone Linux binary inside docker"
    echo "  deb          Build Debian (.deb) package inside docker"
    echo "  rpm          Build RPM (.rpm) package inside docker"
    echo "  all          Run tests and build all formats inside docker"
    echo "  build-image  Explicitly build/rebuild the docker builder image"
}

ACTION=${1:-all}

# Ensure the builder image is built
if [ "$ACTION" = "build-image" ]; then
    echo "Building/rebuilding docker builder image..."
    docker compose build
    exit 0
fi

# If image does not exist, build it
if ! docker image inspect manuskript-builder:latest &> /dev/null; then
    echo "Builder image 'manuskript-builder:latest' not found. Building it now..."
    docker compose build
fi

# Helper function to run build command on a copy inside the container
# and copy the outputs back to the host. This avoids permission issues
# and read-only host mounts (e.g. virtiofs on macOS Lima VM).
run_build_in_container() {
    local cmd="$1"
    local container_name="manuskript-build-temp-$(date +%s)"
    
    echo "Starting build container..."
    docker run --name "$container_name" \
        -v "$(pwd)":/workspace:ro \
        manuskript-builder:latest \
        bash -c "mkdir -p /app && rsync -a /workspace/ /app/ && cd /app && $cmd"
    
    echo "Extracting built artifacts from container..."
    mkdir -p dist rpmbuild
    docker cp "$container_name":/app/dist/. ./dist/ 2>/dev/null || true
    docker cp "$container_name":/app/rpmbuild/. ./rpmbuild/ 2>/dev/null || true
    
    echo "Cleaning up container..."
    docker rm "$container_name" > /dev/null
}

case "$ACTION" in
    test)
        echo "Running pytest..."
        # Running tests doesn't need to write to the host, so we can run directly
        # with a read-only workspace mount.
        docker compose run --rm manuskript-builder
        ;;
    pyinstaller)
        echo "Building Linux standalone binary with PyInstaller..."
        run_build_in_container "pyinstaller manuskript.spec --clean --noconfirm"
        ;;
    deb)
        echo "Building Debian (.deb) package..."
        run_build_in_container "package/create_deb.sh"
        ;;
    rpm)
        echo "Building RPM (.rpm) package..."
        run_build_in_container "package/create_rpm.sh"
        ;;
    all)
        echo "Running tests..."
        docker compose run --rm manuskript-builder
        
        echo "Building Linux standalone binary with PyInstaller..."
        run_build_in_container "pyinstaller manuskript.spec --clean --noconfirm"
        
        echo "Building Debian (.deb) package..."
        run_build_in_container "package/create_deb.sh"
        
        echo "Building RPM (.rpm) package..."
        run_build_in_container "package/create_rpm.sh"
        ;;
    *)
        print_usage
        exit 1
        ;;
esac

echo "Done!"
