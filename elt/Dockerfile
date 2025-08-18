FROM python:3.8-slim

# Install PostgreSQL 17 client tools
RUN apt-get update && apt-get install -y postgresql-client

COPY elt_script.py .

CMD ["python", "elt_script.py"]