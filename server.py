#!/usr/bin/env python3

from bluetooth import *
import sys
import pickle
import pika
import time
import requests
import json
from pymongo import MongoClient
from rmq_params import rmq_params
from cryptography.fernet import Fernet
from keys import key1


#key = Fernet.generate_key()
#f1 = Fernet(key)
f = Fernet(key1)

client = MongoClient('localhost', 27017)
db = client.BT
users = db.users


#
# TESTING for easily inserting new documents to the mongodb database
def insertM():
    #name = 'Armon'
    token = '4511~3NiLJMyYdKLs22i357zSfk3Q0Aayn6pSJS536U5dCbmF91K160CPJSUa9OHDUbcO'
    MAC = '14:56:8E:0F:4E:88'
    users.insert({'token':f.encrypt(token.encode()), 'MAC':MAC})
    #name = 'Andrew'
    token = '4511~GQcH0fUmjvtRoFawOBpCSmRyMM9mG3JwG6VS8MuczKlPfVO298Tl0iOSl8cmiCG6'
    MAC = '40:4E:36:5A:46:6E'
    users.insert({'token':f.encrypt(token.encode()), 'MAC':MAC})
#
#
#insertM()

# TESTING for changing a plaintext name to an encrypted one
def postM():
    entry = users.find_one({'name':'Armon'})
    name = entry['name']
    MAC = entry['MAC']
    users.replace_one({'name':'Armon'}, {'name':f.encrypt(name.encode()), 'MAC':f.encrypt(MAC.encode())})
    print(users.find_one({'MAC':entry['MAC']}))

#postM()


VHOST = rmq_params['vhost']
USERNAME = rmq_params['username']
PASSWORD = rmq_params['password']
EXCHANGE = rmq_params['exchange']
BT_QUEUE = rmq_params['bt_queue']
IO_QUEUE = rmq_params['io_queue']
ACK_QUEUE = rmq_params['ack_queue']

HOST = 'localhost'

IO_ROUTE = 'IO'
BT_ROUTE = 'BT'
ACK_ROUTE = 'ACK'
PORT = '5672'

credentials = pika.PlainCredentials(USERNAME, PASSWORD)
params = pika.ConnectionParameters(HOST, PORT, VHOST, credentials)

connection = pika.BlockingConnection(params)
channel = connection.channel()

print("Connected to vhost '%s' on RMQ server at '%s' as user '%s'" % (VHOST, HOST, USERNAME))
print('Setting up exchanges and queues...')

channel.exchange_declare(EXCHANGE, exchange_type='direct', auto_delete=True)

channel.queue_declare(queue=IO_QUEUE, auto_delete=True)
channel.queue_bind(exchange=EXCHANGE, queue=IO_QUEUE, routing_key=IO_ROUTE)

channel.queue_declare(queue=BT_QUEUE, auto_delete=True)
channel.queue_bind(exchange=EXCHANGE, queue=BT_QUEUE, routing_key=BT_ROUTE)

channel.queue_declare(queue=ACK_QUEUE, auto_delete=True)
channel.queue_bind(exchange=EXCHANGE, queue=ACK_QUEUE, routing_key=ACK_ROUTE)

############################################################

clear = False

def callback(ch, method, properties, body):
    global clear
    newbody = body.decode()
    if (newbody == 'end'):
        print('User exited room. Returning room to normal.')
        print('')
        eload = {'Projector':'Up', 'Lights':'0', 'Blinds':'Open'}
        loads = pickle.dumps(eload)
        channel.basic_publish(exchange=EXCHANGE, routing_key=IO_ROUTE, body=loads)
        clear = False
        return 0
    else:
        print('Recieved MAC address: %s' % newbody)
    if (clear):
        return 0
    dic = users.find_one({'MAC':newbody})
    if dic == None:
        print('Unrecognized MAC: %s' % newbody)
        print()
        load = pickle.dumps(['Invalid', newbody])
        channel.basic_publish(exchange=EXCHANGE, routing_key=ACK_ROUTE, body=load)
        return 0
    print('Valid MAC Address')
    load = pickle.dumps(['Valid', newbody])
    channel.basic_publish(exchange=EXCHANGE, routing_key=ACK_ROUTE, body=load)
    clear = True
    name = f.decrypt(dic['token'])
    #print(name.decode())
    access_token = name.decode()
    #access_token = '4511~GQcH0fUmjvtRoFawOBpCSmRyMM9mG3JwG6VS8MuczKlPfVO298Tl0iOSl8cmiCG6'
    down_url = 'https://canvas.vt.edu/api/v1/users/self/folders/by_path/MyProfile'
    # Set up a session
    session = requests.Session()
    session.headers = {'Authorization': 'Bearer %s' % access_token}
    r = session.get(down_url)
    r.raise_for_status()
    r = r.json()
    leng = len(r)
    for i in range(0, leng):
        if(r[i]['name'] == 'MyProfile'):
            down_url = str(r[i]["files_url"])

    r = session.get(down_url)
    r.raise_for_status()
    r = r.json()
    leng = len(r)
    for i in range(0, leng):
        #print (r[i]['filename'])
        if(r[i]['filename'] == 'class_profile.txt'):
            down2_url = str(r[i]["url"])
    r = session.get(down2_url)
    r.raise_for_status()
    t = r.content.decode("ascii")
    t2 = json.loads(t)
    print(t2)
    print('')
    send = pickle.dumps(t2)
    channel.basic_publish(exchange=EXCHANGE, routing_key=IO_ROUTE, body=send)

channel.basic_consume(callback, queue=BT_QUEUE, no_ack=True)
print("Consuming from RMQ queue: %s"%(BT_QUEUE))
print('')
channel.start_consuming()