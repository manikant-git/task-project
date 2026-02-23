-- ──────────────────────────────────────────────
-- PostgreSQL initialisation script
-- Runs automatically on first container start
-- ──────────────────────────────────────────────

-- This runs as the postgres superuser during DB init

CREATE TABLE IF NOT EXISTS tasks (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    priority    VARCHAR(10)  DEFAULT 'medium'
                CHECK (priority IN ('low', 'medium', 'high')),
    status      VARCHAR(10)  DEFAULT 'pending'
                CHECK (status  IN ('pending', 'done')),
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- Seed some sample tasks so the app looks alive on first load
INSERT INTO tasks (title, description, priority) VALUES
  ('Set up Docker on server',      'Install Docker Engine and Docker Compose',       'high'),
  ('Configure Nginx reverse proxy','Set proxy_pass rules for backend services',      'high'),
  ('Write Dockerfile for backend', 'Multi-stage build with Gunicorn',                'medium'),
  ('Set up PostgreSQL backups',    'pg_dump cron job to S3',                         'medium'),
  ('Add HTTPS with Certbot',       'Use Let''s Encrypt for SSL certificates',        'low');
