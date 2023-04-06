## Access the FLORA Lighthouse API from your own PC

## Locally
### Prerequisites
- During this guide we assume you are working on either a Linux machine or on Windows Subsystem for Linux (WSL).

- Make sure you have created a `data` folder within the `api` folder in the root of the application. This folder is not included in the GitHub repository due to privacy reasons.

  - Make sure that within the `data` folder there is also an `essays`, `processLabel`, `spiderScript`, and `test` folder. Finally, a `label_names.csv` file must be present in the `data` folder.
  - The `essays` folder contains the text-written essays.
  - The `processLabel` folder contains the patterns for every student which is necessary for plotting the graphs.
  - The `spiderScript` folder contains the language scaffolds needed for the script to process text from the essays.
  - The `test` folder contains the pre- and posttest files needed for each pilot as a baseline.

You should have access to these files, if not please contact the product owner.

### Steps
1. In your command line, clone the repository using the command `git clone https://github.com/PeaceDucko/flora-lighthouse.git`
2. Create a virtual environment using `virtualenv venv` in the root folder of the project. If you don't have virtualenv pre-installed then follow the steps in the command line to install virtualenv
3. Once the virtual environment is created type `source venv/bin/activate` (Linux) to activate the environment
4. Install the required packages into the environment using `pip install -r requirements.txt`. Due to some large language packages this might take a while
5. When the packages are installed you can run the application. Change into the `api` folder using `cd api` and run Flask:
       

    $ flask run --port=5000

Sometimes port 5000 is taken, in that case use another port.

6. Congrats! Your app is running. Go to `localhost:<port>` to check out the api and `localhost:5000/docs` to check the api documentation. 
   7. If you want to see the results of a single user (for example user fsh4_360 on port 5000) go to `localhost:5000/result?studentNumber=fsh4_360`

## On the server
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
