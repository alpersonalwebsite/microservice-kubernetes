[![CircleCI](https://circleci.com/gh/alpersonalwebsite/microservice-kubernetes.svg?style=svg)](https://circleci.com/gh/alpersonalwebsite/microservice-kubernetes)

# Microservices and kubernetes

## Project Overview
Operationalize a Machine Learning Microservice API using [kubernetes](https://kubernetes.io/)

`sklearn` model that has been trained to predict housing prices in Boston according to several features, such as average rooms in a home and data about highway access, teacher-to-pupil ratios, and so on. [Data source site](https://www.kaggle.com/c/boston-housing).


---

## Setup the Environment

* Create a virtualenv and activate it
```shell
python3 -m venv ~/.devops
source ~/.devops/bin/activate
```

You should see something like:
`(.devops) User-MacBook-Pro project-ml-microservice-kubernetes $`

* Run `make install` to install the necessary dependencies. `pylint` is pinned in `requirements.txt`, so there is no separate install step.

* Run `make train`. This fits the model and the scaler from `model_data/housing.csv`
and writes `model_data/boston_housing_prediction.joblib` and
`model_data/scaler.joblib`.

  **No model is committed to this repository, on purpose.** The `.joblib` that used
  to be here was written by a scikit-learn old enough that the version pinned in
  `requirements.txt` could no longer load it (it referenced
  `sklearn.ensemble.gradient_boosting` and `sklearn.externals.joblib`, both removed
  by 0.24). Generating it locally means the scikit-learn you installed is always the
  one that wrote it. `app.py` tells you to run this if the artifacts are missing.

* Run `make lint`. Expected result: `Your code has been rated at 10.00/10`

While you still have your `.devops` environment activated, you will still need to install:

* Docker: `https://docs.docker.com/docker-for-mac/install/`. Then, execute from the command line: `docker --version` your should see the proper Docker version. Example: `Docker version 19.03.2, build 6a30dfc`

* Hadolint: `brew install hadolint` | Check version: `hadolint --version`

* Kubernetes (Minikube): `brew install minikube` | Check version: `kubectl version`

At this point, you environment should be ready.

### Running `app.py`

1. Standalone:  `python app.py`

   It listens on **8080** by default, not 80: the container runs as a non-root user
   and an unprivileged user cannot bind a port below 1024. Override with `PORT`.
2. Run in Docker:  First, be sure that you have `Docker` running. Then: `./run_docker.sh`

Example output:
```shell
Successfully built 9239a8065d32
Successfully tagged app:latest
```

Open a new `terminal` and execute `./make_prediction.sh`
In this terminal you should see (example prediction):
```shell
Port: 8000
{
  "prediction": [
    20.35373177134412
  ]
}
```

... and, in the one running docker...
```shell
[2020-03-23 16:12:55,767] INFO in app: Received a prediction request
[2020-03-23 16:12:55,785] INFO in app: Scaling payload with the trained scaler
[2020-03-23 16:12:55,790] INFO in app: Prediction: [28.320740468089017]
172.17.0.1 - - [23/Mar/2020 16:12:55] "POST /predict HTTP/1.1" 200 -
```

The request payload is no longer echoed into the log. Prediction inputs are
somebody's data, and a log is the wrong place for it.

3. Upload your Docker image
* [Create an account](cloud.docker.com) and log into the Docker public registry
* If you did not built the docker image yet: `./run_docker.sh`
* Upload docker image to `Docker Hub`: `./upload_docker.sh`

Example output:
```shell
Password: 
Login Succeeded
Docker ID and Image: underneaththebridge/app
The push refers to repository [docker.io/underneaththebridge/app]
****51376e: Pushed 
****264e1a: Pushed 
****a4c474: Pushed 
****7872c8: Mounted from library/python 
****504689: Mounted from library/python 
****08035a: Mounted from library/python 
****02680a: Mounted from library/python 
****c551a0: Mounted from library/python 
****31157b: Mounted from library/python 
****68cde9: Mounted from library/python 
****6dff9d: Mounted from library/python 
latest: digest: sha256:****abba3738bab84e4e7ebecee309e6b64570d15a25**** size: 3057
```

4. Run Kubernetes locally
* Start a local cluster: `minikube start`
* Check the cluster(/s): `kubectl config view`

Example output:
```shell
apiVersion: v1
clusters:
- cluster:
    certificate-authority: /Users/your-user/.minikube/ca.crt
    server: https://192.168.64.2:8443
  name: minikube
contexts:
- context:
    cluster: minikube
    user: minikube
  name: minikube
current-context: minikube
kind: Config
preferences: {}
users:
- name: minikube
  user:
    client-certificate: /Users/your-user/.minikube/client.crt
    client-key: /Users/your-user/.minikube/client.key
```

5. Deploy with Kubernetes
* Run in Kubernetes:  `./run_kubernetes.sh`

This applies `k8s-deployment.yaml` and waits for the rollout before forwarding the
port.

**What changed and why.** The script used to run:

```shell
kubectl run app --image=$dockerpath --port=80
kubectl port-forward deployment/app 8000:80
```

In 2020 `kubectl run` still created a Deployment through `--generator`, which is why
the output pasted below says `deployment.apps/app created` alongside a deprecation
warning. `kubectl` 1.18 removed that generator, so today the same command creates a
bare **Pod** and `port-forward deployment/app` fails with `deployments.apps "app" not
found`. The manifest does the job explicitly instead, and adds what a review would
ask for either way: resource requests and limits, `runAsNonRoot` with the UID the
image actually uses, `allowPrivilegeEscalation: false`, a read-only root filesystem
with an `emptyDir` on `/tmp`, all capabilities dropped, and readiness and liveness
probes.

The second thing it fixes is the race the old output shows. `kubectl port-forward`
ran immediately after `kubectl run`, so the first invocation always failed with
`unable to forward port because pod is not running`, and the README told you to run
the whole script again. `kubectl rollout status` waits instead.

Example output:
```shell
deployment.apps/app created
service/app created
Waiting for deployment "app" rollout to finish: 0 of 1 updated replicas are available...
deployment "app" successfully rolled out
NAME                   READY   STATUS    RESTARTS   AGE
app-597cb487b7-pvbbk   1/1     Running   0          18s
Forwarding from 127.0.0.1:8000 -> 8080
Forwarding from [::1]:8000 -> 8080
```

* Open a new tab and make a prediction as you did before: `./make_prediction.sh`
```shell
Port: 8000
{
  "prediction": [
    28.320740468089017
  ]
}
```

* Tear the deployment down without deleting the cluster: `kubectl delete -f k8s-deployment.yaml`

6. Delete cluster: `minikube delete`
Output:
```shell
🔥  Deleting "minikube" in hyperkit ...
💀  Removed all traces of the "minikube" cluster.
```