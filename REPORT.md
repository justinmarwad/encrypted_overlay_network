# General Overview

# Cryptography Overview

We utilize Transport Layer Security (TLS) in our project to ensure that connections are secure. The TLS handshake works with Perfect Forward Secrecy and provides privacy and data integrity protection and prevents replay attacks. The TLS algorithm is very effective because it is both extremely secure as well as very efficient. It utilizes both asymmetric and symmetric cryptography because it recognizes the former to be highly secure while also understanding that the latter is much faster.  

TLS requires a certificate authority but based on the nature of this project, we could not pay for a certificate. Therefore, there could be a possibility of a Man in the middle attack(MiTm).

Under the create keys method we implemented openssl to create the public and private keys. This solves for authentication. Once the keys are created, we ping the network server and provide our name, IP Address and our public key. We then ask the server for all the clients that are connected to the network and the server responds with all the clients that are connected to the network. 

Once the required information is gathered, the clients authenticate each other using TLS with their public key and then the sender pings the client to which it responds back with a pong over TLS.

Our implemenation solved for the MiTm theoretically. TLS implements message authentication code(MAC) solves for both confidentiality, integrity and prevent replay attacks considering the fact that MAC is a unique code. We prevent downgrade attacks by blocking TLS versions below 1.3. 