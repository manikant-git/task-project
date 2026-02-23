# ──────────────────────────────────────────────
# Frontend Dockerfile
# Serves static HTML via Nginx
# ──────────────────────────────────────────────
FROM nginx:1.27-alpine

# Remove the default Nginx page
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the frontend files
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
