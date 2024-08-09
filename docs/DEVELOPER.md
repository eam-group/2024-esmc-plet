# DEVELOPER.md

This document is intended to help a developer get up and running with the PLET module.

## Table of Contents

1. [Code Structure](#1-code-structure)

2. [Notable Technologies Used](#2-notable-technologies-used)

3. [General Notes](#3-general-notes)

4. [AWS Server Setup](#4-development-environment-setup)

5. [Common Development Tasks](#5-common-development-tasks)

6. [Testing and Debugging](#6-testing-and-debugging)

7. [Version Control](#7-version-control)

8. [Contact Information](#8-contact-information)

## 1. Code Structure

- __code__ - Contains all code associated with the PLET module.
    - `__init__.py` - Initializes PLET module functions.
    - `flask_app.py` - Configuration for deploying the PLET module flask app.
    - `main.py` - The root of the PLET module.
    - `plet_functions.py` - Contains key PLET module functions.
    - [other data processing scripts? XXXX]
- __data__ - Contains all data required to run the PLET module.
- __docs__ - Contains all of the documentation for the PLET module.
- __lookups__ - Contains all the lookup tables required to run the PLET module.
- `.gitignore` - Specifies all of the files that will __not__ be version controlled using git.
- requirements.txt - Dependencies for the PLET module.
- `README.md` - Describes a broad overview of the PLET module. See __docs__ for more information.

## 2. Notable Technologies Used

- [Flask](https://flask.palletsprojects.com/en/1.1.x/) - Flask is a lightweight web app framework written in Python. It is used for the PLET module backend.
- [Python](https://www.python.org/downloads/release/python-390/) - Python (version 3.9) is used here for data analysis.
- [nginx](https://nginx.org/en/) - nginx is a web server software for reverse proxy, load banalcing, and caching to maximize stability and performance. nginx receives the request and then passes it to gunicorn and then passes the reply from gunicorn back to the original client.
- [gunicorn](https://gunicorn.org/) - gunicorn is a Python-based application server software used to handle multiple, simulatious requests. gunicorn will process the request from nginx.
- [git](https://git-scm.com/) - Git is used for version control and collaboration.

## 3. General Notes

[add any additional details here XXXX]

## 4. Amazon Web Services (AWS) Server Setup

[should we include this? they will not have to do this b/c they have their own server. XXXX]

## 5. Common Development Tasks

### 5.1 Clone the Git Repository

### 5.2 Install Python on the Virtual Environment

### 5.3 Install the Flask Python Package

### 5.4 Test the Flask App

### 5.5 Install gunicorn

### 5.6 Start a gunicorn Service

### 5.7 Install nginx

### ???? Test the Flask App again?

## 6. Testing and Debugging



## 7. Version Control



## 8. Contact Information

