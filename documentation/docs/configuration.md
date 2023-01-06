The configuration of an MSE application is written in a TOML file.
The `mse.toml` file located in the current directory is used with `mse deploy` subcommand, you can specify another TOML file with argument `--path` if needed.

```{.bash}
$ cat my_project/mse.toml
───────┬──────────────────────────────
   1   │ name = "my_project"
   2   │ version = "0.1.0"
   3   │ project = "default"
   4   │ plan = "free"
   5   │
   6   │ [code]
   7   │ location = "my_project/code"
   8   │ python_application = "app:app"
   9   │ health_check_endpoint = "/"
   10  | docker = "ghcr.io/cosmian/mse-pytorch:20230104085621"
───────┴──────────────────────────────
```

### Main section

|      Keys       | Mandatory |            Types            |                                      Description                                      |
| :-------------: | :-------: | :-------------------------: | :-----------------------------------------------------------------------------------: |
|      name       |     ✔️     |             str             |              Name of the application. It should be unique per `project`               |
|     version     |     ✔️     |             str             | Version of the application. Useful if multiple version of the same application exists |
|     project     |     ✔️     |      `default` or str       |                    Project name to regroup application for payment                    |
|      plan       |     ✔️     | `free` or other plans names |                            Plan used for your application                             |
|       dev       |           | `true` / `false` (default)  |    Developer mode allows to use Cosmian certificate for testing before production     |
| expiration_date |           |      YY-MM-DD HH/mm/ss      |                 Expiration date (UTC) before the application shutdown                 |

#### Expiration date of the application

The expiration date is tied to the self-signed certificate. When the expiration date is reached, the application will not be available.

If the plan is `free` then the expiration date will be overwritten to **1  day**.

In case the SSL certificate is provided by the application owner, this value should be lower than the expiration date of the certificate.

If no `expiration_date` is specified in the configuration file, the expiration date of the application is the expiration date of the certificate.
Otherwise, it takes the value inherited from the chosen plan.

In dev mode, the expiratation date is not used because the certificate is the one provided by Cosmian.

### Code section

|         Keys          | Mandatory | Types |                                          Description                                          |
| :-------------------: | :-------: | :---: | :-------------------------------------------------------------------------------------------: |
|       location        |     ✔️     |  str  |                         Relative path to the application code folder                          |
|        docker         |     ✔️     |  str  |                                 URL to the mse docker to run                                  |
|  python_application   |     ✔️     |  str  |                                module_name:flask_variable_name                                |
| health_check_endpoint |     ✔️     |  str  | `GET` endpoint to check if the application is ready. This endpoint should be unauthenticated. |

#### MSE docker

The MSE docker parameter defines which docker image will run in the MSE node. *Cosmian* offers one docker: 

- [ghcr.io/cosmian/mse-pytorch:20230104085621](https://github.com/Cosmian/mse-docker-pytorch/pkgs/container/mse-pytorch). This docker contains plenty of flask and machine learning dependencies.

You can test that your code properly runs inside this docker using [`mse test`](subcommand/test.md).

If you need to install other dependencies, you can create a new docker from [ghcr.io/cosmian/mse-base:20230104084742](https://github.com/Cosmian/mse-docker-base). 
This docker will be allowed to be started in an MSE architecture after a review by a *Cosmian* member. To do so, please contact tech@cosmian.com and provide your `Dockerfile` and the link to your docker image.

Note that, the `requirements.txt` from your source code directory won't be read. Your dependencies must be installed in this docker.


### SSL section

Needed if you want to use your own custom domain name. 
For more information, see [scenarii](scenarii.md).

|    Keys     | Mandatory | Types |                                                 Description                                                  |
| :---------: | :-------: | :---: | :----------------------------------------------------------------------------------------------------------: |
| domain_name |     ✔️     |  str  | Custom domain name of your application. Should also be in CN and Subject Alternative Name of the certificate |
| private_key |     ✔️     |  str  |                                Private key of the SSL connection (PEM format)                                |
| certificate |     ✔️     |  str  |                         Full certification chain of the SSL connection (PEM format)                          |

[LetsEncrypt](https://letsencrypt.org/getting-started/) is supported and recommended to get a certificate for your custom domain.

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
