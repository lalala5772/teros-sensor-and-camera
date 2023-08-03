import sys
import time
import json
import boto3
import serial
import schedule
from datetime import datetime
from picamera import PiCamera
from multiprocessing import Process, Lock
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
# import pymysql

#Pi Camera
camera = PiCamera()


#Arduino
PORT = '/dev/ttyACM0'
BaudRate = 9600

ARD= serial.Serial(PORT,BaudRate)



#For AWS MQTT, S3 
ENDPOINT = "a1uzkrfj5nueia-ats.iot.ap-northeast-2.amazonaws.com"
CLIENT_ID = "semsPi"
PATH_TO_CERT = "/home/pi/certification/b6d2a152084610caf7945cd67e0cf8b7cc4080fa0cdf88bac1c79a5ecb555a8f-certificate.pem.crt"
PATH_TO_KEY = "/home/pi/key/b6d2a152084610caf7945cd67e0cf8b7cc4080fa0cdf88bac1c79a5ecb555a8f-private.pem.key"
PATH_TO_ROOT = "/home/pi/CA/AmazonRootCA1.pem"
TOPIC = "test/testing" 
BUCKET_NAME = "semstestbucket"
AWS_ACCESS_KEY = 'AKIA6GY63CLQL4P7VTP4'
AWS_SECRET_KEY = '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'
AWS_REGION= 'ap-northeast-2'
DYNAMODB_TABLE = 'TEROS_TB'


def publish_Data():
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
    
    #teros sensor value 가져오기
    print('Begin Publish')
    data = sensorData()
    soilMoist = float(data[0])
    temperature = float(data[1])
    state = data[2]
        
    message = { "soilMoist" : soilMoist, "temperature" : temperature, "state" : state}
    mqtt_connection.publish(topic=TOPIC, payload=json.dumps(message), qos=mqtt.QoS.AT_LEAST_ONCE)
    print("Published: '" + json.dumps(message) + "' to the topic: " + "'test/testing'")
    time.sleep(0.1)
    print('Publish End')
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    

def sensorData():
    time.sleep(0.1)
    lock.acquire()

    Data = ARD.readline().decode()

    DataList = Data.split(',')
    lock.release()

    return DataList
        

#로컬 db에 저장하던 코드 -> 현재 사용 X
# def dbsaver():
#     data = sensorData()
    
#     sensordb = pymysql.connect(
#     user='root',
#     passwd='',
#     host='127.0.0.1',
#     db='testDB'
#     )
    
#     cursor = sensordb.cursor(pymysql.cursors.DictCursor)

    
#     try:
#         sql = "INSERT INTO sensor(date, soilMoist, temperature, state) VALUES(DEFAULT, %s, %s, %s)"
#         val = (float(data[0]), float(data[1]), data[2])
#         cursor.execute(sql, val)
    
#         sensordb.commit()
    
#     finally:
#         sensordb.close()
#         print(data)


def upload_to_s3(BUCKET_NAME, file_name, s3_file):
    s3 = boto3.resource('s3')
    s3.Bucket(BUCKET_NAME).upload_file(file_name, s3_file)
        

def exit():
    sys.exit()

def take_Pic():
    file_name = '/home/pi/Pictures/image.jpg'

    camera.start_preview()

    time.sleep(3)

    camera.capture(file_name)

    camera.stop_preview()

    s3_file = 'images/' + time.strftime('%Y-%m-%d-%H-%M-%S') + '.jpg'
    boto3.setup_default_session(aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    upload_to_s3(BUCKET_NAME, file_name, s3_file)



def auto_Mqtt():
    schedule.every().day.at("09:00").do(publish_Data)
    schedule.every().day.at("13:00").do(publish_Data)
    schedule.every().day.at("17:00").do(publish_Data)

    while True:
        schedule.run_pending()
        time.sleep(1)  
    
    
def auto_Cam():
    schedule.every().day.at("09:00").do(take_Pic)
    schedule.every().day.at("13:00").do(take_Pic)
    schedule.every().day.at("17:00").do(take_Pic)

    while True:
        schedule.run_pending()
        time.sleep(1)



    
#로컬 db에 저장하는 코드 -> 현재 사용 X
# def auto_DB():
#     #test
#     schedule.every().day.at("16:11").do(dbsaver)
#     schedule.every().day.at("09:31").do(dbsaver)

#     while True:
#         schedule.run_pending()
#         time.sleep(1)
    
    

    
if __name__ == '__main__':
    lock = Lock()
 
    cam_process = Process(target = auto_Cam)
    mqtt_process = Process(target = auto_Mqtt)
    # db_process = Process(target = auto_DB)
        
    cam_process.start()
    mqtt_process.start()
    # db_process.start()
        
    cam_process.join()
    mqtt_process.join()
    # db_process.join()

