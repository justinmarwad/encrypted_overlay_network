
# General Plan

Split the projet into six parts and each of us will take two parts. Deadline to finish the parts will be by Monday and then we can spend the days after putting things together and testing before the Friday submission date. 


1. Overlay communication network based on Actiity #1 
2. Secure TLS communication  
3. Installing/setting up CA
4. Writing the Report 

# Useful Tools 

1. Use the Python socket library
2. Use TLS for secure communication (socket library has a TLS mode that needs a certificate signed by a CA) 
3. Setup a simple CA to sign TLS certificates ([Easy-RSA is pretty easy to setup](https://www.digitalocean.com/community/tutorials/how-to-set-up-and-configure-a-certificate-authority-ca-on-debian-10))
4. TLS by default doesn't verify clients, we should give each client a certificate so that we can verify them (maybe??? not too sure about this one since we want any cient to be able to connect to our overlay without needing a certificate).  


