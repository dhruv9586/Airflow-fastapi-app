from airflow.decorators import dag, task, task_group
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
from airflow.utils.trigger_rule import TriggerRule

default_args = {
    "owner": "dhruv",
    "start_date": datetime(2024, 3, 24),
    "catchup": False,
}


@dag(
    dag_id="trigger_rule_dag",
    schedule_interval="@daily",
    default_args=default_args,
)
def trigger_rule_example():

    start = EmptyOperator(task_id="start")

    @task_group
    def grouped_task():
        @task
        def task_1():
            return "Task 1 "

        @task
        def task_2(result: str):
            return result + " Task 2 "

        @task
        def task_3(result: str):
            print(result + " Task 3 ")

        task_3(task_2(task_1()))

    @task(trigger_rule=TriggerRule.ALL_SUCCESS)
    def all_success():
        print("✅ AllTask succeeded!")

    @task(trigger_rule=TriggerRule.ONE_FAILED)
    def one_failed():
        print("❌ One Task failed!")

    end = EmptyOperator(task_id="end")

    start >> grouped_task() >> [all_success(), one_failed()] >> end


trigger_rule_example()
