
!!! info "Welcome to Microservice Encryption deployment tutorial"

    To launch your first confidential microservice, follow this tutorial in your favorite terminal.

## Install

The CLI tool `mse` requires at least [Python](https://www.python.org/downloads/) 3.8 and [OpenSSL](https://www.openssl.org/source/) 1.1.1 series.
It is recommended to use [pyenv](https://github.com/pyenv/pyenv) to manage different Python interpreters.

```{.console}
$ pip3 install mse-cli
$ mse --help     
usage: mse [-h] [--version]
               {context,deploy,init,list,login,logout,remove,scaffold,status,stop,test,verify} ...

Microservice Encryption CLI.

options:
  -h, --help            show this help message and exit
  --version             The version of the CLI

subcommands:
  {context,deploy,init,list,login,logout,remove,scaffold,status,stop,test,verify}
    context             Manage your MSE context files
    deploy              Deploy the application from the current directory into a MSE node
    init                Create a configuration file in the current directory.
    list                Print the list of apps from a project
    login               Sign up or login a user
    logout              Log out the current user
    remove              Stop and remove the MSE app from the project
    scaffold            Create a new empty app in the current directory
    status              Print the status of a MSE app
    stop                Stop a MSE app
    test                Test locally the application in the MSE docker
    verify              Verify the trustworthiness of an MSE app (no sign-in required)
```

## Log in

```{.console}
$ mse login
```

It will open your browser to sign up and/or log in on [console.cosmian.com](https://console.cosmian.com).

If it's the first time you are using Microservice Encryption (MSE), you need to use the sign up tab.
Don't forget to confirm your email and complete the information of your account.
You can skip the payment information by selecting a free plan.

The credential tokens are saved in `~/.config` on Linux/MacOS and `C:\Users\<username>\AppData` on Windows.

## Deploy your first web application

!!! Examples

    Visit [mse-app-examples](https://github.com/Cosmian/mse-app-examples) to find MSE application examples.


Let's start with a simple Flask Hello World application:

```{.console}
$ git clone https://github.com/Cosmian/mse-app-examples
$ tree mse-app-examples/helloworld
├── code
│   └── app.py
├── config
│   ├── dev.toml
│   └── zero_trust.toml
└── README.md
```

The file `app.py` is a basic flask application with no extra code and adapt your own application to MSE does not require any modification to your python code:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    """Get a simple example."""
    return "Hello world"
```

Let's deploy it. 

Using a `free` plan is longer to deploy than non-free plans because the memory and CPU dedicated are limited.
It should take around 60 seconds to deploy against a few seconds with non-free plans.


!!! info "Pre-requisites"

    Before deploying an app, verify that docker service is up and your current user can use the docker client without privilege


```{.console}
$ mse deploy --path mse-app-examples/helloworld/config/zero_trust.toml
An application with the same name in that project is already running...
Temporary workspace is: /tmp/tmpntxibdo6
Encrypting your source code...
Deploying your app...
App <uuid> creating for helloworld:1.0.0 with 512M EPC memory and 0.38 CPU cores...
✅ App created! 
Checking app trustworthiness...
The code fingerprint is dc54c709ab979543625ea8cbb30ae945ff50b9a86b9c3d97a53dbc8a883c5998
Verification: success
✅ The verified certificate has been saved at: /tmp/tmpntxibdo6/cert.conf.pem
Unsealing your private data from your mse instance...
Waiting for application to be ready...
Your application is now fully deployed and started...
✅ It's now ready to be used on https://<uuid>.cosmian.app until 2022-12-19 19:06:07.212101+01:00
The context of this creation can be retrieved using `mse context --export <uuid>`
```

That's it!

Your microservice is up at `https://{uuid}.cosmian.app` (replace `{uuid}` with the one from `mse deploy` command output).

You can test your app using `curl`:

```{.console}
$ export MSE_UUID="..." # your UUID here
$ # force curl CA bundle to be /tmp/tmpntxibdo6/cert.conf.pem
$ curl "https://$MSE_UUID.cosmian.app" --cacert /tmp/tmpntxibdo6/cert.conf.pem
```

## Scaffold your own project

The `scaffold` subcommand allows you to prepare your own project starting with a new fresh Flask application with only one endpoint `/`. See also the [init](subcommand/init.md) subcommand which enables you to initialize  the config file in an interactive way. 

```{.console}
$ mse scaffold my_project
$ tree my_project            
my_project
├── code
│   └── app.py
└── mse.toml

1 directory, 3 files
```

!!! warning "Compatibility with ASGI"


    To be compliant with MSE your Python application must be an [ASGI](https://asgi.readthedocs.io) application. It is not possible to deploy a standalone Python program. 


Edit the `app.py` with your own code and edit the default configuration file `mse.toml` as needed (see [Configuration](configuration.md)).

```{.bash}
$ cat my_project/mse.toml 
───────┬──────────────────────────────
   1   │ name = "my_project"
   2   │ version = "0.1.0"
   3   │ project = "default"
   4   │ plan = "free"
   5   │ 
   6   │ [code]
   7   │ location = "my_project/code"
   8   │ python_application = "app:app"
   9   │ health_check_endpoint = "/"
   10  | docker = "ghcr.io/cosmian/mse-pytorch:20230104085621"
───────┴──────────────────────────────
```

It's a good practice before deploying your app, to test it locally:

```{.console}
$ cd my_project
$ mse test --path mse.toml
$ curl http://localhost:5000/
$ pytest
```

You can now deploy your app as described previously.