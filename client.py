from json import dumps, loads
from requests import post as post_request
from socket import socket, AF_INET, SOCK_STREAM 


## OUR CLIENT CODE ##
class Client: 
    """ Main client code..."""
    def __init__(self, name="Rick_Astley", server="https://127.0.0.1:5000"): 
        self.name=name 
        self.server=server 

    def run(self): 
        """ Main method: this is where the magic happens!"""

        clients = self.get_client_list()

        for client in clients: 
            self.send()

            self.recieve()
        

    def get_client_list(self, client_ip="127.0.0.1"): 
        """ Method to get a list of clients from the server. """
        
        response = post_request(self.server, data=dumps({
            "client_name": self.name, 
            "client_ip": client_ip
        }))

    def send(self, address="127.0.0.1", message="ping"): 
        """ Method to send message to another client. """
        pass

    def recieve(self): 
        """ Method to recieve message to another client. """
        pass

if __name__ == '__main__':
    Client().run()


## RECEIVER STARTER CODE ##
class Receiver:
    def __init__(self, server, username, password):
        """
        Args:
            server (str) - the server url
            username (str) - the login username
            password (str) - the login password
        """
 
        self.server = server
        self.username = username
        self.token = self.get_login_token(password)

    def get_login_token(self, password):
        """Connect with the server, provide correct username and password, and
        obtain the login token.

        Args:
            password (str) - the login password

        Returns:
            A login token for future operations
        """

        server = self.server + '/login'
        data = dumps({'username': self.username, 'password': password})

        response = post_request(server, data=data)
        if response.status_code != 200:
            raise Exception('Unexpected response code from the server.')

        return loads(response.content)['token']

    def receive_messages(self):
        """Listen indefinitely and receive messages from multiple users."""

        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind(('0.0.0.0', 9999))
        sock.listen(10)
        print(f'Receiver started for user {self.username}.')

        while True:
            (client_sock, _) = sock.accept()
            received = loads(client_sock.recv(2048).decode())

            # the msgtype is a field in the recieved message that will have a
            # value of chat when a user sends a chat message.
            if 'msgtype' in received and received['msgtype'] == 'chat':
                self.handle_user_message(received)
                client_sock.send(b'Received')

            client_sock.close()

    def handle_user_message(self, received):
        """Parse the received encrypted message, decrypt and print the
        confidential message.

        Args:
            received (str) - the received encrypted message
        """

        # all the messages are in hex format, need to convert to bytes.
        sender_info = bytes.fromhex(received['senderinfo'])
        message = bytes.fromhex(received['message'])

        # decrypt the sender info to obtain sender name, ip and secret.
        cipher = AES.new(str.encode(self.token), AES.MODE_ECB)
        sender_info = loads(unpad(cipher.decrypt(sender_info), 16))

        username = sender_info['username']
        ip_addr = sender_info['ip_addr']
        secret_key = sender_info['secret']

        # now, decrypt the encrypted user message using the secret.
        cipher = AES.new(str.encode(secret_key), AES.MODE_ECB)
        message = unpad(cipher.decrypt(message), 16).decode()

        print(f'{username} ({ip_addr}) - {message}')


# if __name__ == '__main__':
#     receiver = Receiver(server='http://192.168.7.83:8080', username='jmarwad',
#                         password='1qazxsW@1')
#     receiver.receive_messages()


from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from json import dumps, loads 
from requests import post as post_request
from socket import socket, AF_INET, SOCK_STREAM


## SENDER STARTER CODE ##
  
class Sender:
    def __init__(self, server, username, password):
        """
        Args:
            server (str) - the server url
            username (str) - the login username
            password (str) - the login password
        """

        self.server = server
        self.username = username
        self.token = self.get_login_token(password)

    def get_login_token(self, password):
        """Connect with the server, provide correct username and password, and
        obtain the login token.

        Args:
            password (str) - the login password

        Returns:
            A login token for future operations
        """

        server = self.server + '/login'
        data = dumps({'username': self.username, 'password': password})

        response = post_request(server, data=data)
        if response.status_code != 200:
            raise Exception('Unexpected response code from the server.')

        return loads(response.content)['token']

    def get_receiver_info(self, receiver):
        """Connect with the server, provide correct username and token, and
        receive information related to messaging a receiver.

        Args:
            receiver (str) - the receiver username

        Returns:
            A JSON object containing the following keys.
                receiver: the receiver username
                ip_addr: the receiver IP address
                secret: secret key to connect with receiver
                senderinfo: encrypted packet with sender information
        """

        server = self.server + '/userinfo'
        data = dumps({'username': self.username, 'token': self.token,
                      'receiver': receiver})

        response = post_request(server, data=data)
        if response.status_code != 200:
            raise Exception('Unexpected response code from the server.')

        return loads(response.content)

    def send_message(self, receiver, message):
        """Send a confidential message to the receiver.

        Args:
            receiver (str) - the receiver username
            message (str) - the confidential message
        """

        # convert message to bytes and pad to 16.
        message = pad(str.encode(message), 16)

        receiver_info = self.get_receiver_info(receiver)
        ip_addr = receiver_info['ip_addr']
        port = 9999
        secret_key = receiver_info['secret']
        sender_info = receiver_info['senderinfo']

        # prepare the message by encrypting it using the shared secret.
        # without the senderinfo packet, there is no way for receiver
        # to decrypt the message so transmit that as well.
        cipher = AES.new(str.encode(secret_key), AES.MODE_ECB)
        tx_message = dumps({'msgtype': 'chat',
                            'message': cipher.encrypt(message).hex(),
                            'senderinfo': sender_info})

        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((ip_addr, port))
        sock.send(str.encode(tx_message))
        print(f'Message Status: {sock.recv(32).decode()}')
        sock.close()


# if __name__ == '__main__':
#     sender = Sender(server='http://192.168.7.83:8080', username='snarain',
#                     password='1qazxsW@1')
#     sender.send_message(receiver='snarain', message='Hello')
