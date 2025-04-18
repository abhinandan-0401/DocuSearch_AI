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
