from datetime import datetime
from airflow import DAG
from docker.types import Mount
from airflow.utils.dates import days_ago
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from airflow.providers.docker.operators.docker import DockerOperator
import subprocess


CONN_ID = ''

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}


def create_dbt_profile():
    import os
    profile_content = """custom_postgres:
  outputs:
    dev:
      type: postgres
      threads: 1
      host: destination_postgres
      port: 5432
      user: postgres
      pass: secret
      dbname: destination_db
      schema: public
  target: dev"""
    
    os.makedirs('/opt/dbt', exist_ok=True)
    with open('/opt/dbt/profiles.yml', 'w') as f:
        f.write(profile_content)
    print("dbt profile created successfully")

dag = DAG(
    'elt_and_dbt',
    default_args=default_args,
    description='An ELT workflow with dbt',
    start_date=datetime(2025, 8, 19),
    catchup=False
)

t1 = AirbyteTriggerSyncOperator(
    task_id="airbyte_postgres_postgres",
    airbyte_conn_id='airbyte',
    connection_id=CONN_ID,
    asynchronous=False,
    Timeout=3600,
    wait_seconds=3,
    dag=dag
)

t1_5 = PythonOperator(
    task_id="create_dbt_profile",
    python_callable=create_dbt_profile,
    dag=dag
)

t2 = DockerOperator(
    task_id="dbt_run",
    image='ghcr.io/dbt-labs/dbt-postgres:1.4.7',
    command=[
        "run",
        "--profiles-dir",
        "/root",
        "--project-dir",
        "/dbt"
    ],
    auto_remove=True,
    docker_url='unix://var/run/docker.sock',
    network_mode="elt-pipeline_elt_network",
    mount_tmp_dir=False,  # Add this to fix the temp mount issue
    mounts=[
        Mount(source='/Users/sachinshet/Desktop/ELT-Pipeline/custom_postgres',
              target='/dbt', type='bind'),
        Mount(source='/Users/sachinshet/Desktop/ELT-Pipeline/custom_postgres',
              target='/root', type='bind') 
    ],
    dag=dag
)

t1  >> t2