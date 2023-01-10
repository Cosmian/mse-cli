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

Let's start with a simple Flask Hello World application:

```{.console}
$ mse scaffold helloworld
An example app has been generated in the current directory
You can configure your mse application in: helloworld/mse.toml
You can now test it locally from 'helloworld/' directory using: `mse test` then `pytest`
Or deploy it from 'helloworld/' directory using: `mse deploy`
Refer to the 'helloworld/README.md' for more details.
$ tree helloworld/
helloworld/
├── mse_code
│   └── app.py
├── mse.toml
├── README.md
├── requirements-dev.txt
└── tests
    ├── conftest.py
    └── test_app.py

2 directories, 6 files
```

The file `app.py` is a basic flask application with no extra code. Adapt your own application to MSE does not require any modification to your python code:

```python
from http import HTTPStatus

from flask import Flask, Response

app = Flask(__name__)


@app.get("/health")
def health_check():
    """Health check of the application."""
    return Response(status=HTTPStatus.OK)


@app.route('/')
def hello():
    """Get a simple example."""
    return "Hello world"


if __name__ == "__main_":
    app.run(debug=True)

```

The [configuration file](./configuration.md) is a TOML file:

```{.toml}
name = "helloworld"
version = "0.1.0"
project = "default"
plan = "free"

[code]
location = "mse_code"
docker = "ghcr.io/cosmian/mse-pytorch:20230104085621"
python_application = "app:app"
healthcheck_endpoint = "/health"
```

This project also contains a test directory enabling you to test this project locally without any mse consideration:

```{.console}
$ cd helloworld
$ python3 mse_code/app.py
$ # From another terminal
$ curl http://127.0.0.1:5000
$ pytest
```

Let's now deploy it! 

!!! warning "Free plan"

    Using a `free` plan is longer to deploy than non-free plans because the memory and CPU dedicated are limited. It should take around 60 seconds to deploy against a few seconds with non-free plans.

For your first deployment, to make things easier to understand and faster to run, we disable some security features. The `--no-verify` and `--untrusted-ssl` will be removed in the next sections. 

```{.console}
$ cd helloworld
$ mse deploy --no-verify --untrusted-ssl

TODO
```

That's it!

Your microservice is up at `https://{uuid}.cosmian.app` (replace `{uuid}` with the one from `mse deploy` command output).

You can test your first app using `curl`:

```{.console}
$ export MSE_UUID="..." # your UUID here
$ curl "https://$MSE_UUID.cosmian.app" 
```

At this point, you can write your own Flask application and deploy it into MSE. 

!!! warning "Compatibility with ASGI"

    To be compliant with MSE your Python application must be an [ASGI](https://asgi.readthedocs.io) application. It is not possible to deploy a standalone Python program. 


!!! Examples

    Visit [mse-app-examples](https://github.com/Cosmian/mse-app-examples) to find MSE application examples.


## Remove `--no-verify`

In this step, we will redeploy your previous app by removing the `--no-verify`. Using this argument is insecure: when you deploy an app, you need to verify if the running app is well your code and if it is running inside an intel sgx enclave signed by Cosmian. For more details, please refer to [the security model](security.md)

!!! info "Pre-requisites"

    Before deploying the app, verify that docker service is up and your current user can use the docker client without privilege


```{.console}
$ cd helloworld
$ mse deploy --untrusted-ssl

TODO
```

As you can see, the warning message has been removed for the output of your previous command and the trustworthiness of the app has been checked.


## Remove `--untrusted-ssl` 

In this step, we will redeploy your previous app by removing the `--untrusted-ssl`. Using this argument is insecure: you need to use a direct SSL connection from you to the enclave. That way, no one, but the enclave can read the content of the queries. For more details, please refer to [the app deployment flow](how_it_works_deploy.md) and [the app usage flow](how_it_works_use.md).


```{.console}
$ cd helloworld
$ mse deploy

TODO
```

As you can see, the warning message has been removed for the output of your previous command. 

Your microservice is up at `https://{uuid}.cosmian.app` (replace `{uuid}` with the one from `mse deploy` command output).

You can test your app using `curl`:

```{.console}
$ export MSE_UUID="..." # your UUID here
$ # force curl CA bundle to be /tmp/tmpntxibdo6/cert.conf.pem
$ curl "https://$MSE_UUID.cosmian.app" --cacert /tmp/tmpntxibdo6/cert.conf.pem
```

## Test your application locally

Before any deployment, it's strongly recommanded to test your application locally against the mse docker image specified into your `mse.toml`. It enables you to verify that your application is compatible with the MSE environment and all required dependencies are installed. 

Now you have installed docker on your own machine, you can run: 

```{.console}
$ cd helloworld
$ mse test 
$ # from another terminal
$ curl http://localhost:5000/
$ pytest
```

!!! info "Requirements"

    The mse environment is running on `Ubuntu 22.04` with `python 3.8`.


## Build your own mse docker

When you scaffold a new project, the configuration file contains a default docker containing minimal flask packages. For many reasons, this docker could be not enough to run your own application. If your `mse_code` directory contains a `requirements.txt`, these packages will be installed when running the docker. It enables you to quickly test your application in an MSE environment without generating a new docker. However:

- It could be hard to clearly define your dependencies and run them against the installed packages on the remote environment
- It makes your installation not reproductible. Therefore after a deployment, it's strongly likely that your users won't be able to verify the trustworthiness of your application
  
Then, we recommand to build your own docker from our [mse-base image](https://github.com/Cosmian/mse-docker-base) and integrates all your dependencies. 
You can test your application against your own docker by editing the field `docker` in your `mse.toml` and running: 

```{.console}
$ cd helloworld
$ mse test 
$ # from another terminal
$ curl http://localhost:5000/
$ pytest
```

Refer to [docker configuration](./configuration.md#mse-docker) for more details.