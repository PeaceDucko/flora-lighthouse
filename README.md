## Access the FLORA Lighthouse API from your own PC
### Prerequisites
To get access to the FLORA Lighthouse API you first need access to the credentials which are required to establish a secure shell tunnel into the Radboud servers. These credentials are found in the main folder of the shared Google Drive under the name `credentials.txt`. When you have the credentials you can continue to the next step.

### Next steps

1) Establish a secure shell between your PC and the Radboud servers by executing the command `ssh joep@131.174.75.218` from your command window. Enter the password when asked. **Note:** if this is your first time logging into the server you will be asked to confirm the fingerprint. Answer *yes*.
2) Once in the server, type and execute `./start.sh` to execute the bash script. This should launch the API on localhost 127.0.0.1 and port 5000
3) Open a new command window and make sure you are **not** logged into the server. Execute the command `ssh -N -L 5000:localhost:5000 joep@131.174.75.218` and enter the password which you used before. Nothing interesting should happen but when you navigate to 127.0.0.1:5000/home you should see the text `"This is my first API call!"`

## Using the API
Once the SSH tunnel is established between the server and your local machine you can start working with the API. Documentation of the API, its usage and endpoints can be viewed on the URI `/docs` (so: on localhost this is http://127.0.0.1:5000/docs/)

## Authentication
This API does not yet use authentication methods
