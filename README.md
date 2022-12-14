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

## Test

You first need to login in in order to generate a session. Then run the test.
```console
$ mse-ctl login
$ set -a
$ source .env.test
$ pytest
```

Also, if your test environment is not the default one, you can run the tests as follow:

```
$ MSE_CTL_BASE_URL="https://example.backend.dev.mse.cosmian.com" pytest
```

## Documentation

```console
$ cd documentation
$ mkdocs serve
```

then open your browser on: `http://127.0.0.1:8003/`
