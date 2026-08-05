FROM python:3.7.3-stretch

## Step 1:
# Create a working directory
WORKDIR /app

## Step 2:
# Install packages from requirements.txt first, so a source change does not
# invalidate the dependency layer.
COPY requirements.txt /app/
# DL3013 is for the unpinned `--upgrade pip`. The ignore must be the line directly
# above the RUN: hadolint attaches it to the instruction that follows, so anything
# in between, even another comment, silently detaches it.
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --upgrade pip &&\
    pip install --no-cache-dir -r requirements.txt

## Step 3:
# Copy the source. The previous version ran `COPY . app.py /app/` and
# `COPY . model_data /app/`, which each copied the whole build context (including
# the .git directory), twice. .dockerignore keeps the context small as well.
COPY app.py train.py /app/
COPY model_data/ /app/model_data/

## Step 4:
# Train inside the image, so the model and the scaler are written by the exact
# scikit-learn installed above. The repository deliberately ships no .joblib.
RUN python train.py

## Step 5:
# Drop root. The service binds 8080 rather than 80 because an unprivileged user
# cannot bind a port below 1024.
# UID pinned so k8s-deployment.yaml's runAsUser can match it exactly rather than
# assuming what useradd happens to allocate.
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser &&\
    chown -R appuser:appuser /app
USER appuser

## Step 6:
# Expose the unprivileged port
EXPOSE 8080

## Step 7:
# Run app.py at container launch
CMD ["python", "app.py"]
