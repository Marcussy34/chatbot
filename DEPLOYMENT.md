# Deployment Guide - Render

This guide will help you deploy your Mindhive AI Chatbot to Render cloud platform.

## Prerequisites

1. ✅ **GitHub Repository**: Your code must be in a GitHub repository
2. ✅ **Render Account**: Create a free account at [render.com](https://render.com)
3. ✅ **Environment Ready**: All dependencies in requirements.txt

## Pre-Deployment Checklist

### 1. Verify Requirements.txt
Your `requirements.txt` should be clean (sqlite3 removed as it's built into Python):

```txt
# Core LangChain dependencies for Phase 1
langchain==0.1.0
langchain-community==0.0.10
langchain-core==0.1.7
langchain-openai==0.0.2

# Memory and conversation management
langchain-experimental==0.0.40

# For later phases (FastAPI, testing, etc.)
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
httpx==0.25.2

# Vector store and embeddings (for Phase 4)
faiss-cpu==1.7.4
sentence-transformers==2.2.2

# Database support (for Phase 4)
sqlalchemy==2.0.23

# Testing framework
pytest==7.4.3
pytest-asyncio==0.21.1

# Environment management
python-dotenv==1.0.0

# For web scraping (Phase 4)
beautifulsoup4==4.12.2
requests==2.31.0
```

### 2. Test Locally
Before deploying, test your app locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI app
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/health
curl "http://localhost:8000/calculator?expr=2+3"
```

### 3. Push to GitHub
Make sure all your changes are committed and pushed:

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Render Deployment Steps

### Step 1: Create a New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** button in the top right
3. Select **"Web Service"**

### Step 2: Connect Your Repository

1. Choose **"Build and deploy from a Git repository"**
2. Click **"Next"**
3. Connect your GitHub account if not already connected
4. Select your chatbot repository
5. Click **"Connect"**

### Step 3: Configure Deployment Settings

Fill in the following settings:

| Setting | Value |
|---------|-------|
| **Name** | `mindhive-chatbot` (or your preferred name) |
| **Region** | Choose closest to your users (e.g., Oregon USA) |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python run.py` |

### Step 4: Choose Instance Type

- For **development/testing**: Select **Free** tier
- For **production**: Consider **Starter** ($7/month) or higher for better performance

### Step 5: Environment Variables (Optional)

If your app needs environment variables:

1. Click **"Advanced"** 
2. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI)
   - `LOG_LEVEL`: `info`
   - Any other custom variables your app needs

### Step 6: Deploy

1. Review all settings
2. Click **"Create Web Service"**
3. Render will start building your application

## Post-Deployment

### Monitor the Build

1. Watch the build logs in real-time
2. The build process typically takes 2-5 minutes
3. Look for any error messages during installation

### Test Your Deployed App

Once deployed, you'll get a URL like: `https://mindhive-chatbot.onrender.com`

Test these endpoints:

```bash
# Health check
curl https://your-app-name.onrender.com/health

# Calculator test
curl "https://your-app-name.onrender.com/calculator?expr=5*4"

# Product search test
curl "https://your-app-name.onrender.com/products?query=black tumbler"

# Outlet query test
curl "https://your-app-name.onrender.com/outlets?query=outlets in SS2"
```

### Access API Documentation

Visit: `https://your-app-name.onrender.com/docs`

This will show the interactive Swagger UI where you can test all endpoints.

## Important Notes

### Free Tier Limitations

- **Sleep Mode**: Free apps sleep after 15 minutes of inactivity
- **Build Minutes**: Limited build time per month
- **Performance**: Lower CPU and memory allocation

### Data Files

Your SQLite database (`data/zus_outlets.db`) and FAISS index (`data/product_index.faiss`) will be included in the deployment as they're part of your repository.

### Production Considerations

For production use, consider:

1. **Upgrade to paid plan** for better performance
2. **Add persistent storage** if you need to write data
3. **Set up monitoring** and alerts
4. **Configure custom domain** if needed
5. **Add SSL certificate** (included with Render)

## Troubleshooting

### Common Issues

#### Build Fails
- Check build logs for specific error messages
- Verify `requirements.txt` has correct dependencies
- Ensure Python version compatibility

#### App Won't Start
- Check start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Verify your `app/main.py` file structure
- Check for missing environment variables

#### Import Errors
- Ensure all required packages are in `requirements.txt`
- Check for case-sensitive file/module names
- Verify file paths are correct

#### Database Issues
- SQLite database should be included in repository
- Check file paths in your code (use relative paths)
- Ensure database files have proper permissions

### Getting Help

1. Check [Render Documentation](https://render.com/docs)
2. Review build logs carefully
3. Test locally first to isolate issues
4. Check the [Render Community Forum](https://community.render.com/)

## Success! 🎉

Your Mindhive AI Chatbot should now be live and accessible worldwide through your Render URL!

### Next Steps

1. Share your deployment URL for demo purposes
2. Test all endpoints thoroughly
3. Monitor performance and logs
4. Consider upgrading for production workloads

---

**Demo URL Format**: `https://your-app-name.onrender.com`
**API Docs**: `https://your-app-name.onrender.com/docs` 