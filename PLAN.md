
# General Plan

Split the projet into three parts and each of us will take a part. Deadline to finish the parts will be by Monday and then we can spend the days after putting things together and testing before the Friday submission date. 


1. Finish client.py (Nandan due by Tuesday 6:30 PM)
2. Finish network.py (Justin due by Tuesday 6:30 PM)
3. Implement TLS on both client.py & network.py (Manoj between Tuesday 6:30 PM to Wednesday evening) 
4. Write the report (all of us Friday)

# Next Steps

Parts 1 and 2 are done, we must start on part 3. Here are the next steps: 

1. Setup client-side TLS and give clients public and private keys 
2. Setup client.py to use certificates during communication 

# Useful Tools 

1. Use the Python socket library
2. Use TLS for secure communication (socket library has a TLS mode that needs a certificate signed by a CA) 
3. TLS by default doesn't verify clients, we should give each client a certificate so that we can verify them (maybe??? not too sure about this one since we want any cient to be able to connect to our overlay without needing a certificate).  


