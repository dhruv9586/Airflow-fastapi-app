from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from datetime import datetime


def decide_branch():
    today = datetime.today().weekday()
    if today < 5:
        return "process_task"
    return "skip_task"


default_args = {"owner": "dhruv", "start_date": datetime(2025, 3, 21), "retries": 1}

with DAG(
    dag_id="branch_operator_dag",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
) as dag:

    branch_task = BranchPythonOperator(
        task_id="decide_branch", python_callable=decide_branch
    )

    prcoess_task = PythonOperator(
        task_id="process_task", python_callable=lambda: print("Processing the task")
    )

    skip_task = PythonOperator(
        task_id="skip_task", python_callable=lambda: print("Skipping the task")
    )

    branch_task >> [prcoess_task, skip_task]
