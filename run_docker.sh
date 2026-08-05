#!/usr/bin/env bash
# Builds and runs the image locally.
set -euo pipefail

# Step 1:
# Build image and add a descriptive tag
docker build --tag=app .

# Step 2:
# List docker images
docker image ls

# Step 3:
# Run flask app. The container listens on 8080 (unprivileged, so it can run as a
# non-root user); 8000 is the host port the prediction script talks to.
docker run -p 8000:8080 app
