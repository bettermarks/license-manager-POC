# license-manager-POC
A POC for a generic License Manager ...

## Concept
The concept for implementing such a License Manager can be found here:
[License Manager concept](./docs/concept.md)

## Application Start (DEV)
To start the application, you can either start it on your local machine:
```sh
cd <license-manager-POC>
export PYTHONPATH=$PWD/src
uvicorn licm.main:app --reload --workers 1 --host 0.0.0.0 --port 8000
```
Before you can start for the first time, please create a database manually 
on your local postgreSQL database using the SQL query

```sql
CREATE DATABASE licm;
```

Alternatively, you can run the whole application in a Docker container. 
In order to build and start the container, just use the command

```sh
docker compose up -d --build
```

In any case, you can now use the API:

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
