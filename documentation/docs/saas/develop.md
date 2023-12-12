One of the advantages of using Cosmian Enclave to protect your application and your data in the cloud, is that your original Python application does not need to be modified.
You simply need to pick your original code, design a standard Flask application without any specific intruction, write a configuration TOML file and run the `deploy` subcommand.

In this section are shared good practices and some considerations you need to know before developing or deploying your application inside an Cosmian Enclave SaaS node.

!!! info "Requirements"

    The Cosmian Enclave node environment is running on `Ubuntu 20.04` with `python 3.8`.



## Test your application locally

This method is well-suited to test the remote environment when deploying your app.

We recall that your application is deployed into a constraint environment under a specific architecture.
This method emulates as close as possible the Cosmian Enclave SaaS node environment in production.

Before any deployment, it's strongly recommended to test your application locally against the Cosmian Enclave Docker image specified into your `mse.toml`.
It enables you to verify that your application is compatible with the Cosmian Enclave environment and all required dependencies are installed.

Since you have installed `docker` in the previous step on your own machine, you can run:

```{.console}
$ cd helloworld
$ mse cloud localtest
```


## Install dependencies

When you scaffold a new project, the configuration file contains a default Docker including minimal Flask packages.
For many reasons, this Docker could be not enough to run your own application.

Please remember that any file written in `mse_src` directory will be sent remotely to the Cosmian Enclave SaaS node.
If your `mse_src` directory contains a `requirements.txt`, these packages will be installed when running the Docker.
It enables you to quickly setup and test your application in a Cosmian Enclave environment without generating a new Docker.

However:

- There could be conflicts on underlying dependencies (ie: C dependencies) between installed packages and default environment ones
- It makes your installation not reproducible. Therefore, after a deployment, it's strongly likely that your users won't be able to verify the trustworthiness of your application
  
Then, we recommend to fork [mse-docker-flask](https://github.com/Cosmian/mse-docker-flask) to build your own Docker by integrating all your dependencies.
You can test your application against your brand new Docker by editing the field `docker` in your `mse.toml` then run:

```{.console}
$ cd helloworld
$ mse cloud localtest
```

Refer to [ docker configuration](./configuration.md#mse-docker) for more details.

## Using a third-party service with secrets

Before sending the Python code of your microservice, each file is encrypted but:

- `requirements.txt`

This code is supposed to be sharable, as your convenience, to any users in order to check the trustworthiness of your app.
As a matter of fact, *do not write any secret into your code*.
For example: passwords or keys to connect to a third-party service like a remote storage or a database.

For the same reason, do not store your SSL secret key or the configuration TOML file in the code directory.

If you need such secrets to run your code, you can write a `secrets.json` file and specify this file into the `cloud.secrets` field in the TOML configuration file. Please see the example below. This file will be sent to the enclave after the latter has been verified during the app deployment. Your application will then be able to read it to retrieve the secrets it needs.

Example of configuation file: 

```toml
name = "helloworld"
python_application = "app:app"
healthcheck_endpoint = "/whoami"
tests_cmd = "pytest"
tests_requirements = [ "intel-sgx-ra>=1.0.1,<1.1", "pytest==7.2.0",]

[cloud]
code = "./code"
tests = "./tests"
docker = "ghcr.io/cosmian/mse-pytorch:20230104085621"
project = "default"
hardware = "4g-eu-001"
secrets = "secrets.json"

[cloud.ssl]
domain_name="example.com"
certificate="./cert.secret.pem"
private_key="./key.secret.pem"
```

As you can see, the code directory (defined in `cloud.code` field) does not contain the SSL private key (defined in `ssl.private_key` field) nor the secrets file (defined in `cloud.secrets`).

!!! info "Good practice"

    Note that the configuration file does not contain any secrets values and can easily be commited into a code repository. 


Example of a `secrets.json` file:

```json
{
    "login": "username",
    "password": "azerty"
}
```

Which is used by this application code example:

```python
import os
import json

from pathlib import Path
from flask import Flask

app = Flask(__name__)


@app.route('/whoami')
def whoami():
    """A simple example manipulating secrets."""
    secrets = json.loads(Path(os.getenv("SECRETS_PATH")).read_text())
    return secrets["login"]
```

## The paths

Find below a small example using paths:

```python
import os

from http import HTTPStatus
from pathlib import Path
from datetime import datetime
from flask import Flask, Response

app = Flask(__name__)

WORKFILE: Path = Path(os.getenv("HOME")) / "date.txt"


@app.post('/')
def write_date():
    """A simple example of file writing."""
    WORKFILE.write_text(str(datetime.now()))
    return Response(status=HTTPStatus.OK)


@app.route('/')
def read_date():
    """A simple example of file reading."""
    if not WORKFILE.exists():
        return Response(response="You should write before read",
                        status=HTTPStatus.NOT_FOUND)

    txt = WORKFILE.read_text()
    WORKFILE.unlink()
    return txt
```

Your application owns a dedicated storage up to 10GB. The useful directories are the followings:

|       Env       |              Path               | Encrypted (1) | Persistent (2) |                                                   Comments                                                    |
| :-------------: | :-----------------------------: | :-----------: | :------------: | :-----------------------------------------------------------------------------------------------------------: |
|     `$HOME`     |             `/root`             |       ✔️       |       ✖️        | Could be used by third-party libraries (your application dependencies) to store caches or configuration files |
| `$SECRETS_PATH` | `$HOME/.cache/mse/secrets.json` |       ✔️       |       ✖️        |                The application secrets file you have sent as described in the previous section                |
|   `$TMP_PATH`   |             `/tmp`              |       ✔️       |       ✖️        |                                              A temporary folder                                               |
| `$MODULE_PATH`  |           `/mse-app`            |       ✔️       |       ✖️        |                                   Containing the decrypted application code                                   |

Please note that writing operations in `$HOME` are about 2.5 times slower than in a `$TMP_PATH`. However, the max file size you can allocate in `$TMP_PATH` is `hardware_memory / 4` and the number of files has no limit since the sum of their size is lower than the size still available. Choose wisely the file location based on your own application constraints.

(1) Only the enclave containing this version of your code can decrypt this directory. Another enclave or even another version of your application won't be able to read it

(2) The data will be removed when the application is stopped 

## `.mseignore` file

You can edit a `.mseignore` file in your code directory. This file is read by the CLI when deploying an app and avoid sending some files remotely.
The syntax is the same as `.gitignore`.

A default `.mseignore` is generated by the `mse cloud scaffold` command.

## Memory size

When you declare the memory size through the field `hardware` in the `mse.toml`, you shall consider that a part of this memory is used by the system itself.

All the libraries needed to run your application will be loaded in that memory. Therefore, the effective memory size available for your application is about: `hardware_memory - libraries_size`.

When running the Docker container locally, you can use the option `--memory` to estimate your effective memory size. See our [github](https://github.com/Cosmian/mse-docker-base#determine-the-enclave-memory-size-of-your-image) for more details.


## Limitations

!!! info "Requirements"

    The Cosmian Enclave environment is running on `Ubuntu 22.04` with `python 3.10`.


Please find below limitations that you need to consider to be able to run your application in Cosmian Enclave:

- Do not fork processes
- Do not run subprocess (command execution)

Trying to use these system operations could make the app crash.