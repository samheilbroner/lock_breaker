# Project Name

## Local Setup

1. Install dependencies: 
    pip install -r requirements.txt

2. Set up the development cloud environment: 
    make dev_environment

3. Configure cloud settings and environment variables: 
    make setup

## Cloud Development Environment

1. Set up the development cloud environment: 
    make dev_environment

2. Configure cloud settings: 
    make setup

3. Start the application: 
    make app

## Cloud Production Environment

Follow the steps for the development environment, but use the following command to set up the production environment:
    make prod_environment

## User Management

Users are managed locally using the Flask CLI:

- To create a user, run: 
    flask create-user

- To delete a user, run: 
    flask delete-user

- To list current users, run: 
    flask list-users
