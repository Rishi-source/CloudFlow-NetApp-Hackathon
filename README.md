# CloudFlow Intelligence Platform

**Stop overpaying for cloud storage. Let AI optimize it for you.**

---

## The Problem We're Solving

Ever looked at your AWS bill and wondered why you're paying $5,000/month for files nobody's touched in 6 months? Or tried moving data between clouds and spent days figuring out APIs and permissions?

We've been there. Companies today use multiple cloud providers (AWS, Azure, GCP) but have zero visibility into which files are actually being used. Hot data sits in expensive storage, cold data blocks fast tiers, and nobody has time to manually optimize it all.

## What CloudFlow Does

Think of CloudFlow as a smart assistant for your cloud storage. It watches how you access your files, learns your patterns, and automatically suggests (or executes) moves that save money without slowing you down.

Upload a file once, and CloudFlow figures out:
- Should this live in hot storage (fast but pricey) or cold storage (slow but cheap)?
- Which cloud provider offers the best price for this access pattern?
- When should we move it as usage patterns change?

The best part? It all happens in real-time. You see migrations happening live, get instant notifications when something completes, and can track every dollar saved.

## What Makes CloudFlow Different

### 1. Actually Smart Classification
We don't just guess based on file age. Our system tracks:
- How often files are accessed
- Access time patterns (workday vs weekend)
- Read vs write operations
- File size and type

Then it categorizes files as Hot (accessed daily), Warm (accessed weekly), or Cold (rarely touched).

### 2. AI That Learns Your Patterns
The ML model isn't just for show. It genuinely learns:
- When you typically access certain file types
- Which files tend to be accessed together
- Seasonal patterns (end-of-month reports, quarterly data)
- Cost-performance tradeoffs specific to your usage

After a week of learning, it starts making suggestions that actually save money.

### 3. Real Multi-Cloud Support
Not just "supports AWS." We mean:
- Connect your AWS, Azure, and GCP accounts
- Move files between them with one click
- Compare costs across providers in real-time
- Handle all the encryption, auth, and API quirks

### 4. Real-Time Everything
Built on Apache Kafka and WebSockets:
- Watch migrations happen live (no refresh button)
- Get notified the second something completes
- See cost savings update in real-time
- Track performance metrics as they happen

### 5. Production-Ready Features
We didn't skip the hard stuff:
- **Retry logic** - Network hiccups don't kill migrations
- **Conflict resolution** - Handles concurrent updates gracefully
- **Transaction logging** - Every operation is auditable
- **Performance tracking** - P50/P90/P95/P99 latency metrics
- **Data deduplication** - Don't pay to store the same file twice
- **Compression** - Reduce storage costs automatically
- **Disaster recovery** - Backup systems in place
- **Security** - Encryption at rest and in transit, RBAC, JWT auth

## Key Features

**Data Management**
- Upload files or connect existing cloud storage
- Automatic classification (Hot/Warm/Cold)
- Multi-cloud migration with one click
- Real-time progress tracking

**Cost Optimization**
- ML-powered recommendations
- Projected savings calculations
- Cost breakdown by location and tier
- Historical cost tracking

**Performance Monitoring**
- Average latency tracking
- Throughput measurements (MB/s)
- Success rate monitoring
- Percentile analysis (P50/P90/P95/P99)

**Real-Time Updates**
- Kafka event streaming
- WebSocket live updates
- Email notifications
- Alert system for cost/performance thresholds

**User Experience**
- Interactive 14-step guided tour
- Tooltips on every element
- Beautiful gradient metrics cards
- Responsive design

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- 8GB RAM available
- Ports 3000, 8000, 9092, 27017 free

### Run Everything (2 commands)

```bash
# Clone and enter directory
cd /path/to/Netapp_Hackathon

# Start the entire stack
./run.sh
```

That's it! The script will:
1. Start MongoDB
2. Start Apache Kafka
3. Start the Python backend
4. Start the React frontend
5. Run database migrations

### Access the Platform

Open your browser to **http://localhost:3000**

**First-time users:** The platform includes an interactive tour that starts automatically. Just follow along!

**Demo credentials:**
- Email: `demo@cloudflow.com`
- Password: `demo123`

Or register a new account - it takes 10 seconds.

### Generate Sample Data

Once logged in:
1. Click "Generate Sample Data" (creates 10 test files)
2. Click "Simulate Access" (trains the ML model)
3. Watch the ML Recommendations appear!

## Tech Stack

We chose each technology for a specific reason:

**Frontend (React)**
- Users expect modern, responsive interfaces
- Real-time updates via WebSockets
- Material-UI for professional design

**Backend (Python + FastAPI)**
- Fast to develop and iterate
- Excellent ML library ecosystem
- Async support for concurrent operations
- Type hints for better code quality

**Database (MongoDB)**
- Flexible schema as we iterate features
- Great for JSON-heavy data
- Easy horizontal scaling

**Streaming (Apache Kafka)**
- Industry standard for event streaming
- Handles millions of events reliably
- Perfect for real-time notifications

**Deployment (Docker + Kubernetes)**
- Consistent environments (dev = prod)
- Easy scaling
- Cloud-agnostic deployment

**ML (scikit-learn + TensorFlow)**
- Battle-tested libraries
- Pre-built models we can customize
- Good documentation and community

## Project Structure

```
CloudFlow/
├── backend/           # Python FastAPI backend
│   ├── api/          # REST API endpoints
│   ├── ml/           # Machine learning models
│   ├── services/     # Business logic (cloud, security, metrics)
│   ├── models/       # Data models
│   └── streaming/    # Kafka producers/consumers
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   └── services/    # API clients
│   └── public/
├── deployment/       # Kubernetes configs
├── docs/            # Documentation
├── tests/           # Unit & integration tests
└── scripts/         # Utility scripts
```

## Architecture Overview

**3-Tier Architecture:**
1. **Frontend Layer** - React app, handles UI/UX
2. **Backend Layer** - Python services, business logic, ML
3. **Data Layer** - MongoDB (metadata), Kafka (events)

**Key Components:**
- Classification Engine (categorizes files)
- ML Prediction Engine (learns patterns, makes suggestions)
- Migration Orchestrator (handles actual data movement)
- Performance Tracker (monitors everything)
- Alert Manager (cost/performance notifications)

**See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.**

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Environment Variables

Copy `.env.example` to `.env` and configure:
- MongoDB connection
- Kafka settings
- Cloud provider credentials (optional)
- SMTP settings (optional)

## Features We're Proud Of

1. **The ML actually works** - After simulating access patterns, it genuinely suggests cost-saving moves
2. **Real-time feels real** - Kafka + WebSockets make it instant
3. **Professional UI** - Gradient cards, interactive tour, tooltips everywhere
4. **Production-ready** - Retry logic, conflict resolution, performance tracking
5. **Multi-cloud that works** - We handle AWS, Azure, and GCP authentication/APIs

## What's Next?

If we had more time, we'd add:
- More cloud providers (Oracle, IBM Cloud)
- Advanced cost forecasting (predict next month's bill)
- Automated policy enforcement (move files automatically)
- Team collaboration features
- Advanced analytics dashboard

## Built For

**NetApp Data in Motion Hackathon**
*Building the Future of Intelligent Cloud Storage*

---

## Contributing

Found a bug? Have an idea? We'd love to hear it!

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - use it, modify it, sell it, we don't care!

---

**Questions?** Open an issue or reach out to the team.

**Want to see it in action?** Run `./run.sh` and open http://localhost:3000
