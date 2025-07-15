from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults


class MyCustomOperator(BaseOperator):
    @apply_defaults
    def __init__(self, file_path: str, content: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path = file_path
        self.content = content

    def execute(self, context):
        with open(self.file_path, "w") as f:
            f.write(self.content)

        self.log.info(f"File written successfully at: {self.file_path}")
