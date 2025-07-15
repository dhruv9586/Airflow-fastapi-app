from airflow.decorators import dag, task, task_group
from airflow.operators.empty import EmptyOperator
from datetime import datetime


@dag(
    dag_id="task_group_dag",
    schedule=None,
    start_date=datetime(2024, 3, 20),
    catchup=False,
)
def user_data_pipeline():
    start = EmptyOperator(task_id="start")

    @task_group
    def EXTRACT() -> None:
        @task
        def extract_users():
            print("Extracting user data...")

        @task
        def extract_transactions():
            print("Extracting transactions...")

        extract_users() >> extract_transactions()

    @task_group
    def TRANSFORM() -> None:
        @task
        def clean_data():
            print("Cleaning data...")

        @task
        def normalize_data():
            print("Normalizing data...")

        clean_data() >> normalize_data()

    @task_group
    def LOAD() -> None:
        @task
        def load_to_database():
            print("Loading data into the database...")

        @task
        def generate_report():
            print("Generating report...")

        load_to_database() >> generate_report()

    end = EmptyOperator(task_id="end")

    start >> EXTRACT() >> TRANSFORM() >> LOAD() >> end


user_data_pipeline()
