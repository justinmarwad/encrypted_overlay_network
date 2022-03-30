import socket, requests, json, ssl, os, json  

## OUR CLIENT CODE ##
class Client: 
    """ Main client code..."""
    def __init__(self, name="Rick_Astley", certfile=None, keyfile=None, port=9090, server="https://127.0.0.1:5000"): 
        self.name=name
        self.certfile=certfile
        self.keyfile=keyfile


        self.port=port  
        self.server=server 

    def create_keys(self, keyfile="server.key", certfile="server.crt"): 
        """ Method to create keys and then self sign them. """

        # 1. Delete all the temp files 
        # 2. Name keys to random key name 

        os.system("openssl genrsa -des3 -out {keyfile}.orig.key 2048")
        os.system("openssl rsa -in {keyfile}.orig.key -out {keyfile}")
        os.system("openssl req -new -key {keyfile} -out {certfile}")
        os.system("openssl x509 -req -days 365 -in {certfile} -signkey {keyfile} -out {certfile}")


    def get_client_list(self, client_ip="127.0.0.1"): 
        """ Method to get a list of clients from the server. """

        response = requests.post(self.server, data=dumps({
            "client_name": self.name, 
            "client_ip": client_ip,
            "client_key": client_pub_key 
        }), verify=False)

        if response.status_code == 200: 
            return(json.loads(response.content)["clients"])
        else:
            raise Exception(f"[ERROR] Could not recieve information from the server {self.server}.")



    def run(self): 
        """ Main method: this is where the magic happens!"""
        clients = self.get_client_list()

        for client in clients: 
            print(f"[INFO] Found {client['client_name']}@{client['client_ip']}")

            # Use threads or multiprocessing to run these at the same time -- or impliment a queue 
            self.send(client["client_name"], client["client_ip"])
            self.recieve()
        
    def send(self, client_name, client_ip="127.0.0.1", message="ping"): 
        """ Method to send message to another client. """

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.verify_mode = ssl.CERT_OPTIONAL 
        context.check_hostname = False
        context.load_verify_locations(self.CA_pem_key)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                print(ssock.version())

        connection = socket(AF_INET, SOCK_STREAM)
        connection.connect((client_ip, self.port))

        connection.send(str.encode(dumps({
            "message": message,
            "client_name": self.name 
        })))

        print(f'[INFO] Response from {client_name}@{client_ip}: {connection.recv(32).decode()}')
        connection.close()

    def recieve(self): 
        """ Method to recieve message to another client. """

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(self.client_pem_key, self.client_priv_key)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            sock.bind(("0.0.0.0", self.port))
            sock.listen(10)

            with context.wrap_socket(sock, server_side=True) as tls_socket:
                conn, addr = tls_socket.accept()

                connstream = ssl.wrap_socket(
                    conn,
                    server_side=True,
                    certfile=self.certfile,
                    keyfile=self.keyfile
                )
                
                try:
                    deal_with_client(connstream)
                finally:
                    connstream.shutdown(socket.SHUT_RDWR)
                    connstream.close()

                data = tls_socket.recv(2048)
                print(data)
                # message = loads(data.decode())
                
                tls_socket.send(b"pong") 

        # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        # context.load_cert_chain(certfile="cert.pem", keyfile=self.client_pem_key)

        # s = socket.socket()
        # s.bind(("0.0.0.0", self.port))
        # s.listen(10)

        # while True:
        #     temp_socket, fromaddr = s.accept()
        #     tls_socket = context.wrap_socket(temp_socket, server_side=True)
        #     try:
        #         data = tls_socket.recv(1024)
        #         while data:
        #             print(data)
        #             data = tls_socket.recv(1024)
        #             # message = loads(data.decode())

        #         tls_socket.send(b"pong") 

        #     finally:
        #         tls_socket.shutdown(socket.SHUT_RDWR)
        #         tls_socket.close()

if __name__ == '__main__':
    Client().run(name="client1")