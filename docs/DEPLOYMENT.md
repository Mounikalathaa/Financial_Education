# Deployment Guide

## Production Deployment Options

### Option 1: Streamlit Cloud (Recommended for Quick Deploy)

#### Prerequisites
- GitHub account
- Streamlit Cloud account (free at streamlit.io)
- OpenAI API key

#### Steps

1. **Push to GitHub**
```bash
cd financial_education
git init
git add .
git commit -m "Initial commit: Financial Education Quiz Engine"
git remote add origin https://github.com/yourusername/financial-education.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Click "New app"
- Select your repository
- Main file path: `app.py`
- Click "Deploy"

3. **Configure Secrets**
In Streamlit Cloud dashboard:
- Go to App settings → Secrets
- Add:
```toml
OPENAI_API_KEY = "sk-your-key-here"
MCP_SERVER_URL = "https://your-mcp-server.com"
```

4. **Deploy MCP Server Separately**
- Use Heroku, Railway, or similar for the FastAPI server
- Update MCP_SERVER_URL in secrets

---

### Option 2: Heroku

#### Prerequisites
- Heroku account
- Heroku CLI installed

#### MCP Server Deployment

1. **Create Procfile**
```bash
cd financial_education
cat > Procfile << EOF
web: uvicorn mcp_server:app --host=0.0.0.0 --port=\$PORT
EOF
```

2. **Create runtime.txt**
```bash
echo "python-3.11.0" > runtime.txt
```

3. **Deploy**
```bash
heroku create your-mcp-server
heroku config:set OPENAI_API_KEY=sk-your-key
git push heroku main
```

#### Streamlit App Deployment

1. **Separate Streamlit to its own Heroku app**
```bash
heroku create your-streamlit-app
heroku config:set OPENAI_API_KEY=sk-your-key
heroku config:set MCP_SERVER_URL=https://your-mcp-server.herokuapp.com
```

2. **Update Procfile for Streamlit**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

### Option 3: AWS (Production-Grade)

#### Architecture
```
CloudFront (CDN)
    ↓
Application Load Balancer
    ↓
    ├─→ ECS/Fargate (Streamlit containers)
    └─→ ECS/Fargate (MCP Server containers)
         ↓
    RDS PostgreSQL (User data)
         ↓
    S3 (Vector store backup)
```

#### Steps

1. **Containerize Applications**

**Dockerfile.streamlit**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Dockerfile.mcp**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "mcp_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Push to ECR**
```bash
aws ecr create-repository --repository-name financial-education-streamlit
aws ecr create-repository --repository-name financial-education-mcp

# Build and push
docker build -f Dockerfile.streamlit -t financial-education-streamlit .
docker tag financial-education-streamlit:latest [account-id].dkr.ecr.[region].amazonaws.com/financial-education-streamlit:latest
docker push [account-id].dkr.ecr.[region].amazonaws.com/financial-education-streamlit:latest
```

3. **Create ECS Services**
- Define task definitions for both containers
- Set up auto-scaling
- Configure load balancer
- Set environment variables

4. **Set up RDS**
```bash
aws rds create-db-instance \
    --db-instance-identifier financial-education-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username admin \
    --master-user-password [password]
```

5. **Configure CloudFront**
- Set up distribution
- Point to ALB
- Enable caching for static assets
- Configure SSL certificate

---

### Option 4: Google Cloud Platform

#### Using Cloud Run (Serverless)

1. **Enable APIs**
```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

2. **Build and Deploy MCP Server**
```bash
gcloud builds submit --tag gcr.io/[project-id]/mcp-server
gcloud run deploy mcp-server \
    --image gcr.io/[project-id]/mcp-server \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

3. **Build and Deploy Streamlit**
```bash
gcloud builds submit --tag gcr.io/[project-id]/streamlit-app
gcloud run deploy streamlit-app \
    --image gcr.io/[project-id]/streamlit-app \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars MCP_SERVER_URL=[mcp-url]
```

---

### Option 5: Docker Compose (Self-Hosted)

#### docker-compose.yml
```yaml
version: '3.8'

services:
  mcp-server:
    build:
      context: .
      dockerfile: Dockerfile.mcp
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: always

  streamlit:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MCP_SERVER_URL=http://mcp-server:8000
    depends_on:
      - mcp-server
    restart: always

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=financial_education
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

**Deploy**
```bash
docker-compose up -d
```

---

## Database Migration (For Production)

### Replace In-Memory Storage with PostgreSQL

1. **Install SQLAlchemy**
```bash
pip install sqlalchemy psycopg2-binary alembic
```

2. **Create Models** (database/models.py)
```python
from sqlalchemy import create_engine, Column, String, Integer, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    hobbies = Column(JSON)
    # ... other fields

class Transaction(Base):
    __tablename__ = 'transactions'
    transaction_id = Column(String, primary_key=True)
    user_id = Column(String)
    # ... other fields

# ... other models
```

3. **Update MCP Server** to use SQLAlchemy sessions instead of dicts

---

## Environment-Specific Configurations

### Development
```yaml
# config.dev.yaml
debug: true
llm:
  temperature: 0.9  # More creative
logging:
  level: DEBUG
```

### Staging
```yaml
# config.staging.yaml
debug: false
llm:
  temperature: 0.7
logging:
  level: INFO
```

### Production
```yaml
# config.prod.yaml
debug: false
llm:
  temperature: 0.7
  max_tokens: 1500  # Cost optimization
logging:
  level: WARNING
rate_limiting:
  enabled: true
  requests_per_minute: 60
```

---

## Monitoring & Observability

### Application Insights (Azure)

```python
from applicationinsights import TelemetryClient

tc = TelemetryClient(instrumentation_key='your-key')

# Track events
tc.track_event('quiz_generated', {
    'user_id': user_id,
    'concept': concept,
    'duration_ms': duration
})

# Track metrics
tc.track_metric('quiz_generation_time', duration)
```

### CloudWatch (AWS)

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

cloudwatch.put_metric_data(
    Namespace='FinancialEducation',
    MetricData=[
        {
            'MetricName': 'QuizGenerationTime',
            'Value': duration,
            'Unit': 'Milliseconds'
        }
    ]
)
```

---

## Performance Optimization

### 1. Caching

```python
from functools import lru_cache
import redis

# Redis cache
redis_client = redis.Redis(host='localhost', port=6379)

def cache_quiz_result(quiz_id, result):
    redis_client.setex(
        f"quiz:{quiz_id}",
        3600,  # 1 hour TTL
        json.dumps(result)
    )
```

### 2. Load Balancing

Use nginx or cloud load balancer:

```nginx
upstream streamlit_backend {
    server streamlit1:8501;
    server streamlit2:8501;
    server streamlit3:8501;
}

server {
    listen 80;
    location / {
        proxy_pass http://streamlit_backend;
    }
}
```

### 3. CDN for Static Assets

- Use CloudFront, Cloudflare, or Fastly
- Cache images, CSS, JS
- Reduce latency globally

---

## Security Checklist

- [ ] HTTPS enabled (SSL/TLS certificates)
- [ ] API keys in environment variables (never in code)
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (use ORMs)
- [ ] CORS configured properly
- [ ] Authentication/authorization (for production)
- [ ] Data encryption at rest and in transit
- [ ] Regular security audits
- [ ] Dependency vulnerability scanning

---

## Cost Optimization

### OpenAI API Costs

**Estimated costs per quiz:**
- Story generation: ~$0.02 (GPT-4 Turbo)
- Question generation: ~$0.01
- Embeddings: ~$0.0001
- **Total: ~$0.03 per quiz**

**For 1000 users taking 5 quizzes/month:**
- 1000 users × 5 quizzes = 5000 quizzes
- 5000 × $0.03 = **$150/month**

**Optimization strategies:**
1. Cache common queries
2. Use GPT-3.5 Turbo for simpler tasks
3. Batch API requests
4. Implement request throttling
5. Pre-generate common quiz variations

---

## Backup & Disaster Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh

# Database backup
pg_dump -U admin financial_education > backup_$(date +%Y%m%d).sql

# Vector store backup
tar -czf vector_store_$(date +%Y%m%d).tar.gz data/vector_store/

# Upload to S3
aws s3 cp backup_$(date +%Y%m%d).sql s3://backups/financial-education/
aws s3 cp vector_store_$(date +%Y%m%d).tar.gz s3://backups/financial-education/
```

**Schedule with cron:**
```cron
0 2 * * * /path/to/backup.sh
```

---

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          # Your deployment commands
```

---

## Support & Maintenance

### Health Checks

```python
# Add to MCP server
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### Monitoring Alerts

Set up alerts for:
- High error rates (> 5%)
- Slow response times (> 10s)
- API quota exhaustion
- Server downtime
- Database connection issues

---

## Scaling Roadmap

**Phase 1: MVP** (Current)
- Single server
- In-memory storage
- Local vector store

**Phase 2: Growth** (100-1000 users)
- Load balancer
- PostgreSQL database
- Redis caching
- Managed vector store

**Phase 3: Scale** (1000-10000 users)
- Multi-region deployment
- CDN for assets
- Horizontal scaling
- Advanced caching

**Phase 4: Enterprise** (10000+ users)
- Microservices architecture
- Event-driven design
- Real-time analytics
- A/B testing platform
