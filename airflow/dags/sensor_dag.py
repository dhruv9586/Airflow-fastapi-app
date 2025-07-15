from datetime import datetime
from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import PythonOperator

default_args = {"owner": "dhruv", "start_date": datetime(2025, 3, 21), "retries": 1}

with DAG(
    dag_id="my_sensor_dag",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
) as dag:

    wait_for_file = FileSensor(
        task_id="wait_for_file",
        filepath="/tmp/data.csv",
        poke_interval=30,
        timeout=600,
        mode="reschedule",  # reschedule
    )

    def process_file():
        print("Got the file and processing is done...")

    process_task = PythonOperator(task_id="process_file", python_callable=process_file)

    wait_for_file >> process_task
