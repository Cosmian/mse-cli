# Cosmian Enclave Command-Line Interface

[![PyPI version](https://badge.fury.io/py/mse-cli.svg)](https://badge.fury.io/py/mse-cli)

## Overview

Python CLI for Cosmian Enclave (formerly Microservice Encryption - MSE).
See [GitHub repository](https://github.com/Cosmian/mse-cli).

Read the [Cosmian Enclave documentation](https://docs.staging.cosmian.com/compute/cosmian_enclave/overview/).

## Install

```console
$ pip install mse-cli
```

## Usage

You can run the Cosmian Enclave CLI to manage microservice deployed on the Cosmian cloud infrastructure
using `mse cloud` or deployed on SGX hardware using `mse home`.

Cosmian Enclave SaaS ☁️ is designed to start a Cosmian Enclave application on Cosmian SGX SaaS infrastructure in a 
fully zero trust environment.

Cosmian Enclave Bare Metal 🏕️ is designed to start a Cosmian Enclave application on SGX hardware or that of
a cloud provider without using the Cosmian Enclave SaaS infrastructure.

In the Cosmian Enclave Bare Metal scenario, two separate roles are defined:

- The code provider (who can also consume the result of the Cosmian Enclave application)
- The SGX operator (who also owns the data to run against the Cosmian Enclave application)

To avoid writing the subcommand part `home` or `cloud` every time, set the `MSE_DEFAULT_ENV` env 
variable to one of these values and then just omit that word in the future commands. By default, the CLI will target 
this default environment. For example: `mse cloud test` turns into `mse test`

## Usage - Cosmian Enclave SaaS

```console
$ mse cloud -h
```

Note: if you declare the env variable `MSE_BACKTRACE` to the value `full`, a python stacktrace will be printed in case
of errors.

### Pre-requisites

First of all sign up or sign in using:

```console
$ mse login
```

Download the [mse-app-examples](https://github.com/Cosmian/mse-app-examples) repository. And go to the `helloworld`
directory.

You can find an example of `flask` application and a `mse.toml` configuration file.

### Deployment

You can deploy this application as follows:

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

## Usage - Cosmian Enclave Bare Metal

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

### Create the Cosmian Enclave package with the code and the docker image

__User__: the code provider

```console
$ mse home package --project example/ \
                   --output workspace/code_provider 
```

The generated package can now be sent to the sgx operator.

### Spawn the Cosmian Enclave docker

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

If the verification succeeds, you get the RA-TLS certificate (written as a file named `ratls.pem`) and you can now seal
the code key to share it with the SGX operator.

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

Assume the SGX operator gets a result as follows: `curl https://localhost:7788/result --cacert /tmp/ratls.pem > 
result.enc`

Then, the code provider can decrypt the result as follows:

```console
$ mse home decrypt --key key.txt \
                   --output workspace/code_provider/result.plain \
                   result.enc
$ cat workspace/code_provider/result.plain
```

### Manage the Cosmian Enclave docker

__User__: the SGX operator

You can stop and remove the docker as follows:

```console
$ mse home stop [--remove] <app_name>
```

You can restart a stopped and not removed docker as follows:

```console
$ mse home restart <app_name>
```

You can get the Cosmian Enclave docker logs as follows:

```console
$ mse home logs <app_name>
```

You can get the Cosmian Enclave docker status as follows:

```console
$ mse home status <app_name>
```

You can get the list of running Cosmian Enclave dockers:

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

Then you first need to login in order to generate a session. Then run the test.

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

## Dockerisation

You can work with `mse home` without having internet access even to install the CLI by running the CLI docker. Or you
can easily run `mse cloud` by just pulling the CLI docker.

You can build a docker for `mse` as follows:

```console
$ docker build -t mse . 
```

Then run it.

In the following, the current directory inside the docker is `/mnt/workspace`. You can retrieve all generated files in
your current host in: `/mnt/workspace`. Make sure to create it before all at the exact location `/mnt/workspace` (it
will not work if both locations are not aligned).

### Cosmian Enclave SaaS

You need to login through the web browser, which is not possible through Docker. You should then run the `mse login`
inside the docker and copy/paste the displayed URL into the host web browser to be logged in inside the docker.

Make sure to mount `$HOME/.config/mse` into `/root/.config/mse` to be able to reuse the login credentials or recover
your previous deployment information when chaining the commands.

If you need to target another environment, use the docker parameter `-e` to specify the previous mentionned Cosmian Enclave env
variables.

```console
$ # You have to create /mnt/workspace
$ sudo mkdir /mnt/workspace
$ # Log in
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v $HOME/.config/mse:/root/.config/mse \
             -v /var/run/docker.sock:/var/run/docker.sock \
             --network=host \
             mse cloud login
$ # Scaffold an app
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v $HOME/.config/mse:/root/.config/mse \
             -v /var/run/docker.sock:/var/run/docker.sock \
             mse cloud scaffold my_app
$ # Test it
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v $HOME/.config/mse:/root/.config/mse \
             -v /var/run/docker.sock:/var/run/docker.sock\
             --network=host \
             mse cloud localtest --path my_app/mse.toml 
$ # Deploy the app (make sure to use --workspace .)
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v $HOME/.config/mse:/root/.config/mse \
             -v /var/run/docker.sock:/var/run/docker.sock \
             --network=host \
             mse cloud deploy --path my_app/mse.toml \
                              --workspace .
$ # Query it
$ curl https://ae5ed58137d7ec20.dev.cosmian.io/health --cacert /mnt/workspace/ratls.pem
$ # Test it
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v $HOME/.config/mse:/root/.config/mse \
             -v /var/run/docker.sock:/var/run/docker.sock \
             --network=host \
             mse cloud test
$ # Manage the context files
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v $HOME/.config/mse:/root/.config/mse \
             -v /var/run/docker.sock:/var/run/docker.sock \
             mse context --export 631a988f-4001-4593-a023-d316eb57d1f1
$ # Verify the app
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v $HOME/.config/mse:/root/.config/mse \
             -v /var/run/docker.sock:/var/run/docker.sock \
             --network=host \
             mse context --context 631a988f-4001-4593-a023-d316eb57d1f1.toml \
                         --code my_app/mse_src \
                         --workspace . \
                         ae5ed58137d7ec20.dev.cosmian.io 
$ # List your apps
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v $HOME/.config/mse:/root/.config/mse \
             -v /var/run/docker.sock:/var/run/docker.sock \
             mse list 
$ # Get your app status
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v $HOME/.config/mse:/root/.config/mse \
             -v /var/run/docker.sock:/var/run/docker.sock \
             mse status 631a988f-4001-4593-a023-d316eb57d1f1
$ # Get your app logs
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v $HOME/.config/mse:/root/.config/mse \
             -v /var/run/docker.sock:/var/run/docker.sock \
             mse logs 631a988f-4001-4593-a023-d316eb57d1f1
$ # Stop it
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v $HOME/.config/mse:/root/.config/mse \
             -v /var/run/docker.sock:/var/run/docker.sock \
             mse stop 631a988f-4001-4593-a023-d316eb57d1f1
```

### MSE Home

```console
$ # You have to create /mnt/workspace
$ sudo mkdir /mnt/workspace
$ # Scaffold a project
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock \
            mse home scaffold example
$ # Test it
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock \
             --network=host \
             mse home localtest --project example
$ # Package it
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock \
             mse home package --project example \
                              --output .
$ # Spawn it
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock \
             --network=host \
             mse home spawn --host localhost \
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
             mse home verify --package package_example_1688025211482089576.tar \
                             --evidence evidence.json \
                             --output .
$ # Seal the secrets
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock \
             mse home seal --secrets example/secrets_to_seal.json \
                           --cert ratls.pem \
                           --output  .
$ # Complete the configuration
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock \
            --network=host \
            mse home run --sealed-secrets secrets_to_seal.json.sealed test_docker
$ # Query it
$ curl https://localhost:7779 --cacert /mnt/workspace/ratls.pem 
$ # Test it
$ docker run -v /mnt/workspace:/mnt/workspace \
             -v /var/run/docker.sock:/var/run/docker.sock \
             --network=host \
             mse home test --test example/tests \
                           --config mse.toml test_docker
$ # Remove it
$ docker run -v /var/run/docker.sock:/var/run/docker.sock \
             mse home stop --remove test_docker
```

## Use case

Let's assume your microservice has to interface with a frontend. The main issue you will face up is that the RA-TLS
certificate is not allowed in your web browser, mainly because it is a self-signed cert. Also, the RA-TLS extension 
is not checked by your webbrowser, yet any query to the webservice must verify the RA-TLS extension of the 
certificate: the security is based on this verification.

Therefore, the frontend can't interact straightaway with your webservice through the web browser. You need to develop an
intermediate backend acting like a proxy. Or a simpler way could be to use the following nginx configuration:

```nginx
server {
    listen       8080 default_server;
    listen       [::]:8080 default_server;
    server_name  _;

    location / {
         proxy_pass	https://9cc36ebf3c351eba.dev.cosmian.io;
	     # We need the next two lines because the RA-TLS certificate
         proxy_ssl_trusted_certificate /tmp/tmp4b0174yn/ratls.pem;
         proxy_ssl_verify on;
	     # We need the next two lines to allow sni routing by the haproxy
         proxy_ssl_name 9cc36ebf3c351eba.dev.cosmian.io;
         proxy_ssl_server_name on;
    }
}
```