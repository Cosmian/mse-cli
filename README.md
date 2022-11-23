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

Copy `examples/login.toml` in `~/.config/mse-ctl/`.

Download the [mse-app-demo](http://gitlab.cosmian.com/core/mse-app-demo) repository. And go to the `helloworld` directory. 

You can find an example of `flask` application and a `mse.toml` configuration file.

### Deployment

You can deploy this application as follow:

```console
$ cd helloworld
$ mse-ctl deploy
```

`mse_ctl` creates `<uuid>.toml` in `$MSE_CTL_CONF_PATH/services` for each new deployment containing some context data.

`mse_ctl` is expecting a `mse.toml` in the current directory when using `deploy` subcommand.

### More subcommands

```console
$ mse-ctl --help
```

### More parameters

You can use these following env variables:

- `MSE_CTL_CONF_PATH` to use another directory than `~/.config/mse-ctl/`
- `MSE_CTL_DOCKER_REMOTE_URL` to use another docker url than `gitlab.cosmian.com:5000/core/mse-docker`
- `MSE_BACKEND_URL` to use another backend url than `https://backend.mse.cosmian.com`

## Documentation

!!TODO!!

Get started with [https://docs.cosmian.com/microservice-encryption/](https://docs.cosmian.com/microservice-encryption/) and generate the documentation of the Python client:

```console
$ pip install sphinx numpydoc sphinx_rtd_theme sphinx_mdinclude
```

then

```console
$ sphinx-build docs docs/_build -E -a -W
```
