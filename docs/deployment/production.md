# Production Deployment Guide

This guide covers deploying the 20 Newsgroups Search API to production environments with proper security, scalability, and monitoring.

---

## 🏗️ Production Architecture

### Recommended Architecture
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│    Load Balancer    │    │      API Layer      │    │    Data Layer       │
│   (nginx/ALB)       │────┤  (Multiple Apps)    │────┤   (Elasticsearch    │
│   - SSL Termination │    │  - Auto Scaling     │    │    Cluster)         │
│   - Rate Limiting   │    │  - Health Checks    │    │   - Replication     │
│   - CORS            │    │  - Logging          │    │   - Persistence     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     │
                    ┌─────────────────────────────────┐
                    │        Monitoring               │
                    │  - Metrics (Prometheus)        │
                    │  - Logs (ELK/Grafana)         │
                    │  - Alerts (PagerDuty)         │
                    │  - Health Dashboards           │
                    └─────────────────────────────────┘
```

---

## 🔒 Security Configuration

### 1. Elasticsearch Security

#### Enable Authentication
```yaml
# elasticsearch.yml
xpack.security.enabled: true
xpack.security.http.ssl.enabled: true
xpack.security.transport.ssl.enabled: true
xpack.security.http.ssl.key: certs/elasticsearch.key
xpack.security.http.ssl.certificate: certs/elasticsearch.crt
xpack.security.transport.ssl.key: certs/elasticsearch.key
xpack.security.transport.ssl.certificate: certs/elasticsearch.crt
```

#### Create Service User
```bash
# Create API user with limited permissions
curl -X POST "https://elasticsearch:9200/_security/user/newsgroups_api" \
  -H "Content-Type: application/json" \
  -u "elastic:${ELASTIC_PASSWORD}" \
  -d '{
    "password": "secure_api_password",
    "roles": ["newsgroups_api_role"],
    "full_name": "Newsgroups API Service Account"
  }'

# Create role with minimal required permissions
curl -X POST "https://elasticsearch:9200/_security/role/newsgroups_api_role" \
  -H "Content-Type: application/json" \
  -u "elastic:${ELASTIC_PASSWORD}" \
  -d '{
    "cluster": ["monitor"],
    "indices": [
      {
        "names": ["newsgroups"],
        "privileges": ["read", "write", "create", "index", "delete"]
      }
    ]
  }'
```

### 2. API Security

#### Environment Variables
```bash
# Never put these in code or config files!
export ELASTICSEARCH_USERNAME=newsgroups_api
export ELASTICSEARCH_PASSWORD=secure_api_password
export ELASTICSEARCH_CA_CERT=/etc/ssl/certs/elasticsearch-ca.pem
export ELASTICSEARCH_VERIFY_CERTS=true
export API_SECRET_KEY=$(openssl rand -hex 32)
```

#### Rate Limiting (nginx)
```nginx
# /etc/nginx/conf.d/ratelimit.conf
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=search:10m rate=20r/m;
    
    upstream newsgroups_api {
        server app1:8182 max_fails=3 fail_timeout=30s;
        server app2:8182 max_fails=3 fail_timeout=30s;
        server app3:8182 max_fails=3 fail_timeout=30s;
    }
    
    server {
        listen 443 ssl http2;
        server_name api.newsgroups.example.com;
        
        # SSL Configuration
        ssl_certificate /etc/ssl/certs/newsgroups.crt;
        ssl_certificate_key /etc/ssl/private/newsgroups.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        
        # Rate limiting
        location /search {
            limit_req zone=search burst=5 nodelay;
            proxy_pass http://newsgroups_api;
        }
        
        location / {
            limit_req zone=api burst=10 nodelay;
            proxy_pass http://newsgroups_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## 📦 Container Orchestration

### 1. Docker Swarm Deployment

#### docker-compose.prod.yml
```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:9.1.2
    environment:
      - cluster.name=newsgroups-prod
      - discovery.type=single-node
      - xpack.security.enabled=true
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
      - elasticsearch_certs:/usr/share/elasticsearch/config/certs
    networks:
      - newsgroups_network
    deploy:
      replicas: 1
      resources:
        limits:
          memory: 4g
        reservations:
          memory: 2g
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s

  newsgroups:
    image: newsgroups-api:${VERSION}
    environment:
      - ELASTICSEARCH_PROTOCOL=https
      - ELASTICSEARCH_HOST=elasticsearch
      - ELASTICSEARCH_PORT=9200
      - ELASTICSEARCH_USERNAME=${ELASTICSEARCH_USERNAME}
      - ELASTICSEARCH_PASSWORD=${ELASTICSEARCH_PASSWORD}
      - ELASTICSEARCH_VERIFY_CERTS=true
      - LOG_LEVEL=WARNING
      - ELASTICSEARCH_INDEX=newsgroups
    networks:
      - newsgroups_network
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 512m
        reservations:
          memory: 256m
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
        window: 120s
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8182/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
    networks:
      - newsgroups_network
    depends_on:
      - newsgroups
    deploy:
      replicas: 1
      restart_policy:
        condition: any

volumes:
  elasticsearch_data:
    driver: local
  elasticsearch_certs:
    driver: local

networks:
  newsgroups_network:
    driver: overlay
    encrypted: true
```

#### Deployment Commands
```bash
# Initialize swarm
docker swarm init

# Build and push image
docker build -t newsgroups-api:1.0.0 app/
docker tag newsgroups-api:1.0.0 registry.example.com/newsgroups-api:1.0.0
docker push registry.example.com/newsgroups-api:1.0.0

# Deploy stack
export VERSION=1.0.0
export ELASTIC_PASSWORD=$(openssl rand -base64 32)
export ELASTICSEARCH_USERNAME=newsgroups_api
export ELASTICSEARCH_PASSWORD=$(openssl rand -base64 32)

docker stack deploy -c docker-compose.prod.yml newsgroups
```

### 2. Kubernetes Deployment

#### namespace.yaml
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: newsgroups
  labels:
    name: newsgroups
```

#### secrets.yaml
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: newsgroups-secrets
  namespace: newsgroups
type: Opaque
stringData:
  elasticsearch-username: newsgroups_api
  elasticsearch-password: your-secure-password
  elasticsearch-ca-cert: |
    -----BEGIN CERTIFICATE-----
    [CA Certificate Content]
    -----END CERTIFICATE-----
```

#### elasticsearch-deployment.yaml
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: elasticsearch
  namespace: newsgroups
spec:
  serviceName: elasticsearch
  replicas: 3
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:9.1.2
        ports:
        - containerPort: 9200
        - containerPort: 9300
        env:
        - name: cluster.name
          value: "newsgroups-prod"
        - name: node.name
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: discovery.seed_hosts
          value: "elasticsearch-0.elasticsearch,elasticsearch-1.elasticsearch,elasticsearch-2.elasticsearch"
        - name: cluster.initial_master_nodes
          value: "elasticsearch-0,elasticsearch-1,elasticsearch-2"
        - name: ES_JAVA_OPTS
          value: "-Xms2g -Xmx2g"
        - name: xpack.security.enabled
          value: "true"
        - name: ELASTIC_PASSWORD
          valueFrom:
            secretKeyRef:
              name: newsgroups-secrets
              key: elasticsearch-password
        volumeMounts:
        - name: data
          mountPath: /usr/share/elasticsearch/data
        resources:
          limits:
            memory: 4Gi
            cpu: 2
          requests:
            memory: 2Gi
            cpu: 1
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
```

#### api-deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: newsgroups-api
  namespace: newsgroups
spec:
  replicas: 3
  selector:
    matchLabels:
      app: newsgroups-api
  template:
    metadata:
      labels:
        app: newsgroups-api
    spec:
      containers:
      - name: newsgroups-api
        image: registry.example.com/newsgroups-api:1.0.0
        ports:
        - containerPort: 8182
        env:
        - name: ELASTICSEARCH_PROTOCOL
          value: "https"
        - name: ELASTICSEARCH_HOST
          value: "elasticsearch"
        - name: ELASTICSEARCH_PORT
          value: "9200"
        - name: ELASTICSEARCH_USERNAME
          valueFrom:
            secretKeyRef:
              name: newsgroups-secrets
              key: elasticsearch-username
        - name: ELASTICSEARCH_PASSWORD
          valueFrom:
            secretKeyRef:
              name: newsgroups-secrets
              