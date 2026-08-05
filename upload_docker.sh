#!/usr/bin/env bash
# Tags and uploads the image to Docker Hub.
# Assumes an image built via run_docker.sh.
set -euo pipefail

# Step 1:
# Your Docker ID. Override without editing this file:
#   DOCKER_ID=someone-else ./upload_docker.sh
DOCKER_ID="${DOCKER_ID:-underneaththebridge}"
dockerpath="${DOCKER_ID}/app"

# Step 2:
# Authenticate & tag. docker login prompts for the password; never pass it as an
# argument, where it would land in the shell history and in `ps` output.
docker login --username "$DOCKER_ID"
docker tag app "$dockerpath"
echo "Docker ID and Image: $dockerpath"

# Step 3:
# Push image to a docker repository
docker push "$dockerpath"
