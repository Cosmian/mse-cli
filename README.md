# Microservice Encryption Cloud Command-Line (MSE)

[![PyPI version](https://badge.fury.io/py/mse-cli.svg)](https://badge.fury.io/py/mse-cli)

## Overview

Python CLI for Microservice Encryption. See [Github repository](https://github.com/Cosmian/mse-cli).

Read the [MSE documentation](https://docs.cosmian.com/microservice_encryption/).

## Install

```console
$ pip install -r requirements.txt
$ pip install -U .
```

## Usage

You can run MSE CLI to manage microservice deployed on the Cosmian cloud infrastructure using `mse cloud` or deployed on your own SGX infrastructure using `mse home`.

MSE Cloud ☁️ is designed to start an MSE application on Cosmian SGX hardware in a fully zero trust environment. 

MSE Home 🏕️ is designed to start an MSE application on your own SGX hardware without using all the MSE cloud infrastructure. We explain later how all the subscommands can be chained to deploy your own application. 

In that latter usage, two actors are required:
- The code provider (who can also consume the result of the MSE application)
- The SGX operator (who also owns the data to run against the MSE application)

If writting `home` or `cloud` every time upsets you, you can set the `MSE_DEFAULT_ENV` env variable to one of these values and then just omit that word in the future commands. By default, the cli will target this default environment. 


## Usage - MSE cloud

```console
$ mse cloud -h
```

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


## Usage - MSE Home

```console
$ mse home -h
```

Note: if you set the env variable `MSE_BACKTRACE=full`, a Python stacktrace will be printed in case of errors.


You can find below the use flow step by step.

### Scaffold your app

__User__: the code provider

```console
$ mse home scaffold example
```

### Test your app, your docker and your mse home configuration

__User__: the code provider

```console
$ mse home localtest --project example/
```

### Create the MSE package with the code and the docker image

__User__: the code provider

```console
$ mse home package --project example/ \
                   --output workspace/code_provider 
```

The generated package can now be sent to the sgx operator.

### Spawn the MSE docker

__User__: the SGX operator

```console
$ mse home spawn --host myapp.fr \
                 --port 7777 \
                 --size 4096 \
                 --package workspace/code_provider/package_mse_src_1683276327723953661.tar \
                 --output workspace/sgx_operator/ \
                 app_name
```

At this moment, evidences have been automatically collected and the microservice is up.

Evidences are essential for the code provider to verify the trustworthiness of the running application.

The file `workspace/sgx_operator/evidence.json` can now be shared with the other participants.

### Check the trustworthiness of the application

__User__: the code provider

The trustworthiness is established based on multiple information:
- the full code package (tarball)
- the arguments used to spawn the microservice
- evidences captured from the running microservice

Verification of the enclave information:

```console
$ mse home verify --package workspace/code_provider/package_mse_src_1683276327723953661.tar \
                  --evidence output/evidence.json \
                  --output /tmp
```

If the verification succeeds, you get the RA-TLS certificate (written as a file named `ratls.pem`) and you can now seal the code key to share it with the SGX operator.

### Seal your secrets

__User__: the code provider

```console
$ mse home seal --secrets example/secrets_to_seal.json \
                --cert /tmp/ratls.pem \
                --output workspace/code_provider/
```

### Finalize the configuration and run the application

__User__: the SGX operator

```console
$ mse home run --sealed-secrets workspace/code_provider/secrets_to_seal.json.sealed \
               app_name
```

### Test the deployed application

__User__: the SGX operator

```console
$ mse home test --test workspace/sgx_operator/tests/ \
                --config workspace/sgx_operator/mse.toml \
                app_name
```

### Decrypt the result

__User__: the code provider

Assume the SGX operator gets a result as follow: `curl https://localhost:7788/result --cacert /tmp/ratls.pem > result.enc`

Then, the code provider can decrypt the result as follow:

```console
$ mse home decrypt --key key.txt \
                   --output workspace/code_provider/result.plain \
                   result.enc
$ cat workspace/code_provider/result.plain
```

### Manage the MSE docker

__User__: the SGX operator

You can stop and remove the docker as follow:

```console
$ mse home stop [--remove] <app_name>
```

You can restart a stopped and not removed docker as follow:

```console
$ mse home restart <app_name>
```

You can get the MSE docker logs as follow:

```console
$ mse home logs <app_name>
```

You can get the MSE docker status as follow:

```console
$ mse home status <app_name>
```

You can get the list of running MSE dockers:

```console
$ mse home list
```
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
$ pytest -m 'not home not cloud'
$ mse login
$ export MSE_TEST_DOMAIN_NAME="EDIT"
$ export MSE_TEST_PRIVATE_KEY="EDIT"
$ export MSE_TEST_PUBLIC_KEY="EDIT"
$ pytest -m 'cloud'
$ # The following tests requires a SGX machine on the host
$ export TEST_PCCS_URL="https://pccs.staging.mse.cosmian.com" 
$ export TEST_SIGNER_KEY="/opt/cosmian-internal/cosmian-signer-key.pem"
$ pytest -m 'home'
```

## Documentation

```console
$ cd documentation
$ mkdocs serve
```

then open your browser on: `http://127.0.0.1:8003/`

## Dockerisation

You can build a docker for `mse home` as follow:

```console
$ docker build -t mse-home . 
```

Then run it:

```console
$ # You have to create /mnt/workspace
$ sudo mkdir /mnt/workspace
$ # Scaffold a project
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock \
            --network=host \
            mse-home scaffold example
$ # Test it
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock\
             --network=host \
             mse-home localtest --project example
$ # Package it
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock \
             --network=host \
             mse-home package --project example \
                              --output .
$ # Spawn it
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock \
             --network=host \
             mse-home spawn --host localhost \
                            --port 7779 \
                            --days 365 \
                            --signer-key /opt/cosmian-internal/cosmian-signer-key.pem \
                            --size 32768 \
                            --pccs https://pccs.staging.mse.cosmian.com \
                            --package package_example_1688025211482089576.tar \
                            --output . \
                            test_docker
$ # Verify the evidences
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock \
             --network=host \
             mse-home verify --package package_example_1688025211482089576.tar \
                             --evidence evidence.json \
                             --output .
$ # Seal the secrets
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock \
             --network=host \
             mse-home seal --secrets example/secrets_to_seal.json \
                           --cert ratls.pem \
                           --output  .
$ # Complete the configuration
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock \
            --network=host \
            mse-home run --sealed-secrets secrets_to_seal.json.sealed test_docker
$ # Query it
$ curl https://localhost:7779 --cacert /mnt/workspace/ratls.pem 
$ # Test it
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock \
             --network=host \
             mse-home test --test example/tests \
                           --config mse.toml test_docker
$ # Remove it
$ docker run -v /var/run/docker.sock:/var/run/docker.sock \
             --network=host \
             mse-home stop --remove test_docker
```

The current directory inside the docker is `/mnt/workspace`. You can retrieve all generated files in your current host in: `/mnt/workspace`. Make sure to create it before all at the exact location `/mnt/workspace` (it will not work if both locations are not aligned).  

Then you can work with `mse home` without having internet access even to install the CLI. 

Note: the docker does not contain `mse cloud`. It makes no sens since `mse cloud` is designed to be used with Internet. Plus: you need to login through the web browser, which is not possible using the docker. 