The configuration of an MSE application is written in a TOML file.
The `mse.toml` file located in the current directory is used with `mse deploy` subcommand, you can specify another TOML file with argument `--path` if needed.

```{.toml}
name = "my_project"
project = "default"
resource = "free"

[code]
location = "my_project/code"
python_application = "app:app"
healthcheck_endpoint = "/"
docker = "ghcr.io/cosmian/mse-flask:20230228091325"
```

### Main section

|      Keys       | Required |       Types       |                      Description                       |
| :-------------: | :------: | :---------------: | :----------------------------------------------------: |
|      name       |    ✔️     |      string       | Name of the application. It must be unique per project |
|     project     |    ✔️     |      string       |    Project name to regroup applications for payment    |
|    resource     |    ✔️     |      string       |   Resource name you own to use for your application    |
| expiration_date |          | YY-MM-DD HH/mm/ss | Expiration date (UTC) before the application shutdowns |

Two applications from the same project with the same name cannot be running at the same time.

You can find the name of the resources [here](https://console.cosmian.com/subscriptions).

#### Expiration date of the application

The expiration date is tied to the self-signed certificate. When the expiration date is reached, the application is not available anymore.

If the plan is `free` then the expiration date of the app will be overwritten to **4 hours**.

In case the SSL certificate is provided by the application owner, the expiration date of the app should be lower than the expiration date of the certificate.

If no `expiration_date` is specified in the configuration file, the expiration date of the application is the expiration date of the certificate.
Otherwise, it takes the value inherited from the chosen plan.

### Code section

```{.toml}
[code]
location = "my_project/code"
python_application = "app:app"
healthcheck_endpoint = "/"
docker = "ghcr.io/cosmian/mse-flask:20230228091325"
```

|         Keys         | Required | Types  |                                                                                Description                                                                                |
| :------------------: | :------: | :----: | :-----------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
|       location       |    ✔️     | string |                                                               Relative path to the application code folder                                                                |
|        docker        |    ✔️     | string | URL to the mse docker to run. It could be a local docker to run local test but it must be a remote url when deploying. See [below section](./configuration.md#mse-docker) |
|  python_application  |    ✔️     | string |                                                                      module_name:flask_variable_name                                                                      |
| healthcheck_endpoint |    ✔️     | string |       `GET` endpoint (starting with a `/`) to check if the application is ready. This endpoint should be unauthenticated and shouldn't require any parameters/data.       |
|       secrets        |          | string |     A file path (absolute or relative to the configuration file) containing secrets needed by your application to run. See [this page](develop.md) for more  details.     |

#### MSE docker

The `docker` parameter defines which Docker image will run in the MSE node. *Cosmian* offers several Docker images (use the tag with the most recent date):

- [mse-flask](https://github.com/Cosmian/mse-docker-flask/pkgs/container/mse-flask): containing flask dependencies.
- [mse-pytorch](https://github.com/Cosmian/mse-docker-pytorch/pkgs/container/mse-pytorch): containing flask and machine learning dependencies using pytorch.
- [mse-tensorflow](https://github.com/Cosmian/mse-docker-tensorflow/pkgs/container/mse-tensorflow): containing flask and machine learning dependencies using tensorflow.
- [mse-ds](https://github.com/Cosmian/mse-docker-ds/pkgs/container/mse-ds): containing flask and data science dependencies.
- [mse-fastapi](https://github.com/Cosmian/mse-docker-fastapi/pkgs/container/mse-fastapi): containing fastapi dependencies.

You can test your code properly runs inside this Docker using [`mse test`](subcommand/test.md).

If you need to install other dependencies, you can create a new Docker by forking [mse-docker-flask](https://github.com/Cosmian/mse-docker-flask).
This Docker will be allowed to be started in an MSE architecture after a review by a *Cosmian* member. To do so, please contact tech@cosmian.com and provide your `Dockerfile` and the link to your docker image.

Note that, the `requirements.txt` from your source code directory will still be read when the docker will run. We strongly recommend to put all your requirements into the docker and remove the `requirements.txt` from your source code.


### SSL section

```{.toml}
[ssl]
domain_name="demo.owner.com"
private_key="key.pem"
certificate="cert.pem"
```

Useful if you want to use your own custom domain name.
For more information, see [scenarii](scenarios.md).

|    Keys     | Mandatory | Types  |                                                               Description                                                               |
| :---------: | :-------: | :----: | :-------------------------------------------------------------------------------------------------------------------------------------: |
| domain_name |     ✔️     | string |              Custom domain name of your application. Should also be in CN and Subject Alternative Name of the certificate               |
| private_key |     ✔️     | string |       A file path (absolute or relative to the configuration file) containing the private key of the SSL connection (PEM format)        |
| certificate |     ✔️     | string | A file path (absolute or relative to the configuration file) containing the full certification chain of the SSL connection (PEM format) |

[LetsEncrypt](https://letsencrypt.org/getting-started/) is supported and recommended to get a certificate for your custom domain. 
Be aware that the expiration date is set to 3 months for all LetsEncrypt certificate: to run a long-life application you should probably use another certificate authority.

Here is the procedure to generate the certificate with *LetsEncrypt* (e.g. *example.domain.com*).

1. In your DNS provider interface, register a `CNAME` field *example.domain.com* to the Cosmian proxy `proxy.mse.cosmian.com`. This registration must be effective before running `mse deploy`.
2. To generate a certificate, the DNS-001 challenge will be used. With `certbot` run:
```{.console}
$ sudo certbot certonly -d example.domain.com --manual --preferred-challenges dns -m tech@domain.com --agree-tos
Saving debug log to /var/log/letsencrypt/letsencrypt.log

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Would you be willing, once your first certificate is successfully issued, to
share your email address with the Electronic Frontier Foundation, a founding
partner of the Let's Encrypt project and the non-profit organization that
develops Certbot? We'd like to send you email about our work encrypting the web,
EFF news, campaigns, and ways to support digital freedom.
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(Y)es/(N)o: Y
Account registered.
Requesting a certificate for example.domain.com

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Please deploy a DNS TXT record under the name:

_acme-challenge.example.domain.com.

with the following value:

M1XAAAAAAAAAAAAAAAAAAAAAAAAAAA5Yo

[...]

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Press Enter to Continue

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/example.domain.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/example.domain.com/privkey.pem
This certificate expires on 2023-03-07.
These files will be updated when the certificate renews.

[...]
```

3. A DNS `TXT` record should be registered under a given name in your DNS provider interface. After doing that, the certificate will be generated. Delete this record at the end of the process.
4. Read the two PEM files and create your own `ssl` section in the MSE configuration file. You are now ready to deploy your app using: `mse deploy`.
