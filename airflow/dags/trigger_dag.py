from airflow.decorators import dag, task
from airflow.triggers.temporal import TimeDeltaTrigger
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 3, 24),
    "catchup": False,
}


@dag(
    dag_id="my_trigger_dag",
    schedule_interval="@daily",
    default_args=default_args,
)
def trigger_example():
    from airflow.operators.empty import EmptyOperator
    from airflow.operators.trigger_dagrun import TriggerDagRunOperator

    start = EmptyOperator(task_id="start")

    trigger_task = TriggerDagRunOperator(
        task_id="deferred_trigger",
        trigger_dag_id="task_group_dag",
        wait_for_completion=True,
        deferrable=True,
    )

    end = EmptyOperator(task_id="end")

    start >> trigger_task >> end


trigger_example()
