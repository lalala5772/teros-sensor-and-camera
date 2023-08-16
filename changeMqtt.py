import sys
import time
import json
import boto3
from datetime import datetime
from multiprocessing import Process, Lock
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder

#For AWS MQTT, S3 
ENDPOINT = "a1uzkrfj5nueia-ats.iot.ap-northeast-2.amazonaws.com"
CLIENT_ID = "semsPi"
PATH_TO_CERT = "/home/pi/certification/b6d2a152084610caf7945cd67e0cf8b7cc4080fa0cdf88bac1c79a5ecb555a8f-certificate.pem.crt"
PATH_TO_KEY = "/home/pi/key/b6d2a152084610caf7945cd67e0cf8b7cc4080fa0cdf88bac1c79a5ecb555a8f-private.pem.key"
PATH_TO_ROOT = "/home/pi/CA/AmazonRootCA1.pem"
TOPIC = "test/testing" 
BUCKET_NAME = "semstestbucket"
AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''
AWS_REGION= 'ap-northeast-2'
DYNAMODB_TABLE = 'TEROS_TB'


event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=PATH_TO_CERT,
            pri_key_filepath=PATH_TO_KEY,
            client_bootstrap=client_bootstrap,
            ca_filepath=PATH_TO_ROOT,
            client_id=CLIENT_ID,
            clean_session=False,
            keep_alive_secs=6
            )

connect_future = mqtt_connection.connect()
connect_future.result()
print("Connected!")
    
    
print('Begin Publish')
soilMoist = 20.3
temperature = 26.1
state = "low"
imageUrl = "https://semstestbucket.s3.ap-northeast-2.amazonaws.com/4-26-16-6.jpg"

last_id = get_last_id_from_database()  
next_id = last_id + 1
        
topic = f"test/{next_id}/testing"
    
message = {"soilMoist": soilMoist, "temperature": temperature, "state": state}
mqtt_connection.publish(topic=topic, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
print("Published: '" + json.dumps(message) + "' to the topic: " + topic)
time.sleep(0.1)
print('Publish End')
disconnect_future = mqtt_connection.disconnect()
disconnect_future.result()
