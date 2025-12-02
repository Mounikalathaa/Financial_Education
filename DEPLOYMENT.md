# 🚀 Deployment Guide - Financial Education Quiz Engine

Complete guide for deploying the Financial Education Quiz Engine in various environments.

## 📋 Table of Contents
1. [Local Development](#local-development)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Configuration](#configuration)

---

## 🏠 Local Development

### Prerequisites
- Python 3.9+
- Azure OpenAI API access
- 4GB RAM minimum

### Setup Steps

1. **Navigate to project directory**
```bash
cd /Users/mounikas@backbase.com/Documents/FinancialEducationQuiz
```

2. **Run setup script**
```bash
bash setup.sh
```

This will:
- Check Python version
- Create virtual environment
- Install dependencies
- Verify .env configuration
- Initialize knowledge base
- Run verification tests

3. **Start the application**
```bash
bash start.sh
```

Or manually:
```bash
# Terminal 1: MCP Server
source venv/bin/activate
python mcp_server.py

# Terminal 2: Streamlit UI
source venv/bin/activate
streamlit run app.py
```

4. **Access the application**
- Local: http://localhost:8501
- Network: http://YOUR_IP:8501

---

## 🏭 Production Deployment

### System Requirements
- Ubuntu 20.04+ / CentOS 8+ / macOS 11+
- Python 3.9+
- 8GB RAM recommended
- 10GB disk space
- SSL certificate (for HTTPS)

### Production Setup

1. **Install system dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3-pip python3-venv nginx

# CentOS/RHEL
sudo yum install python39 python39-pip nginx
```

2. **Clone/Copy project**
```bash
git clone <your-repo> financial-education-quiz
cd financial-education-quiz
```

3. **Configure environment**
```bash
cp .env.example .env
nano .env  # Edit with production credentials
```

4. **Run setup**
```bash
bash setup.sh
```

5. **Configure systemd services**

Create `/etc/systemd/system/financial-edu-mcp.service`:
```ini
[Unit]
Description=Financial Education MCP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/financial-education-quiz
Environment="PATH=/path/to/financial-education-quiz/venv/bin"
ExecStart=/path/to/financial-education-quiz/venv/bin/python mcp_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/financial-edu-ui.service`:
```ini
[Unit]
Description=Financial Education Streamlit UI
After=network.target financial-edu-mcp.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/financial-education-quiz
Environment="PATH=/path/to/financial-education-quiz/venv/bin"
ExecStart=/path/to/financial-education-quiz/venv/bin/streamlit run app.py --server.port=8501 --server.headless=true
Restart=always

[Install]
WantedBy=multi-user.target
```

6. **Enable and start services**
```bash
sudo systemctl daemon-reload
sudo systemctl enable financial-edu-mcp
sudo systemctl enable financial-edu-ui
sudo systemctl start financial-edu-mcp
sudo systemctl start financial-edu-ui
```

7. **Configure Nginx reverse proxy**

Create `/etc/nginx/sites-available/financial-education`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/financial-education /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

8. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🐳 Docker Deployment

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data/vector_store

# Expose ports
EXPOSE 8501 8000

# Run initialization
RUN python scripts/load_knowledge_base.py

CMD ["bash", "start.sh"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    container_name: financial-edu-mcp
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MODEL_API_VERSION=${MODEL_API_VERSION}
      - MODEL_NAME=${MODEL_NAME}
      - OPENAI_ENDPOINT=${OPENAI_ENDPOINT}
    command: python mcp_server.py
    restart: unless-stopped
    volumes:
      - ./data:/app/data

  streamlit-ui:
    build: .
    container_name: financial-edu-ui
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MODEL_API_VERSION=${MODEL_API_VERSION}
      - MODEL_NAME=${MODEL_NAME}
      - OPENAI_ENDPOINT=${OPENAI_ENDPOINT}
      - MCP_SERVER_URL=http://mcp-server:8000
    command: streamlit run app.py --server.port=8501 --server.headless=true
    restart: unless-stopped
    depends_on:
      - mcp-server
    volumes:
      - ./data:/app/data
```

### Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## ☁️ Cloud Deployment

### AWS Deployment

#### Using EC2

1. **Launch EC2 instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance type: t3.medium or larger
   - Security groups: Allow 80, 443, 8501, 8000

2. **SSH into instance**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Follow production setup steps** (see above)

#### Using AWS Elastic Beanstalk

1. **Install EB CLI**
```bash
pip install awsebcli
```

2. **Initialize EB**
```bash
eb init -p python-3.9 financial-education-quiz
```

3. **Create environment**
```bash
eb create production
```

4. **Deploy**
```bash
eb deploy
```

### Azure Deployment

#### Using Azure App Service

1. **Install Azure CLI**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

2. **Login**
```bash
az login
```

3. **Create resource group**
```bash
az group create --name financial-edu-rg --location eastus
```

4. **Create App Service plan**
```bash
az appservice plan create \
  --name financial-edu-plan \
  --resource-group financial-edu-rg \
  --sku B1 \
  --is-linux
```

5. **Create web app**
```bash
az webapp create \
  --resource-group financial-edu-rg \
  --plan financial-edu-plan \
  --name financial-education-quiz \
  --runtime "PYTHON|3.9"
```

6. **Deploy code**
```bash
az webapp up \
  --name financial-education-quiz \
  --resource-group financial-edu-rg
```

### Google Cloud Platform

#### Using Cloud Run

1. **Build container**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/financial-edu
```

2. **Deploy to Cloud Run**
```bash
gcloud run deploy financial-education-quiz \
  --image gcr.io/PROJECT_ID/financial-edu \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## ⚙️ Configuration

### Environment Variables

Required variables in `.env`:
```bash
# Azure OpenAI (Required)
OPENAI_API_KEY=your_api_key
MODEL_API_VERSION=2024-02-01
MODEL_NAME=gpt-4o
OPENAI_ENDPOINT=https://your-resource.openai.azure.com

# Optional
GOOGLE_API_KEY=your_google_api_key
MCP_SERVER_URL=http://localhost:8000
CLASSIFIER_MODEL_PROVIDER='openai'
```

### Application Configuration

Edit `config.yaml` to customize:

```yaml
# LLM Settings
llm:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.7
  max_tokens: 2000

# Gamification
gamification:
  points_per_correct: 10
  points_per_quiz: 50
  levels:
    - name: "Beginner"
      min_points: 0
      max_points: 100
```

---

## 🔍 Monitoring & Logging

### Application Logs

```bash
# MCP Server logs
tail -f logs/mcp_server.log

# Streamlit logs
tail -f logs/streamlit.log
```

### Health Checks

```bash
# MCP Server
curl http://localhost:8000/health

# Streamlit UI
curl http://localhost:8501/_stcore/health
```

### Monitoring Tools

Recommended:
- **Prometheus** + **Grafana** for metrics
- **ELK Stack** for log aggregation
- **Sentry** for error tracking

---

## 🔒 Security Best Practices

1. **Never commit .env files** to version control
2. **Use secrets management** (AWS Secrets Manager, Azure Key Vault)
3. **Enable HTTPS** with SSL certificates
4. **Implement rate limiting** on API endpoints
5. **Regular security updates** for dependencies
6. **Use firewall rules** to restrict access
7. **Enable CORS** appropriately
8. **Sanitize user inputs**

---

## 🔄 Updates & Maintenance

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart services
sudo systemctl restart financial-edu-mcp
sudo systemctl restart financial-edu-ui
```

### Backup Strategy

```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Backup database (if using)
# mysqldump or pg_dump commands here
```

---

## 🆘 Troubleshooting

### Common Issues

**Services won't start**
```bash
# Check logs
sudo journalctl -u financial-edu-mcp -n 50
sudo journalctl -u financial-edu-ui -n 50
```

**Port conflicts**
```bash
# Check what's using the port
sudo lsof -i :8501
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

**Permission issues**
```bash
# Fix ownership
sudo chown -R www-data:www-data /path/to/app

# Fix permissions
chmod +x start.sh setup.sh
```

---

## 📞 Support

For deployment issues:
1. Check logs first
2. Review this guide
3. Consult documentation in `/docs`
4. Open an issue on GitHub

---

**Happy Deploying! 🚀**
