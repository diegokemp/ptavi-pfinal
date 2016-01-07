#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys

XML = sys.argv[1]
METODO = sys.argv[2]
opcion = sys.argv[3]

if METODO == "REGISTER":
    mensaje = "REGISTER sip:leonard@bigbang.org:1234 SIP/2.0\r\n" + \
                "Expires: " + opcion
    print(mensaje)
elif METODO == "INVITE":
    mensaje = "INVITE sip:" + opcion + " SIP/2.0\r\n" + \
                "Content-Type: application/sdp\r\n\r\n" + \
                "v=0\r\n" + "o=leonard@bigbang.org 127.0.0.1\r\n" + \
                "s=misesion\r\n" + "t=0\r\n" + "m=audio 34543 RTP"
    print(mensaje)
elif METODO == "BYE":
    mensaje = "BYE sip:" + opcion + "SIP/2.0\r\n"
    print(mensaje)

IP = "127.0.0.1"
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((IP, 3443))

my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
i=0
while i < 1:
    data = my_socket.recv(1024)
    respuesta = data.decode('utf-8')
    if respuesta != "":
        print(respuesta)
        serv_resp = respuesta.split(" ")
        print(serv_resp)
        if serv_resp[1] == "100":
            pass
        elif server_resp[1] == "180":
            pass
        elif server_resp[1] == "200":
            pass
            print("BIENNNN")
            #send[invite//ack//cierre]?¿?¿?¿
        elif server_resp[1] == "400":
            i = 2
        elif server_resp[1] == "401":
            reauten = mensaje + "\r\n" + \
                        "Authorization: response=1232132123211223213212"
        elif server_resp[1] == "404":
            i = 2
        elif server_resp[1] == "405":
            i = 2
my_socket.close()
print("THE END")
