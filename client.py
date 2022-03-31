import socket, requests, json, ssl, os, json, random, string, threading  

## OUR CLIENT CODE ## 
class Client: 
    """ Main client code..."""
    def __init__(self, name="Rick_Astley", certfile=None, keyfile=None, port=9090, server="https://127.0.0.1:5000"): 
        self.name=name
        self.certfile=''.join(random.choices(string.ascii_lowercase, k=5)) + ".crt"
        self.keyfile=''.join(random.choices(string.ascii_lowercase, k=5)) + ".key"

        self.port=port  
        self.server=server 

    def create_keys(self): 
        """ Method to create keys and then self sign them. """ 
        os.system("openssl genrsa -des3 -out temp.orig.key 2048 -passin pass:1qazxsw@! -passout pass:1qazxsw@!")
        os.system("openssl rsa -in temp.orig.key -out {self.keyfile} -pass pass:1qazxsw@!")
        os.system("openssl req -new -key {self.keyfile} -out {self.certfile} -pass pass:1qazxsw@!")
        os.system("openssl x509 -req -days 365 -in {self.certfile} -signkey {self.keyfile} -out {self.certfile} -pass pass:1qazxsw@!")

        os.system("rm temp.orig.key")


    def get_client_list(self, client_ip="127.0.0.1"): 
        """ Method to get a list of clients from the server. """

        response = requests.post(self.server, data=json.dumps({
            "client_name": self.name, 
            "client_ip": client_ip,
            "client_key": self.certfile,
        }), verify=False)

        if response.status_code == 200: 
            return(json.loads(response.content)["clients"])
        else:
            raise Exception(f"[ERROR] Could not recieve information from the server {self.server}.")


        
    def send(self, client_name, client_ip="127.0.0.1", message="ping"): 
        """ Method to send message to another client. """


        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
            with ssl.wrap_socket(s, ca_certs=self.certfile, cert_reqs=ssl.CERT_REQUIRED) as ssl_sock:
                
                ssl_sock.connect((client_ip, self.port))
                
                try:
                    ssl_sock.write(str.encode(json.dumps({
                        "message": message,
                        "client_name": self.name 
                    })))
                    
                    print(f'[INFO] Sent {message} and got response from {client_name}@{client_ip}: {connection.recv(32).decode()}')

                finally:
                    connstream.shutdown(socket.SHUT_RDWR)
                    connstream.close()


    def recieve(self): 
        """ Method to recieve message to another client. """

        with socket.socket() as sock:
            sock.bind(("0.0.0.0", self.port))
            sock.listen(10)
            conn, addr = sock.accept() 

            with ssl.wrap_socket(conn, server_side=True, certfile=self.certfile, keyfile=self.keyfile) as tls_socket:
                
                try:
                    data = tls_socket.recv(2048)
                    print(data)
                    # message = json.loads(data.decode())
                    
                    tls_socket.send(b"pong") 

                finally:
                    tls_socket.shutdown(socket.SHUT_RDWR)
                    tls_socket.close()


if __name__ == "__main__":
    client_runner = Client(name="client1")
    clients = client_runner.create_keys()
    clients = client_runner.get_client_list()

    for client in clients: 
        print(f"[INFO] Found {client['client_name']}@{client['client_ip']}")

        sender    = threading.Thread(target=client_runner.send, args=(client["client_name"], client["client_ip"], ))
        reciever  = threading.Thread(target=client_runner.recieve)
        
        reciever.start()
        sender.start()

        #client_runner.send(client["client_name"], client["client_ip"])
        #client_runner.recieve()