# Interview-video-analysis

This repo is a web application that allows you to analyze interview videos and generate a report of the candidate's performance.

## Requirements

- Python 3.10
- pip
- Docker

### Docker compose Setup:

Steps to setup the app using docker compose:

1. create a .env file and add the following variables:  
```bash
GEMINI_API_KEY = "your_gemini_api_key"
AZURE_SUBSCRIPTION_KEY = "your_azure_subscription_key"
```
2. Build the docker image and run the container
```bash
docker compose up --build
```
3. Open the browser and navigate to http://localhost:80





