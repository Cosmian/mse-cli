# Microservice Encryption Control (CLI)

## Overview

Python CLI for Microservice Encryption.

## Install

```console
$ pip install -r requirements.txt
$ pip install -U .
```

## Usage

### Pre-requisites

First of all sign up or sign in using:

```console
$ mse-ctl login
```

Then, download the [mse-app-demo](http://gitlab.cosmian.com/core/mse-app-demo) repository. And go to the `helloworld` directory.

You can find an example of `flask` application and a `mse.toml` configuration file.

### Deployment

You can deploy this application as follow:

```console
$ cd helloworld
$ mse-ctl deploy --path conf/dev.toml
```

`mse_ctl` creates `<uuid>.toml` in `$MSE_CTL_CONF_PATH/context` for each new deployment containing some context data.

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

## Documentation

```console
$ cd documentation
$ mkdocs serve
```

then open your browser on: `http://127.0.0.1:8003/`

