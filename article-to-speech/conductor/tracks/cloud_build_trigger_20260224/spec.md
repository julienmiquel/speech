# Specification: Cloud Build Trigger for Auto-Deployment

## Overview
This track aims to automate the build, test, and deployment process for the "article-to-speech" project using Google Cloud Build. Every commit to the repository (specifically targeting the staging/development environment) will trigger a workflow that runs tests, builds a Docker image, and deploys the application to Cloud Run.

## Functional Requirements
- **Automated Trigger:** Configure a Cloud Build trigger connected to the GitHub repository.
- **Continuous Integration (CI):**
    - Execute the test suite (using `pytest`) on every push.
    - Ensure build fails if tests do not pass.
- **Containerization:**
    - Build a Docker image from the project's `Dockerfile`.
    - Push the image to Google Artifact Registry.
- **Continuous Deployment (CD):**
    - Deploy the built image to Google Cloud Run.
    - Targeting the Staging/Dev environment.

## Non-Functional Requirements
- **Reliability:** Deployment should only occur if all previous steps (testing and building) succeed.
- **Security:** Use appropriate service accounts and IAM roles for Cloud Build to interact with Artifact Registry and Cloud Run.
- **Observability:** Logs for each build and deployment step should be accessible in the Google Cloud Console.

## Acceptance Criteria
- [ ] Cloud Build trigger is successfully created and linked to the GitHub repository.
- [ ] A push to the branch triggers a new build.
- [ ] The build successfully executes `pytest`.
- [ ] A Docker image is created and stored in Artifact Registry.
- [ ] The application is deployed to Cloud Run.
- [ ] The deployment URL is accessible and the application is functional.

## Out of Scope
- Production environment setup (this trigger is for Staging/Dev).
- Automated rollback mechanism (can be added in a future track).
- Infrastructure as Code (Terraform) for initial project setup (will be done manually or via script).
