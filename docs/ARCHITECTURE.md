# CloudFlow Architecture

**How everything fits together**

---

## The Big Picture

Imagine CloudFlow as a three-layer cake:

**Top Layer (What You See):**
A React frontend where you manage your files, see metrics, and watch migrations happen in real-time.

**Middle Layer (The Brain):**
Python backend services that handle all the logic - classification, ML predictions, orchestrating migrations, tracking performance.

**Bottom Layer (The Data):**
MongoDB storing all your metadata, and Kafka streaming events everywhere in real-time.

These layers talk to each other constantly. Frontend polls the backend for updates, backend queries MongoDB for data, Kafka broadcasts events that everyone listens to.

---

## Core Components

### Frontend Layer

**Main Dashboard**
- The control center. Everything starts here.
- Shows all your files, migrations, costs, and metrics
- Updates in real-time without refreshing (thank you WebSockets!)

**Key Features:**
- File upload interface
- Cloud credential management
- Interactive tour (teaches new users)
- 30+ tooltips explaining everything
- Real-time Kafka event stream viewer

**Tech:**
- React 18 (hooks, context, modern patterns)
- Material-UI (professional components)
- Recharts (beautiful graphs)
- WebSocket client (real-time updates)
- React-Joyride (interactive tour)

### Backend Layer

This is where the magic happens. We split it into focused services instead of one giant monolith.

#### Classification Engine
**What it does:** Figures out if a file is Hot, Warm, or Cold

**How:**
1. Tracks every file access (read, write, metadata lookup)
2. Calculates access frequency over time windows
3. Considers file size (big files treated differently)
4. Assigns tier based on thresholds

**Why it matters:** Wrong classification = wasted money

#### ML Prediction Engine
**What it does:** Learns patterns and suggests cost-saving moves

**How:**
1. Collects features (access frequency, file size, current cost, time of day)
2. Trains a model on historical data
3. Predicts future access patterns
4. Recommends optimal tier/location changes

**Models used:**
- Random Forest for classification (hot/warm/cold prediction)
- Linear Regression for cost estimation
- Anomaly detection for unusual access patterns

**Why it matters:** This is what makes CloudFlow "intelligent"

#### Migration Orchestrator
**What it does:** Actually moves files between clouds

**How:**
1. User triggers migration (or accepts ML recommendation)
2. Orchestrator queues the job
3. Validates source and destination
4. Handles authentication with cloud APIs
5. Streams data with progress tracking
6. Updates metadata on completion
7. Broadcasts events via Kafka

**Edge cases handled:**
- Network failures (retry with exponential backoff)
- Concurrent migrations (queuing system)
- Partial failures (transaction logging for recovery)
- Large files (chunked uploads)

#### Performance Tracker
**What it does:** Monitors everything

**Tracks:**
- Migration duration (latency)
- Data transfer speed (throughput)
- Success/failure rates
- Percentiles (P50, P90, P95, P99)

**Why it matters:** You can't improve what you don't measure

#### Alert Manager
**What it does:** Notifies you when things need attention

**Triggers:**
- Cost exceeds threshold
- Migration fails
- Latency spikes
- Storage nearing limits

**Channels:**
- Email (via SMTP)
- In-app notifications
- Kafka events (for integrations)

### Data Layer

#### MongoDB
**What we store:**
- User accounts and auth
- File metadata (not the actual files!)
- Migration history
- Access logs
- Cost data
- ML model parameters

**Why MongoDB:**
- Our data model evolves rapidly
- No fixed schema means faster iteration
- Great for JSON-heavy data
- Easy to scale horizontally

**Indexing strategy:**
- User ID (most queries filter by user)
- File name (for lookups)
- Timestamps (for time-based queries)
- Current location (for filtering)

#### Apache Kafka
**What we stream:**
- Migration events (started, progress, completed, failed)
- Email notifications
- Performance metrics
- Cost updates
- System alerts

**Topics:**
- `migration-events` - All migration lifecycle events
- `email-notifications` - Outgoing emails
- `performance-metrics` - Real-time metrics
- `cost-updates` - Cost changes

**Why Kafka:**
- Need reliable event delivery
- Multiple consumers (frontend, email service, analytics)
- Can replay events if needed
- Industry standard (proven at scale)

---

## How It All Works Together

Let's walk through a typical flow: **User uploads a file**

1. **Frontend:** User drags file into upload zone
2. **API:** POST /api/v1/upload
3. **Backend:** 
   - Validates file
   - Generates unique ID
   - Stores metadata in MongoDB
   - Calculates initial classification
4. **Classification Engine:** Assigns "warm" tier (new files start here)
5. **Kafka:** Broadcasts "file_uploaded" event
6. **Frontend:** WebSocket receives event, updates UI

Now let's say the file gets accessed a lot...

7. **Access Tracking:** Every time user accesses file, we log it
8. **Classification Engine:** Runs hourly, notices high access count
9. **ML Engine:** Suggests upgrade to "hot" tier
10. **Frontend:** Shows recommendation in dashboard
11. **User:** Clicks "Apply"
12. **Migration Orchestrator:** Queues migration job
13. **Kafka:** Broadcasts "migration_started"
14. **Frontend:** Shows progress bar
15. **Orchestrator:** Executes migration (progress updates via Kafka)
16. **Kafka:** Broadcasts "migration_completed"
17. **Frontend:** Updates UI, shows success message
18. **Email Service:** Sends completion email
19. **Performance Tracker:** Records migration metrics

All of this happens in 4-5 seconds with live updates!

---

## Data Flow Diagrams

### File Upload Flow
```
User → Frontend → API → Backend
                           ↓
                      MongoDB (metadata)
                           ↓
                      Classification
                           ↓
                         Kafka → WebSocket → Frontend (update)
```

### Migration Flow
```
User clicks Migrate
    ↓
Frontend → API → Migration Orchestrator
                      ↓
                 Queue Job
                      ↓
                Validate (source, dest, auth)
                      ↓
                Cloud API (AWS/Azure/GCP)
                      ↓
                Transfer Data (with progress)
                      ↓
                Update MongoDB
                      ↓
                Kafka → WebSocket → Frontend
                      ↓
                Email Service (notification)
```

### ML Recommendation Flow
```
Access Logs → ML Engine
                 ↓
            Feature Extraction
                 ↓
            Model Prediction
                 ↓
            Cost Calculation
                 ↓
            Save Recommendation
                 ↓
            Frontend (display)
```

---

## Design Decisions Explained

### Why Microservices?

**Considered:** Monolith (everything in one app)
**Chose:** Microservices (separate services)

**Reasoning:**
- Heavy ML processing shouldn't block simple file lookups
- Can scale services independently (more migration workers if needed)
- Easier to maintain (each service has clear responsibility)
- Team can work on different services without conflicts

**Tradeoff:**
- More complex deployment
- Need service discovery
- But Docker Compose makes it manageable

### Why Async Python?

**Considered:** Sync Python, Node.js, Go
**Chose:** Async Python (FastAPI + asyncio)

**Reasoning:**
- FastAPI is blazing fast (comparable to Node)
- Async handles concurrent migrations well
- Python has best ML libraries
- Type hints catch bugs early
- Team knows Python well

### Why Kafka Over RabbitMQ/Redis?

**Considered:** RabbitMQ, Redis Pub/Sub, AWS SNS
**Chose:** Apache Kafka

**Reasoning:**
- Need event replay (RabbitMQ deletes on consumption)
- Multiple consumers per event (Redis Pub/Sub is 1-to-1)
- Want to keep events for analytics later
- Industry standard (hiring is easier)

**Tradeoff:**
- Heavier than Redis
- But we need the guarantees

### Why MongoDB Over PostgreSQL?

**Considered:** PostgreSQL, MySQL
**Chose:** MongoDB

**Reasoning:**
- Data model changes frequently during development
- No fixed schema = no migrations
- Great for JSON data (metadata varies per cloud provider)
- Easy horizontal scaling with sharding

**Tradeoff:**
- No foreign keys (have to enforce in code)
- No joins (have to denormalize)
- But flexibility is worth it

---

## Scalability Approach

### Current (Single Instance)
- One backend container
- One MongoDB container
- One Kafka container
- One frontend container

**Handles:** ~100 concurrent users, ~1000 files

### Horizontal Scaling (Production)
- Multiple backend containers (load balanced)
- MongoDB replica set (read replicas)
- Kafka cluster (multiple brokers)
- Frontend served from CDN

**Handles:** ~10,000 concurrent users, ~1M files

### Bottlenecks We'd Address

1. **MongoDB writes:** Use bulk inserts
2. **ML inference:** Cache predictions for similar patterns
3. **Migration bandwidth:** Parallel uploads (within cloud limits)
4. **Kafka throughput:** Partition topics by user ID

---

## Security Architecture

### Authentication
- JWT tokens (stateless, scalable)
- Refresh tokens (long-lived)
- Password hashing (bcrypt)

### Authorization
- Role-based access control (RBAC)
- User can only see their own files
- Admin role for platform management

### Encryption
- Data at rest (MongoDB encryption)
- Data in transit (TLS/SSL)
- Cloud credentials encrypted (AES-256)

### API Security
- Rate limiting (prevent abuse)
- Input validation (prevent injection)
- CORS configured (prevent CSRF)

---

## Deployment Architecture

### Development (Docker Compose)
```yaml
services:
  - MongoDB (port 27017)
  - Kafka (port 9092)
  - Backend (port 8000)
  - Frontend (port 3000)
```

### Production (Kubernetes)
```yaml
Deployments:
  - backend (3 replicas, auto-scaling)
  - frontend (2 replicas)
  
StatefulSets:
  - mongodb (3 replicas, primary + 2 secondaries)
  - kafka (3 replicas)
  
Services:
  - backend-service (LoadBalancer)
  - frontend-service (LoadBalancer)
  - mongodb-service (ClusterIP)
  - kafka-service (ClusterIP)
  
Ingress:
  - Route external traffic
  - TLS termination
```

**See `/deployment/kubernetes/` for configs**

---

## Monitoring & Observability

**What we track:**
- Request latency (P50, P90, P95, P99)
- Error rates
- Migration success rates
- Kafka lag
- Database query times
- Memory/CPU usage

**How:**
- Performance tracker service
- Custom metrics exposed to frontend
- Logs aggregated to console (could use ELK stack)

**Alerts:**
- Latency > 5s
- Error rate > 5%
- Kafka lag > 1000 messages
- Disk usage > 80%

---

## What We'd Do Next

If we had 6 more months:

1. **GraphQL API** - More flexible than REST
2. **Caching Layer** - Redis for frequently accessed data
3. **Advanced ML** - Deep learning for better predictions
4. **More Clouds** - Oracle, IBM, Alibaba
5. **Team Features** - Shared folders, permissions
6. **Audit Logs** - Complete history of all changes
7. **Cost Forecasting** - Predict next month's bill
8. **Automated Policies** - Move files automatically based on rules

---

## Learning Resources

Want to understand this better?

**Kafka:** https://kafka.apache.org/documentation/
**FastAPI:** https://fastapi.tiangolo.com/
**MongoDB:** https://docs.mongodb.com/
**React:** https://react.dev/
**Kubernetes:** https://kubernetes.io/docs/

**Our Code:** Read `/backend/api/main.py` to see how it all connects

---

**Questions?** Open an issue or ping the team!
