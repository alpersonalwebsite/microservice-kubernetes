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

* Run `make install` to install the necessary dependencies. To ensure you have the right version of `pylint` run: `pip3 install pylint`

* Run `make lint`. Expected result: `Your code has been rated at 10.00/10 (previous run: 8.93/10, +1.07)`

While you still have your `.devops` environment activated, you will still need to install:

* Docker: `https://docs.docker.com/docker-for-mac/install/`. Then, execute from the command line: `docker --version` your should see the proper Docker version. Example: `Docker version 19.03.2, build 6a30dfc`

* Hadolint: `brew install hadolint` | Check version: `hadolint --version`

* Kubernetes (Minikube): `brew install minikube` | Check version: `kubectl version`

At this point, you environment should be ready.

### Running `app.py`

1. Standalone:  `python app.py`
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
[2020-03-23 16:12:55,767] INFO in app: JSON payload: 
{'CHAS': {'0': 0}, 'RM': {'0': 6.575}, 'TAX': {'0': 296.0}, 'PTRATIO': {'0': 15.3}, 'B': {'0': 396.9}, 'LSTAT': {'0': 4.98}}
[2020-03-23 16:12:55,778] INFO in app: Inference payload DataFrame: 
   CHAS     RM    TAX  PTRATIO      B  LSTAT
0     0  6.575  296.0     15.3  396.9   4.98
[2020-03-23 16:12:55,785] INFO in app: Scaling Payload: 
   CHAS     RM    TAX  PTRATIO      B  LSTAT
0     0  6.575  296.0     15.3  396.9   4.98
172.17.0.1 - - [23/Mar/2020 16:12:55] "POST /predict HTTP/1.1" 200 -
```

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

Example output:
```shell
(.devops) user@User-MacBook-Pro project-ml-microservice-kubernetes (master) (email@outlook.com)  $ ./run_kubernetes.sh
kubectl run --generator=deployment/apps.v1 is DEPRECATED and will be removed in a future version. Use kubectl run --generator=run-pod/v1 or kubectl create instead.
deployment.apps/app created
NAME                   READY   STATUS    RESTARTS   AGE
app-597cb487b7-pvbbk   0/1     Pending   0          0s
error: unable to forward port because pod is not running. Current status=Pending
```

* Wait a couple of minutes until the pod is ready, then you can run the script again: `./run_kubernetes.sh`. *Waiting*: You can check on your pod’s status with a call to `kubectl get pod` and you should see the status change to Running. Then you can run the full `./run_kuberenets.sh` script again.

Example output:
```shell
Error from server (AlreadyExists): deployments.apps "app" already exists
NAME                   READY   STATUS    RESTARTS   AGE
app-597cb487b7-pvbbk   1/1     Running   0          9m59s
Forwarding from 127.0.0.1:8000 -> 80
Forwarding from [::1]:8000 -> 80
```

* Open a new tab an make a prediction as you did before: `./make_prediction.sh`
In this terminal you should see (example prediction):
```shell
Port: 8000
{
  "prediction": [
    20.35373177134412
  ]
}

```

* Run: `./run_kuberenets.sh`
Example output:
```shell
Error from server (AlreadyExists): deployments.apps "app" already exists
NAME                   READY   STATUS    RESTARTS   AGE
app-597cb487b7-pvbbk   1/1     Running   0          14m
Forwarding from 127.0.0.1:8000 -> 80
Forwarding from [::1]:8000 -> 80
```

6. Delete cluster: `minikube delete`
Output:
```shell
🔥  Deleting "minikube" in hyperkit ...
💀  Removed all traces of the "minikube" cluster.
```