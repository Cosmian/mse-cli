# MicroService Encryption Control (CLI)

## Overview

Python CLI for MicroService Encryption.

## Install

```console
$ pip install mse-ctl
```

## Usage

```console
$ export MSE_CTL_BASE_URL="http://localhost:8080" 
$ export MSE_CTL_USER_CONF=examples/user.example.toml
$ python3 mse_ctl.py deploy
```

## Documentation

Get started with [https://docs.cosmian.com/microservice-encryption/](https://docs.cosmian.com/microservice-encryption/) and generate the documentation of the Python client:

```console
$ pip install sphinx numpydoc sphinx_rtd_theme sphinx_mdinclude
```

then

```console
$ sphinx-build docs docs/_build -E -a -W
```
