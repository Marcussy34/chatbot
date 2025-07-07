#!/bin/bash

# Google Cloud Run Deployment Script for Mindhive Chatbot
# ========================================================

set -e  # Exit on any error

# Configuration
PROJECT_ID="sincere-amulet-465112-b9"
SERVICE_NAME="mindhive-chatbot"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
MEMORY="2Gi"
CPU="2"
MAX_INSTANCES="3"
MIN_INSTANCES="0"
TIMEOUT="1200s"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

# Check if PROJECT_ID is set
check_project_id() {
    if [ -z "$PROJECT_ID" ]; then
        print_error "PROJECT_ID is not set. Please edit this script and set your Google Cloud Project ID."
        print_warning "Edit deploy.sh and set PROJECT_ID at the top of the file."
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI is not installed. Please install it first:"
        echo "https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first:"
        echo "https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Not authenticated with gcloud. Please run: gcloud auth login"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Set up gcloud
setup_gcloud() {
    print_step "Setting up gcloud configuration..."
    
    gcloud config set project $PROJECT_ID
    gcloud config set run/region $REGION
    
    # Enable required APIs
    print_step "Enabling required Google Cloud APIs..."
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    
    print_success "gcloud setup complete"
}

# Build and push Docker image using Cloud Build
build_and_push() {
    print_step "Building and pushing Docker image using Cloud Build..."
    
    # Use Cloud Build to build for correct architecture
    print_step "Building Docker image: $IMAGE_NAME"
    gcloud builds submit --tag $IMAGE_NAME .
    
    print_success "Image built and pushed successfully"
}

# Deploy to Cloud Run
deploy_to_cloud_run() {
    print_step "Deploying to Google Cloud Run..."
    
    gcloud run deploy $SERVICE_NAME \
        --image=$IMAGE_NAME \
        --platform=managed \
        --region=$REGION \
        --allow-unauthenticated \
        --memory=$MEMORY \
        --cpu=$CPU \
        --timeout=$TIMEOUT \
        --max-instances=$MAX_INSTANCES \
        --min-instances=$MIN_INSTANCES \
        --set-env-vars="PYTHONPATH=/app" \
        --port=8080 \
        --execution-environment=gen2 \
        --no-cpu-throttling
    
    print_success "Deployment completed successfully"
}

# Get service URL
get_service_url() {
    print_step "Getting service URL..."
    
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
        --platform=managed \
        --region=$REGION \
        --format='value(status.url)')
    
    print_success "Service deployed at: $SERVICE_URL"
    
    # Test the service
    print_step "Testing the deployed service..."
    echo "Health check: $SERVICE_URL/health"
    echo "API docs: $SERVICE_URL/docs"
    echo "Calculator test: $SERVICE_URL/calculator?expr=2+3"
}

# Test local Docker build (optional)
test_local() {
    print_step "Testing local Docker build..."
    
    # Build for local testing
    docker build -t $SERVICE_NAME-local .
    
    print_success "Local build successful. To test locally run:"
    echo "docker run -p 8080:8080 -e PORT=8080 $SERVICE_NAME-local"
    echo "Then visit: http://localhost:8080"
}

# Main deployment function
deploy() {
    echo "🚀 Mindhive Chatbot - Google Cloud Run Deployment"
    echo "================================================"
    
    check_project_id
    check_prerequisites
    setup_gcloud
    build_and_push
    deploy_to_cloud_run
    get_service_url
    
    echo ""
    print_success "🎉 Deployment completed successfully!"
    echo ""
    echo "Your Mindhive Chatbot is now running on Google Cloud Run:"
    echo "Service URL: $SERVICE_URL"
    echo ""
    echo "API Endpoints:"
    echo "• Health Check: $SERVICE_URL/health"
    echo "• Calculator: $SERVICE_URL/calculator?expr=2+3"
    echo "• Products: $SERVICE_URL/products?query=black+tumbler"
    echo "• Outlets: $SERVICE_URL/outlets?query=outlets+in+PJ"
    echo "• API Docs: $SERVICE_URL/docs"
    echo ""
    echo "Submission URLs for Mindhive:"
    echo "• GitHub Repo: [Your GitHub URL]"
    echo "• Hosted Demo: $SERVICE_URL"
}

# Handle command line arguments
case "${1:-deploy}" in
    "test-local")
        test_local
        ;;
    "deploy")
        deploy
        ;;
    *)
        echo "Usage: $0 [deploy|test-local]"
        echo "  deploy     - Deploy to Google Cloud Run (default)"
        echo "  test-local - Test Docker build locally"
        exit 1
        ;;
esac 
