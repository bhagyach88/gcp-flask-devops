# DevOps Capstone Project: Containerized Python Flask Application on Google Cloud

## 1. Project Overview

This project demonstrates a complete DevOps workflow for a containerized Python Flask application on Google Cloud Platform. The application provides a simple REST API to create and retrieve data from a Firestore database. The entire infrastructure is provisioned and managed using the `gcloud` CLI.

## 2. Architecture Flow

```
+-----------+     +----------------+     +-------------------+     +----------------+     +--------------+
| Developer | --> |  GitHub Repo   | --> |   Cloud Build     | --> | Artifact Registry | --> |  Cloud Run   |
+-----------+     +----------------+     +-------------------+     +----------------+     +--------------+
      |                                        | (CI/CD)                 | (Docker Image)          | (Deployment)
      |                                        |                         |                         |
      +----------------------------------------+-------------------------+-------------------------+
                                               |
                                               v
                                     +-----------------+
                                     |   API Gateway   |
                                     +-----------------+
                                               |
                                               v
                                     +-----------------+
                                     | Firestore DB    |
                                     +-----------------+
```

- **Developer:** Pushes code to a Git repository.
- **Cloud Build:** Automatically triggers a build on code changes, runs tests, builds a Docker image, and pushes it to Artifact Registry.
- **Artifact Registry:** Stores the containerized application image.
- **Cloud Run:** Deploys and runs the container image as a scalable serverless service.
- **API Gateway:** Exposes the Cloud Run service through a secure and managed API endpoint.
- **Firestore:** A NoSQL database used by the Flask application to persist data.
- **Cloud Monitoring & Logging:** Provide observability into the application's performance and health.

## 3. Prerequisites

- **Google Cloud Account:** With billing enabled.
- **Google Cloud SDK:** Installed and configured (`gcloud auth login`, `gcloud config set project [PROJECT_ID]`).
- **Git:** Installed on your local machine.

## 4. Project Folder Structure

```
gcp-flask-devops/
├── app/
│   ├── main.py
│   └── requirements.txt
├── Dockerfile
├── cloudbuild.yaml
├── openapi.yaml
└── README.md
```

## 5. Flask Application Setup

The Flask application (`app/main.py`) provides three endpoints:
- `GET /`: Health check.
- `POST /api/data`: Creates a message in Firestore.
- `GET /api/data/{doc_id}`: Retrieves a message from Firestore.

## 6. Docker Containerization

The `Dockerfile` defines the steps to build a container image for the Flask application.

## 7. Artifact Registry Setup

Create a Docker repository in Artifact Registry to store the container images.

```bash
# Set your region
export REGION=us-central1
export REPO_NAME=devops-repo

# Create the repository
gcloud artifacts repositories create $REPO_NAME 
    --repository-format=docker 
    --location=$REGION 
    --description="Docker repository for DevOps project"
```

## 8. CI/CD Pipeline with Cloud Build

The `cloudbuild.yaml` file defines the CI/CD pipeline.

### 8.1. Enable Required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable apigateway.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable iam.googleapis.com
```

### 8.2. Grant Permissions to Cloud Build Service Account

```bash
export PROJECT_ID=$(gcloud config get-value project)
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
export CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

# Grant Cloud Run Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID 
    --member="serviceAccount:${CLOUD_BUILD_SA}" 
    --role="roles/run.admin"

# Grant IAM Service Account User role
gcloud projects add-iam-policy-binding $PROJECT_ID 
    --member="serviceAccount:${CLOUD_BUILD_SA}" 
    --role="roles/iam.serviceAccountUser"

# Grant API Gateway Admin role
gcloud projects add-iam-policy-binding $PROJECT_ID 
    --member="serviceAccount:${CLOUD_BUILD_SA}" 
    --role="roles/apigateway.admin"
```

### 8.3. Create a Cloud Build Trigger

1.  Fork this repository to your GitHub account.
2.  Go to the [Cloud Build Triggers page](https://console.cloud.google.com/cloud-build/triggers).
3.  Click **Create trigger**.
4.  Configure the trigger:
    -   **Name:** `flask-api-trigger`
    -   **Region:** `us-central1`
    -   **Event:** Push to a branch
    -   **Source:** Connect your forked repository.
    -   **Branch:** `main` (or your default branch)
    -   **Configuration:** Cloud Build configuration file (yaml or json)
    -   **Location:** `/cloudbuild.yaml`
5.  Click **Create**.

## 9. Deployment to Cloud Run

The `cloudbuild.yaml` handles the deployment to Cloud Run. The first deployment can also be done manually to verify.

```bash
# Manual deployment (optional)
export SERVICE_NAME=flask-api
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME
gcloud run deploy $SERVICE_NAME 
    --image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME 
    --region=$REGION 
    --platform=managed 
    --allow-unauthenticated
```

## 10. API Gateway Setup

### 10.1. Create a Service Account for the Backend

```bash
export BACKEND_SA_NAME=api-gateway-backend-sa
gcloud iam service-accounts create $BACKEND_SA_NAME 
    --display-name="API Gateway Backend Service Account"

export BACKEND_SA_EMAIL="${BACKEND_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
```

### 10.2. Grant Cloud Run Invoker Role to the Backend SA

```bash
gcloud run services add-iam-policy-binding $SERVICE_NAME 
    --member="serviceAccount:${BACKEND_SA_EMAIL}" 
    --role="roles/run.invoker" 
    --region=$REGION
```

### 10.3. Update `cloudbuild.yaml` and `openapi.yaml`

-   In `cloudbuild.yaml`, replace the `_BACKEND_SA` placeholder with your backend service account email (`$BACKEND_SA_EMAIL`).
-   In `openapi.yaml`, replace the `address` placeholders with your Cloud Run service URL (from the deployment step).

### 10.4. Create the API and Gateway

```bash
export API_NAME=flask-api-gw
export GATEWAY_NAME=flask-gateway

# Create the API
gcloud api-gateways apis create $API_NAME --project=$PROJECT_ID

# Create the Gateway
gcloud api-gateways gateways create $GATEWAY_NAME 
  --api=$API_NAME 
  --location=$REGION 
  --project=$PROJECT_ID
```
The CI/CD pipeline will create the API config and update the gateway.

## 11. Firestore Database Configuration

```bash
# Create Firestore database in Native mode
gcloud firestore databases create --location=nam5 --type=firestore-native
```

## 12. Cloud Monitoring Setup

1.  Go to the [Monitoring page](https://console.cloud.google.com/monitoring).
2.  An workspace will be created automatically if it's the first time.

### Create an Uptime Check

1.  Go to **Uptime checks** and click **Create uptime check**.
2.  Configure the check:
    -   **Target:** Select `Cloud Run Service` and your `flask-api` service.
    -   **Path:** `/`
3.  Click **Create**.

## 13. Cloud Logging Commands

```bash
# View logs for the Cloud Run service
gcloud logging read "resource.type="cloud_run_revision" AND resource.labels.service_name="$SERVICE_NAME"" --limit 50

# View logs for the API Gateway
gcloud logging read "resource.type="api_gateway"" --limit 50
```

## 14. Alert and Notification Setup

### 14.1. Create a Notification Channel

1.  Go to the [Notification channels page](https://console.cloud.google.com/monitoring/alerting/channels).
2.  Click **Add new** and choose a channel type (e.g., Email).
3.  Follow the instructions to set up the channel.

### 14.2. Create an Alerting Policy

1.  Go to **Alerting** and click **Create policy**.
2.  **Select a metric:**
    -   **Resource Type:** `Cloud Run Revision`
    -   **Metric:** `Request Count`
3.  **Configure trigger:**
    -   **Condition:** `is above`
    -   **Threshold:** `10`
    -   **For:** `1 minute`
4.  **Configure notifications:**
    -   Select your notification channel.
5.  **Name the policy** and click **Create policy**.

## 15. Testing the API Endpoint

Once the gateway is updated, get the gateway URL:

```bash
export GATEWAY_URL=$(gcloud api-gateways gateways describe $GATEWAY_NAME --location $REGION --format="value(defaultHostname)")
```

### Test POST endpoint:
```bash
curl -X POST "https://${GATEWAY_URL}/api/data" 
-H "Content-Type: application/json" 
-d '{"message": "Hello from API Gateway!"}'
```
Note the `id` from the response.

### Test GET endpoint:
```bash
# Replace {doc_id} with the ID from the POST response
curl "https://${GATEWAY_URL}/api/data/{doc_id}"
```

## 16. Cleanup Commands

```bash
# Delete Cloud Build trigger
gcloud alpha builds triggers delete flask-api-trigger --region=$REGION

# Delete Cloud Run service
gcloud run services delete $SERVICE_NAME --region=$REGION

# Delete API Gateway
gcloud api-gateways gateways delete $GATEWAY_NAME --location=$REGION

# Delete API
gcloud api-gateways apis delete $API_NAME

# Delete Artifact Registry repository
gcloud artifacts repositories delete $REPO_NAME --location=$REGION

# Delete Firestore documents (manually from console)
# Delete Service Accounts
gcloud iam service-accounts delete $BACKEND_SA_EMAIL

# Remove IAM policy bindings
gcloud projects remove-iam-policy-binding $PROJECT_ID 
    --member="serviceAccount:${CLOUD_BUILD_SA}" 
    --role="roles/run.admin"
gcloud projects remove-iam-policy-binding $PROJECT_ID 
    --member="serviceAccount:${CLOUD_BUILD_SA}" 
    --role="roles/iam.serviceAccountUser"
gcloud projects remove-iam-policy-binding $PROJECT_ID 
    --member="serviceAccount:${CLOUD_BUILD_SA}" 
    --role="roles/apigateway.admin"
```
