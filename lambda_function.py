import json
import boto3
from datetime import datetime
import uuid

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('drowsiness-final')

def lambda_handler(event, context):

    file_key = event['Records'][0]['s3']['object']['key']

    id = str(uuid.uuid4())
    driver_id = int(datetime.now().timestamp())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    table.put_item(
        Item={
            'id': id,
            'driver_id': driver_id,
            'timestamp': timestamp,
            'status': "drowsy",
            'file_name': file_key
        }
    )

    sns.publish(
        TopicArn='arn:aws:sns:ap-south-1:406681475983:drowsiness-alert-topic',
        Message=f"Drowsiness detected! Driver {driver_id} at {timestamp}",
        Subject="Alert"
    )

    return {"statusCode": 200}
