# Azure DevOps Flask CI/CD Pipeline

This project demonstrates a simple end-to-end CI/CD pipeline using Flask, Docker, Kubernetes, Minikube, DockerHub, and Azure DevOps.

---

## Project Overview

The application is containerized using Docker, pushed to DockerHub, and deployed into a Kubernetes cluster running on Minikube. Azure DevOps Pipelines automates the CI/CD workflow using a self-hosted local agent to build, push, and deploy the application.

This pipeline handles:

✅ Build Automation
✅ Docker Image Creation
✅ DockerHub Push
✅ Kubernetes Deployment
✅ Continuous Delivery Workflow
✅ Using of Local Agent

---

## Architecture

![Pipeline](diagrams/architecture.png)

## Prerequisites
* Flask App
* Docker
* Kubernetes CLI (kubectl)
* Minikube
* Azure Devops Account
* GitHub Account
* DockerHub Account
* Private Repo in DockerHub

## Project Workflow
1. Create Dockerfile and requirements.txt
2. Build Docker image
3. Push image to DockerHub
4. Create Kubernetes namespace and secrets
5. Create and Deploy deployment and service manifests
6. Configure Azure DevOps self-hosted agent
7. Create Azure Pipeline YAML
8. Trigger automated pipeline

---

## Create Dockerfile and requirements.txt

Create a docker

```bash
FROM python:3.13-alpine
LABEL maintainer="YOUREMAIL@EMAIL.COM"
COPY . /mysite
WORKDIR /mysite
RUN pip install -r requirements.txt
EXPOSE 5000
# ENTRYPOINT ["python"]
CMD ["python","flask_app.py"] 
```

Create requirements.txt

```bash
echo "flask==3.1.0" > requirements.txt
```

## Build the Docker image:

```bash
# Start your local minikube
minikube start

# Build your image with tagging, (eg. <username>/<flask-app-name>:<tag>)
docker build -t mkbmr/my-flask-app:v1 .

# Verify image build
docker images | grep flask

```

## Push image to DockerHub:

```bash
# Login into Docker Account
docker login -u <username>

# Push image to dockerhub
docker push mkbmr/flask-app:v1
```

## Create Kubernetes Namespace and Secrets

```bash
# Create namespace
kubectl create namespace flask-app

# Apply secret to namespace
kubectl create secret docker-registry regcred \
  --docker-username='YOUR_USERNAME' \
  --docker-password="YOUR_PAT_TOKEN" \
  --docker-email='YOUR_EMAIL' \
  -n flask-app

# Verify secret
kubectl -n flask-app get secret regcred -o yaml
```


## Create & Deploy deployment and service manifests

Create your deployment.yaml and service.yaml

flask-app-deployment.yaml
```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-app
  namespace: flask-app
spec:
  replicas: 3
  selector:
    matchLabels:
      components: flask-demo-app
  template:
    metadata:
      labels:
        components: flask-demo-app
    spec:
      imagePullSecrets:
        - name: regcred
      containers:
        - name: flask-demo-app
          image: mkbmr/my-flask-app:v1
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5000
```

flask-app-service.yaml
```bash
apiVersion: v1
kind: Service
metadata:
  name: flask-demo-app-service
  namespace: flask-app
spec:
  type: LoadBalancer
  selector:
    components: flask-demo-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 5000
```


Applying both manifest
```bash
# Apply deployments
kubectl apply -f flask-app-deployment.yaml
kubectl apply -f flask-app-service.yaml

# Verify deployments
kubectl -n flask-app get pods -o wide
kubectl -n flask-app describe pod -l components=flask-demo-app
kubectl get svc -n flask-app
```

## Verify with Minikube
```bash
# Open another terminal tab and run minikube tunnel
minikube tunnel

# Get External IP
kubectl get svc -n flask-app

# Verify with Curl (or paste the IP and port into your web-browser)
curl -v <External-IP>:<Port>
```

**Keep it running so that we can test with the pipeline later. Ensure to make this work before proceeding to the next steps.**

## Configure Azure DevOps self-hosted agent

Here are guides to install self-hosted agents:

* [Linux agent](https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/linux-agent?view=azure-devops&tabs=IP-V4)
* [macOS agent](https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/osx-agent?view=azure-devops&tabs=IP-V4)
* [Windows agent](https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/windows-agent?view=azure-devops&tabs=IP-V4)

**Ensure that agent is online before proceeding to the next step**


## Create Azure Pipeline YAML

The Azure DevOps pipeline performs the following steps:

* Check for syntax error in flask_app.py
* Build Docker image
* Push image to DockerHub
* Update deployment image tags
* Deploy application to Kubernetes

```bash
trigger:
  - main

pool:
  name: Agents

steps:
  - task: CmdLine@2
    displayName: "Syntax check (fail fast)"
    inputs:
      script: |
        python -m py_compile flask_app.py

  - task: CmdLine@2
    displayName: "Building Docker Image"
    inputs:
      script: |
        docker build -t mkbmr/my-flask-app:$(Build.BuildNumber) .

  - task: CmdLine@2
    displayName: "Push Image"
    inputs:
      script: |
        docker push mkbmr/my-flask-app:$(Build.BuildNumber)

  - task: CmdLine@2
    displayName: "Update Deployment Image tag"
    inputs:
      script: |
        set -e
        kubectl get namespace flask-app || kubectl create namespace flask-app
        TAG=$(Build.BuildNumber)
        sed -i "s|image: .*|image: mkbmr/my-flask-app:$TAG|g" deploy/flask-app-deployment.yaml
        git --no-pager diff -- deploy/flask-app-deployment.yaml || true

  - task: CmdLine@2
    displayName: "Applying Updated Manifest"
    inputs:
      script: |
        kubectl apply -f deploy/flask-app-service.yaml -n flask-app
        kubectl apply -f deploy/flask-app-deployment.yaml -n flask-app
        kubectl rollout status deployment/flask-app -n flask-app --timeout=60s

```

## Trigger Automated Pipeline

Make changes to the flask_app.py or to any of the HTML files in the templates folder.

**If pipeline is successfull, changes made will be seen on the website after your pipeline task is completed.**

If there are errors, click on the task jobs in the AzureDevops Pipeline page and see what are the errors.


## Troubleshooting

Common issues encountered during setup:

### ImagePullBackOff

Usually caused by:
* Incorrect DockerHub credentials
* Missing Kubernetes secret
* Incorrect image name or tag

### CrashLoopBackOff

Usually caused by:

* Flask application errors
* Missing dependencies (eg missing requirements.txt)
* incorrect container port configuration

Check errors using the following commands:

```bash
# Get all pod
kubectl get pods -n flask-app

# Image/loopback issues
kubectl -n flask-app describe pod -l components=flask-demo-app

# See pod's logs
kubectl logs <pod-name> -n flask-app
```

## Learning Outcome
* CI/CD Fundamentals
* Kubernetes Deployments
* Docker Image Management
* Azure DevOps Pipelines
* Self-hosted Agents
* Container Orchestration

## Future Improvements
* Add Helm charts
* Add GitHub Actions workflow
* Add Ingress controller
* Add monitoring with Prometheus and Grafana
* Add automated rollback strategy
* Add Terraform provisioning

## Author

Khalis Ruzli
