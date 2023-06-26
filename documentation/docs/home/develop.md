One of the advantages of using MSE to protect your application and your data in the cloud, is that your original Python application does not need to be modified.
You simply need to pick your original code, design a standard Flask application without any specific intruction, write a configuration TOML file and run the `deploy` subcommand.

In this section are shared good practices and some considerations you need to know before developing or deploying your application inside an MSE node.

!!! info "Requirements"

    The MSE node environment is running on `Ubuntu 20.04` with `python 3.8`.


## Using a third-party service with secrets

Before sending the Python code of your microservice, each file is encrypted but:

- `requirements.txt`

This code is supposed to be sharable, as your convenience, to any user in order to check the trustworthiness of your app.
As a matter of fact, *do not write any secret into your code*.
For example: passwords or keys to connect to a third-party service like a remote storage or a database.

If you need such secrets to run your code, write them in a `secrets.json` file. Please see the example below.
This file will be sent to the enclave after the latter has been verified during the app deployment.
Note that this file is not encrypted and can be read by the SGX operator.
Your application will then be able to read it to retrieve the secrets it needs.

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

!!! info "Encrypting some secrets"

    If your application requires some secrets to be hidden from the SGX operator, write those secrets in another file, for example `secrets_to_seal.json`.
    Then you can seal this `secrets_to_seal.json` file with the `msehome seal` command.
    This command encrypts the `secrets.json` file using the trusted RA-TLS certificate.
    This certificate embeds the public key of the enclave, ensuring that only the enclave is able to decrypt the sealed `secrets.json` file.


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

Your application owns a dedicated storage up to 10GB. The useful directories are the following:

|          Env           |                  Path                  | Encrypted (1) | Persistent (2) |                                                   Comments                                                    |
| :--------------------: | :------------------------------------: | :-----------: | :------------: | :-----------------------------------------------------------------------------------------------------------: |
|        `$HOME`         |                `/root`                 |       ✅       |       ❌        | Could be used by third-party libraries (your application dependencies) to store caches or configuration files |
|    `$SECRETS_PATH`     |    `$HOME/.cache/mse/secrets.json`     |       ✅       |       ❌        |                The application secrets file you have sent as described in the previous section                |
| `$SEALED_SECRETS_PATH` | `$HOME/.cache/mse/sealed_secrets.json` |       ✅       |       ❌        |          The application secrets file you have sent __sealed__ as described in the previous section           |
|      `$TMP_PATH`       |                 `/tmp`                 |       ✅       |       ❌        |                                              A temporary folder                                               |
|     `$MODULE_PATH`     |               `/mse-app`               |       ✅       |       ❌        |                                   Containing the decrypted application code                                   |

Please note that writing operations in `$HOME` are about 2.5 times slower than in a `$TMP_PATH`. However, the max file size you can allocate in `$TMP_PATH` is `hardware_memory / 4` and the number of files has no limit since the sum of their size is lower than the size still available. Choose wisely the file location based on your own application constraints. 

(1) Only the enclave containing this version of your code can decrypt this directory. Another enclave or even another version of your application won't be able to read it

(2) The data will be removed when the application is stopped 

## `.mseignore` file

You can edit a `.mseignore` file in your code directory. This file is read by the CLI when deploying an app and avoid sending some files remotely.
The syntax is the same as `.gitignore`.

A default `.mseignore` is generated by the `mse scaffold` command.

## Memory size

When you declare the memory size through the field `hardware` in the `mse.toml`, you shall consider that a part of this memory is used by the system itself. 

All the libraries needed to run your application will be loaded in that memory. Therefore, the effective memory size available for your application is about: `hardware_memory - libraries_size`. 

When running the Docker container locally, you can use the option `--memory` to estimate your effective memory size. See our [github](https://github.com/Cosmian/mse-docker-base#determine-the-enclave-memory-size-of-your-image) for more details.


## Limitations

!!! info "Requirements"

    The MSE environment is running on `Ubuntu 20.04` with `python 3.8`.


Please find below limitations that you need to consider to be able to run your application in MSE:

- Do not fork processes
- Do not run subprocess (command execution)

Trying to use these system operations could make the app crash.