# Microservice Encryption Cloud Command-Line (MSE)

[![PyPI version](https://badge.fury.io/py/mse-cli.svg)](https://badge.fury.io/py/mse-cli)

## Overview

Python CLI for Microservice Encryption Cloud. See [Github repository](https://github.com/Cosmian/mse-cli).

Read the [MSE documentation](https://docs.cosmian.com/microservice_encryption/).

## Install

```console
$ pip install -r requirements.txt
$ pip install -U .
```

## Usage

Note: if you declare the env variable `MSE_BACKTRACE` to the value `full`, a python stacktrace will be printed in case of errors.

### Pre-requisites

First of all sign up or sign in using:

```console
$ mse login
```

Download the [mse-app-examples](https://github.com/Cosmian/mse-app-examples) repository. And go to the `helloworld` directory.

You can find an example of `flask` application and a `mse.toml` configuration file.

### Deployment

You can deploy this application as follow:

```console
$ cd helloworld
$ mse deploy --path mse.toml
```

`mse` creates `<uuid>.toml` in `$MSE_CONF_PATH/context` for each new deployment which contains some context data.

If `--path` is not provided, `mse` is expecting a `mse.toml` in the current directory when using `deploy` subcommand.

### More subcommands

```console
$ mse --help
```

### More parameters

You can use these following env variables:

- `MSE_CONF_PATH` to use another directory than `~/.config/mse/`
- `MSE_BASE_URL` to use another backend url than `https://backend.mse.cosmian.com`
- `MSE_AUTH0_DOMAIN_NAME` to specify another auth0 login url
- `MSE_AUTH0_CLIENT_ID` to specify another auth0 tenant client id
- `MSE_AUTH0_AUDIENCE` to specify another tenant audience
- `MSE_CONSOLE_URL` to specify another console URL
- `MSE_PCCS_URL` to specify another PCCS URL 


## Development & Test

To work with the development/test environment, you shall edit the following variables with their proper values:

- `MSE_CONF_PATH`
- `MSE_AUTH0_CLIENT_ID`
- `MSE_AUTH0_DOMAIN_NAME`
- `MSE_BASE_URL`
- `MSE_AUTH0_AUDIENCE`
- `MSE_CONSOLE_URL`
- `MSE_PCCS_URL`

Do the same, if you need to use de staging environment.

Then you first need to login in in order to generate a session. Then run the test.
```console
$ mse login
$ export MSE_TEST_DOMAIN_NAME="EDIT"
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
