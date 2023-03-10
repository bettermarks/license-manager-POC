# license-manager-POC
A POC for a generic License Manager ...

## Concept
The concept for implementing such a License Manager can be found here:
[License Manager concept](./docs/concept.md)

A sequence diagram describing some kind of 'purchasing a license' process and 'redeeming a license' 
process can be found here:
[Purchasing and redeeming process](./docs/purchase_redeem_process.md)

We also describe two architecture models for client-service communication here.
[Client Service Communication](./docs/service-communication.md)

And some comparison between the new 'seat model' and the classic GLU 'Simple Inheritance License Model'.
[General License Models](./docs/seat-model-vs-simple-inheritance-model.md)


## Data Model
This is the currently imple,ented data model:
[License Manager data model](./docs/license-manager-ERD-2023-02-6.svg)

## Installation
Create a 'dotenv' file:
Create a file named '.env' in the root folder of the app and provide your database paramaters and credentials like so:

```
DB_USER=<<your 'postgres' user name (root user of the RDBMS)>>
DB_PASSWORD=<<your 'postgres' users (root user of the RDBMS) password>>
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME=<<the name of the 'license-manager' database you will create in the following step (licm)>>
```
Before you can start the application, you have to install a database. Please create a database manually
on your local postgreSQL database using the SQL query

```sql
CREATE DATABASE licm;
```

Alternatively, you can run the whole application in a Docker container.
In order to build and start the container, just use the command

```sh
docker compose up -d --build
```

## Application Start (DEV)
You can start the application using the following commands:
```sh
cd <license-manager-POC>
export PYTHONPATH=$PWD/src
uvicorn licensing.main:app --reload --workers 1 --host 0.0.0.0 --port 8000
```

You can now use the API:

(If you run the app in docker container)
* API docs: http://localhost:8002/docs
* license API: http://localhost:8002/licenses

(If you run the app by not using Docker)
* API docs: http://localhost:8000/docs
* license API: http://localhost:8000/licenses

## Migrations with 'alembic'

* generate new migrations:
    ```sh
    alembic revision --autogenerate -m "<some meaningful title>"
    ```

* apply the migrations:
    ```sh
    alembic upgrade head
    ```
