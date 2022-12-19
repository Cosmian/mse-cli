
!!! info "Welcome to Microservice Encryption deployment tutorial"

    To launch your first confidential microservice, follow this tutorial in your favorite terminal.

## Install

The CLI tool `mse-ctl` requires at least [Python](https://www.python.org/downloads/) 3.8 and [OpenSSL](https://www.openssl.org/source/) 1.1.1 series.
It is recommended to use [pyenv](https://github.com/pyenv/pyenv) to manage different Python interpreters.

```{.bash}
$ pip3 install mse-ctl
$ mse-ctl --help     
usage: mse-ctl [-h] [--version] {context,deploy,init,list,login,remove,scaffold,signup,status,stop,verify} ...

Microservice Encryption Control.

optional arguments:
  -h, --help            show this help message and exit
  --version             The version of the CLI

subcommands:
  {context,deploy,init,list,login,remove,scaffold,signup,status,stop,verify}
    context             Manage your MSE context files
    deploy              Deploy the application from the current directory into a MSE node
    init                Create a configuration file in the current directory.
    list                Print the list of apps from a project
    login               Login an existing user
    remove              Stop and remove the MSE app from the project
    scaffold            Create a new empty app in the current directory
    signup              Sign up a new user
    status              Print the status of a MSE app
    stop                Stop a MSE app
    verify              Verify the trustworthiness of an MSE app (no sign-in required)
```

## Log in

```{.bash}
$ mse-ctl login
```

It will open your browser to sign up and/or log in on [console.cosmian.com](https://console.cosmian.com).

If it's the first time you are using Microservice Encryption (MSE), you need to use the sign up tab.
Don't forget to confirm your email and complete the information of your account.
You can skip the payment information by selecting a free plan.

The credential tokens are saved in `~/.config` on Linux/MacOS and `C:\Users\<username>\AppData` on Windows.

## Deploy your first web application

Let's start with a simple Flask Hello World application:

```{.bash}
$ git clone http://gitlab.cosmian.com/core/mse-app-demo
$ tree mse-app-demo/helloworld
├── code
│   ├── app.py
│   └── requirements.txt
├── config
│   ├── dev.toml
│   └── zero_trust.toml
└── README.md
```

The `app.py` is a basic flask app with no extra code. Mse-ify your application is pretty straightforward, it doesn't require any modification of your own application:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    """Get a simple example."""
    return "Hello world"
```

Let's deploy it. 

Using a `free` plan, the deployment takes about 60 seconds. For non-free plans, the deployment takes few seconds only. On use also, the performance of your application depends on the chosen plan which determines the amount of memory and CPU dedicated to your own application.

```
$ mse-ctl deploy --path mse-app-demo/helloworld/config/zero_trust.toml
An application with the same name in that project is already running...
Temporary workspace is: /tmp/tmpntxibdo6
Encrypting your source code...
Deploying your app...
App creating for helloworld:1.0.0 with 512M EPC memory and 0.38 CPU cores...
✅ App created with uuid: <uuid>
Checking app trustworthiness...
The code fingerprint is dc54c709ab979543625ea8cbb30ae945ff50b9a86b9c3d97a53dbc8a883c5998
Verification: success
✅ The verified certificate has been saved at: /tmp/tmpntxibdo6/cert.conf.pem
Unsealing your private data from your mse instance...
Waiting for application to be ready...
Your application is now fully deployed and started...
✅ It's now ready to be used on https://<uuid>.cosmian.app until 2022-12-19 19:06:07.212101+01:00
The context of this creation can be retrieved using `mse-ctl context --export <uuid>`
```

That's it!

Your microservice is up at `https://{uuid}.cosmian.app` (replace `{uuid}` with the one from `mse-ctl deploy` command output).

You can test your app using `curl`:

```{.console}
$ export MSE_UUID="..." # your UUID here
$ # force curl CA bundle to be /tmp/tmpntxibdo6/cert.conf.pem
$ curl "https://$MSE_UUID.cosmian.app" --cacert /tmp/tmpntxibdo6/cert.conf.pem
```

## Scaffold your own project

The `scaffold` subcommand allows you to prepare your own project starting with a new fresh Flask application with only one endpoint `/`. See also the [init](subcommand/init.md) subcommand which enables you to initialize  the config file on a interactive way. 

```{.bash}
$ mse-ctl scaffold my_project
$ tree my_project            
my_project
├── code
│   ├── app.py
│   └── requirements.txt
└── mse.toml

1 directory, 3 files
```

!!! warning "Micro service applications only"


    To be mse compliant, your app should be a python micro service (using flask for instance). You can't deploy a standalone program under mse. 


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
───────┴──────────────────────────────
```

It's a good practice before deploying your app, to test it locally:

//TODO\\

You can now deploy your app as described previously.