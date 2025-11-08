# CloudFlow User Guide

**Your step-by-step guide to optimizing cloud storage costs**

---

## What You'll Learn

By the end of this guide, you'll know how to:
- Upload and manage files
- Connect your cloud accounts
- Use ML recommendations to save money
- Monitor migrations in real-time
- Understand performance metrics

**Time needed:** 15 minutes

---

## Getting Started

### First Launch

1. Open http://localhost:3000 in your browser
2. You'll see the login page

**New here?** Click "Register" and create an account. Takes 30 seconds.

**Already have an account?** Just log in.

### The Welcome Tour

First-time users get an automatic tour! It starts 1 second after you log in.

**The tour covers:**
- System status indicators
- Kafka event stream
- How to generate sample data
- ML recommendations
- Performance metrics
- Your files and migrations

**Pro tip:** You can skip the tour and click the **?** button (bottom-right corner) anytime to restart it.

---

## Your First 5 Minutes

Let's get you comfortable with CloudFlow.

### Step 1: Generate Sample Data

See that "Generate Sample Data" button? Click it.

**What happens:**
- Creates 10 random files
- Assigns them random tiers (Hot/Warm/Cold)
- Places them across different locations
- Shows them in your dashboard

**Why?** So you have data to play with without uploading real files.

### Step 2: Watch the Kafka Stream

Look at the dark blue box labeled "Kafka Event Stream" - it should now show:
```
[10:15:23] Topic: migration-events Type: file_created ...
[10:15:24] Topic: migration-events Type: file_created ...
```

This is live event streaming! Every action in CloudFlow broadcasts events here.

### Step 3: Check Your Summary Cards

Four colorful cards show your platform status:
- **Total Objects:** How many files you have
- **Monthly Cost:** Current storage costs
- **Avg Latency:** How fast operations run
- **Active Migrations:** Files being moved right now

Hover over each card - there's a tooltip explaining it!

### Step 4: Simulate Access Patterns

Click "Simulate Access" button.

**What happens:**
- Generates fake access logs for your files
- Some files get accessed a lot (become Hot candidates)
- Some files rarely accessed (become Cold candidates)
- ML model learns from this data

**Wait 2-3 seconds...**

### Step 5: See ML Recommendations

A yellow box appears: "ML Recommendations - Save $X/month"

**What you're seeing:**
- AI-suggested tier changes
- Estimated monthly savings
- Reasons for each recommendation

**Try it:** Click "Apply" on one recommendation and watch the migration happen!

---

## Understanding the Dashboard

### Top Section: System Status

Three status chips show service health:
- **Kafka: Connected** - Event streaming is working
- **Email SMTP: Ready** - Notifications will be sent
- **WebSocket: Connected** - Real-time updates enabled

**Green = good. Red = something's wrong.**

### Middle Section: Data Distribution

Three charts show how your data is distributed:

**Data by Tier (Pie Chart)**
- Hot (red): Frequently accessed files
- Warm (yellow): Moderate access
- Cold (blue): Rarely accessed

**Data by Location (Pie Chart)**
- AWS, Azure, GCP, On-Premise
- Shows where your files physically live

**Cost Breakdown (Bar Chart)**
- Monthly cost per cloud provider
- Helps identify expensive locations

### Bottom Section: Files & Migrations

**Your Files Table:**
- All your uploaded files
- Tier, location, size, monthly cost
- Click the ↑ icon to migrate a file

**Recent Migrations Table:**
- Active and completed migrations
- Real-time progress bars
- Status (in_progress, completed, failed)

---

## Managing Your Files

### Uploading Files

1. Click "Upload" tab (top navigation)
2. Drag files into the upload zone (or click to browse)
3. Select files from your computer
4. Watch them upload!

**What happens behind the scenes:**
- File gets stored temporarily
- Classification engine analyzes it
- Assigns initial tier (usually "warm")
- Shows up in your dashboard

**File limits:**
- Max size: 100 MB (configurable)
- Any file type supported

### Viewing File Details

In the "Your Files" table, you can see:
- **Name:** What you called it
- **Size:** In MB
- **Tier:** Hot/Warm/Cold (hover for explanation)
- **Location:** Which cloud it's on
- **Cost/mo:** Monthly storage cost

### Migrating Files Manually

Want to move a file? Here's how:

1. Find the file in "Your Files" table
2. Click the ↑ icon in the "Actions" column
3. A dialog pops up
4. Select target location (AWS, Azure, GCP, or simulation)
5. Click "Migrate"

**Watch the magic:**
- Kafka broadcasts "migration_started"
- Progress bar appears in "Recent Migrations"
- Email sent when complete
- File's location updates automatically

**Pro tip:** Check the Kafka stream to see events in real-time!

---

## Using ML Recommendations

This is where CloudFlow saves you money.

### How Recommendations Work

The ML model analyzes:
- Access frequency (how often file is used)
- Access patterns (when it's accessed)
- Current tier and cost
- Alternative tier costs

Then suggests moves that save money without hurting performance.

### Reading Recommendations

Each recommendation shows:
- **File name:** Which file to move
- **Current:** Where it is now
- **Recommended:** Where it should go
- **Reason:** Why this saves money
- **Savings:** How much you'll save per month

### Applying Recommendations

Two ways to use them:

**Option 1: One at a time**
- Click "Apply" button on any recommendation
- Confirm the migration
- Watch it happen!

**Option 2: Bulk apply** (coming soon)
- Select multiple recommendations
- Apply all at once

**What if I disagree?**
- Just ignore the recommendation
- The ML model learns from your choices
- Over time, it gets better at suggesting moves you actually want

---

## Connecting Cloud Accounts

Want to migrate to real clouds? You'll need to add credentials.

### Adding AWS Credentials

1. Click "Credentials" tab
2. Click "Add AWS Credentials"
3. Enter:
   - **Access Key ID** (from AWS IAM)
   - **Secret Access Key** (from AWS IAM)
   - **Default Bucket** (e.g., "my-cloudflow-bucket")
4. Click "Save"

**Where to get AWS credentials:**
- Log into AWS Console
- Go to IAM → Users → Your user
- Security Credentials → Create Access Key
- Copy the keys (you only see them once!)

### Adding Azure Credentials

1. Click "Add Azure Credentials"
2. Enter:
   - **Storage Account Name**
   - **Storage Account Key**
   - **Container Name**
3. Click "Save"

**Where to get Azure credentials:**
- Azure Portal → Storage Accounts
- Select your account
- Access Keys → Show keys
- Copy key1 or key2

### Adding GCP Credentials

1. Click "Add GCP Credentials"
2. Upload your Service Account JSON file
3. Enter default bucket name
4. Click "Save"

**Where to get GCP credentials:**
- Google Cloud Console
- IAM & Admin → Service Accounts
- Create key → JSON
- Download the file

**Security note:** All credentials are encrypted before storage!

---

## Understanding Performance Metrics

Scroll down to see performance metrics. Here's what they mean:

### Average Latency
**What:** How long operations take (in milliseconds)
**Good:** < 100ms
**Needs attention:** > 500ms

**Lower is better!**

### Throughput
**What:** Data transfer speed (MB/s)
**Good:** > 10 MB/s
**Needs attention:** < 1 MB/s

**Higher is better!**

### Success Rate
**What:** Percentage of migrations that complete successfully
**Good:** > 95%
**Needs attention:** < 90%

**Higher is better!**

### Data Processed
**What:** Total data migrated in last 60 minutes
**Just informational** - shows how busy the system is

### Latency Percentiles

These show latency distribution:
- **P50 (Median):** Half of operations complete faster
- **P90:** 90% complete faster
- **P95:** 95% complete faster  
- **P99:** 99% complete faster (worst-case)

**Why it matters:** P99 shows your worst-case user experience.

---

## Real-Time Monitoring

### Watching Migrations Live

When you trigger a migration:

1. **Kafka Event Stream** shows:
   ```
   [10:20:15] Type: migration_started Job: abc123 ...
   [10:20:16] Type: migration_update Progress: 25% ...
   [10:20:17] Type: migration_update Progress: 50% ...
   [10:20:18] Type: migration_complete Job: abc123 ✓
   ```

2. **Recent Migrations table** shows progress bar filling up

3. **Alert appears** at top: "Migration completed successfully"

4. **Email sent** (if SMTP configured)

**No refresh needed - it's all real-time!**

### System Alerts

Watch for alerts at the top of the page:
- **Green (Success):** Migration completed, data generated, etc.
- **Yellow (Warning):** Slow performance, high latency
- **Red (Error):** Migration failed, system error

Click the X to dismiss them.

---

## Tips & Tricks

### Save Money with These Strategies

1. **Trust the ML:** After simulating access, recommendations are usually spot-on
2. **Cold storage is cheap:** Rarely-accessed files belong in cold tier
3. **Batch migrations:** Move multiple files together to save time
4. **Monitor trends:** Check cost breakdown chart weekly

### Using the Platform Efficiently

1. **Use the tour:** Don't skip it - saves time in the long run
2. **Hover everything:** Tooltips explain every feature
3. **Watch Kafka:** Helps you understand what's happening
4. **Check percentiles:** P99 latency reveals problems

### Common Workflows

**Weekly Optimization:**
```
1. Review ML recommendations
2. Apply money-saving suggestions
3. Check cost breakdown chart
4. Celebrate savings!
```

**Monthly Audit:**
```
1. Export data (coming soon)
2. Review access patterns
3. Adjust tiers manually if needed
4. Update cloud credentials if needed
```

---

## Troubleshooting

### "Migration Failed"

**Possible causes:**
- Invalid cloud credentials
- Network timeout
- Insufficient permissions
- Target storage full

**Solutions:**
- Check credentials in Credentials tab
- Retry the migration
- Check cloud provider dashboard

### "WebSocket Disconnected"

**What it means:** Real-time updates stopped

**Solutions:**
- Refresh the page
- Check backend is running
- Wait 30 seconds (auto-reconnect)

### "No Recommendations Available"

**Why:** ML model needs data to learn

**Solutions:**
- Click "Simulate Access" to generate patterns
- Wait a few hours for real access data
- Upload more files

### "Slow Performance"

**Causes:**
- Too many concurrent migrations
- Large files
- Slow cloud provider API

**Solutions:**
- Migrate one file at a time
- Wait for current migrations to finish
- Check performance metrics for bottlenecks

---

## Advanced Features

### Cost Optimization Strategies

**Tiering Strategy:**
```
Hot Tier (AWS S3 Standard):
- Files accessed daily
- $0.023/GB/month

Warm Tier (AWS S3 Infrequent Access):
- Files accessed weekly  
- $0.0125/GB/month (46% savings!)

Cold Tier (AWS S3 Glacier):
- Files accessed rarely
- $0.004/GB/month (83% savings!)
```

**Multi-Cloud Strategy:**
- Use AWS for hot data (fast API)
- Use GCP for warm data (competitive pricing)
- Use Azure for cold data (archive storage)

### Keyboard Shortcuts

- **?** - Restart tour
- **Esc** - Close dialogs
- **Ctrl/Cmd + K** - Quick search (coming soon)

---

## Best Practices

1. **Start with sample data** before uploading real files
2. **Simulate access patterns** to train the ML model
3. **Apply recommendations incrementally** (one at a time at first)
4. **Monitor performance metrics** to catch issues early
5. **Keep cloud credentials updated** (they can expire)
6. **Use tooltips** when confused about a feature
7. **Watch the Kafka stream** to understand workflows

---

## What's Next?

Now that you know the basics:

1. Upload your own files
2. Add real cloud credentials
3. Run optimizations weekly
4. Track your savings!

**Questions?**
- Hover over any element for tooltips
- Click the ? button for the tour
- Check the README.md for setup help
- Read ARCHITECTURE.md to understand how it works

---

**Happy optimizing! 🚀**

Every dollar saved is a dollar earned.
