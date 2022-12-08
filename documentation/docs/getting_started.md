
!!! info "Welcome to Microservice Encryption"

    To launch your first microservice, follow this tutorial. Start with a shell on your Linux distro.


## Install mse-ctl

=== "Linux"

```{.bash}
$ pip install mse-ctl
```


## Login

You first need to login using the following command: 

```{.bash}
$ mse-ctl login
```

A web-page will be opened in your web browser and prompt for sign-up/login information.

If it's the first time you are using Microservice Encryption (MSE), you need to use the sign up tab. You will need to confirm your email and complete the configuration of your account. You can skip the payment information and start with a free plan. The plan can be upgrade later.

The credential tokens are retrieved and stored in your home folder.

You can then go back in your shell terminal and proceed to the next step.

## Deploy your first hello-world

Let's start with a ready-to-use code.

=== "Linux"

```{.bash}
$ git clone http://gitlab.cosmian.com/core/mse-app-demo
$ mse-ctl deploy --path mse-app-demo/helloworld/config/zero_trust.toml
```

Your service is now up and running !

## More subcommands

```{.bash}
$ mse-ctl --help
usage: mse-ctl [-h] [--version] {context,deploy,init,list,login,remove,scaffold,status,stop,verify} ...

Microservice Encryption Control.

options:
  -h, --help            show this help message and exit
  --version             The version of the CLI

subcommands:
  {context,deploy,init,list,login,remove,scaffold,status,stop,verify}
    context             Manage your MSE context files
    deploy              Deploy the application from the current directory into a MSE node
    init                Create a configuration file in the current directory.
    list                Print the list of apps from a project
    login               Sign up or login a user
    remove              Stop and remove the MSE app from the project
    scaffold            Create a new empty app in the current directory
    status              Print the status of a MSE app
    stop                Stop a MSE app
    verify              Verify the trustworthiness of an MSE app (no sign-in required)
```
