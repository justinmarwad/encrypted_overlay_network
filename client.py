import socket, requests, json, ssl, json, random  
import os, string, multiprocessing, signal
from colorama import Fore, Style


## OUR CLIENT CODE ## 
class Client: 
    """ Main client code..."""
    def __init__(self, name="Rick_Astley", certfile=None, keyfile=None, port=9090, server="https://127.0.0.1:5000"): 
        self.name=name
        self.pub_key=f"public-{''.join(random.choices(string.ascii_lowercase, k=5))}.crt"
        self.priv_key=f"private-{''.join(random.choices(string.ascii_lowercase, k=5))}.key"

        self.port=port  
        self.server=server 

        self.clients=[]
        self.connected_clients=[]

    def create_keys(self): 
        """ Method to create keys """ 
        output=os.popen(f"openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout {self.priv_key} -out  {self.pub_key} -subj '/CN=rick.local/'").read() 
        print(output)

    def delete_keys(self):
        """ Delete all keys. Run this method on exit please."""
        print(os.popen(f"rm {self.priv_key} {self.priv_key}"))

    def get_local_ip(self): 
        """ Returns the local ip address as a string.""" 
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return(s.getsockname()[0])

    def get_client_list(self): 
        """ Method to get a list of clients from the server. """            

        with open(self.pub_key, "rb") as f:
            pub_key_text = f.read().decode("utf-8") 

        response = requests.post(self.server, data=json.dumps({
            "client_name": self.name, 
            "client_ip": self.get_local_ip(),
            "public_key": pub_key_text,
        }), verify=False)

        if response.status_code == 200: 
            self.clients = json.loads(response.content)["clients"]
        else:
            raise Exception(f"[ERROR] Could not recieve information from the server {self.server}.")

        
    def send(self, client, message="ping!"): 
        """ Method to send message to another client. """

        for client in self.clients: 
            if client in self.connected_clients: 
                return 
            else: 
                self.connected_clients.append(client)
            

            client["client_ip"] = "127.0.0.1"
            client_pub_key = f"read-{self.pub_key}"

            with open(client_pub_key, "wb") as f:
                f.write(client["public_key"].encode("utf-8")) 

            try: 
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        
                    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=client_pub_key)
                    context.load_cert_chain(certfile=self.pub_key, keyfile=self.priv_key)

                    with context.wrap_socket(sock, server_side=False, server_hostname="rick.local") as secure_sock: 
                        secure_sock.connect((client["client_ip"], self.port))
        
                        try: 
                            secure_sock.send(str.encode(json.dumps({
                                "message": message,
                                "client_name": self.name 
                            })))
                        
                        except ConnectionResetError: 
                            print(Fore.RED + f"[-] - Sender | Connection Reset." + Style.RESET_ALL)

                        print(Fore.GREEN + f"[+] - Sender | Sent {message} and {client['client_name']}@{client['client_ip']} replied: {secure_sock.recv(32).decode()}"  + Style.RESET_ALL)
                        
                        secure_sock.close()
                        break 

            except ssl.SSLCertVerificationError:
                self.connected_clients.remove(client)
                print(Fore.RED + f"[-] Sender | SSL Verification Error." + Style.RESET_ALL)
                continue 

    def recieve(self): 
        """ Method to recieve message from another client. """


        client_pub_key = f"read-{self.pub_key}"


        with socket.socket() as bindsocket: 
            try: 
                bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                bindsocket.bind(("0.0.0.0", self.port))
                bindsocket.listen(5)
            except OSError:
                print(Fore.RED + f"[-] Reciever | Could not bind port {self.port}." + Style.RESET_ALL)
                return null 

            while True:
                self.get_client_list()
                
                for client in self.clients: 
                    try: 
                        with open(client_pub_key, "wb") as f: f.write(client["public_key"].encode("utf-8")) 

                        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                        context.verify_mode = ssl.CERT_REQUIRED
                        context.load_cert_chain(certfile=self.pub_key, keyfile=self.priv_key)
                        context.load_verify_locations(cafile=client_pub_key)

                        
                        print(Fore.BLUE + "[+] Reciever ready for connections."  + Style.RESET_ALL)
                        newsocket, fromaddr = bindsocket.accept()
                        #print(f"Client connected: {fromaddr[0]}:{fromaddr[1]}")
                        with context.wrap_socket(newsocket, server_side=True) as secure_sock: 
                            #print(f"RECIEVER | SSL established. Peer: {secure_sock.getpeercert()}")
                            host, port = secure_sock.getpeername()

                            try:
                                data = json.loads(secure_sock.recv(4096)) 
                                print(Fore.BLUE + f"[RECIEVER INFO] {data['client_name']}@{host} said: {data['message']}" + Style.RESET_ALL)
                                secure_sock.send(str.encode("pong!"))
                            
                            finally:
                                secure_sock.shutdown(socket.SHUT_RDWR)
                                secure_sock.close()
                                    
                    except ssl.SSLError or ssl.SSLCertVerificationError:
                        print(Fore.RED + f"[ERROR] Public key of {client} did not work." + Style.RESET_ALL)
                        continue 


 
def handler(signum, frame):
    try: 
        confirm = input(Fore.RED + "Ctrl-c was pressed. Do you really want to exit? y/n ")
        if confirm != 'n':
            sender.terminate() 
            reciever.terminate()

            exit(1)
    
    except EOFError: 
        sender.terminate() 
        reciever.terminate()
        exit(1)

global sender
global reciever

if __name__ == "__main__":
    client_runner = Client(name="client1")
    client_runner.create_keys()

    for client in client_runner.clients: 
        print(f"[INFO] Found {client['client_name']}@{client['client_ip']}")

        sender    = multiprocessing.Process(target=client_runner.send, args=(client, ))
        # reciever  = multiprocessing.Process(target=client_runner.recieve)
        
        try:
            # reciever.start()
            sender.start()
        except KeyboardInterrupt:
            client_runner.delete_keys() 
            # sender.terminate() 
            # reciever.terminate()
            exit(1)       



