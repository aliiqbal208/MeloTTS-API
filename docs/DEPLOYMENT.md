# Deployment Guide

This guide covers various deployment options for the MeloTTS API.

## Docker Deployment

### Single Container

1. **Build the image:**
   ```bash
   docker build -t melotts-api .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8080:8080 melotts-api
   ```

3. **With environment variables:**
   ```bash
   docker run -p 8080:8080 \
     -e DEVICE=cuda \
     -e MAX_WORKERS=8 \
     -e CORS_ORIGINS="https://yourdomain.com" \
     melotts-api
   ```

### Docker Compose

1. **Start services:**
   ```bash
   docker-compose up -d
   ```

2. **With reverse proxy:**
   ```bash
   docker-compose --profile proxy up -d
   ```

3. **Stop services:**
   ```bash
   docker-compose down
   ```

## Cloud Deployment

### Google Cloud Run

1. **Build and push to Google Container Registry:**
   ```bash
   # Build
   docker build -t gcr.io/PROJECT_ID/melotts-api .
   
   # Push
   docker push gcr.io/PROJECT_ID/melotts-api
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy melotts-api \
     --image gcr.io/PROJECT_ID/melotts-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 4Gi \
     --cpu 2 \
     --timeout 300
   ```

### AWS ECS/Fargate

1. **Create ECS task definition:**
   ```json
   {
     "family": "melotts-api",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "2048",
     "memory": "4096",
     "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "melotts-api",
         "image": "your-account.dkr.ecr.region.amazonaws.com/melotts-api:latest",
         "portMappings": [
           {
             "containerPort": 8080,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "PORT",
             "value": "8080"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/melotts-api",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

2. **Deploy using AWS CLI:**
   ```bash
   aws ecs register-task-definition --cli-input-json file://task-definition.json
   aws ecs create-service --cluster your-cluster --service-name melotts-api --task-definition melotts-api
   ```

### Azure Container Instances

1. **Deploy using Azure CLI:**
   ```bash
   az container create \
     --resource-group myResourceGroup \
     --name melotts-api \
     --image your-registry.azurecr.io/melotts-api:latest \
     --cpu 2 \
     --memory 4 \
     --ports 8080 \
     --environment-variables PORT=8080
   ```

## Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: melotts-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: melotts-api
  template:
    metadata:
      labels:
        app: melotts-api
    spec:
      containers:
      - name: melotts-api
        image: melotts-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: PORT
          value: "8080"
        - name: DEVICE
          value: "cpu"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: melotts-api-service
spec:
  selector:
    app: melotts-api
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

### Deploy to Kubernetes

```bash
kubectl apply -f deployment.yaml
kubectl get services
```

## Production Considerations

### Performance Optimization

1. **GPU Support:**
   ```bash
   # For CUDA
   docker run --gpus all -p 8080:8080 melotts-api
   
   # For MPS (Apple Silicon)
   docker run -p 8080:8080 -e DEVICE=mps melotts-api
   ```

2. **Resource Limits:**
   - Minimum: 2GB RAM, 1 CPU
   - Recommended: 4GB RAM, 2 CPU
   - GPU: 8GB VRAM for CUDA

3. **Scaling:**
   - Use load balancers for multiple instances
   - Consider Redis for model caching
   - Implement health checks

### Security

1. **HTTPS:**
   ```bash
   # With nginx reverse proxy
   docker run -p 443:443 \
     -v /path/to/ssl:/etc/nginx/ssl \
     nginx:alpine
   ```

2. **Authentication:**
   - Add API key authentication
   - Implement rate limiting
   - Use proper CORS configuration

3. **Network Security:**
   - Use private networks
   - Implement firewall rules
   - Monitor access logs

### Monitoring

1. **Health Checks:**
   ```bash
   # Basic health check
   curl http://localhost:8080/health
   
   # Detailed health check
   curl http://localhost:8080/health | jq
   ```

2. **Logging:**
   ```bash
   # View logs
   docker logs melotts-api-container
   
   # Follow logs
   docker logs -f melotts-api-container
   ```

3. **Metrics:**
   - Add Prometheus metrics
   - Monitor CPU/Memory usage
   - Track request latency

### Environment Variables

| Variable | Production Value | Description |
|----------|------------------|-------------|
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8080 | Server port |
| `DEVICE` | cuda | Use GPU if available |
| `MAX_WORKERS` | 8 | Increase for production |
| `CORS_ORIGINS` | https://yourdomain.com | Restrict CORS |
| `LOG_LEVEL` | WARNING | Reduce log verbosity |
| `MAX_TEXT_LENGTH` | 1000 | Limit text length |

### Backup and Recovery

1. **Model Backup:**
   ```bash
   # Backup models
   docker cp melotts-api-container:/app/models ./backup-models
   
   # Restore models
   docker cp ./backup-models melotts-api-container:/app/models
   ```

2. **Configuration Backup:**
   ```bash
   # Backup configuration
   docker cp melotts-api-container:/app/config.py ./backup-config.py
   ```

## Troubleshooting

### Common Issues

1. **Model Loading Fails:**
   - Check available memory
   - Verify CUDA installation
   - Check model download

2. **High Memory Usage:**
   - Reduce MAX_WORKERS
   - Use CPU instead of GPU
   - Implement model caching

3. **Slow Response:**
   - Enable GPU acceleration
   - Increase worker threads
   - Optimize text length

### Debug Mode

```bash
# Run with debug logging
docker run -p 8080:8080 -e LOG_LEVEL=DEBUG melotts-api

# Check container logs
docker logs melotts-api-container

# Access container shell
docker exec -it melotts-api-container /bin/bash
```

### Performance Testing

```bash
# Run performance tests
python scripts/test_api.py

# Load testing with Apache Bench
ab -n 100 -c 10 -H "Content-Type: application/json" \
   -p test_payload.json http://localhost:8080/synthesize
```

## Maintenance

### Updates

1. **Update API:**
   ```bash
   # Pull latest changes
   git pull origin main
   
   # Rebuild and restart
   docker-compose down
   docker-compose up -d --build
   ```

2. **Update Models:**
   ```bash
   # Clear model cache
   rm -rf models/
   
   # Restart to download latest models
   docker-compose restart
   ```

### Monitoring Commands

```bash
# Check service status
docker-compose ps

# View resource usage
docker stats

# Check logs
docker-compose logs -f

# Health check
curl http://localhost:8080/health
```
