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
```

---

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
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
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
