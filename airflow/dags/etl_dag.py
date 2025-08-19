from datetime import datetime, timedelta
from airflow import DAG
from docker.types import Mount
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator
import subprocess

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}

def run_elt_script():
    script_path = "/opt/airflow/elt/elt_script.py"
    result = subprocess.run(["python", script_path], capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Script failed with error: {result.stderr}")
    else:
        print(result.stdout)

# Create dbt profile inline
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

t1 = PythonOperator(
    task_id="run_elt_script",
    python_callable=run_elt_script,
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

t1 >> t1_5 >> t2