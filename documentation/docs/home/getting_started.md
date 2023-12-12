!!! info "Welcome to the Cosmian Enclave Bare Metal deployment tutorial"

    To launch your first confidential microservice, follow this tutorial in your favorite terminal.
    This is the bare metal tutorial: you will need to configure an SGX machine either on premise or at your cloud 
    provider first.

!!! important "Cosmian Enclave Bare Metal use to be called MSE Home"

    There are quite a few locations where the old name is still in use.

Cosmian Enclave Bare Metal is designed to start an application on your own SGX hardware or that of your cloud provider.
It does not require the use of the Cosmian Enclave SaaS Infrastructure.

This tutiorial goes into the details of the deployment flow. If you want to quickly deploy an application, you can
chain all the subcommands, as shown later.

The tutorial defines two actors:

- The code provider (who can also consume the result of the application)
- The SGX operator (who also owns the data to run against the application)

Read [the flow page](flow.md) to get more details about the role of each participant and the overall flow.

## Pre-requisites

You have to install and configure an SGX machine either on-premise or at your cloud provider first.
Cosmian provides hardware and OS requirements, as well as Ansible scripts to facilitate the deployment. 

## Install the Cosmian Enclave Bare Metal CLI

The [CLI tool](https://github.com/Cosmian/mse-cli) requires at
least [Python](https://www.python.org/downloads/) 3.8 and [OpenSSL](https://www.openssl.org/source/) 1.1.1 series.
It is recommended to use [pyenv](https://github.com/pyenv/pyenv) to manage different Python interpreters.

```{.console}
$ pip3 install mse-cli
$ mse home --help
usage: mse home [-h]
                {decrypt,evidence,scaffold,list,localtest,logs,package,restart,run,status,seal,spawn,stop,test,verify}
                ...

options:
  -h, --help            show this help message and exit

operations:
  {decrypt,evidence,scaffold,list,localtest,logs,package,restart,run,status,seal,spawn,stop,test,verify}
    decrypt             decrypt a file using Fernet symmetric encryption
    evidence            collect the evidences to verify on offline mode the application
                        and the enclave
    scaffold            create a new boilerplate application
    list                list the running applications
    localtest           test locally a MSE app in a development context
    logs                print the MSE docker logs
    package             generate a package containing the Docker image and the code to
                        run on MSE
    restart             restart an stopped MSE docker
    run                 finalise the configuration of the application docker and run the
                        application code
    status              print the MSE docker status
    seal                seal the secrets to be share with an MSE app
    spawn               spawn a MSE docker
    stop                stop and optionally remove a running MSE docker
    test                test a deployed MSE app
    verify              verify the trustworthiness of a running MSE web application and
                        get the RA-TLS certificate
```

!!! info "Pre-requisites"

    Before deploying the app, verify that the Docker service is up and your current user is part of Docker group (current user may use the Docker client without privilege)

## Scaffold your app

!!! info "User"

    This command is designed to be used by the **code provider**

```console
$ mse home scaffold example
$ tree -a example
example/
├── mse.toml
├── Dockerfile
├── mse_src
    ├── app.py
│   └── .mseignore
├── README.md
├── secrets.json
├── secrets_to_seal.json
└── tests
    ├── conftest.py
    └── test_app.py

2 directories, 9 files
```

The `mse_src` is your application directory designed to be started by `mse home` cli.

The `Dockerfile` should inherit from the `mse-docker-base` and include all dependencies required to run your app. This
docker will be run by the SGX operator.

The file `app.py` is a basic Flask application with no extra code. Adapting your own application to Cosmian Enclave 
does not require any modification to your Python code.

Example of a basic Flask application (a FastAPI application would work too!):

```python
from http import HTTPStatus
from flask import Flask, Response

app = Flask(__name__)


@app.get("/health")
def health_check():
    """Health check of the application."""
    return Response(response="OK", status=HTTPStatus.OK)


@app.route('/')
def hello():
    """Get a simple example."""
    return "Hello world"

# other endpoints
# ...
```

The [ configuration file](../cloud/configuration.md) is a TOML file used to give information to the SGX operator,
allowing to start correctly the application:

```{.toml}
name = "example"
python_application = "app:app"
healthcheck_endpoint = "/health"
tests_cmd = "pytest"
tests_requirements = [
    "cryptography>=40.0.2,<41.0",
    "intel-sgx-ra",
    "pytest==7.2.0",
]
```

This project also contains a test directory enabling you to test this project locally  and
enabling the SGX operator to test the deployed application.

!!! warning "Compatibility with WSGI/ASGI"

    To be compliant with MSE your Python application must be an [ASGI](https://asgi.readthedocs.io) or [WSGI](https://wsgi.readthedocs.io) application. It is not possible to deploy a standalone Python program. 
    In the next example, this documentation will describe how to deploy Flask applications. You can also use other ASGI applications, for instance: FastAPI.

!!! Examples "Examples"

    Visit [Cosmian Enclaves Applications Examples](https://github.com/Cosmian/mse-app-examples) to find sample 
    application examples.

## Test your app, your docker and your configuration

!!! info "User"

    This command is designed to be used by the **code provider**

```console
$ mse home localtest --code example/mse_src/ \
                     --dockerfile example/Dockerfile \
                     --config example/mse.toml \
                     --test example/tests/
```

or more concisely:

```console
$ mse home localtest --project example
```

Testing your code before sending it to the SGX operator is recommended. Be aware that any error will require to restart
the deployment flow from scratch.

## Create the application package with the code and the docker image

!!! info "User"

    This command is designed to be used by the **code provider**

This command generates a tarball named `package_<app_name>_<timestamp>.tar`.

The generated package can now be sent to the SGX operator.

```console
$ mse home package --code example/mse_src/ \
                   --dockerfile example/Dockerfile \
                   --config example/mse.toml \
                   --test example/tests/ \
                   --output code_provider/
```

or more concisely:

```console
$ mse home package --project example \
                   --output code_provider/
```

## Spawn the application docker image

!!! info "User"

    This command is designed to be used by the **SGX operator**

```console
$ mse home spawn --san myapp.fr \
                 --port 7777 \
                 --size 4096 \
                 --package code_provider/package_mse_src_1683276327723953661.tar \
                 --output sgx_operator/ \
                 app_name
```

Mandatory arguments are:

- `san`: Subject Alternative Name to use for routing with SSL passthrough (domain name, IP address or localhost)
- `port`: port used by Docker to bind the application
- `size`: memory size (in MB) of the enclave to spawn. Must be a power of 2 greater than 1024. This size is bounded by
  the SGX EPC memory.
- `pccs`: the URL of the PCCS (Provisioning Certificate Caching Service) used to generate certificate
- `package`: the application package containing the Docker images and the code
- `output`: directory to write the evidence file

This command first unpacks the tarball specified by the `--package` argument. Note that a lot of files are created
in `output` folder.

The generated file `sgx_operator/evidence.json` contains cryptographic proofs related to the enclave. It can be shared
with other participants.

This evidence file is helpful for the code provider to [ verify](#check-the-trustworthiness-of-the-application) the
running app.

The application is now started in an intermediate state waiting for any secret: we call that the configuration server.

## Collect the evidences to verify the application

!!! info "User"

    This command is designed to be used by the **SGX operator**

```console
$ mse home evidence --output sgx_operator/ \
                    app_name
```

This command collects cryptographic proofs related to the enclave and serialize them as a file named `evidence.json`.

This command will determine your PCCS URL by parsing the `aesmd` service configuration
file: `/etc/sgx_default_qcnl.conf`. You can choose another PCCS by specifying the `--pccs` parameter.

The file `sgx_operator/evidence.json` and the previous file `sgx_operator/args.toml` can now be shared with other
participants.

## Check the trustworthiness of the application

!!! info "User"

    This command is designed to be used by the **code provider**

The trustworthiness is established based on multiple information:

- the full code package (tarball)
- evidences captured from the running microservice

Verification of the enclave information:

```console
$ mse home verify --package code_provider/package_mse_src_1683276327723953661.tar \
                  --evidence output/evidence.json \
                  --output /tmp
```

If the verification succeeds, the RA-TLS certificate is written as a file named `ratls.pem`, and you can now seal the
code's key to share it with the SGX operator.

## Seal your secrets

!!! info "User"

    This command is designed to be used by the **code provider**

A sealed secrets file is designed to be shared with the application by hidding them from the SGX operator.

```console
$ mse home seal --input example/secrets_to_seal.json \
                --cert /tmp/ratls.pem \
                --output code_provider/secrets_to_seal.json.seal
```

In this example, sealed secrets file is generated as `secrets_to_seal.json.seal` file.

Share the sealed secrets file with the SGX operator.

## Finalize the configuration and run the application

!!! info "User"

    This command is designed to be used by the **SGX operator**

```console
$ mse home run --sealed-secrets code_provider/secrets_to_seal.json.seal \
               --secrets example/secrets.json \
               app_name
```

From now, the initial application developed by the code provider is fully operational and running. The configuration
server which started during the previous `spawn` step has been shutdown. Therefore, if you want to change the
configuration or the secrets, you need to stop & remove this application and restart the deployment flow from scratch.

## Test the deployed application

!!! info "User"

    This command is designed to be used by the **SGX operator**

```console
$ mse home test --test sgx_operator/tests/ \
                --config sgx_operator/mse.toml \
                app_name
```

This step is mandatory to check that the application is executed properly as the code provider expects.

Always run this step before communicating to the users about the deployment completion.

## Decrypt the results

!!! info "User"

    This command is designed to be used by the **code provider**

## Fetching `/result/secrets` endpoint

First, the SGX operator collects the result (which is encrypted):

```console
$ curl --cacert /tmp/ratls.pem https://myapp.fr:7788/result/secrets > result.enc
```

!!! info "Hostname and certificate"

    At the [ spawn](#spawn-the-mse-docker) step, remember that the parameter `--san`
    has been set to `myapp.fr` and Subject Alternative Name (SAN) is added to `/tmp/ratls.pem`.
    If Common Name (CN) or Subject Alternative Name is different from hostname, a SSL message 
    will legitimately complain and no secure connection can be established.

This encrypted result is then sent by external means to the code provider.

Finally, the code provider can decrypt the result:

```console
$ # key.bin contains the URL Safe Base64 encoded key
$ mse home decrypt --input result.enc \
                   --key key.bin
                   --output code_provider/result.plain
$ cat code_provider/result.plain
secret message with secrets.json
```

Note that the `--key` parameter contains the same key as in `secrets.json`.
Looking back at the Flask code shows that the `/result/secrets` endpoint loads
the env variable `SECRETS_PATH` to get the `key` value, using it to encrypt a text message.

This demonstrates that `secrets.json` file has been well setup for the enclave and is easily accessible through an env
variable.

## Fetching `/result/sealed_secrets` endpoint

!!! info "Sealed secrets"

    From a user perspective, this is exactly the same as fetching `/result/secrets` endpoint.
    Under the hoods, the original JSON file `secrets_to_seal.json` is transfered
    sealed to the enclave (see how to [ seal secrets](#seal-your-secrets)).

    When [ starting](#finalize-the-configuration-and-run-the-application), 
    the app seamlessly decrypts this file with the enclave's private key, 
    as sealed secrets are encrypted using the enclave's public key.
    Data from `secrets_to_seal.json` is then accessible from the Flask app, through `SEALED_SECRETS_PATH` env variable.

    This is the way to protect secrets from the SGX operator.

First, the SGX operator collects the encrypted result:

```console
$ curl --cacert /tmp/ratls.pem https://myapp.fr:7788/result/sealed_secrets > result.enc
```

Then this encrypted result is sent to the code provider by external means.

Finally, the code provider can decrypt the result:

```console
$ mse home decrypt --input result.enc
                   --key key.bin \
                   --output code_provider/result.plain
$ cat code_provider/result.plain
```

Note that the `--key` parameter is the key contained in `secrets_to_seal.json`.

The `decrypt` command only supports [Fernet](https://cryptography.io/en/latest/fernet/) algorithm. If the code
provider implements another way to encrypt the result in its microservice, another decryption code must also be
written outside Cosmian Enclave Bare Metal.

!!! info "Fix or Update"

    In case of errors at any step of the deployment flow or if the code/the configuration needs to be updated, you shall stop and remove the current running application and restart from scratch the whole deployment flow. 

