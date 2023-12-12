!!! info "Welcome to Microservice Encryption SaaS deployment tutorial"

    To launch your first confidential application, follow this tutorial in your favorite terminal.
    Your application will run on the [Cosmian Enclave Saas platform](https://console.cosmian.com/)


!!! important "Cosmian Enclave SaaS used to be called MSE Cloud"

    There are quite a few locations where the old MSE name is still in use.


## Install

The CLI tool `mse` requires at least [Python](https://www.python.org/downloads/) 3.8 and [OpenSSL](https://www.openssl.org/source/) 1.1.1 series.
It is recommended to use [pyenv](https://github.com/pyenv/pyenv) to manage different Python interpreters.

```{.console}
$ pip3 install mse-cli
$ mse cloud --help
usage: mse cloud [-h]
                 {context,deploy,init,list,login,logout,logs,scaffold,status,stop,test,verify}
                 ...

options:
  -h, --help            show this help message and exit

operations:
  {context,deploy,init,list,login,logout,logs,scaffold,status,stop,test,verify}
    context             manage context of your deployed applications
    deploy              deploy an ASGI web application to Cosmian Enclave
    init                create a new configuration file in the current directory
    list                list deployed Cosmian Enclave web application from a project
    login               sign up or login to console.cosmian.com
    logout              log out the current user
    logs                logs (last 64kB) of a specific Cosmian Enclave web application
    scaffold            create a new boilerplate Cosmian Enclave web application
    status              status of a specific Cosmian Enclave web application
    stop                stop a specific Cosmian Enclave web application
    test                test locally the application in the Cosmian Enclave docker
    verify              verify the trustworthiness of a running Cosmian Enclave web application (no
                        sign-in required)
```

## Log in

```{.console}
$ mse cloud login
```

It will open your browser to sign up and/or log in on [console.cosmian.com](https://console.cosmian.com).

If it's the first time you are using Cosmian Enclave SaaS, you need to use the sign-up tab.
Don't forget to confirm your email and complete the information of your account.
You can skip the payment information by selecting a free plan.

The credential tokens are saved in `~/.config` on Linux/MacOS and `C:\Users\<username>\AppData` on Windows.

## Deploy your first web application

Let's start with a simple Flask Hello World application:

```{.console}
$ mse cloud scaffold helloworld
An example app has been generated in the current directory
You can configure your Cosmian Enclave application in: helloworld/mse.toml
You can now test it locally from 'helloworld/' directory using: `mse cloud localtest`
Or deploy it from 'helloworld/' directory using: `mse cloud deploy`
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

The `mse_src` is your application directory designed to be dispatched by `mse-cli` to the Microservice Encryption infrastructure. The other files or directories will stay on your own host. 

The file `app.py` is a basic Flask application with no extra code. Adapting your own application to Cosmian Enclave does not require any modification to your Python code:

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

The [ configuration file](./configuration.md) is a TOML file:

```toml
name = "helloworld"
python_application = "app:app"
healthcheck_endpoint = "/"
tests_cmd = "pytest"
tests_requirements = [ "intel-sgx-ra>=1.0.1,<1.1", "pytest==7.2.0",]

[cloud]
code = "mse_src"
tests = "tests"
docker = "ghcr.io/cosmian/mse-flask:20230710125733"
project = "default"
hardware = "4g-eu-001"
```

This project also contains a test directory enabling you to test this project locally without any Cosmian Enclave consideration.
Please ensure `flask` is installed locally, before running the following tests:

```{.console}
$ cd helloworld
$ # Install dev requirements to run the tests
$ pip install -U -r requirements-dev.txt
$ # Run your application server
$ python3 mse_src/app.py
$ # From another terminal, query your server or start the unit tests
$ curl http://127.0.0.1:5000
$ pytest
```

Now let's deploy it! 

!!! warning "Free plan"

    Using a `free` plan is longer to deploy than non-free plans because the memory and CPU dedicated are limited. It should take around 60 seconds to deploy against a few seconds with non-free plans.

For your first deployment, to make things easier to understand and faster to run, we disable some security features. The `--no-verify` and `--untrusted-ssl` will be removed in the next sections. 

```{.console}
$ cd helloworld
$ mse cloud deploy --no-verify --untrusted-ssl
⚠️ This app runs in untrusted-ssl mode with an operator certificate. The operator may access all communications with the app. See Documentation > Security Model for more details.
Temporary workspace is: /tmp/tmpzdvizsb5
Encrypting your source code...
Deploying your app...
App 04e9952c-981d-4601-a610-81152fe21315 creating for helloworld with 512M EPC memory and 0.38 CPU cores...
You can now run `mse cloud logs 04e9952c-981d-4601-a610-81152fe21315` if necessary
✅ App created!
⚠️ App trustworthiness checking skipped. The app integrity has not been checked and shouldn't be used in production mode!
Sending secret key and decrypting the application code...
Waiting for application to be ready...
Your application is now fully deployed and started...
✅ It's now ready to be used on https://123456789abcdef.cosmian.dev until 2023-01-10 20:30:36.860596+01:00. The application will be automatically stopped after this date.
The context of this creation can be retrieved using `mse cloud context --export 04e9952c-981d-4601-a610-81152fe21315`
You can now quickly test your application doing: `curl https://123456789abcdef.cosmian.dev/health`
```

That's it!

Your microservice is up at `https://123456789abcdef.cosmian.io`.

You can test your first app using `curl`:

```{.console}
$ export APP_DOMAIN_NAME="..." # your DN here
$ curl "https://$APP_DOMAIN_NAME" 
```

At this point, you can write your [own Flask application](#going-further) and deploy it into Cosmian Enclave SaaS.

!!! warning "Compatibility with WSGI/ASGI"

    To be compliant with Cosmian Enclave your Python application must be an [ASGI](https://asgi.readthedocs.io) or [WSGI](https://wsgi.readthedocs.io) application. It is not possible to deploy a standalone Python program. 
    In the next example, this documentation will describe how to deploy Flask applications. You also can use other ASGI applications, for instance: FastAPI.

!!! Examples "Examples"

    Visit [Cosmian Enclave Examples](https://github.com/Cosmian/mse-app-examples) to find application examples.


## Verify the trustworthiness of your app (remove `--no-verify`)

!!! info "Pre-requisites"

    Before deploying the app, verify that docker service is up and your current user can use the docker client without privilege


In this step, we will redeploy your previous app but without the insecure argument `--no-verify`.
When you deploy an app, you need to verify that the running app is indeed your code and is running inside an Intel SGX enclave signed by Cosmian.
For more details, please refer to [the security model](security.md).


```{.console}
$ cd helloworld
$ mse cloud deploy -y --untrusted-ssl
An application with the same name in that project is already running...
Stopping the previous app (force mode enabled)...
⚠️ This app runs in untrusted-ssl mode with an operator certificate. The operator may access all communications with the app. See Documentation > Security Model for more details.
Temporary workspace is: /tmp/tmpucnl7zfd
Encrypting your source code...
Deploying your app...
App 74638f07-c85c-41d3-be82-238d0099e2d3 creating for helloworld with 8192M EPC memory and 6.00 CPU cores...
You can now run `mse cloud logs 74638f07-c85c-41d3-be82-238d0099e2d3` if necessary
✅ App created!
Checking app trustworthiness...
The code fingerprint is 9bb0342fa8a09c2707632ed8556accc5fac168515bf2453bf88992c9fa84e849
Verification: success
Sending secret key and decrypting the application code...
Waiting for application to be ready...
Your application is now fully deployed and started...
✅ It's now ready to be used on https://74638f07-c85c-41d3-be82-238d0099e2d3.cosmian.dev until 2023-01-10 21:23:28.929299+01:00. The application will be automatically stopped after this date.
The context of this creation can be retrieved using `mse cloud context --export 74638f07-c85c-41d3-be82-238d0099e2d3`
You can now quickly test your application doing: `curl https://74638f07-c85c-41d3-be82-238d0099e2d3.cosmian.dev/health`
```

As you can see, the warning message has been removed for the output of your previous command and the trustworthiness of the app has been checked.


## Secure the SSL connection (remove `--untrusted-ssl`)

In this step, we will redeploy your previous app but without the insecure argument `--untrusted-ssl`. You need to use an end-to-end SSL connection from you to the application. That way, no one but the enclave can read the content of the queries. For more details, please refer to [the app deployment flow](how_it_works_deploy.md) and [the app usage flow](how_it_works_use.md).


```{.console}
$ cd helloworld
$ mse cloud deploy -y
An application with the same name in that project is already running...
Stopping the previous app (force mode enabled)...
Temporary workspace is: /tmp/tmp4u_gcjwk
Encrypting your source code...
Deploying your app...
App 248fce63-bc05-49a6-816a-4436b456fa27 creating for helloworld with 8192M EPC memory and 6.00 CPU cores...
You can now run `mse cloud logs 248fce63-bc05-49a6-816a-4436b456fa27` if necessary
✅ App created!
Checking app trustworthiness...
The code fingerprint is ecd2ed83c65906bec65d5b8bc02e18d439c0d1401272e207fed254f7228eee7e
Verification: success
✅ The verified certificate has been saved at: /tmp/tmp4u_gcjwk/ratls.pem
Sending secret key and decrypting the application code...
Waiting for application to be ready...
Your application is now fully deployed and started...
✅ It's now ready to be used on https://123456789abcdef.cosmian.io until 2023-01-10 21:24:28.162324+01:00. The application will be automatically stopped after this date.
The context of this creation can be retrieved using `mse cloud context --export 248fce63-bc05-49a6-816a-4436b456fa27`
You can now quickly test your application doing: `curl https://123456789abcdef.cosmian.io/health --cacert /tmp/tmp4u_gcjwk/ratls.pem`
```

Your microservice is up at `https://123456789abcdef.cosmian.io`.

You can test your app using `curl`:

```{.console}
$ # force curl CA bundle to be /tmp/tmpntxibdo6/ratls.pem
$ curl "https://123456789abcdef.cosmian.io" --cacert /tmp/tmpntxibdo6/ratls.pem
```


!!! info "Production deployment"

    The previous fully secured deployment method without any insecure arguments is the preferred way to deploy your application in production


## Going further

Read [develop your own app](develop.md) to go further, such as:

- Test your application
- Use dependencies 
- Use secrets to query third party services
- Use paths
- Use `mse-ignore`
- Understand memory size
- Understand environment limitations
