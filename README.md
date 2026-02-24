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
```

---

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
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
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
