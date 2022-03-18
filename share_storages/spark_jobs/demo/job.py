print("Job1 say hello!")

from pyspark.sql import SparkSession
import tensorflow as tf
import pandas as pd
import numpy as np
from PIL import Image
import os
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions
from pyspark.sql.functions import col, pandas_udf, PandasUDFType


os.environ['PYSPARK_SUBMIT_ARGS'] = \
    '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.2,' \
    + 'org.apache.spark:spark-streaming-kafka-0-10_2.12:3.0.2,' \
    + 'org.apache.kafka:kafka-clients:3.1.0,org.apache.spark:spark-core_2.12:3.0.2,' \
    + 'org.apache.spark:spark-streaming_2.12:3.0.2,' \
    + 'org.apache.spark:spark-token-provider-kafka-0-10_2.12:3.0.2,' \
    + 'org.apache.hadoop:hadoop-core:1.2.1' \
    + ' pyspark-shell'
    
print("Tensorflow:", tf.__version__)

# Load SS, SC
ss  = SparkSession.builder.master('spark://spark-master:7077') \
                  .appName("test") \
                  .config("spark.executor.memory", "2g") \
                  .config("spark.driver.memory", "2g") \
                  .config("spark.executor.cores", "2") \
                  .config("spark.driver.cores", "2") \
                  .getOrCreate()
sc = ss.sparkContext
print(sc)


def preprocess(img_data):
    img = Image.open(img_data).convert('RGB')
    img = img.resize([224, 224])
    x = np.asarray(img, dtype="float32")
    return preprocess_input(x)

 
def keras_model_udf(model_fn):
    def predict(image_batch_iter):
        model = model_fn()
        for img_series in image_batch_iter:
            processed_images = np.array([preprocess(img) for img in img_series])
            predictions = model.predict(processed_images, batch_size=64)
            predicted_labels = [x[0] for x in decode_predictions(predictions, top=1)]
            yield pd.DataFrame(predicted_labels)
    return_type = "class: string, desc: string, score:float"
    return pandas_udf(return_type, PandasUDFType.SCALAR_ITER)(predict)


model = ResNet50()
bc_model_weights = sc.broadcast(model.get_weights())
 
def resnet50_fn():
    model = ResNet50(weights=None)
    model.set_weights(bc_model_weights.value)
    return model

model = resnet50_fn()

resnet50_udf = keras_model_udf(resnet50_fn)


data = [['//usr/local/share_storages/data/image/flowers/1.png', 'bee'],['//usr/local/share_storages/data/image/flowers/2.png','pot']] 
for i in range(10):
    data+= [['//usr/local/share_storages/data/image/flowers/1.png', 'bee'],['//usr/local/share_storages/data/image/flowers/2.png','pot']] 
pandasDF = pd.DataFrame(data, columns = ['content', 'class']) 

df = ss.createDataFrame(pandasDF)
print(df.show())

predictions = df.withColumn("prediction", resnet50_udf(col("content")))

print(predictions.show())