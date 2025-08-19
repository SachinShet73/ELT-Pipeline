from datetime import datetime
from airflow import DAG
from docker.types import Mount
from airflow.utils.dates import days_ago
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.python_operator import PythonOperator
import subprocess

# You'll need to update this after creating the connection in Airbyte UI
CONN_ID = 'your-connection-id-here'  # Update this after setting up Airbyte connection

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
    'elt_and_dbt_with_airbyte',
    default_args=default_args,
    description='An ELT workflow with Airbyte and dbt',
    start_date=datetime(2025, 8, 19),
    catchup=False,
    schedule_interval='@daily'
)

# Task 1: Trigger Airbyte sync
t1 = AirbyteTriggerSyncOperator(
    task_id="airbyte_postgres_to_postgres",
    airbyte_conn_id='airbyte_default',  # This is the Airflow connection to Airbyte
    connection_id=CONN_ID,  # This is the Airbyte connection ID
    asynchronous=False,
    timeout=3600,
    wait_seconds=3,
    dag=dag
)

# Task 2: Create dbt profile
t2 = PythonOperator(
    task_id="create_dbt_profile",
    python_callable=create_dbt_profile,
    dag=dag
)

# Task 3: Run dbt transformations
t3 = DockerOperator(
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
    mount_tmp_dir=False,
    mounts=[
        Mount(source='/opt/dbt',  # Updated to use container path
              target='/dbt', type='bind'),
        Mount(source='/opt/dbt',  # Updated to use container path
              target='/root', type='bind') 
    ],
    dag=dag
)

# Task 4: Run dbt tests
t4 = DockerOperator(
    task_id="dbt_test",
    image='ghcr.io/dbt-labs/dbt-postgres:1.4.7',
    command=[
        "test",
        "--profiles-dir",
        "/root",
        "--project-dir",
        "/dbt"
    ],
    auto_remove=True,
    docker_url='unix://var/run/docker.sock',
    network_mode="elt-pipeline_elt_network",
    mount_tmp_dir=False,
    mounts=[
        Mount(source='/opt/dbt',
              target='/dbt', type='bind'),
        Mount(source='/opt/dbt',
              target='/root', type='bind') 
    ],
    dag=dag
)

# Set up task dependencies
t1 >> t2 >> t3 >> t4