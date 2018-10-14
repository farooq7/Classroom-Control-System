# The same copy of this file should be used by 
# server.py, led.py, processor.py and client.py.
# Each use this to establish a connection with the RabbitMQ Server.
# DO NOT change the key names in this dictionary.
# Feel free to change the values.
#
# Example:
# rmq_params = {"vhost": "vcoolhost", 
# "username": "bryan", 
# "password": "imahokie123", 
# "exchange": "sysexchange", 
# "order_queue": "orders",
# "led_queue": "ledstatus"}

rmq_params = {"vhost": "myserver", 
"username": "abc", 
"password": "123", 
"exchange": "asdf", 
"bt_queue": "bt",
"io_queue": "io",
"ack_queue":"ack"}