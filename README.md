# Microservice Encryption Control (CLI)

## Overview

Python CLI for Microservice Encryption.

## Install

```console
$ pip install -r requirements.txt
$ pip install -U .
```

Your python version must use Openssl.
You can check your ssl lib from python's console :

```console
$ >>> import ssl
$ >>> ssl.OPENSSL_VERSION
```

For Mac users, your might have to install another Python version and not use the default one (which is probably `LibreSSL`).

```console
$ brew install python@3.x
// Update your export PATH to switch to this new version
$ pip3.x install  -U .
```

## Usage

### Pre-requisites

First of all sign up or sign in using:

```console
$ mse-ctl login
```

Download the [mse-app-demo](http://gitlab.cosmian.com/core/mse-app-demo) repository. And go to the `helloworld` directory.

You can find an example of `flask` application and a `mse.toml` configuration file.

### Deployment

You can deploy this application as follow:

```console
$ cd helloworld
$ mse-ctl deploy --path conf/dev.toml
```

`mse_ctl` creates `<uuid>.toml` in `$MSE_CTL_CONF_PATH/context` for each new deployment which contains some context data.

If `--path` is not provided, `mse_ctl` is expecting a `mse.toml` in the current directory when using `deploy` subcommand.

### More subcommands

```console
$ mse-ctl --help
```

### More parameters

You can use these following env variables:

- `MSE_CTL_CONF_PATH` to use another directory than `~/.config/mse-ctl/`
- `MSE_CTL_DOCKER_REMOTE_URL` to use another docker url than `gitlab.cosmian.com:5000/core/mse-docker`
- `MSE_CTL_BASE_URL` to use another backend url than `https://backend.mse.cosmian.com`
- `MSE_AUTH0_DOMAIN_NAME` to specify another auth0 login url
- `MSE_AUTH0_CLIENT_ID` to specify another auth0 tenant client id
- `MSE_AUTH0_AUDIENCE` to specify another tenant audience
- `MSE_CTL_CONSOLE_URL` to specify another console URL

## Developpement & Test

To work with the development/test environment, you shall edit the following variables with their proper values:

- `MSE_CTL_CONF_PATH`
- `MSE_CTL_AUTH0_CLIENT_ID`
- `MSE_CTL_AUTH0_DOMAIN_NAME`
- `MSE_CTL_BASE_URL`
- `MSE_CTL_AUTH0_AUDIENCE`
- `MSE_CTL_CONSOLE_URL`

Do the same, if you need to use de staging environment.

Then you first need to login in in order to generate a session. Then run the test.
```console
$ mse-ctl login
$ export MSE_TEST_PRIVATE_KEY="EDIT"
$ export MSE_TEST_PUBLIC_KEY="EDIT"
$ pytest
```

## Documentation

```console
$ cd documentation
$ mkdocs serve
```

then open your browser on: `http://127.0.0.1:8003/`
