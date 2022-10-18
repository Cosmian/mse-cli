# MicroService Encryption Control (CLI)

## Overview

Python CLI for MicroService Encryption.

## Install

```console
$ pip install mse-ctl
```

## Usage

```console
$ cd examples
$ export MSE_CTL_BASE_URL="http://localhost:8080" 
$ export MSE_CTL_CONF_PATH=.
$ python3 mse_ctl.py deploy
```

`mse_ctl` creates:
- `login.toml` in `$MSE_CTL_CONF_PATH` containing user credentials
- `<uuid>.toml` in `$MSE_CTL_CONF_PATH/services` for each new deployement containing some context data

`mse_ctl` is expecting a `mse.toml` in the current directory when using `deploy` subcommand.

## Documentation

Get started with [https://docs.cosmian.com/microservice-encryption/](https://docs.cosmian.com/microservice-encryption/) and generate the documentation of the Python client:

```console
$ pip install sphinx numpydoc sphinx_rtd_theme sphinx_mdinclude
```

then

```console
$ sphinx-build docs docs/_build -E -a -W
```
