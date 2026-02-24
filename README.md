<<<<<<< HEAD
# ⚡ TaskFlow — CI/CD Pipeline with GitHub Actions
### Stage 2 of DevOps Learning | Automated Test → Build → Deploy

---

## 🔄 Pipeline Overview

```
Developer pushes code to GitHub
              │
              ▼
┌─────────────────────────────────┐
│   STAGE 1: TEST  🧪             │
│   - Spins up real PostgreSQL    │
│   - Runs 10 unit tests          │
│   - Lints Python code           │
│   - ❌ Fails here = no deploy   │
└──────────────┬──────────────────┘
               │ Tests pass ✅
               ▼
┌─────────────────────────────────┐
│   STAGE 2: BUILD  🐳            │
│   - Builds backend image        │
│   - Builds frontend image       │
│   - Pushes both to Docker Hub   │
│   - Tags with :latest + SHA     │
└──────────────┬──────────────────┘
               │ Build succeeds ✅
               ▼
┌─────────────────────────────────┐
│   STAGE 3: DEPLOY  🚀           │
│   - SSHs into production server │
│   - git pull latest code        │
│   - docker compose pull         │
│   - docker compose up -d        │
│   - App is live! 🎉             │
└─────────────────────────────────┘
```

**Key rule:** If tests fail → pipeline stops. Broken code never reaches production.

---

## 📁 New Files Added

```
task-project/
│
├── .github/
│   └── workflows/
│       ├── cicd.yml          ← Main pipeline (test → build → deploy)
│       └── pr-check.yml      ← Runs on Pull Requests only
│
├── backend/
│   └── tests/
│       ├── __init__.py
│       └── test_app.py       ← 10 automated tests for the API
│
└── docker-compose.yml        ← Updated to pull images from Docker Hub
=======
# ⚡ TaskFlow — Three-Tier Architecture Project
### Built for DevOps Learning | Frontend + Backend + Database

---

## 📐 Architecture Overview

```
                        INTERNET
                           │
                    ┌──────▼──────┐
                    │   PORT 80   │  ← Only port open to outside world
                    └──────┬──────┘
                           │
              ┌────────────▼────────────┐
              │   TIER 1: FRONTEND      │
              │   Nginx + HTML/CSS/JS   │
              │   Container: frontend   │
              └────────────┬────────────┘
                           │  /api/* requests (reverse proxy)
                           │  Network: frontend-net
              ┌────────────▼────────────┐
              │   TIER 2: BACKEND       │
              │   Python Flask API      │
              │   Container: backend    │
              │   Port 5000 (internal)  │
              └────────────┬────────────┘
                           │  SQL queries
                           │  Network: backend-net
              ┌────────────▼────────────┐
              │   TIER 3: DATABASE      │
              │   PostgreSQL 16         │
              │   Container: db         │
              │   Port 5432 (internal)  │
              └─────────────────────────┘
```

### Why Three Tiers?
| Tier | Responsibility | Technology |
|------|---------------|------------|
| **Presentation** | What users see & interact with | Nginx, HTML, CSS, JS |
| **Application**  | Business logic & API endpoints | Python Flask |
| **Data**         | Store & retrieve data persistently | PostgreSQL |

---

## 📁 Project Structure

```
taskflow/
│
├── docker-compose.yml        ← Orchestrates all 3 containers
├── .env                      ← Environment variables (passwords etc.)
├── .gitignore
│
├── frontend/
│   ├── Dockerfile            ← Builds Nginx + HTML image
│   ├── nginx.conf            ← Nginx config + reverse proxy rules
│   └── index.html            ← The entire frontend app
│
├── backend/
│   ├── Dockerfile            ← Builds Flask API image
│   ├── app.py                ← All API routes (CRUD for tasks)
│   └── requirements.txt      ← Python dependencies
│
└── postgres/
    └── init.sql              ← Creates tables + seeds sample data
>>>>>>> 8c30b9ec4ba98e4e027071d1dee7b24b4f1264b1
```

---

<<<<<<< HEAD
## 🔐 GitHub Secrets Setup

GitHub Secrets store your passwords safely — they are **never visible** in logs.

### Step 1 — Go to your repo secrets
```
GitHub Repo → Settings → Secrets and variables → Actions → New repository secret
```

### Step 2 — Add these 5 secrets

| Secret Name | Value | Where to get it |
|-------------|-------|----------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username | hub.docker.com |
| `DOCKERHUB_TOKEN` | Docker Hub access token | hub.docker.com → Account Settings → Security |
| `SERVER_HOST` | Your server IP address | AWS/DigitalOcean dashboard |
| `SERVER_USER` | SSH username | Usually `ubuntu` (AWS) or `root` |
| `SERVER_SSH_KEY` | Private SSH key content | `cat ~/.ssh/id_rsa` on your local machine |

### How to create Docker Hub token
```
1. Login to hub.docker.com
2. Click your profile → Account Settings
3. Go to Security → New Access Token
4. Name it "github-actions"
5. Copy the token → paste as DOCKERHUB_TOKEN secret
```

### How to get SSH key for server
```bash
# On your LOCAL machine — generate a key pair if you don't have one
ssh-keygen -t ed25519 -C "github-actions"

# Copy PUBLIC key to your server
ssh-copy-id ubuntu@YOUR_SERVER_IP

# Copy PRIVATE key content → paste as SERVER_SSH_KEY secret
cat ~/.ssh/id_ed25519
```

---

## 🖥️ Server Setup (One Time Only)

SSH into your server and run these commands once:

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# 2. Install Docker Compose
sudo apt install docker-compose-plugin -y

# 3. Clone your project
git clone https://github.com/manikant-git/task-project ~/task-project
cd ~/task-project

# 4. Create .env file with your values
cat > .env << EOF
POSTGRES_DB=taskflow
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=your_strong_password
DOCKERHUB_USERNAME=your_dockerhub_username
EOF

# 5. First manual run to verify everything works
docker compose up -d
```

After this, **every git push will auto-deploy**. You never SSH manually again!

---

## 🚀 How to Trigger the Pipeline

```bash
# Make any change to your code
echo "# updated" >> README.md

# Commit and push
git add .
git commit -m "trigger ci/cd pipeline"
git push origin main

# Watch it run live:
# GitHub Repo → Actions tab → click the running workflow
```

---

## 🧪 Running Tests Locally

```bash
# Install test dependencies
pip install pytest pytest-cov

# Set environment variables
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=taskflow_test
export DB_USER=taskuser
export DB_PASSWORD=taskpass

# Run tests
cd backend
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=term-missing
```

**Expected output:**
```
test_app.py::test_health_check                ✅ PASSED
test_app.py::test_get_tasks_returns_list      ✅ PASSED
test_app.py::test_create_task_success         ✅ PASSED
test_app.py::test_create_task_missing_title   ✅ PASSED
test_app.py::test_create_task_invalid_priority ✅ PASSED
test_app.py::test_create_task_default_priority ✅ PASSED
test_app.py::test_update_task_status          ✅ PASSED
test_app.py::test_update_task_invalid_status  ✅ PASSED
test_app.py::test_update_nonexistent_task     ✅ PASSED
test_app.py::test_delete_task                 ✅ PASSED
test_app.py::test_delete_nonexistent_task     ✅ PASSED
══════════════ 11 passed in 2.34s ══════════════
```

---

## 📋 Pipeline Stages Explained

### Stage 1: TEST
```yaml
services:
  postgres:           # Real DB spun up just for tests
    image: postgres:16-alpine
```
- GitHub Actions spins up a **real PostgreSQL container** for testing
- All 11 tests run against it
- If any test fails → pipeline stops immediately

### Stage 2: BUILD
```yaml
tags: |
  myusername/taskflow-backend:latest       # Always latest
  myusername/taskflow-backend:abc1234      # Git commit SHA
```
- Images are tagged with **both** `:latest` AND the git commit SHA
- This means you can always roll back to any previous version:
  ```bash
  docker pull myusername/taskflow-backend:abc1234
  ```

### Stage 3: DEPLOY
```bash
git pull origin main          # Get latest code
docker compose pull           # Get new images from Docker Hub
docker compose up -d          # Restart only changed containers
docker image prune -f         # Clean up old images
```
- Uses `--no-deps` flag so only changed containers restart (zero downtime)

---

## 🔁 Pull Request Flow

When you open a PR, only **test + lint** runs (no deploy):

```
PR opened
    ↓
flake8 lint check          ← Catches syntax errors
    ↓
Tests run                  ← Functional check
    ↓
docker compose config      ← Validates YAML
    ↓
✅ Green = safe to merge
❌ Red   = fix before merge
=======
## 🚀 How to Run (Step by Step)

### Prerequisites
```bash
# Check Docker is installed
docker --version          # Should show Docker version

# Check Docker Compose is installed
docker compose version    # Should show v2.x.x
```

### Step 1 — Clone / create the project folder
```bash
cd ~
# If you downloaded a zip, unzip it
# Or if using git:
git clone <your-repo-url> taskflow
cd taskflow
```

### Step 2 — Build all Docker images
```bash
docker compose build
```
This reads each `Dockerfile` and creates images for frontend and backend.
The `db` uses a ready-made image from Docker Hub so no build needed.

### Step 3 — Start all containers
```bash
docker compose up -d
```
- `-d` means "detached" (runs in background)
- Docker starts containers in the right order: **db → backend → frontend**

### Step 4 — Open the app
```
http://localhost
```
You should see the TaskFlow app with 5 pre-loaded tasks!

---

## 🔧 Useful Commands

### View running containers
```bash
docker compose ps
```

### View logs (very useful for debugging!)
```bash
docker compose logs             # All containers
docker compose logs frontend    # Only frontend logs
docker compose logs backend     # Only backend logs
docker compose logs db          # Only DB logs
docker compose logs -f backend  # Follow/live logs (Ctrl+C to stop)
```

### Stop everything
```bash
docker compose down
```

### Stop and DELETE data (fresh start)
```bash
docker compose down -v          # -v removes volumes (deletes DB data)
```

### Rebuild after making code changes
```bash
docker compose build backend    # Rebuild only backend
docker compose up -d            # Restart
```

### Connect to the database directly
```bash
docker exec -it taskflow-db psql -U taskuser -d taskflow

# Once inside PostgreSQL:
\dt                          # List tables
SELECT * FROM tasks;         # View all tasks
\q                           # Quit
```

### Connect to backend container shell
```bash
docker exec -it taskflow-backend sh
```

---

## 🌐 API Endpoints

The backend exposes these REST API routes:

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/tasks` | Get all tasks |
| POST | `/api/tasks` | Create a new task |
| PUT | `/api/tasks/<id>` | Update task status |
| DELETE | `/api/tasks/<id>` | Delete a task |

### Test API manually (curl)
```bash
# Health check
curl http://localhost/api/health

# Get all tasks
curl http://localhost/api/tasks

# Create a task
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Kubernetes","priority":"high","description":"Start with pods"}'

# Mark task as done (replace 1 with actual ID)
curl -X PUT http://localhost/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"done"}'

# Delete a task
curl -X DELETE http://localhost/api/tasks/1
```

---

## 🔒 Traffic Flow & Security

```
USER BROWSER
    │
    │  HTTP :80  (only open port)
    ▼
┌─────────────────────────────────────────┐
│  NGINX (frontend container)             │
│                                         │
│  GET /           → serve index.html     │
│  GET /api/*      → proxy to backend:5000│
└─────────────────────────────────────────┘
    │
    │  Internal Docker network (frontend-net)
    │  Port 5000 — NOT exposed to internet
    ▼
┌─────────────────────────────────────────┐
│  FLASK (backend container)              │
│                                         │
│  Receives API calls from Nginx only     │
│  Talks to DB via SQL                    │
└─────────────────────────────────────────┘
    │
    │  Internal Docker network (backend-net)
    │  Port 5432 — NOT exposed to internet
    ▼
┌─────────────────────────────────────────┐
│  POSTGRESQL (db container)              │
│                                         │
│  Only backend can connect to it         │
│  Data stored in Docker volume           │
└─────────────────────────────────────────┘
```

**Key security rules applied:**
- Only port 80 is open to the outside world
- Backend and DB ports are internal only
- Two separate Docker networks isolate tiers
- DB credentials are in `.env` file, not hardcoded

---

## 🐳 Dockerfile Explanation

### Backend Dockerfile (Multi-stage build)
```dockerfile
# Stage 1: Install dependencies
FROM python:3.12-slim AS builder
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: Smaller runtime image (no build tools)
FROM python:3.12-slim
COPY --from=builder /install /usr/local  # Only copy what we need
COPY app.py .
CMD ["gunicorn", "app:app"]              # Production WSGI server
```
**Why multi-stage?** Final image is much smaller because build tools are discarded.

### Frontend Dockerfile
```dockerfile
FROM nginx:alpine                        # Tiny Nginx image
COPY nginx.conf /etc/nginx/conf.d/       # Our routing rules
COPY index.html /usr/share/nginx/html/   # Our app
```

---

## ⚙️ How Services Connect (DNS Magic)

Docker Compose creates an internal DNS server.  
Each service's **name in docker-compose.yml becomes a hostname**.

| Service Name | Hostname | Port |
|-------------|----------|------|
| `frontend` | `frontend` | 80 |
| `backend` | `backend` | 5000 |
| `db` | `db` | 5432 |

That's why in `nginx.conf` you see:
```nginx
proxy_pass http://backend:5000;   # "backend" = Docker service name
```
And in `app.py`:
```python
host = os.getenv("DB_HOST", "db")  # "db" = Docker service name
>>>>>>> 8c30b9ec4ba98e4e027071d1dee7b24b4f1264b1
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
<<<<<<< HEAD
| Tests fail in Actions | Check `Actions` tab → click failed job → read logs |
| Docker Hub push fails | Verify `DOCKERHUB_TOKEN` secret is correct |
| SSH deploy fails | Check `SERVER_HOST`, `SERVER_USER`, `SERVER_SSH_KEY` secrets |
| Server not updating | SSH in → `cd ~/task-project && docker compose pull && docker compose up -d` |
| See pipeline history | GitHub Repo → Actions → select workflow |

---

## 📊 What You Can Now Say in Interviews

✅ "I set up a CI/CD pipeline using GitHub Actions with 3 stages: test, build, deploy"
✅ "Pipeline runs automated tests against a real PostgreSQL instance on every push"
✅ "Docker images are built and tagged with git SHA for version traceability"
✅ "Deployment happens automatically via SSH — zero manual intervention"
✅ "Pull Requests are gated by lint + test checks before merge is allowed"
✅ "Images are stored in Docker Hub with both :latest and commit SHA tags for rollback"

---

## 🔜 Stage 3 Options (Next Level)

1. **Kubernetes** — convert Docker Compose → K8s Deployments + Services + Ingress
2. **AWS Deployment** — deploy to EC2 with proper VPC, security groups, HTTPS
3. **Monitoring** — Prometheus + Grafana dashboards for your running app

---

*Stage 2 complete. You now have a real CI/CD pipeline! 🚀*
=======
| App not loading | `docker compose logs frontend` |
| API errors | `docker compose logs backend` |
| DB connection failed | `docker compose logs db` — wait 10s and retry |
| Port 80 already in use | Change `"80:80"` to `"8080:80"` in compose file |
| Want fresh start | `docker compose down -v && docker compose up -d` |

---

## 📈 What You Learn From This Project

✅ **Docker** — writing Dockerfiles, multi-stage builds  
✅ **Docker Compose** — orchestrating multi-container apps  
✅ **Nginx** — serving static files + reverse proxy  
✅ **REST APIs** — GET/POST/PUT/DELETE  
✅ **PostgreSQL** — relational DB, tables, SQL queries  
✅ **Network segmentation** — isolating tiers with separate networks  
✅ **Environment variables** — managing config with `.env`  
✅ **Health checks** — making containers wait for dependencies  
✅ **Volumes** — persisting data across restarts  

---

## 🔜 Next Steps (Level Up!)

1. **Add HTTPS** with Let's Encrypt + Certbot
2. **Deploy to a cloud server** (AWS EC2, DigitalOcean Droplet)
3. **Add CI/CD pipeline** with GitHub Actions
4. **Add monitoring** with Prometheus + Grafana
5. **Migrate to Kubernetes** (convert compose → K8s YAML)
6. **Add a load balancer** and scale backend to 3 replicas

---

*Happy learning! This project covers the core concepts every DevOps engineer needs.*
>>>>>>> 8c30b9ec4ba98e4e027071d1dee7b24b4f1264b1
