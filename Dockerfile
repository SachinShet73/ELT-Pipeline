FROM apache/airflow:2.10.2

# Install curl for health checks
USER root
RUN apt-get update && apt-get install -y curl && apt-get clean

# Install Docker provider (latest compatible version)
USER airflow
RUN pip install apache-airflow-providers-docker==3.13.0 \
    && pip install apache-airflow-providers-http \
    && pip install apache-airflow-providers-airbyte