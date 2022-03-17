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
    application="/storages/spark_jobs/{}/document_etl.py".format(spark_app_name),
    name=spark_app_name,
    dag= dag)

paragraph_extract = SparkSubmitOperator(
    task_id="paragraph_extract",
    application="/storages/spark_jobs/{}/document_etl.py".format(spark_app_name),
    name=spark_app_name,
    dag= dag)

field_extract = SparkSubmitOperator(
    task_id="field_extract",
    application="/storages/spark_jobs/{}/document_etl.py".format(spark_app_name),
    name=spark_app_name,
    dag= dag)

ocr = SparkSubmitOperator(
    task_id="ocr",
    application="/storages/spark_jobs/{}/document_etl.py".format(spark_app_name),
    name=spark_app_name,
    dag= dag)

transform_to_json = SparkSubmitOperator(
    task_id="transform_to_json",
    application="/storages/spark_jobs/{}/document_etl.py".format(spark_app_name),
    name=spark_app_name,
    dag= dag)


document_etl >> paragraph_extract >> field_extract >> ocr >> transform_to_json