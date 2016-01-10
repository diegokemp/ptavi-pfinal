class ProxySIPHandler(socketserver.DatagramRequestHandler):


    def handle(self):
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            lineutf = line.decode('utf-8')
            if lineutf != "":
                method = lineutf.split(" sip:")
                resp = lineutf.split(" ")
                if method[0]=="REGISTER":
                    tracker = lineutf.split("Expires: ")
                    tracker = tracker[1].split("\r\n")
                    expires = tracker[0]
                    #expires
                    if expires != "0":
                        if tracker[1] != "":
                            print("autorizado")
                            contraseña = tracker[1].split("response=")
                            contraseña = contraseña[1]
                            #contraseña comparar
                            register_resp = "SIP/2.0 200 OK\r\n\r\n"
                            #guardar
                        else
                            print("no autorizado")
                            register_resp = "SIP/2.0 401 Unauthorized\r\n" + \
                                        "WWW Authenticate: nonce=7777777777"
                        self.wfile.write(bytes(register_resp))
                if method[0]=="INVITE":
                    #puertobuscar por @
                    mensaje = lineutf
                    my_socket.connect(("127.0.0.1", PUERTO))
                    my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
                elif method[0]=="ACK":
                    #puertobuscar por @
                    mensaje = lineutf
                    my_socket.connect(("127.0.0.1", PUERTO))
                    my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
                elif method[0]=="BYE":
                    #puertobuscar por @
                    mensaje = lineutf
                    my_socket.connect(("127.0.0.1", PUERTO))
                    my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
                elif resp[1] == "100":
                    print("100--")
                    if resp[3] == "180":
                        print("180--")
                        if resp[5] == "200":
                            print("200 concatenado")
                            #¿?¿
                            #puertobuscar por @
                            mensaje = lineutf
                            my_socket.connect(("127.0.0.1", PUERTO))
                            my_socket.send(bytes(mensaje, 'utf-8') + b'\r\n')
                            #okdelinvite
                            #sdp
                elif resp[1] == "200":
                    #okdelbye
                else:
                    self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")
            if not line:
                break

if __name__ == "__main__":
    try:
        XML = sys.argv[1]
        # uaobj = uaserver(XML)
        # print(uaobj.diccionario["rtport"])
        # servIP = uaobj.diccionario["uasip"]
        # servPort = uaobj.diccionario["uasport"]
        serv = socketserver.UDPServer(("127.0.0.1", 4000), ProxySIPHandler)
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except:
        print("Usage: python3 server.py IP port audio_file")
    print("Listening...")
    serv.serve_forever()
