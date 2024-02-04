import config
import pandas as pd
import os
import boto3
import pickle
import io

#Set up access to s3 environment
s3 = boto3.resource('s3')
data_bucket = os.environ['data_bucket']

#Read in the original data from s3
try:
    og_file_key = os.environ['og_file_key']
    df_og = pickle.loads(s3.Bucket(data_bucket).Object(og_file_key).get()['Body'].read())
    print("Succeeded in loading original data from s3 bucket")
except:
    print("Error while loading original data from s3 bucket")

#Transform the origal data to synthetic data
df_syn = df_og[0:10000].copy()

#Write synthetic data to s3
try:
    pickle_buffer = pickle.dumps(df_syn)
    s3.Object(bucket_name=data_bucket, key='group_1/df_syn.pkl').put(Body=pickle_buffer)
    print("Succeeded in writing synthetic data to s3 bucket")
except:
    print("Error while writing synthetic data to s3 bucket")