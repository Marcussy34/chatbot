# Google Cloud Run Deployment Guide

This guide covers deploying the Mindhive AI Chatbot to Google Cloud Run for production use.

## 🏗️ Architecture Overview

The application is deployed as a containerized FastAPI service on Google Cloud Run with:

- **Container**: Multi-stage Docker build with Python 3.11 slim image
- **Memory**: 1GB RAM (required for sentence-transformers model)
- **CPU**: 1 vCPU
- **Scaling**: 0-10 instances (scales to zero when not in use)
- **Port**: 8080 (Cloud Run standard)
- **Timeout**: 300s (5 minutes for model loading)

## 📋 Prerequisites

1. **Google Cloud Project**:
   - Create a project at [Google Cloud Console](https://console.cloud.google.com)
   - Enable billing for the project

2. **Local Tools**:
   ```bash
   # Install Google Cloud CLI
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   
   # Install Docker
   # Visit: https://docs.docker.com/get-docker/
   
   # Authenticate
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

## 🚀 Quick Deployment

### Option 1: Automated Script (Recommended)

1. **Edit the deployment script**:
   ```bash
   # Edit deploy.sh and set your PROJECT_ID
   nano deploy.sh
   # Set: PROJECT_ID="your-google-cloud-project-id"
   ```

2. **Deploy**:
   ```bash
   ./deploy.sh
   ```

The script will:
- ✅ Check prerequisites
- ✅ Enable required Google Cloud APIs
- ✅ Build and push Docker image
- ✅ Deploy to Cloud Run
- ✅ Provide service URL

### Option 2: Manual Deployment

1. **Set up environment**:
   ```bash
   export PROJECT_ID="your-google-cloud-project-id"
   export SERVICE_NAME="mindhive-chatbot"
   export REGION="us-central1"
   ```

2. **Enable APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

3. **Build and push image**:
   ```bash
   # Build
   docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .
   
   # Configure Docker for GCR
   gcloud auth configure-docker
   
   # Push
   docker push gcr.io/$PROJECT_ID/$SERVICE_NAME
   ```

4. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy $SERVICE_NAME \
     --image=gcr.io/$PROJECT_ID/$SERVICE_NAME \
     --platform=managed \
     --region=$REGION \
     --allow-unauthenticated \
     --memory=1Gi \
     --cpu=1 \
     --timeout=300s \
     --max-instances=10 \
     --min-instances=0 \
     --set-env-vars="PYTHONPATH=/app" \
     --port=8080
   ```

5. **Get service URL**:
   ```bash
   gcloud run services describe $SERVICE_NAME \
     --platform=managed \
     --region=$REGION \
     --format='value(status.url)'
   ```

## 🧪 Testing the Deployment

Once deployed, test the endpoints:

```bash
# Replace YOUR_SERVICE_URL with your actual Cloud Run URL

# Health check
curl https://YOUR_SERVICE_URL/health

# Calculator API
curl "https://YOUR_SERVICE_URL/calculator?expr=2+3*4"

# Product search
curl "https://YOUR_SERVICE_URL/products?query=black+tumbler"

# Outlet queries
curl "https://YOUR_SERVICE_URL/outlets?query=outlets+in+PJ"

# API documentation
open https://YOUR_SERVICE_URL/docs
```

## 🔧 Local Testing

Test the Docker container locally before deploying:

```bash
# Test local build
./deploy.sh test-local

# Or manually:
docker build -t mindhive-chatbot-local .
docker run -p 8080:8080 -e PORT=8080 mindhive-chatbot-local

# Test locally
curl http://localhost:8080/health
```

## 🎯 CI/CD with Cloud Build

For automated deployment on git push:

1. **Create trigger**:
   ```bash
   gcloud builds triggers create github \
     --repo-name=your-repo \
     --repo-owner=your-username \
     --branch-pattern="^main$" \
     --build-config=cloudbuild.yaml
   ```

2. **Push to main branch** → Automatically deploys

## 📊 Monitoring & Logs

### View Logs
```bash
# Real-time logs
gcloud run services logs tail mindhive-chatbot --region=us-central1

# Recent logs
gcloud run services logs read mindhive-chatbot --region=us-central1 --limit=50
```

### Monitoring Dashboard
- Visit [Cloud Run Console](https://console.cloud.google.com/run)
- Select your service → Metrics tab
- Monitor: Requests, Latency, CPU, Memory

### Health Monitoring
The app includes a `/health` endpoint that Cloud Run uses for:
- Startup probes
- Liveness checks
- Load balancer health checks

## 💰 Cost Optimization

Cloud Run pricing is pay-per-use:

- **Free Tier**: 2 million requests/month
- **Scaling to Zero**: No cost when idle
- **Memory**: ~$0.0000024 per GB-second
- **CPU**: ~$0.0000096 per vCPU-second
- **Requests**: $0.40 per million requests

**Estimated Monthly Cost**: $1-10 for light usage

## 🔒 Security Features

- ✅ **Non-root container**: Runs as `appuser`
- ✅ **No secrets in image**: Environment variables only
- ✅ **Input validation**: FastAPI + Pydantic validation
- ✅ **Rate limiting**: Cloud Run built-in protection
- ✅ **HTTPS only**: Automatic SSL certificates

## 🐛 Troubleshooting

### Common Issues

1. **"Project not found"**:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **"APIs not enabled"**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com
   ```

3. **"Permission denied"**:
   ```bash
   gcloud auth login
   gcloud auth configure-docker
   ```

4. **"Service startup timeout"**:
   - Check logs: `gcloud run services logs read mindhive-chatbot`
   - Increase timeout: `--timeout=600s`
   - Check memory: Use `--memory=2Gi`

5. **"Container fails to start"**:
   ```bash
   # Test locally first
   docker build -t test .
   docker run -p 8080:8080 -e PORT=8080 test
   ```

### Debug Commands

```bash
# Check service status
gcloud run services describe mindhive-chatbot --region=us-central1

# View detailed logs
gcloud run services logs read mindhive-chatbot --region=us-central1 --format="table(timestamp,severity,textPayload)"

# Check revisions
gcloud run revisions list --service=mindhive-chatbot --region=us-central1
```

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [FastAPI Production Guide](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)

## 📄 Service Information

After successful deployment, you'll receive URLs for:

- **Health Check**: `https://YOUR_SERVICE_URL/health`
- **API Documentation**: `https://YOUR_SERVICE_URL/docs`
- **Calculator**: `https://YOUR_SERVICE_URL/calculator?expr=2+3`
- **Products**: `https://YOUR_SERVICE_URL/products?query=tumbler`
- **Outlets**: `https://YOUR_SERVICE_URL/outlets?query=SS2`

**For Mindhive submission**:
- **GitHub Repo**: Your repository URL
- **Hosted Demo**: Your Cloud Run service URL 