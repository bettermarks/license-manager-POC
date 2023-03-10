# pull official base image
FROM python:3.11.0-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /code
WORKDIR /code

RUN python3 -m pip install --no-cache-dir -IU pip 

RUN pip install --no-cache-dir .
RUN pip install --no-cache-dir -r requirements-dev.in
# RUN pytest --cov licensing
