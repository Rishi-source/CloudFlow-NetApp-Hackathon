# CLAUDE.md - AI Assistant Guide for CloudFlow

**Last Updated:** 2025-11-23
**Repository:** https://github.com/Rishi-source/CloudFlow-NetApp-Hackathon
**Live Demo:** https://cloudflow.rishigarg.dev

---

## Purpose of This Document

This guide helps AI assistants (like Claude) understand the CloudFlow codebase structure, development workflows, and conventions. Use this as your reference when helping with development, debugging, or feature implementation.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Codebase Structure](#codebase-structure)
3. [Technology Stack](#technology-stack)
4. [Development Workflow](#development-workflow)
5. [Git Conventions](#git-conventions)
6. [Code Conventions](#code-conventions)
7. [Testing Strategy](#testing-strategy)
8. [Common Tasks](#common-tasks)
9. [Important Patterns](#important-patterns)
10. [What to Avoid](#what-to-avoid)
11. [Deployment](#deployment)
12. [Troubleshooting](#troubleshooting)

---

## Project Overview

### What is CloudFlow?

CloudFlow is an **AI-powered cloud storage optimization platform** built for the NetApp Data in Motion Hackathon 2025. It uses machine learning to analyze file access patterns and recommend cost-saving migrations across multi-cloud environments (AWS, Azure, GCP).

### Key Features

- **AI-Powered Classification:** Automatically categorizes files as Hot/Warm/Cold based on access patterns
- **ML Cost Optimization:** Machine learning suggests moves that save 30-40% on storage costs
- **Multi-Cloud Support:** AWS, Azure, GCP with one-click migrations
- **Real-Time Updates:** Apache Kafka event streaming + WebSocket live updates
- **Production-Ready:** Retry logic, encryption, RBAC, monitoring, disaster recovery

### Architecture Style

**3-Tier Microservices Architecture:**
- **Frontend:** React 18 SPA with Material-UI
- **Backend:** Python FastAPI with async/await patterns
- **Data Layer:** MongoDB (metadata) + Apache Kafka (event streaming)

### Project Statistics

- **85+ source files** (Python + JavaScript/JSX)
- **~1,474 lines** of backend Python code
- **8 REST API route modules**
- **13 React components**
- **7 data models** (Pydantic)
- **3 ML models** (classification, prediction, anomaly detection)

---

## Codebase Structure

### High-Level Directory Layout

```
CloudFlow-NetApp-Hackathon/
├── backend/              # Python FastAPI backend (main business logic)
│   ├── api/             # REST API endpoints and FastAPI app setup
│   ├── config/          # Application settings and database config
│   ├── engines/         # Classification engine (Hot/Warm/Cold)
│   ├── middleware/      # Auth middleware and rate limiting
│   ├── ml/              # Machine learning models and training
│   ├── models/          # Pydantic data models
│   ├── orchestration/   # Migration job orchestrator
│   ├── services/        # Business logic services
│   └── streaming/       # Kafka producers/consumers, WebSocket
├── frontend/            # React 18 frontend
│   ├── public/          # Static assets
│   └── src/
│       ├── components/  # React UI components
│       └── services/    # API client services
├── deployment/          # Kubernetes production configs
│   └── kubernetes/      # StatefulSets, Deployments, HPA, Ingress
├── docs/               # Documentation
│   ├── ARCHITECTURE.md  # Technical architecture deep-dive
│   ├── USER_GUIDE.md    # End-user tutorial
│   └── CloudFlow_Technical_Presentation.pdf
├── images/             # Screenshots for README
├── scripts/            # Utility scripts (sample data, access simulation)
├── tests/              # Test suite
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── docker-compose.yml  # Local development orchestration
├── run.sh             # One-command startup script
├── .env.example       # Environment variable template
└── README.md          # Main documentation
```

### Backend Deep Dive

#### `/backend/api/` - REST API Layer

- **main.py:** FastAPI application setup, CORS, middleware registration, WebSocket endpoints
- **routes/:** 8 modular route files
  - `auth.py` - User registration, login, JWT tokens
  - `credentials.py` - Cloud provider credential management
  - `data.py` - File metadata CRUD operations
  - `upload.py` - File upload handling
  - `migration.py` - Migration job management
  - `recommendations.py` - ML-based cost optimization suggestions
  - `analytics.py` - Cost analytics and insights
  - `metrics.py` - Performance metrics endpoints

#### `/backend/models/` - Data Models (Pydantic)

All models use Pydantic for type safety and validation:
- `user.py` - User accounts and authentication
- `data_object.py` - File metadata (name, size, tier, location, cost)
- `cloud_credential.py` - Encrypted cloud provider credentials
- `migration_job.py` - Migration task tracking
- `access_log.py` - File access tracking for ML training
- `policy.py` - Access policies and RBAC rules

#### `/backend/services/` - Business Logic

**Cloud Integration (`services/cloud/`):**
- `aws_handler.py` - AWS S3 operations with multipart upload support
- `azure_handler.py` - Azure Blob Storage integration
- `gcp_handler.py` - Google Cloud Storage integration
- `cloud_adapter.py` - Abstract base class for cloud providers
- `retry_manager.py` - Exponential backoff retry logic
- `transaction_logger.py` - Audit trail for all migrations
- `consistency_manager.py` - Data consistency verification
- `conflict_resolver.py` - Handles concurrent operation conflicts
- `region_selector.py` - Optimal cloud region selection

**Security (`services/security/`):**
- `auth_service.py` - Authentication business logic
- `encryption_service.py` - AES-256 encryption for credentials
- `rbac.py` - Role-based access control enforcement
- `policy_engine.py` - Policy evaluation engine

**Monitoring (`services/metrics/`):**
- `performance_tracker.py` - P50/P90/P95/P99 latency tracking, throughput monitoring

**Alerts (`services/alerts/`):**
- `alert_manager.py` - Alert generation and distribution
- `alert_rules.py` - Configurable alert rule engine
- `email_notifier.py` - SMTP email notifications

**Data Optimization:**
- `deduplication/hash_manager.py` - SHA-256 based file deduplication
- `compression/compressor.py` - Data compression before transfer
- `disaster_recovery/backup_manager.py` - Backup management

#### `/backend/ml/` - Machine Learning

- `prediction_engine.py` - Random Forest classifier for tier predictions
- `model_trainer.py` - ML model training pipeline
- `anomaly_detector.py` - Detects unusual access patterns

#### `/backend/streaming/` - Real-Time Communication

- `kafka_producer.py` - Publishes events to Kafka topics
- `kafka_consumer.py` - Consumes and processes Kafka events
- `websocket_manager.py` - Manages WebSocket connections for real-time frontend updates

#### `/backend/orchestration/` - Migration Management

- `migration_orchestrator.py` - Manages migration job queue, execution, retry logic, and state management

#### `/backend/engines/` - Classification

- `classification_engine.py` - Analyzes access patterns and classifies files as Hot/Warm/Cold

### Frontend Deep Dive

#### `/frontend/src/components/` - React Components

**Core Components:**
1. **Dashboard.js** (23KB) - Main control center
   - Summary cards (files, costs, latency, migrations)
   - ML recommendations display
   - Files table with pagination
   - Migration monitoring
   - Kafka event stream viewer
   - Sample data generation
   - Access pattern simulation

2. **Login.js** - User authentication UI
3. **Register.js** - User registration form
4. **CloudCredentials.js** - Multi-cloud credential management (AWS, Azure, GCP)
5. **FileUpload.js** - Drag-and-drop file upload interface
6. **MigrationMonitor.js** - Real-time migration tracking with progress bars
7. **PerformanceMetrics.js** - P50/P90/P95/P99 latency charts
8. **MLInsights.js** - ML recommendations visualization
9. **DataDistribution.js** - Tier distribution pie charts
10. **CostAnalytics.js** - Cost breakdown by cloud provider
11. **AlertPanel.js** - Real-time alerts display
12. **StreamingViewer.js** - Kafka event stream viewer
13. **TourGuide.js** - 14-step interactive tour with 30+ tooltips (React-Joyride)

#### `/frontend/src/services/` - API Clients

- `auth.js` - Authentication service (login, register, JWT token management)
- `websocket.js` - WebSocket connection manager with auto-reconnect logic

#### `/frontend/src/` - Main App

- `App.js` - Root component with routing, theme provider, protected routes
- `index.js` - Application entry point

---

## Technology Stack

### Backend Stack

**Framework:**
- FastAPI 0.104.1 - Modern async API framework with automatic OpenAPI docs
- Uvicorn 0.24.0 - ASGI server for serving FastAPI
- Pydantic 2.5.0 - Data validation using Python type hints

**Machine Learning:**
- scikit-learn 1.3.2 - Random Forest classifier for tier prediction
- Prophet 1.1.5 - Time series forecasting for access patterns
- pandas 2.1.3 - Data manipulation
- numpy 1.26.2 - Numerical operations

**Cloud SDKs:**
- boto3 1.29.7 - AWS S3 integration
- azure-storage-blob 12.19.0 - Azure Blob Storage
- google-cloud-storage 2.10.0 - Google Cloud Storage

**Data Layer:**
- pymongo 4.6.0 - MongoDB async driver
- redis 5.0.1 - Caching layer
- kafka-python 2.0.2 - Apache Kafka event streaming

**Security:**
- cryptography 41.0.7 - AES-256 encryption
- PyJWT 2.8.0 - JWT token handling
- passlib 1.7.4 - Password hashing (bcrypt)

**Real-Time:**
- websockets 12.0 - WebSocket server
- python-socketio 5.10.0 - Socket.IO support

**Testing:**
- pytest 7.4.3 - Test framework
- pytest-asyncio 0.21.1 - Async test support
- httpx 0.25.2 - Async HTTP client for testing

### Frontend Stack

**Core:**
- React 18.2.0 - UI framework with hooks and context
- react-router-dom 6.20.0 - Client-side routing

**UI Library:**
- @mui/material 5.14.19 - Material Design component library
- @mui/icons-material 5.14.19 - Material Design icons
- @emotion/react, @emotion/styled - CSS-in-JS styling

**Features:**
- recharts 2.10.3 - Responsive charts and data visualizations
- react-joyride 2.9.3 - Interactive guided tour
- axios 1.6.2 - HTTP client for API calls

**Build Tools:**
- react-scripts 5.0.1 - Create React App build tooling

### Infrastructure

**Development:**
- Docker - Container runtime
- Docker Compose - Multi-container orchestration

**Production:**
- Kubernetes - Container orchestration
- MongoDB - NoSQL database
- Apache Kafka - Event streaming platform
- Nginx - Reverse proxy and static file serving

---

## Development Workflow

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/Rishi-source/CloudFlow-NetApp-Hackathon.git
cd CloudFlow-NetApp-Hackathon

# Start all services with one command
./run.sh
```

**What `run.sh` does:**
1. Creates `.env` from `.env.example` if not exists
2. Starts Docker Compose (MongoDB, Kafka, Backend, Frontend)
3. Waits for services to be healthy
4. Displays access URLs

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs (Swagger UI)
- MongoDB: localhost:27017
- Kafka: localhost:9092

### Environment Configuration

Copy `.env.example` to `.env` and configure:

**Required Variables:**
```bash
MONGODB_URL=mongodb://localhost:27017/cloudflow
JWT_SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
```

**Optional Cloud Credentials:**
```bash
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AZURE_STORAGE_ACCOUNT=your-azure-account
AZURE_STORAGE_KEY=your-azure-key
GCP_SERVICE_ACCOUNT_JSON=path/to/gcp-service-account.json
```

**Feature Flags:**
```bash
ENABLE_DEDUPLICATION=true
ENABLE_COMPRESSION=true
ENABLE_ANOMALY_DETECTION=true
ENABLE_EMAIL_NOTIFICATIONS=false  # Set to true with SMTP config
```

### Running Services Individually

**Backend only:**
```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend only:**
```bash
cd frontend
npm install
npm start
```

**MongoDB only:**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:6
```

**Kafka only:**
```bash
docker-compose up -d zookeeper kafka
```

### Development Tools

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Interactive API Testing:**
```bash
# Use the interactive Swagger UI at /docs
# Or use curl/httpx
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'
```

**Database Inspection:**
```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017/cloudflow

# List collections
show collections

# Query users
db.users.find().pretty()
```

**Kafka Monitoring:**
```bash
# List topics
docker exec -it kafka kafka-topics.sh --list --bootstrap-server localhost:9092

# Consume messages
docker exec -it kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic migration-events \
  --from-beginning
```

---

## Git Conventions

### Branch Naming

**Main Branches:**
- `main` - Production-ready code
- `develop` - Integration branch for features

**Feature Branches:**
- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/update-description` - Documentation updates
- `refactor/component-name` - Code refactoring
- `test/test-description` - Test additions

**Claude AI Branches:**
- `claude/claude-md-*` - Auto-generated branches for AI-assisted development

### Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, no logic change)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Build process, tooling, dependencies

**Examples:**
```bash
feat(ml): add anomaly detection for access patterns
fix(migration): handle network timeout with exponential backoff
docs(readme): update installation instructions
refactor(api): extract cloud handlers into separate modules
test(classification): add unit tests for tier assignment
```

### Commit Workflow

```bash
# Create feature branch
git checkout -b feature/new-ml-model

# Make changes
# ... edit files ...

# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat(ml): implement Prophet for time series forecasting"

# Push to remote
git push -u origin feature/new-ml-model

# Create pull request via GitHub
```

### Pull Request Guidelines

**Title Format:**
```
[Type] Brief description
```

**PR Description Template:**
```markdown
## Summary
Brief description of changes

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing Done
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] API documentation updated

## Deployment Notes
Any special deployment considerations
```

---

## Code Conventions

### Python (Backend)

**Style Guide:**
- Follow PEP 8
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use async/await for I/O operations

**Example:**
```python
from typing import List, Optional
from pydantic import BaseModel

async def get_files_by_tier(
    user_id: str,
    tier: str,
    limit: Optional[int] = 100
) -> List[DataObject]:
    """
    Retrieve files filtered by tier for a specific user.

    Args:
        user_id: User identifier
        tier: Storage tier (hot, warm, cold)
        limit: Maximum number of results

    Returns:
        List of data objects matching the tier
    """
    query = {"user_id": user_id, "tier": tier}
    cursor = db.data_objects.find(query).limit(limit)
    return [DataObject(**doc) async for doc in cursor]
```

**Naming Conventions:**
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

**File Organization:**
```python
# 1. Standard library imports
import os
from datetime import datetime
from typing import List, Optional

# 2. Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# 3. Local application imports
from models.data_object import DataObject
from services.auth import get_current_user
```

**Error Handling:**
```python
# Use specific exception types
from fastapi import HTTPException

async def get_file(file_id: str) -> DataObject:
    file = await db.data_objects.find_one({"_id": file_id})
    if not file:
        raise HTTPException(
            status_code=404,
            detail=f"File {file_id} not found"
        )
    return DataObject(**file)
```

### JavaScript/React (Frontend)

**Style Guide:**
- Use ES6+ features (arrow functions, destructuring, spread operator)
- Prefer functional components with hooks
- Use meaningful component and variable names
- Maximum line length: 100 characters

**Example:**
```javascript
import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography } from '@mui/material';

const FileCard = ({ file, onMigrate }) => {
  const [loading, setLoading] = useState(false);

  const handleMigrate = async () => {
    setLoading(true);
    try {
      await onMigrate(file.id);
    } catch (error) {
      console.error('Migration failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">{file.name}</Typography>
        <Typography color="textSecondary">{file.tier}</Typography>
      </CardContent>
    </Card>
  );
};

export default FileCard;
```

**Naming Conventions:**
- Components: `PascalCase`
- Functions/variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- CSS classes: `kebab-case`

**Component Organization:**
```javascript
// 1. Imports
import React, { useState, useEffect } from 'react';
import { Button } from '@mui/material';
import { fetchFiles } from '../services/auth';

// 2. Component definition
const Dashboard = () => {
  // 3. State declarations
  const [files, setFiles] = useState([]);

  // 4. Effects
  useEffect(() => {
    loadFiles();
  }, []);

  // 5. Event handlers
  const loadFiles = async () => {
    const data = await fetchFiles();
    setFiles(data);
  };

  // 6. Render
  return (
    <div>
      {/* JSX */}
    </div>
  );
};

// 7. Export
export default Dashboard;
```

**State Management:**
```javascript
// Use React Context for global state
import { createContext, useContext, useState } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

---

## Testing Strategy

### Backend Testing

**Test Structure:**
```
tests/
├── conftest.py          # Pytest fixtures
├── unit/                # Unit tests (isolated)
│   ├── test_classification.py
│   └── test_security.py
└── integration/         # Integration tests (with DB)
    ├── test_api_endpoints.py
    └── test_new_features.py
```

**Running Tests:**
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_classification.py

# Run specific test
pytest tests/unit/test_classification.py::test_hot_classification

# Run with verbose output
pytest -v
```

**Example Unit Test:**
```python
import pytest
from engines.classification_engine import ClassificationEngine

@pytest.fixture
def classification_engine():
    return ClassificationEngine()

def test_hot_tier_classification(classification_engine):
    """Test that frequently accessed files are classified as hot"""
    access_logs = [
        {"timestamp": "2024-01-01T10:00:00"},
        {"timestamp": "2024-01-01T14:00:00"},
        {"timestamp": "2024-01-02T09:00:00"},
        {"timestamp": "2024-01-02T15:00:00"},
    ]

    tier = classification_engine.classify(
        access_logs=access_logs,
        file_size=1024 * 1024  # 1 MB
    )

    assert tier == "hot"
```

**Example Integration Test:**
```python
import pytest
from httpx import AsyncClient
from api.main import app

@pytest.mark.asyncio
async def test_file_upload():
    """Test file upload endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/upload",
            files={"file": ("test.txt", b"test content", "text/plain")},
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
```

**Mock External Services:**
```python
from unittest.mock import Mock, patch

@patch('services.cloud.aws_handler.boto3.client')
def test_s3_upload(mock_boto3):
    """Test AWS S3 upload with mocked boto3"""
    mock_s3 = Mock()
    mock_boto3.return_value = mock_s3

    handler = AWSHandler()
    handler.upload_file("test.txt", b"content")

    mock_s3.put_object.assert_called_once()
```

### Frontend Testing

**Running Tests:**
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

**Example Component Test:**
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import FileCard from '../components/FileCard';

test('renders file name', () => {
  const file = { id: '1', name: 'test.txt', tier: 'hot' };
  render(<FileCard file={file} />);

  expect(screen.getByText('test.txt')).toBeInTheDocument();
});

test('calls onMigrate when button clicked', () => {
  const mockOnMigrate = jest.fn();
  const file = { id: '1', name: 'test.txt', tier: 'hot' };

  render(<FileCard file={file} onMigrate={mockOnMigrate} />);

  fireEvent.click(screen.getByText('Migrate'));
  expect(mockOnMigrate).toHaveBeenCalledWith('1');
});
```

### Testing Best Practices

1. **Test Coverage Goals:**
   - Unit tests: 80%+ coverage
   - Integration tests: Critical paths covered
   - E2E tests: Main user workflows

2. **What to Test:**
   - ✅ Business logic (classification, cost calculation)
   - ✅ API endpoints (request/response validation)
   - ✅ Error handling (network failures, invalid input)
   - ✅ Authentication/authorization
   - ❌ Third-party libraries
   - ❌ Trivial getters/setters

3. **Test Data:**
   - Use fixtures in `conftest.py` for reusable test data
   - Mock external services (AWS, Azure, GCP)
   - Use in-memory database for integration tests

4. **Async Testing:**
   - Use `pytest-asyncio` for async backend tests
   - Use `@testing-library/react` for async frontend tests

---

## Common Tasks

### Adding a New API Endpoint

1. **Create route in `/backend/api/routes/`:**
```python
# /backend/api/routes/analytics.py
from fastapi import APIRouter, Depends
from services.auth import get_current_user

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/cost-breakdown")
async def get_cost_breakdown(current_user = Depends(get_current_user)):
    """Get cost breakdown by cloud provider"""
    # Implementation
    return {"aws": 50.00, "azure": 30.00, "gcp": 20.00}
```

2. **Register route in `/backend/api/main.py`:**
```python
from api.routes import analytics

app.include_router(analytics.router)
```

3. **Test the endpoint:**
```bash
curl http://localhost:8000/api/v1/analytics/cost-breakdown \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Adding a New React Component

1. **Create component file:**
```javascript
// /frontend/src/components/CostBreakdown.js
import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

const CostBreakdown = ({ data }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Cost Breakdown</Typography>
        <BarChart width={500} height={300} data={data}>
          <XAxis dataKey="provider" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="cost" fill="#8884d8" />
        </BarChart>
      </CardContent>
    </Card>
  );
};

export default CostBreakdown;
```

2. **Import and use in Dashboard:**
```javascript
import CostBreakdown from './CostBreakdown';

// In Dashboard component
<CostBreakdown data={costData} />
```

### Adding a Pydantic Model

1. **Create model file:**
```python
# /backend/models/alert.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Alert(BaseModel):
    id: str = Field(..., description="Unique alert identifier")
    user_id: str
    severity: str  # info, warning, error
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read: bool = False
    metadata: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "alert123",
                "user_id": "user456",
                "severity": "warning",
                "message": "High latency detected",
                "created_at": "2024-01-01T10:00:00",
                "read": False
            }
        }
```

2. **Use in API routes:**
```python
from models.alert import Alert

@router.post("/alerts", response_model=Alert)
async def create_alert(alert: Alert):
    # Save to database
    return alert
```

### Adding a Kafka Event

1. **Define event in producer:**
```python
# /backend/streaming/kafka_producer.py
async def send_cost_alert(user_id: str, cost: float):
    event = {
        "type": "cost_alert",
        "user_id": user_id,
        "cost": cost,
        "timestamp": datetime.utcnow().isoformat()
    }
    producer.send("cost-alerts", value=event)
```

2. **Consume event:**
```python
# /backend/streaming/kafka_consumer.py
def handle_cost_alert(message):
    data = message.value
    # Send email notification
    email_service.send_alert(data["user_id"], data["cost"])
```

3. **Subscribe in frontend:**
```javascript
// WebSocket receives Kafka events
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'cost_alert') {
    showNotification(`Cost alert: $${data.cost}`);
  }
};
```

### Adding an ML Feature

1. **Create feature in `/backend/ml/`:**
```python
# /backend/ml/cost_predictor.py
from sklearn.linear_model import LinearRegression
import numpy as np

class CostPredictor:
    def __init__(self):
        self.model = LinearRegression()

    def train(self, historical_data):
        X = np.array([d["features"] for d in historical_data])
        y = np.array([d["cost"] for d in historical_data])
        self.model.fit(X, y)

    def predict(self, features):
        return self.model.predict([features])[0]
```

2. **Use in recommendations:**
```python
from ml.cost_predictor import CostPredictor

predictor = CostPredictor()
predicted_cost = predictor.predict(file_features)
```

### Running Database Migrations

CloudFlow uses MongoDB (schemaless), so migrations are typically handled in application code. For structural changes:

1. **Create migration script:**
```python
# /scripts/migrate_add_tier_field.py
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.cloudflow

# Add tier field to existing documents
db.data_objects.update_many(
    {"tier": {"$exists": False}},
    {"$set": {"tier": "warm"}}
)
```

2. **Run migration:**
```bash
python scripts/migrate_add_tier_field.py
```

---

## Important Patterns

### Async/Await Pattern (Backend)

**Always use async for I/O operations:**
```python
# ✅ GOOD
async def get_file_metadata(file_id: str) -> dict:
    result = await db.data_objects.find_one({"_id": file_id})
    return result

# ❌ BAD
def get_file_metadata(file_id: str) -> dict:
    result = db.data_objects.find_one({"_id": file_id})  # Blocks event loop
    return result
```

### Dependency Injection (FastAPI)

**Use FastAPI's dependency system:**
```python
from fastapi import Depends
from services.auth import get_current_user

@router.get("/files")
async def list_files(current_user = Depends(get_current_user)):
    # current_user is automatically injected and validated
    return await get_user_files(current_user.id)
```

### Error Handling Pattern

**Backend (FastAPI):**
```python
from fastapi import HTTPException

async def get_file(file_id: str):
    try:
        file = await db.data_objects.find_one({"_id": file_id})
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        return file
    except Exception as e:
        logger.error(f"Error retrieving file {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Frontend (React):**
```javascript
const [error, setError] = useState(null);

const loadFiles = async () => {
  try {
    const response = await fetch('/api/v1/files');
    if (!response.ok) {
      throw new Error('Failed to load files');
    }
    const data = await response.json();
    setFiles(data);
    setError(null);
  } catch (err) {
    setError(err.message);
    console.error('Error loading files:', err);
  }
};
```

### Retry Pattern

**Use exponential backoff for cloud operations:**
```python
from services.cloud.retry_manager import RetryManager

retry_manager = RetryManager(
    max_retries=3,
    base_delay=2,  # seconds
    max_delay=30
)

async def upload_with_retry(file_path: str, content: bytes):
    return await retry_manager.execute(
        lambda: cloud_handler.upload(file_path, content)
    )
```

### Event-Driven Pattern

**Emit events for important actions:**
```python
from streaming.kafka_producer import KafkaProducerService

async def create_migration_job(source, destination):
    job = MigrationJob(source=source, destination=destination)
    await db.migration_jobs.insert_one(job.dict())

    # Emit event
    await kafka_producer.send_event(
        topic="migration-events",
        event_type="migration_started",
        data=job.dict()
    )

    return job
```

### React Hooks Pattern

**Extract reusable logic into custom hooks:**
```javascript
// Custom hook for data fetching
const useFiles = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const response = await fetch('/api/v1/files');
        const data = await response.json();
        setFiles(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchFiles();
  }, []);

  return { files, loading, error };
};

// Usage in component
const Dashboard = () => {
  const { files, loading, error } = useFiles();

  if (loading) return <Loading />;
  if (error) return <Error message={error} />;
  return <FileList files={files} />;
};
```

---

## What to Avoid

### Backend Anti-Patterns

**❌ DON'T block the event loop:**
```python
# BAD - synchronous I/O
def get_file():
    time.sleep(5)  # Blocks all requests
    return data
```

**✅ DO use async:**
```python
# GOOD - non-blocking
async def get_file():
    await asyncio.sleep(5)  # Other requests can process
    return data
```

**❌ DON'T hardcode credentials:**
```python
# BAD
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
```

**✅ DO use environment variables:**
```python
# GOOD
from config.settings import settings
aws_key = settings.AWS_ACCESS_KEY_ID
```

**❌ DON'T expose sensitive data in logs:**
```python
# BAD
logger.info(f"User credentials: {password}")
```

**✅ DO sanitize logs:**
```python
# GOOD
logger.info(f"User authenticated: {user_id}")
```

**❌ DON'T ignore error handling:**
```python
# BAD
result = await db.find_one({"_id": id})
return result["name"]  # Can raise KeyError
```

**✅ DO handle errors:**
```python
# GOOD
result = await db.find_one({"_id": id})
if not result:
    raise HTTPException(status_code=404, detail="Not found")
return result.get("name", "Unknown")
```

### Frontend Anti-Patterns

**❌ DON'T mutate state directly:**
```javascript
// BAD
const [files, setFiles] = useState([]);
files.push(newFile);  // Direct mutation
```

**✅ DO create new arrays/objects:**
```javascript
// GOOD
const [files, setFiles] = useState([]);
setFiles([...files, newFile]);
```

**❌ DON'T forget to cleanup effects:**
```javascript
// BAD - WebSocket never closes
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/ws');
  ws.onmessage = handleMessage;
}, []);
```

**✅ DO cleanup in effect return:**
```javascript
// GOOD
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/ws');
  ws.onmessage = handleMessage;
  return () => ws.close();  // Cleanup
}, []);
```

**❌ DON'T perform side effects in render:**
```javascript
// BAD
const Component = () => {
  fetchData();  // Called on every render
  return <div>...</div>;
};
```

**✅ DO use useEffect:**
```javascript
// GOOD
const Component = () => {
  useEffect(() => {
    fetchData();  // Called once on mount
  }, []);
  return <div>...</div>;
};
```

### Security Anti-Patterns

**❌ DON'T trust user input:**
```python
# BAD - SQL injection vulnerable
query = f"SELECT * FROM users WHERE name = '{user_input}'"
```

**✅ DO validate and sanitize:**
```python
# GOOD - Pydantic validation
class UserInput(BaseModel):
    name: str = Field(..., max_length=100, pattern="^[a-zA-Z0-9_]+$")
```

**❌ DON'T store passwords in plaintext:**
```python
# BAD
user.password = password
```

**✅ DO hash passwords:**
```python
# GOOD
from passlib.hash import bcrypt
user.password_hash = bcrypt.hash(password)
```

---

## Deployment

### Local Development (Docker Compose)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Production (Kubernetes)

**Deploy to Kubernetes:**
```bash
# Apply all configs
kubectl apply -f deployment/kubernetes/

# Check deployment status
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/backend

# Scale backend
kubectl scale deployment backend --replicas=5
```

**Kubernetes Resources:**
- `backend-deployment.yaml` - Backend service (3 replicas, auto-scaling)
- `frontend-deployment.yaml` - Frontend service (2 replicas)
- `mongodb-statefulset.yaml` - MongoDB cluster (3 replicas)
- `kafka-statefulset.yaml` - Kafka cluster (3 brokers)
- `hpa.yaml` - Horizontal Pod Autoscaler
- `ingress.yaml` - External traffic routing

**Monitoring Deployment:**
```bash
# Check pod health
kubectl get pods -w

# Check resource usage
kubectl top pods

# View events
kubectl get events --sort-by='.lastTimestamp'
```

### Environment-Specific Configs

**Development (.env):**
```bash
DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_SWAGGER=true
```

**Production (.env):**
```bash
DEBUG=false
LOG_LEVEL=INFO
ENABLE_SWAGGER=false
MONGODB_URL=mongodb+srv://prod-cluster.mongodb.net/cloudflow
```

---

## Troubleshooting

### Backend Issues

**Issue: "Module not found" error**
```bash
# Solution: Install dependencies
cd backend
pip install -r requirements.txt
```

**Issue: "MongoDB connection refused"**
```bash
# Solution: Ensure MongoDB is running
docker-compose up -d mongodb

# Check MongoDB logs
docker-compose logs mongodb
```

**Issue: "Kafka connection timeout"**
```bash
# Solution: Start Kafka
docker-compose up -d zookeeper kafka

# Wait for Kafka to be ready (30 seconds)
sleep 30
```

**Issue: "Import error: circular dependency"**
```python
# Solution: Use late imports or restructure
# Instead of top-level import:
from services.auth import authenticate

# Use function-level import:
def login():
    from services.auth import authenticate
    return authenticate()
```

### Frontend Issues

**Issue: "CORS error" when calling API**
```javascript
// Solution: Ensure backend has CORS configured
// In backend/api/main.py:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Issue: "WebSocket connection failed"**
```bash
# Solution: Check backend WebSocket endpoint
# Ensure backend is running on port 8000
curl http://localhost:8000/health
```

**Issue: "Module not found" in React**
```bash
# Solution: Install dependencies
cd frontend
npm install

# Clear cache if persists
rm -rf node_modules package-lock.json
npm install
```

### Testing Issues

**Issue: "Async test timeout"**
```python
# Solution: Increase timeout or use pytest-asyncio
@pytest.mark.asyncio
async def test_long_operation():
    # Set timeout
    result = await asyncio.wait_for(
        long_operation(),
        timeout=30.0
    )
```

**Issue: "Database not cleaned between tests"**
```python
# Solution: Add teardown fixture
@pytest.fixture(autouse=True)
async def cleanup():
    yield
    # Clean up after each test
    await db.data_objects.delete_many({})
```

### Performance Issues

**Issue: "High API latency"**
```python
# Diagnose with timing
import time
start = time.time()
result = await expensive_operation()
print(f"Operation took {time.time() - start}s")

# Solutions:
# 1. Add database indexes
db.data_objects.create_index("user_id")

# 2. Use caching
from functools import lru_cache

@lru_cache(maxsize=128)
def get_expensive_data(key):
    return expensive_operation(key)

# 3. Batch operations
await db.data_objects.insert_many(documents)  # Not insert_one in loop
```

**Issue: "Frontend slow rendering"**
```javascript
// Solution: Use React.memo for expensive components
const FileList = React.memo(({ files }) => {
  return files.map(file => <FileCard key={file.id} file={file} />);
});

// Use useMemo for expensive calculations
const sortedFiles = useMemo(
  () => files.sort((a, b) => a.name.localeCompare(b.name)),
  [files]
);
```

### Common Error Messages

**"JWT token expired"**
```bash
# Solution: Re-authenticate
# Token expires after 24 hours (configurable in settings)
```

**"Migration failed: Access denied"**
```bash
# Solution: Check cloud credentials
# Ensure IAM permissions are correct (S3 read/write, Blob access, etc.)
```

**"Kafka consumer lag high"**
```bash
# Solution: Scale consumers
# Add more consumer instances in separate processes
```

---

## Quick Reference

### Essential Files to Know

| File | Purpose |
|------|---------|
| `/backend/api/main.py` | FastAPI app setup, CORS, WebSocket |
| `/backend/api/routes/` | All API endpoints |
| `/backend/models/` | Pydantic data models |
| `/backend/ml/prediction_engine.py` | ML recommendations |
| `/backend/orchestration/migration_orchestrator.py` | Migration job management |
| `/frontend/src/App.js` | React app root, routing |
| `/frontend/src/components/Dashboard.js` | Main UI component |
| `/frontend/src/services/auth.js` | Authentication service |
| `docker-compose.yml` | Local development setup |
| `.env.example` | Environment variable template |

### Key Commands

```bash
# Start everything
./run.sh

# Run backend tests
cd backend && pytest

# Run frontend tests
cd frontend && npm test

# View API docs
open http://localhost:8000/docs

# Check logs
docker-compose logs -f backend

# Rebuild after changes
docker-compose up -d --build

# Deploy to Kubernetes
kubectl apply -f deployment/kubernetes/
```

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/auth/register` | POST | User registration |
| `/api/v1/auth/login` | POST | User login |
| `/api/v1/upload` | POST | Upload file |
| `/api/v1/data` | GET | List files |
| `/api/v1/migration` | POST | Create migration job |
| `/api/v1/recommendations` | GET | Get ML recommendations |
| `/api/v1/metrics` | GET | Performance metrics |
| `/ws` | WebSocket | Real-time updates |
| `/docs` | GET | Interactive API docs |

### Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `MONGODB_URL` | Yes | MongoDB connection string |
| `JWT_SECRET_KEY` | Yes | JWT signing key |
| `ENCRYPTION_KEY` | Yes | AES-256 encryption key |
| `AWS_ACCESS_KEY_ID` | No | AWS credentials |
| `AZURE_STORAGE_KEY` | No | Azure credentials |
| `GCP_SERVICE_ACCOUNT_JSON` | No | GCP credentials |
| `SMTP_HOST` | No | Email server |
| `KAFKA_BOOTSTRAP_SERVERS` | Yes | Kafka connection |

---

## Additional Resources

### Documentation
- [README.md](README.md) - Project overview and quick start
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical architecture deep-dive
- [USER_GUIDE.md](docs/USER_GUIDE.md) - End-user tutorial
- [CloudFlow_Technical_Presentation.pdf](docs/CloudFlow_Technical_Presentation.pdf) - Hackathon presentation

### External Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [MongoDB Manual](https://docs.mongodb.com/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Material-UI Documentation](https://mui.com/material-ui/)

### Learning Resources
- [Python Async Programming](https://docs.python.org/3/library/asyncio.html)
- [React Hooks Guide](https://react.dev/reference/react)
- [Pydantic Tutorial](https://docs.pydantic.dev/)
- [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)

---

## Support

**Issues & Questions:**
- GitHub Issues: https://github.com/Rishi-source/CloudFlow-NetApp-Hackathon/issues
- Documentation: Check `docs/` folder
- Interactive Tour: Click "?" button in dashboard

**For AI Assistants:**
- This document should be your primary reference
- When in doubt, check existing code patterns
- Follow the conventions outlined above
- Test changes thoroughly before committing
- Ask for clarification if requirements are unclear

---

**Last Updated:** 2025-11-23
**Version:** 1.0.0
**Maintained By:** CloudFlow Development Team

---

*This guide is living documentation. Update it as the codebase evolves.*
