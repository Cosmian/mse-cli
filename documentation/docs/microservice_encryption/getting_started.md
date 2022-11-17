
!!! info "Welcome to Microservice Encryption"

    To launch your first microservice, follow this tutorial. Start with a shell on your Linux distro.


## Install mse-ctl

=== "Linux"

```{.bash}
$ pip install mse-ctl
```

## Sign up

If it's the first time you are using Microservice Encryption, you need to sign up for an account:

```{.bash}
$ mse-ctl signup
```

A pop-up will open and prompt for sign-up information.
Sign up can be done using your email address, or via SSO by using your Google or Github account.

You can skip the payment information and start with a free plan. The plan can be upgrade later.

## Login

Now you have an account, let's sign-in:

```{.bash}
$ mse-ctl login
```

A pop-up will open and prompt for sign-in information.
Credentials are retrieved and stored in your home folder.

## Deploy your first hello-world

Let's use a ready-to-use code provided.

=== "Linux"

```{.bash}
$ git clone http://gitlab.cosmian.com/core/mse-app-demo
$ mse-ctl deploy --path mse-app-demo/helloworld
```

Your service is now up and running !

## More subcommands

```{.bash}
$ mse-ctl --help
```
