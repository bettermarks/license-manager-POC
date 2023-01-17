# pull official base image
FROM python:3.11.0-alpine as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /code
WORKDIR /code

RUN python3 -m pip install --no-cache-dir -IU pip 
# TODO:shiv

RUN pip install --no-cache-dir .
RUN pip install --no-cache-dir -r requirements-dev.in
# RUN pytest --cov bm

# CMD [“uvicorn”, bm.main:app”, “ --host=0.0.0.0”, “--reload”]

# RUN shiv . --compile-pyc -c bm-ucm -o app.pyz


# # install dependencies
# RUN set -eux \
#     && apk add --no-cache --virtual .build-deps build-base \
#          openssl-dev libffi-dev gcc musl-dev python3-dev \
#         postgresql-dev bash \
#     && rm -rf /root/.cache/pip
