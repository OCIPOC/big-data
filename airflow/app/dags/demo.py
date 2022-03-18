from datetime import datetime
from airflow.models import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator


###############################################
# Parameters
###############################################
spark_app_name = "demo"


###############################################
# DAG Definition
###############################################
dag =  DAG(
    dag_id= '{}_pipeline'.format(spark_app_name),
    description="This DAG runs a full workflow for {}.".format(spark_app_name),
    schedule_interval=None,
    start_date=datetime(2022, 2, 26),
    catchup=False,
    tags=[spark_app_name])


document_etl = SparkSubmitOperator(
    task_id="document_etl",
    application="//usr/local/share_storages/spark_jobs/demo/job.py",
    name=spark_app_name,
    dag= dag)

document_etl