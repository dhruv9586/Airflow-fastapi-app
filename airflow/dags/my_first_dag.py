from datetime import datetime


from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from custom_operators.my_operator import MyCustomOperator


def hello():
    print("Hello, Airflow! I am first task.")


default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 3, 20),
    "catchup": False,
}

with DAG(
    dag_id="my_first_dag", default_args=default_args, schedule_interval="@daily"
) as dag:
    task1 = PythonOperator(task_id="first_task", python_callable=hello)
    task2 = BashOperator(
        task_id="second_task",
        bash_command="echo hey, i am second task, will be running after first task",
    )

    custom_operator_task = MyCustomOperator(
        task_id="write_to_file",
        file_path="/tmp/airlfow_custom_operator.txt",
        content="Hello i am custom operator",
    )

    task1 >> task2 >> custom_operator_task
