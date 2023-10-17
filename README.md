# Task API

#### Ever Alvarez 9A Software Engineering BIS

---

Task API is a FastAPI-based application for managing tasks. It allows users to perform CRUD (Create, Read, Update, Delete) operations on tasks. This API is protected by Firebase Authentication and provides endpoints for user registration, login, task creation, updating, deletion, and more.

## Table of Contents
- [Overview](#overview)
- [Dependencies](#dependencies)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Options, Head, and Trace Requests](#options-head-and-trace-requests)

## Overview
This FastAPI application is designed for managing tasks with the following features:

- User registration and login using Firebase Authentication.
- Create, read, update, and delete tasks.
- Secure access to tasks based on user authentication.
- Swagger documentation and ReDoc for API reference.

## Dependencies
The following libraries and services are used in this project:

- [FastAPI](https://fastapi.tiangolo.com/): A modern, fast (high-performance) web framework for building APIs.
- [Firebase Authentication](https://firebase.google.com/products/auth): Used for user authentication.
- [Firebase Firestore](https://firebase.google.com/products/firestore): A NoSQL cloud database for storing task data.
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup): Used to interact with Firebase services.
- [python-firebase](https://pypi.org/project/python-firebase/): A Python library for interfacing with Firebase.
- [python-dotenv](https://pypi.org/project/python-dotenv/): For managing environment variables.

## Getting Started
1. Clone this repository to your local machine.
2. Create a Firebase project and configure your credentials.
3. Set the required environment variables in a `.env` file.
4. Install the project dependencies using `pip install -r requirements.txt`.
5. Run the FastAPI application with `uvicorn main:app --reload`.

Make sure to replace `FIREBASE_CREDENTIALS` and other necessary environment variables with your Firebase project configuration.

## API Endpoints
The API provides the following endpoints:

- `POST /register`: User registration.
- `POST /login`: User login.
- `GET /tasks`: Retrieve user-specific tasks.
- `POST /task`: Create a new task.
- `PUT /task/{task_id}`: Update a task.
- `DELETE /task/{task_id}`: Delete a task.
- `PATCH /task/{task_id}/complete`: Mark a task as completed.

For detailed request and response examples, refer to the [Swagger Documentation](/), [ReDoc](/redoc), or the API endpoints section of the code.

## Authentication
User registration and login are required to access protected API endpoints. Firebase Authentication is used to securely manage user authentication. To register a new user, use the `/register` endpoint, and for login, use the `/login` endpoint. You will receive an access token for making authenticated requests to other endpoints.

## Options, Head, and Trace Requests
The API also supports OPTIONS, HEAD, and TRACE requests:

- `OPTIONS /options`: List supported HTTP methods.
- `HEAD /head`: Retrieve headers.
- `TRACE /trace`: Trace HTTP request details.

These endpoints are primarily used for testing and exploring the available HTTP methods.


Note: [Web browsers do not support TRACE requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/TRACE#browser_compatibility). You can test this endpoint using [cURL](https://curl.se/):

```bash
curl -v -X TRACE https://tasks-api-8-methods-bbf271afd2c6.herokuapp.com/trace
```
