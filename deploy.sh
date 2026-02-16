#!/bin/bash

# Face Recognition System Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# Function to publish Docker images to Docker Hub
publish_images() {
    local version=$1
    local docker_hub_user=$2
    
    # Validate arguments
    if [[ -z "$version" ]] || [[ -z "$docker_hub_user" ]]; then
        print_error "Both version and Docker Hub username are required"
        print_status "Usage: $0 publish <version> <docker_hub_user>"
        print_status "Example: $0 publish 1.0.0 myusername"
        return 1
    fi
    
    # Validate that version follows semantic versioning pattern
    if ! [[ $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        print_warning "Version '$version' does not follow semantic versioning (X.Y.Z)"
        print_warning "Continuing with provided version..."
    fi
    
    print_header "Publishing Docker Images"
    print_status "Version: $version"
    print_status "Docker Hub User: $docker_hub_user"
    
    # Check if required Docker images exist
    if ! docker images | grep -q "face_recognition_system-backend.*latest"; then
        print_error "face_recognition_system-backend:latest image not found"
        print_status "Please build the images first using 'docker-compose build'"
        return 1
    fi
    
    if ! docker images | grep -q "face_recognition_system-web.*latest"; then
        print_error "face_recognition_system-web:latest image not found"
        print_status "Please build the images first using 'docker-compose build'"
        return 1
    fi
    
    # Tag and push backend image
    print_status "Tagging backend image..."
    docker tag face_recognition_system-backend:latest ${docker_hub_user}/faceapi-server:${version}
    docker tag face_recognition_system-backend:latest ${docker_hub_user}/faceapi-server:latest
    
    print_status "Pushing backend images..."
    docker push ${docker_hub_user}/faceapi-server:${version}
    docker push ${docker_hub_user}/faceapi-server:latest
    
    # Tag and push web image
    print_status "Tagging web image..."
    docker tag face_recognition_system-web:latest ${docker_hub_user}/faceapi-web:${version}
    docker tag face_recognition_system-web:latest ${docker_hub_user}/faceapi-web:latest
    
    print_status "Pushing web images..."
    docker push ${docker_hub_user}/faceapi-web:${version}
    docker push ${docker_hub_user}/faceapi-web:latest
    
    print_status "✅ Successfully published all images to Docker Hub!"
    print_status "Backend images:"
    print_status "  - ${docker_hub_user}/faceapi-server:v${version}"
    print_status "  - ${docker_hub_user}/faceapi-server:latest"
    print_status "Web images:"
    print_status "  - ${docker_hub_user}/faceapi-web:v${version}"
    print_status "  - ${docker_hub_user}/faceapi-web:latest"
}

#!/bin/bash

# Function to display environment configuration based on mode
source_env() {
    local mode=$1
    local env_file
    local title
    
    # Validate input
    if [ -z "$mode" ]; then
        echo "Error: No mode specified"
        echo "Usage: display_env_config [dev|prod]"
        return 1
    fi
    
    if [ "$mode" != "dev" ] && [ "$mode" != "prod" ]; then
        echo "Error: Invalid mode '$mode'. Must be 'dev' or 'prod'"
        return 1
    fi
    
    # Set environment file and title based on mode
    if [ "$mode" = "dev" ]; then
        env_file=".env.dev"
        title="DEVELOPMENT ENVIRONMENT"
    else
        env_file=".env.prod"
        title="PRODUCTION ENVIRONMENT"
    fi
    
    # Check if env file exists
    if [ ! -f "$env_file" ]; then
        echo "Error: $env_file file not found!"
        return 1
    fi
    
    echo "=============================================="
    echo "    FACE RECOGNITION SYSTEM CONFIGURATION"
    echo "              MODE: $mode"
    echo "=============================================="
    echo
    
    # Source the appropriate env file
    set -a
    source "$env_file"
    set +a
    
    # Display database configuration
    echo "📦 DATABASE CONFIGURATION:"
    echo "-------------------------"
    echo "Milvus Host: $MILVUS_DB_HOST"
    echo "Milvus Port: $MILVUS_DB_PORT"
    echo "Milvus User: $MILVUS_DB_USER"
    echo "Milvus Password: $MILVUS_DB_PASSWORD"
    echo "Milvus DB Name: $MILVUS_DB_DB_NAME"
    echo "SQL Backend: $SQL_BACKEND"
    echo "SQL Host: $SQL_HOST"
    echo "SQL Port: $SQL_PORT"
    echo "SQL Username: $SQL_USERNAME"
    echo "SQL Password: $SQL_PASSWORD"
    echo "SQL Database: $SQL_DATABASE"
    echo
    
    # Display model configuration
    echo "🧠 MODEL CONFIGURATION:"
    echo "----------------------"
    echo "Model Path: $MODEL_PATH"
    echo "Model Loader: $MODEL_LOADER"
    echo "Model Threshold: $MODEL_THRESHOLD"
    echo "Model Device: $MODEL_DEVICE"
    echo "Embedding Dimension: $MODEL_EMB_DIM"
    echo
    
    # Display security settings (including sensitive info)
    echo "🔒 SECURITY SETTINGS:"
    echo "--------------------"
    echo "Project Name: $PROJECT_NAME"
    echo "JWT Secret Key: $JWT_SECRET_KEY"
    echo "JWT Algorithm: $JWT_ALGORITHM"
    echo "Token Expiry: $ACCESS_TOKEN_EXPIRE_MINUTES minutes"
    echo "Password Hash Algorithm: $PASSWORD_HASH_ALGORITHM"
    echo
    
    # Display server configuration
    echo "🌐 SERVER CONFIGURATION:"
    echo "-----------------------"
    echo "Backend Host: $BACKEND_HOST"
    echo "Backend Port: $BACKEND_PORT"
    echo "API Version: $API_V1_STR"
    
    # Show mode-specific configurations
    if [ "$mode" = "dev" ]; then
        echo "Allowed Origins: $ALLOWED_ORIGINS"
        echo "Backend Dev Port: $BACKEND_DEV_PORT"
        echo "Frontend Dev Port: $FRONTEND_DEV_PORT"
    else
        echo "Host Port: $HOST_PORT"
        echo "Domain Name: $DOMAIN_NAME"
    fi
    
    echo "Face Deduplication: $ALLOW_FACE_DEDUPICATION"
    echo
    
    # Development specific section
    if [ "$mode" = "dev" ]; then
        echo "📂 DEVELOPMENT SPECIFIC:"
        echo "----------------------"
        echo "Docker Volume Directory: $DOCKER_VOLUME_DIRECTORY"
        echo
    fi
    
    echo "=============================================="
    echo "Configuration loaded from $env_file"
    echo "Mode: $title"
    echo "⚠️  WARNING: SENSITIVE INFORMATION DISPLAYED - Handle with care!"
    echo "=============================================="
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed."
}

# Check GPU support
check_gpu_support() {
    print_header "Checking GPU Support..."
    
    # Check if nvidia-smi is available
    if ! command -v nvidia-smi &> /dev/null; then
        print_warning "NVIDIA drivers not found. GPU acceleration will not be available."
        print_warning "Install NVIDIA drivers and nvidia-container-toolkit for GPU support."
        return 1
    fi
    
    # Check NVIDIA driver version
    DRIVER_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits 2>/dev/null | head -1)
    if [[ $? -eq 0 ]]; then
        print_status "NVIDIA Driver Version: $DRIVER_VERSION"
    else
        print_warning "Unable to determine NVIDIA driver version"
        return 1
    fi
    
    # Check available GPUs
    GPU_COUNT=$(nvidia-smi --query-gpu=count --format=csv,noheader,nounits 2>/dev/null)
    if [[ $? -eq 0 && $GPU_COUNT -gt 0 ]]; then
        print_status "Found $GPU_COUNT GPU(s)"
        
        # List GPU details
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | \
        while IFS=',' read -r name memory; do
            echo "  - $(echo $name | xargs): $(echo $memory | xargs) MiB VRAM"
        done
        
        # Check Docker GPU support
        if docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi>/dev/null 2>&1; then
            print_status "Docker GPU support is available"
            return 0
        else
            print_warning "Docker GPU support not configured. Install nvidia-container-toolkit."
            return 1
        fi
    else
        print_warning "No GPUs found or unable to query GPU information"
        return 1
    fi
}

# Test GPU functionality
test_gpu() {
    print_header "Testing GPU Functionality..."
    
    # Build and run GPU test container
    cd scripts
    docker build -f Dockerfile.test-gpu -t face-rec-gpu-test .
    
    if docker run --rm --gpus all face-rec-gpu-test; then
        print_status "GPU functionality test passed!"
        cd ..
        return 0
    else
        print_error "GPU functionality test failed!"
        cd ..
        return 1
    fi
}

# Function to safely replace text in files (cross-platform compatible)
safe_sed_replace() {
    local search_pattern="$1"
    local replacement="$2"
    local file="$3"
    
    # Detect OS and use appropriate sed syntax
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/${search_pattern}/${replacement}/g" "$file"
    else
        # Linux and others
        sed -i "s/${search_pattern}/${replacement}/g" "$file"
    fi
}

# Generate secure passwords
generate_env() {
    local env=${1:-dev}

    env_file=".env.$env"
    env_example_file=".env.$env.example"

    if [[ ! -f $env_file ]]; then
        print_warning "Production environment file not found. Creating from example..."
        cp "$env_example_file" "$env_file"
        print_status "Generated $env_file file from $env_example_file for $env environment"
        
        # Generate secure passwords
        safe_sed_replace "your_jwt_secure_secret_key_here" "$(openssl rand -hex 32)" "$env_file"
        safe_sed_replace "your_secure_db_password_here" "$(openssl rand -hex 8)" "$env_file"
        safe_sed_replace "your_secure_minio_password_here" "$(openssl rand -hex 8)" "$env_file"
        
        print_status "Generated secure passwords in $env_file"
        print_warning "Please review and adjust $env_file before deployment!"
    else
        print_status "Using existing $env_file file"
    fi
    source_env "$env"
}

# Deploy development environment
deploy_dev() {
    local use_gpu=${1:-false}
    
    print_status "Deploying development environment..."
    
    # Check GPU support and warn if not available
    if [[ "$use_gpu" == "true" ]]; then
        if check_gpu_support; then
            print_status "GPU support detected - deploying with GPU acceleration"
            COMPOSE_FILE="docker-compose.dev.gpu.yml"
        else
            print_warning "No GPU support detected - falling back to CPU version"
            print_warning "See GPU_SUPPORT.md for GPU setup instructions"
            COMPOSE_FILE="docker-compose.dev.yml"
        fi
    else
        print_status "Deploying CPU-only version"
        COMPOSE_FILE="docker-compose.dev.yml"
    fi
    
    generate_env "dev"
    
    docker-compose -f "$COMPOSE_FILE" down
    docker-compose -f "$COMPOSE_FILE" up -d --build
    
    print_status "Development environment deployed!"
    print_status "See CONTAINER_SUPPORT.md for more information"
    print_status "Frontend URL: http://localhost:${FRONTEND_DEV_PORT}"
    print_status "Backend URL: http://localhost:${BACKEND_DEV_PORT}"

}

# Deploy production environment
deploy_prod() {
    local use_gpu=${1:-false}
    
    print_status "Deploying production environment..."
    
    # Check GPU support
    if [[ "$use_gpu" == "true" ]]; then
        if check_gpu_support; then
            print_status "GPU support detected - deploying with GPU acceleration"
            COMPOSE_FILE="docker-compose.prod.gpu.yml"
        else
            print_warning "No GPU support detected - falling back to CPU version"
            COMPOSE_FILE="docker-compose.prod.yml"
        fi
    else
        print_status "Deploying CPU-only version"
        COMPOSE_FILE="docker-compose.prod.yml"
    fi
    
    generate_env "prod"
    
    docker-compose -f "$COMPOSE_FILE" --env-file .env.prod down
    docker-compose -f "$COMPOSE_FILE" --env-file .env.prod up -d --build
    
    print_status "Production environment deployed!"
    print_status "See CONTAINER_SUPPORT.md for more information"
    print_status "Server URL: http://localhost:${HOST_PORT:-80}"
    # if DOMAIN_NAME
    if [[ -n "$DOMAIN_NAME" ]]; then
        print_status "Server URL: https://$DOMAIN_NAME"
    fi
}

# Rebuild containers
rebuild_containers() {
    local container=$1
    local env=${2:-dev}
    
    if [[ -z "$container" ]]; then
        print_error "Container name is required. Use 'all' to rebuild all containers."
        return 1
    fi
    
    print_header "Rebuilding container(s): $container (Environment: $env)"
    
    if [[ "$container" == "all" ]]; then
        if [[ "$env" == "prod" ]]; then
            docker-compose -f docker-compose.prod.yml --env-file .env.prod build --no-cache
            print_status "All production containers rebuilt successfully!"
        else
            docker-compose build --no-cache
            print_status "All development containers rebuilt successfully!"
        fi
    else
        # Validate container name exists in docker-compose
        if [[ "$env" == "prod" ]]; then
            if ! docker-compose -f docker-compose.prod.yml config --services | grep -q "^${container}$"; then
                print_error "Container '$container' not found in production configuration"
                print_status "Available containers:"
                docker-compose -f docker-compose.prod.yml config --services | sed 's/^/  /'
                return 1
            fi
            docker-compose -f docker-compose.prod.yml --env-file .env.prod build --no-cache "$container"
        else
            if ! docker-compose config --services | grep -q "^${container}$"; then
                print_error "Container '$container' not found in development configuration"
                print_status "Available containers:"
                docker-compose config --services | sed 's/^/  /'
                return 1
            fi
            docker-compose build --no-cache "$container"
        fi
        print_status "Container '$container' rebuilt successfully!"
    fi
}

# Show logs
show_logs() {
    local env=${1:-dev}
    local use_gpu=${2:-false}
    
    if [[ "$env" == "prod" ]]; then
        if [[ "$use_gpu" == "true" ]]; then
            docker-compose -f docker-compose.prod.gpu.yml --env-file .env.prod logs -f
        else
            docker-compose -f docker-compose.prod.yml --env-file .env.prod logs -f
        fi
    else
        if [[ "$use_gpu" == "true" ]]; then
            docker-compose -f docker-compose.dev.gpu.yml logs -f
        else
            docker-compose -f docker-compose.dev.yml logs -f
        fi
    fi
}

# Stop services
stop_services() {
    local env=${1:-dev}
    local use_gpu=${2:-false}

    print_status "Stopping $env environment..."
    
    if [[ "$env" == "prod" ]]; then
        if [[ "$use_gpu" == "true" ]]; then
            docker-compose -f docker-compose.prod.gpu.yml --env-file .env.prod down
        else
            docker-compose -f docker-compose.prod.yml --env-file .env.prod down
        fi
    else
        if [[ "$use_gpu" == "true" ]]; then
            docker-compose -f docker-compose.dev.gpu.yml --env-file .env.dev down
        else
            docker-compose -f docker-compose.dev.yml --env-file .env.dev down
        fi
    fi
    print_status "Services stopped"
}

# Show status
show_status() {
    local env=${1:-dev}
    local use_gpu=${2:-false}
    
    if [[ "$env" == "prod" ]]; then
        if [[ "$use_gpu" == "true" ]]; then
            docker-compose -f docker-compose.prod.gpu.yml --env-file .env.prod ps
        else
            docker-compose -f docker-compose.prod.yml --env-file .env.prod ps
        fi
    else
        if [[ "$use_gpu" == "true" ]]; then
            docker-compose -f docker-compose.dev.gpu.yml --env-file .env.dev ps
        else
            docker-compose -f docker-compose.dev.yml --env-file .env.dev ps
        fi
    fi
}

# Main menu
show_help() {
    echo "Face Recognition System Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND] [--gpu]"
    echo ""
    echo "Commands:"
    echo "  dev          Deploy development environment"
    echo "  prod         Deploy production environment"
    echo "  rebuild      Rebuild containers (use 'rebuild [container]' or 'rebuild all')"
    echo "  gpu-check    Check GPU support and test functionality"
    echo "  logs         Show development logs (use 'logs prod' for production)"
    echo "  status       Show service status (use 'status prod' for production)"
    echo "  stop         Stop development services (use 'stop prod' for production)"
    echo "  publish      Publish Docker images to Docker Hub (publish <version> <docker_hub_user>)"
    echo "  help         Show this help message"
    echo ""
    echo "Options:"
    echo "  --gpu        Use GPU-accelerated version of services"
    echo ""
    echo "Examples:"
    echo "  $0 dev                    # Deploy development environment (CPU)"
    echo "  $0 dev --gpu              # Deploy development environment (GPU)"
    echo "  $0 prod                   # Deploy production environment (CPU)"
    echo "  $0 prod --gpu             # Deploy production environment (GPU)"
    echo "  $0 rebuild backend        # Rebuild backend container"
    echo "  $0 rebuild all            # Rebuild all containers"
    echo "  $0 rebuild frontend prod  # Rebuild frontend in production"
    echo "  $0 gpu-check              # Check and test GPU support"
    echo "  $0 logs prod              # Show production logs"
    echo "  $0 logs prod --gpu        # Show production GPU logs"
    echo "  $0 status --gpu           # Show GPU development status"
    echo "  $0 publish 1.0.0 myuser   # Publish images to Docker Hub"
}

# Global variables for GPU support
USE_GPU=false

# Parse command line arguments
ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --gpu)
            USE_GPU=true
            shift
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done

# Set command from first argument
if [[ ${#ARGS[@]} -gt 0 ]]; then
    COMMAND="${ARGS[0]}"
else
    COMMAND="help"
fi

# Set default command if not provided
COMMAND="${COMMAND:-help}"

# Execute based on command
check_docker

case "$COMMAND" in
    dev)
        deploy_dev "$USE_GPU"
        ;;
    prod)
        deploy_prod "$USE_GPU"
        ;;
    rebuild)
        # Handle rebuild command with additional arguments
        if [[ ${#ARGS[@]} -gt 1 ]]; then
            CONTAINER="${ARGS[1]}"
        else
            CONTAINER=""
        fi
        
        if [[ ${#ARGS[@]} -gt 2 ]]; then
            ENV="${ARGS[2]}"
        else
            ENV="dev"
        fi
        
        rebuild_containers "$CONTAINER" "$ENV"
        ;;
    gpu-check)
        if check_gpu_support; then
            test_gpu
        else
            print_error "GPU support not available. Cannot run GPU tests."
            exit 1
        fi
        ;;
    logs)
        show_logs "${ARGS[0]}" "$USE_GPU"
        ;;
    status)
        show_status "${ARGS[1]}" "$USE_GPU"
        ;;
    stop)
        stop_services "${ARGS[1]}" "$USE_GPU"
        ;;
    publish)
        # Handle publish command with version and user arguments
        if [[ ${#ARGS[@]} -gt 2 ]]; then
            VERSION="${ARGS[1]}"
            DOCKER_HUB_USER="${ARGS[2]}"
            publish_images "$VERSION" "$DOCKER_HUB_USER"
        else
            print_error "Publish command requires version and Docker Hub username"
            print_status "Usage: $0 publish <version> <docker_hub_user>"
            print_status "Example: $0 publish v1.0.0 myusername"
            exit 1
        fi
        ;;
    help|"")
        show_help
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac