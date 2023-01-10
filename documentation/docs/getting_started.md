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
├── mse_src
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


if __name__ == "__main__":
    app.run(debug=True)

```

The [configuration file](./configuration.md) is a TOML file:

```{.toml}
name = "helloworld"
version = "0.1.0"
project = "default"
plan = "free"

[code]
location = "mse_src"
docker = "ghcr.io/cosmian/mse-flask:20230110142022"
python_application = "app:app"
healthcheck_endpoint = "/health"
```

This project also contains a test directory enabling you to test this project locally without any mse consideration:

```{.console}
$ cd helloworld
$ python3 mse_src/app.py
$ # From another terminal
$ curl http://127.0.0.1:5000
$ pytest
```

Now let's deploy it! 

!!! warning "Free plan"

    Using a `free` plan is longer to deploy than non-free plans because the memory and CPU dedicated are limited. It should take around 60 seconds to deploy against a few seconds with non-free plans.

For your first deployment, to make things easier to understand and faster to run, we disable some security features. The `--no-verify` and `--untrusted-ssl` will be removed in the next sections. 

```{.console}
$ cd helloworld
$ mse deploy --no-verify --untrusted-ssl
⚠️ This app runs in untrusted-ssl mode with an operator certificate. The operator may access all communications with the app. See Documentation > Security Model for more details.
Temporary workspace is: /tmp/tmpzdvizsb5
Encrypting your source code...
Deploying your app...
App 04e9952c-981d-4601-a610-81152fe21315 creating for helloworld:0.1.0 with 512M EPC memory and 0.38 CPU cores...
You can now run `mse logs 04e9952c-981d-4601-a610-81152fe21315` if necessary
✅ App created!
⚠️ App trustworthiness checking skipped. The app integrity has not been checked and shouldn't be used in production mode!
Sending secret key and decrypting the application code...
Waiting for application to be ready...
Your application is now fully deployed and started...
✅ It's now ready to be used on https://04e9952c-981d-4601-a610-81152fe21315.dev.cosmian.dev until 2023-01-10 20:30:36.860596+01:00. The application will be automatically stopped after this date.
The context of this creation can be retrieved using `mse context --export 04e9952c-981d-4601-a610-81152fe21315`
You can now quickly test your application doing: `curl https://04e9952c-981d-4601-a610-81152fe21315.dev.cosmian.dev/health`
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


## Verify the trustworthiness of your app (remove `--no-verify`)

!!! info "Pre-requisites"

    Before deploying the app, verify that docker service is up and your current user can use the docker client without privilege


In this step, we will redeploy your previous app but without the insecure argument `--no-verify`. When you deploy an app, you need to verify that the running app is well your code and is running inside an intel sgx enclave signed by Cosmian. For more details, please refer to [the security model](security.md).


```{.console}
$ cd helloworld
$ mse deploy -y --untrusted-ssl
An application with the same name in that project is already running...
Stopping the previous app (force mode enabled)...
⚠️ This app runs in untrusted-ssl mode with an operator certificate. The operator may access all communications with the app. See Documentation > Security Model for more details.
Temporary workspace is: /tmp/tmpucnl7zfd
Encrypting your source code...
Deploying your app...
App 74638f07-c85c-41d3-be82-238d0099e2d3 creating for helloworld:0.1.0 with 8192M EPC memory and 6.00 CPU cores...
You can now run `mse logs 74638f07-c85c-41d3-be82-238d0099e2d3` if necessary
✅ App created!
Checking app trustworthiness...
The code fingerprint is 9bb0342fa8a09c2707632ed8556accc5fac168515bf2453bf88992c9fa84e849
Verification: success
Sending secret key and decrypting the application code...
Waiting for application to be ready...
Your application is now fully deployed and started...
✅ It's now ready to be used on https://74638f07-c85c-41d3-be82-238d0099e2d3.dev.cosmian.dev until 2023-01-10 21:23:28.929299+01:00. The application will be automatically stopped after this date.
The context of this creation can be retrieved using `mse context --export 74638f07-c85c-41d3-be82-238d0099e2d3`
You can now quickly test your application doing: `curl https://74638f07-c85c-41d3-be82-238d0099e2d3.dev.cosmian.dev/health`
```

As you can see, the warning message has been removed for the output of your previous command and the trustworthiness of the app has been checked.


## Secure the SSL connection (remove `--untrusted-ssl`)

In this step, we will redeploy your previous app but without the insecure argument `--untrusted-ssl`. You need to use an end-to-end SSL connection from you to the application. That way, no one but the enclave can read the content of the queries. For more details, please refer to [the app deployment flow](how_it_works_deploy.md) and [the app usage flow](how_it_works_use.md).


```{.console}
$ cd helloworld
$ mse deploy -y
An application with the same name in that project is already running...
Stopping the previous app (force mode enabled)...
Temporary workspace is: /tmp/tmp4u_gcjwk
Encrypting your source code...
Deploying your app...
App 248fce63-bc05-49a6-816a-4436b456fa27 creating for helloworld:0.1.0 with 8192M EPC memory and 6.00 CPU cores...
You can now run `mse logs 248fce63-bc05-49a6-816a-4436b456fa27` if necessary
✅ App created!
Checking app trustworthiness...
The code fingerprint is ecd2ed83c65906bec65d5b8bc02e18d439c0d1401272e207fed254f7228eee7e
Verification: success
✅ The verified certificate has been saved at: /tmp/tmp4u_gcjwk/cert.conf.pem
Sending secret key and decrypting the application code...
Waiting for application to be ready...
Your application is now fully deployed and started...
✅ It's now ready to be used on https://248fce63-bc05-49a6-816a-4436b456fa27.dev.cosmian.app until 2023-01-10 21:24:28.162324+01:00. The application will be automatically stopped after this date.
The context of this creation can be retrieved using `mse context --export 248fce63-bc05-49a6-816a-4436b456fa27`
You can now quickly test your application doing: `curl https://248fce63-bc05-49a6-816a-4436b456fa27.dev.cosmian.app/health --cacert /tmp/tmp4u_gcjwk/cert.conf.pem`
```

Your microservice is up at `https://{uuid}.cosmian.app` (replace `{uuid}` with the one from `mse deploy` command output).

You can test your app using `curl`:

```{.console}
$ export MSE_UUID="..." # your UUID here
$ # force curl CA bundle to be /tmp/tmpntxibdo6/cert.conf.pem
$ curl "https://$MSE_UUID.cosmian.app" --cacert /tmp/tmpntxibdo6/cert.conf.pem
```

This deployment method must be your preferred way to deploy in production.

## Test your application locally

This method is well-suited to test the remote environment when deploying your app.

We recall that your application is deployed into a constraint environment under a specific architecture. This method emulates as close as possible this production environment. 

Before any deployment, it's strongly recommanded to test your application locally against the mse docker image specified into your `mse.toml`. It enables you to verify that your application is compatible with the MSE environment and all required dependencies are installed. 

Since you have installed `docker` in the previous step on your own machine, you can run: 

```{.console}
$ cd helloworld
$ mse test 
$ # from another terminal
$ curl http://localhost:5000/
$ pytest
```

!!! info "Requirements"

    The mse environment is running on `Ubuntu 20.04` with `python 3.8`.


## Build your own mse docker

When you scaffold a new project, the configuration file contains a default docker including minimal flask packages. For many reasons, this docker could be not enough to run your own application. If your `mse_src` directory contains a `requirements.txt`, these packages will be installed when running the docker. It enables you to quickly test your application in an MSE environment without generating a new docker. However:

- It could be hard to clearly define your dependencies and run them against the installed packages on the remote environment
- It makes your installation not reproductible. Therefore after a deployment, it's strongly likely that your users won't be able to verify the trustworthiness of your application
  
Then, we recommand to fork [mse-docker-flask](https://github.com/Cosmian/mse-docker-flask) to build your own docker by integrating all your dependencies. 
You can test your application against your own docker by editing the field `docker` in your `mse.toml` and running: 

```{.console}
$ cd helloworld
$ mse test 
$ # from another terminal
$ curl http://localhost:5000/
$ pytest
```

Refer to [docker configuration](./configuration.md#mse-docker) for more details.