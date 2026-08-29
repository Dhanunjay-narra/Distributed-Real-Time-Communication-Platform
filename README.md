# Chatbot — Distributed Real-Time Communication Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/Dhanunjay-narra/Distributed-Real-Time-Communication-Platform)
[![Compliance](https://img.shields.io/badge/compliance-100%25-blue.svg)](https://github.com/Dhanunjay-narra/Distributed-Real-Time-Communication-Platform)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.4+-blue.svg)](https://www.typescriptlang.org/)

**Chatbot** is an enterprise-grade distributed real-time messaging, social graph, and audio/video calling communication platform architected across 23 Bounded Contexts and 17 milestone phases. The platform delivers monotonic sequence ordering, multi-device synchronization with Vector Clocks, ephemeral Redis presence mesh, Kafka partitioned event backbone, distributed Sagas, WebRTC signaling mesh, Redlock distributed locking, and Raft consensus.

---

## 1. Architectural Overview & Bounded Contexts

```
                      +---------------------------------------+
                      |         Unified API Gateway           |
                      |  - JWT Validation & Claim Injection   |
                      |  - Sliding-Window Rate Limiting       |
                      |  - Distributed Tracing (Correlation)  |
                      +---------------------------------------+
                                          |
        +---------------------------------+---------------------------------+
        |                                 |                                 |
+---------------+                 +---------------+                 +---------------+
| Auth & Device |                 | Messaging &   |                 | WebSocket &   |
|   Service     |                 | Conversations |                 | Presence Mesh |
+---------------+                 +---------------+                 +---------------+
        |                                 |                                 |
+---------------+                 +---------------+                 +---------------+
| Groups & RBAC |                 | Sync Engine   |                 | Media & S3    |
|   Service     |                 | (Vector Clock)|                 | Pipeline      |
+---------------+                 +---------------+                 +---------------+
        |                                 |                                 |
+---------------+                 +---------------+                 +---------------+
| WebRTC Calls  |                 | Notifications |                 | Moderation &  |
| Signaling Mesh|                 | & Search      |                 | Admin Portal  |
+---------------+                 +---------------+                 +---------------+
        |                                 |                                 |
        +---------------------------------+---------------------------------+
                                          |
                      +---------------------------------------+
                      |     Distributed Event Backbone        |
                      |  - Kafka Partitioned Stream Topics    |
                      |  - Saga Orchestrator & Compensations  |
                      |  - Raft Consensus & Redlock Leases    |
                      +---------------------------------------+
```

---

## 2. Dependencies

### System Prerequisites
- **Python**: Version 3.11 or higher
- **Node.js**: Version 18 or 20 LTS
- **Docker & Docker Compose**: Version 24+
- **PostgreSQL**: Version 15+ (Primary Read/Write + Read Replicas)
- **Redis Cluster**: Version 7+
- **Apache Kafka & Zookeeper**: Version 3.5+
- **MinIO / Amazon S3**: S3-compatible object storage
- **OpenSearch**: Version 2.10+

### Key Python Dependencies
- `fastapi`, `uvicorn`, `pydantic-settings`, `sqlalchemy`, `asyncpg`, `aiosqlite`, `redis`, `aiokafka`, `python-jose`, `bcrypt`, `websockets`, `httpx`, `pytest`, `pytest-asyncio`.

---

## 3. Installation

### 3.1 Clone the Repository
```bash
git clone https://github.com/Dhanunjay-narra/Distributed-Real-Time-Communication-Platform.git
cd Distributed-Real-Time-Communication-Platform
```

### 3.2 Setup Python Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install all locked dependencies
pip install -r requirements.txt
```

### 3.3 Setup Frontend Client Applications
```bash
# Install root workspaces dependencies
npm install

# Install Web client dependencies
cd apps/web && npm install && cd ../..

# Install Admin dashboard dependencies
cd apps/admin && npm install && cd ../..
```

---

## 4. Build

### 4.1 Build Docker Containers
```bash
# Build all microservices container images
docker-compose build
```

### 4.2 Build Frontend Production Bundles
```bash
# Build Web Client (TypeScript + Vite)
npm run build --workspace=apps/web

# Build Admin Dashboard
npm run build --workspace=apps/admin
```

---

## 5. Run

### 5.1 Start Infrastructure Services (PostgreSQL, Redis, Kafka, MinIO, OpenSearch)
```bash
docker-compose up -d postgres redis kafka zookeeper minio opensearch
```

### 5.2 Start API Gateway & Backend Services
```bash
# Start API Gateway on port 8000
python -m uvicorn services.api_gateway.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5.3 Start WebSocket Gateway Cluster
```bash
# Start Real-Time WebSocket Gateway on port 8001
python -m uvicorn services.websocket.router:app --host 0.0.0.0 --port 8001 --reload
```

### 5.4 Start Frontend React Web Application
```bash
# Start Web Client on http://localhost:5173
npm run dev --workspace=apps/web
```

---

## 6. Usage & Testing

### Running the Test Suite
```bash
# Run all unit tests and end-to-end integration flows
pytest tests/ -v

# Run with test coverage report
pytest tests/ --cov=packages --cov=services -v
```

---

## 7. Deployment (Kubernetes, Helm & Terraform)

### Kubernetes Manifests
```bash
kubectl apply -f deploy/k8s/namespace.yaml
kubectl apply -f deploy/k8s/deployments.yaml
kubectl apply -f deploy/k8s/ingress.yaml
kubectl apply -f deploy/k8s/hpa.yaml
```

### Helm Chart
```bash
helm install chatbot-platform ./deploy/helm -n chatbot
```

### Terraform Cloud Provisioning
```bash
cd deploy/terraform
terraform init
terraform plan
terraform apply
```

---

## 8. License & Intellectual Property
Proprietary and Confidential. Copyright (c) 2026 Chatbot Communication Platform Inc. All rights reserved.
