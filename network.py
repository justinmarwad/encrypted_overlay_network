from flask import Flask, request
  
app = Flask(__name__)
  
global clients 
clients = [] # global list of al connected clients 

@app.route('/', methods=["GET", "POST"])
def connect():
    """ Recieves json arguments {client_name, client_ip} and returns list [{client_name, client_ip}, {client_name, client_ip}, {client_name, client_ip}] in json"""
    ## Get client information
    content = request.get_json(force=True) # throwing formatting error as of rn 

    client_name = content.get("client_name") 
    client_ip   = content.get("client_ip")
    public_key  = content.get("public_key")

    print(f"Connected {client_name}@{client_ip} - {public_key}") 

    ## Create response 
    response = {
        "clients": clients,
    }

    ## Add client to list of clients

    if client_name in clients: 
        print("[INFO] Client already exists.")
    else:
        clients.append({
            "client_name": client_name, 
            "client_ip": client_ip,
            "public_key": public_key
        })

    ## Return response to client (Flask will automatically convert Python dict to json)
    return(response)


# main driver function
if __name__ == '__main__':
    app.run(host="0.0.0.0", ssl_context='adhoc', debug=True)
