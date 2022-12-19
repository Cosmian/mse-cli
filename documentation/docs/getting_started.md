
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
$ mse-ctl deploy --path mse-app-demo/helloworld/config/zero_trust.toml
```

That's it!

Your microservice will be up in a few seconds at `https://{uuid}.cosmian.app` (replace `{uuid}` with the one from `mse-ctl deploy` command output).

Check the status with `openssl` and `curl`:

```{.console}
$ export MSE_UUID="..." # your UUID here
$ # save SSL certificate of the app in sgx_cert.pem
$ openssl s_client -showcerts -connect "$MSE_UUID.cosmian.app:443" </dev/null 2>/dev/null | openssl x509 -outform PEM >sgx_cert.pem
$ # force curl CA bundle to be sgx_cert.pem
$ curl "https://$MSE_UUID.cosmian.app" --cacert sgx_cert.pem
```

## Scaffold a new project

The `scaffold` subcommand allows you to prepare your own project starting with a new fresh Flask application with only one endpoint `/`.

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

Edit the default configuration file `mse.toml` as needed (see [Configuration)](configuration.md)).

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
