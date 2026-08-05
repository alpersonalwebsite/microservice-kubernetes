#!/usr/bin/env bash
# Runs the image on Kubernetes from the committed manifest.
set -euo pipefail

# Step 1:
# Apply the Deployment and Service. This replaces `kubectl run`, which creates a
# bare Pod: the old script then ran `kubectl port-forward deployment/app` against
# a Deployment that had never been created.
kubectl apply -f k8s-deployment.yaml

# Step 2:
# Point the Deployment at your own image if you pushed one
#   kubectl set image deployment/app app="${DOCKER_ID:-your-id}/app:latest"

# Step 3:
# Wait for it to be ready rather than racing the port-forward
kubectl rollout status deployment/app --timeout=120s

# Step 4:
# List pods
kubectl get pods -l app=sklearn-prediction

# Step 5:
# Forward the container port to the host
kubectl port-forward deployment/app 8000:8080
