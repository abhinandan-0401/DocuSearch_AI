# DocuSearch_AI

### Project Structure:

The project is organized as follows:

. <br>
├── app.py  - Flask application (routes and API endpoints) <br>
├── config.py - Configuration settings (environment variables, API keys) <br>
├── embedding.py - Functions for generating text embeddings via OpenAI API <br>
├── vector_store.py - In-memory vector database and similarity search logic <br>
├── utils.py - Helper functions (cosine similarity, GPT-4 query handling, etc.) <br>
├── requirements.txt - Python dependencies <br>
├── Dockerfile - Container configuration for Docker <br>
├── .dockerignore - Files to exclude when building the Docker image <br>
├── .env.example - Example environment variable definitions <br>
├── app.yaml - Sample Google App Engine configuration <br>
├── zappa_settings.json - Sample Zappa configuration for AWS Lambda <br>
├── postman_collection.json - Postman collection with example API requests <br>
└── README.md-# Documentation and usage instructions <br>

- app.py: Initializes the Flask app and defines the API endpoints (/documents, /search, /ask, /health).

- config.py: Loads environment variables (using .env) and sets configuration values (e.g. OpenAI API key, model names).

- embedding.py: Contains the function to call OpenAI's embedding API (text-embedding-ada-002) and obtain vector embeddings for text.

- vector_store.py: Implements a simple in-memory vector store to save document embeddings and perform similarity search (cosine similarity).

- utils.py: Utility functions, including cosine similarity calculation and a helper to query GPT-4 for answering questions using document context.

- requirements.txt: Lists the required Python packages (Flask, OpenAI SDK, etc.).

- Dockerfile: Defines a container image for the API (using gunicorn for production serving).

- .dockerignore: Specifies files and folders to ignore in the Docker build (e.g. .env, local files).

- .env.example: Template for environment variables (fill in your OpenAI API key here, etc).

- app.yaml: Configuration for deploying on Google App Engine (Standard environment) with environment variables.

- zappa_settings.json: Configuration for deploying on AWS Lambda using Zappa.

- postman_collection.json: A Postman collection with sample requests to test the API.


# Setup and Installation

## Prerequisites:

Python 3.9+ (tested with Python 3.10).

An OpenAI API key with access to the GPT-4 model (for question-answering functionality).


## Installation Steps:

### 1. Clone the repository and navigate into it:

git clone https://github.com/yourusername/ai-document-search-api.git
cd ai-document-search-api


### 2. Create a virtual environment (optional, but recommended) and activate it:

python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate


### 3. Install dependencies:

pip install -r requirements.txt


### 4. Configure environment variables:

Copy the file .env.example to .env:

cp .env.example .env

Open .env in a text editor and insert your OpenAI API key. For example:

OPENAI_API_KEY=sk-your-openai-key-here

(Optional) If you do not have access to GPT-4, you can set QA_MODEL=gpt-3.5-turbo in the .env file to use GPT-3.5 for the question-answering endpoint.

*Security: Never commit your actual .env file or API keys to source control. The application will load this API key from the environment at runtime.*

Running the API Locally

After installation and setup, you can run the Flask API locally for testing.

Using Flask's development server (for quick testing):

python app.py

This will start the server on http://localhost:5000.

Using Gunicorn (production WSGI server):

gunicorn --bind 0.0.0.0:5000 app:app

This will run the app with Gunicorn on port 5000. (Gunicorn is installed via requirements.)


Once running, you can use curl, Postman, or a browser to interact with the API endpoints.
For example, to check if the server is running, open http://localhost:5000/health in your browser or via curl.

API Endpoints

The following endpoints are available in the API:

1. POST /documents – Add a Document

Add (or update) a document in the search index by providing an id and text.

Request: JSON body with the document id (a unique identifier for your document) and text (the content of the document).

Response: Confirmation message with the document ID, or an error message.


Example:

curl -X POST -H "Content-Type: application/json" \
  -d '{"id": "doc1", "text": "Jupiter is the largest planet in our solar system."}' \
  http://localhost:5000/documents

Response:

{ "message": "Document added", "id": "doc1" }

2. GET /search – Search Documents

Query the indexed documents for relevant matches using natural language. This uses semantic embedding similarity to find documents related to the query (rather than exact keyword matching).

Request: URL query parameters:

query (required) – The search query string.

k (optional) – Number of top results to return (defaults to 5).


Response: JSON object with the original query and a list of top matching results. Each result includes:

id – Document ID.

score – Similarity score (cosine similarity between query and document embedding).

snippet – A snippet of the document text.



Example:

curl -X GET "http://localhost:5000/search?query=planet"

Response:

{
  "query": "planet",
  "results": [
    {
      "id": "doc1",
      "score": 0.9876,
      "snippet": "Jupiter is the largest planet in our solar system."
    }
  ]
}

(If more documents matched, they would be listed in the "results" array.)

(The above example assumes a document about "Jupiter" was added, and it is returned as a relevant result for the query "planet.")

3. GET /ask – Ask a Question

Ask a natural language question and get an answer derived from the content of the indexed documents. This endpoint uses GPT-4 (or the model you configure) to generate an answer based on the top relevant documents.

Request: URL query parameter:

question (required) – The question to answer using the documents.


Response: JSON object with:

question – The question asked.

answer – The answer generated by the AI, using the documents as context.



The implementation finds the most relevant documents (using embeddings) and provides their content to GPT-4 to formulate a response.

Example:

curl -X GET "http://localhost:5000/ask?question=What is the largest planet in our solar system?"

Response:

{
  "question": "What is the largest planet in our solar system?",
  "answer": "The largest planet in our solar system is Jupiter."
}

Note: The quality of the answer depends on the indexed documents. Ensure you've added relevant documents via /documents (for example, a document about planets for the question above). Also, this endpoint requires an OpenAI API key with access to the GPT-4 model. If you don't have GPT-4 access, adjust the model via the QA_MODEL environment variable as described above.

4. GET /health – Health Check

A simple health-check endpoint to verify that the service is running.

Request: No parameters or body.

Response: JSON with a status and the count of indexed documents. For example:


Example:

curl -X GET http://localhost:5000/health

Response:

{ "status": "ok", "documents_indexed": 1 }

Deployment

This application is designed to be easily deployable on cloud platforms or containers. Below are guides for deploying to Google Cloud and AWS, as well as using Docker.

Deploying to Google Cloud App Engine

You can deploy this API on Google Cloud App Engine (Standard environment):

1. Setup GCP Project: Ensure you have a Google Cloud project with App Engine enabled, and that you have the gcloud CLI installed and authenticated.


2. Update app.yaml: Edit the provided app.yaml file and:

Verify the runtime (e.g., python310 or python311) is correct for your Python version.

Set the OPENAI_API_KEY in the env_variables section (or consider using GCP Secret Manager for greater security).



3. Deploy: Run the following command from the project directory:

gcloud app deploy

This will deploy the application to App Engine. The entrypoint in app.yaml uses Gunicorn to run the app.


4. Access the API: Once deployed, your API will be accessible at your App Engine URL (e.g., https://<your-project-id>.uc.r.appspot.com). You can test the /health endpoint or others to ensure it's working.



Notes:

The App Engine Standard environment will automatically scale instances. The sample app.yaml uses an F2 instance class for more memory; you can adjust this based on your needs.

For App Engine Flex or Cloud Run, you can use the provided Dockerfile. In App Engine Flex, set runtime: custom in app.yaml and deploy (App Engine will build the image using the Dockerfile). For Cloud Run or other container services, build the Docker image and deploy it (see the Docker section below).


Deploying to AWS Lambda (via Zappa)

You can deploy this Flask application to AWS Lambda using the Zappa framework, which handles packaging the app and setting up API Gateway:

1. Setup AWS: Install the AWS CLI and configure your AWS credentials. Also, create an S3 bucket for Zappa to use (for uploading deployment packages).


2. Install Zappa:

pip install zappa


3. Update zappa_settings.json: Modify the provided Zappa settings:

Set your AWS region (e.g., "aws_region": "us-east-1") and an S3 bucket name (for "s3_bucket").

Ensure app_function is "app.app" (pointing to the Flask app object in app.py).

Add your OPENAI_API_KEY under environment_variables.



4. Deploy with Zappa:

zappa deploy dev

This will package and deploy the app to Lambda. On success, Zappa will output an API Gateway URL for your deployed API.


5. Test the API: Use the provided API Gateway URL to test the endpoints (for example, <api-url>/health to check status).



Notes:

The "dev" stage in zappa_settings.json is an example. You can define multiple stages (e.g., dev, staging, prod) with different settings.

Lambda has a default timeout (typically 30 seconds). The /ask endpoint (GPT-4 call) usually responds in a few seconds, but if your use-case might take longer, consider increasing the timeout in Zappa settings.

Instead of Zappa, you can also use AWS SAM or the Serverless Framework to deploy this app. For example, with AWS SAM you could containerize this app using the Dockerfile or use a WSGI adapter (such as mangum or awslambdaric) to run Flask on Lambda. The provided Dockerfile can also be used to deploy on AWS ECS/Fargate or AWS App Runner.


Deploying with Docker (Container)

The included Dockerfile allows you to run the application in any container environment:

1. Build the Image:

docker build -t ai-doc-search-api .


2. Run the Container:

docker run -p 5000:5000 -e OPENAI_API_KEY=<your-openai-key> ai-doc-search-api

This will start the container and map it to port 5000 on your host. The OpenAI API key is passed as an environment variable at runtime for security.


3. Test the API: Open http://localhost:5000/health in your browser (or via curl) to verify the service is running inside the container.



You can deploy this container image to any container-based service:

Google Cloud Run: Use gcloud run deploy with the image (or use Cloud Build to build and deploy in one step).

AWS ECS/Fargate or AWS Lambda (Container Image): Push the image to ECR and deploy to ECS, or deploy the image directly to Lambda as a container image.

Kubernetes or Docker Compose: Incorporate the image into your pod or docker-compose file.


Ensure that you provide the required environment variables (like OPENAI_API_KEY) in your container deployment settings (for example, in Kubernetes Deployment manifest or Cloud Run environment settings).
