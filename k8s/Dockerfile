FROM python:3.11.0-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code
COPY ./requirements* /code/

RUN python3 -m pip install --no-cache-dir -IU pip 
# RUN python3 -m pip install --no-cache-dir -IU shiv

COPY . /code/
RUN pip install --no-cache-dir .
# RUN shiv . --compile-pyc -c app-ucm -o app.pyz

CMD ["uvicorn", "licensing.main:app", "--host", "0.0.0.0", "--port", ":8000", "--workers", "1"]
