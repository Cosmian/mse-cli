One of the advantages of using `mse` to protect your application and your data in the cloud, is that you don't need to adapt your own Python application. Indeed, you just need to pick your original code, design a standard Flask application without specific intructions, write a configuration TOML file and run the `deploy` subcommand. 

In this section, we will list good practices or various considerations you need to know before developing or deploying your application inside an `mse` node. 

## Using a third-party service with secrets

Before sending the Python code of your microservice, each file is encrypted but:

- `requirements.txt`

This code is supposed to be sharable, as your convenience, to any users in order to check the trustworthiness of your app. As a matter of fact, *do not write any secret into your code*. For example: passwords or keys to connect to a third-party service like a remote storage or a database. 

For the same reason, do not store your SSL secret key or the configuration TOML file in the code directory.

If you need such secrets to run your code, you can write a `secrets.json` file and specify this file into the `code.secrets` field in the TOML configuration file. Please see the example below. This file will be sent to the enclave after the latter has been verified during the app deployment. Your application will then be able to read it to retrieve the secrets it needs.

Example of configuation file: 

```toml
name="helloworld"
project="default"
resource="free"

[code]
location="./code"
python_application="app:app"
healthcheck_endpoint="/whoami"
docker="ghcr.io/cosmian/mse-flask:20230228091325"
secrets="./secrets.json"

[ssl]
domain_name="example.com"
certificate="./cert.secret.pem"
private_key="./key.secret.pem"
```

As you can see, the code directory (defined in `code.location` field) does not contain the SSL private key (defined in `ssl.private_key` field) nor the secrets file (defined in `code.secrets`).

!!! info "Good practice"

    Note that the configuration file does not contain any secrets values and can easily be commited into a code repository. 


Example of a secret file:

```json
{
    "login": "username",
    "password": "azerty"
}
```

Which is used by this application code example:

```toml
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

```toml
import os

from http import HTTPStatus
from pathlib import Path
from datetime import datetime
from flask import Flask, Response

app = Flask(__name__)

WORKFILE: Path = Path(os.getenv("HOME")) / "date.txt"


@app.post('/')
def write_date():
    """A simple example of file writting."""
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

You application owns a dedicated storage up to 10GB. The useful directories are the followings:

|       Env       |              Path               | Encrypted (1) | Persistent (2) |                                                   Comments                                                    |
| :-------------: | :-----------------------------: | :-----------: | :------------: | :-----------------------------------------------------------------------------------------------------------: |
|     `$HOME`     |             `/root`             |       ???       |       ???        | Could be used by third-party libraries (your application dependencies) to store caches or configuration files |
| `$SECRETS_PATH` | `$HOME/.cache/mse/secrets.json` |       ???       |       ???        |                The application secrets file you have sent as described in the previous section                |
|   `$TMP_PATH`   |             `/tmp`              |       ???       |       ???        |                                              A temporary folder                                               |
| `$MODULE_PATH`  |           `/mse-app`            |       ???       |       ???        |                                   Containing the decrypted application code                                   |

Please note that writting operations in `$HOME` are about 2.5 times slower than in a `$TMP_PATH`. However, the max file size you can allocate in `$TMP_PATH` is `resource_memory / 4` and the number of files has no limit since the sum of their size is lower than the size still available. Choose wisely the file location based on your own application constraints. 

(1) Only the enclave containing this version of your code can decrypt this directory. Another enclave or even another version of your application won't be able to read it

(2) The data will be removed when the application is stopped 

## Mseignore file

You can edit a `.mseignore` file in your code directory. This file is read by the cli when deploying an app and avoid sending some files remotely. 
The syntax is the same as `.gitignore`.

A default `.mseignore` is generated by the `mse scaffold` command.

## Memory size

When you declare the memory size through the field `resource` in the `mse.toml`, you shall consider that a part of this memory is used by the system itself. 

All the librairies needed to run your application will be loaded in that memory. Therefore, the effective memory size available for your application is about: `resource_memory - librairies_size`. 

When calling the docker on your localhost, you can use the option `--memory` to estimate your effective memory size. See our [github](https://github.com/Cosmian/mse-docker-base#determine-the-enclave-memory-size-of-your-image) for more details.


## Limitations

Please find below limitations that you need to consider to be able to run your application in MSE:

- Do not fork processes
- Do not run subprocess (command execution)

Trying to use these system functionalities could make the app crash.