from json import dumps, loads
import requests, json
from socket import socket, AF_INET, SOCK_STREAM 


## OUR CLIENT CODE ##
class Client: 
    """ Main client code..."""
    def __init__(self, name="Rick_Astley", port=9090, server="https://127.0.0.1:5000"): 
        self.name=name
        self.port=port  
        self.server=server 

    def get_client_list(self, client_ip="127.0.0.1"): 
        """ Method to get a list of clients from the server. """
        
        response = requests.post(self.server, data=dumps({
            "client_name": self.name, 
            "client_ip": client_ip
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

        connection = socket(AF_INET, SOCK_STREAM)
        connection.bind(('0.0.0.0', self.port))
        connection.listen(10)
 
        while True:
            (listener, _) = connection.accept()
            message = loads(listener.recv(2048).decode())
            print(message)


            # before sending "pong" to the other client, verify the client with the server first
            listener.send(b"pong")

            
            listener.close()

if __name__ == '__main__':
    Client().run()