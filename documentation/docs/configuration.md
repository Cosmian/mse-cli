The configuration of an MSE app is written in a TOML file. This file is read in the current directory when using `deploy` subcommand if an `mse.toml` exists. Otherwise use `--path` to specify its location.

Let's remind the quick start example app configuration file:

```{.bash}
$ cat my_new_hello_world/mse.toml 
───────┬──────────────────────────────
   1   │ name = "my_new_hello_world"
   2   │ version = "0.1.0"
   3   │ project = "default"
   4   │ plan = "free"
   5   │ 
   6   │ [code]
   7   │ location = "/home/user/some/path/my_new_hello_world/code"
   8   │ python_application = "app:app"
   9   │ health_check_endpoint = "/"
───────┴──────────────────────────────
```

Find below the description of the configuration file. 

## The main section

|      Keys       | Mandatory |            Types            |                                                                  Description                                                                  |
| :-------------: | :-------: | :-------------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------: |
|      name       |     ✔️     |             str             |                                          The name of the app. It should be unique in a given project                                          |
|     version     |     ✔️     |             str             |                            The version of the app. An app can exist with various version number in a same project                             |
|     project     |     ✔️     |             str             |                                                        The project the app belongs to                                                         |
|      plan       |     ✔️     | `free` or other plans names |                                                The name of the plan your project is linked to                                                 |
|       dev       |           | `True` / `False` (default)  |                          Whether you want to start your app in dev mode. See <TODO> for more details about dev mode                           |  |
| expiration_date |           |      YY-MM-DD HH/mm/ss      | The expiration date (UTC) of your app once deploy. See [next paragraph](configuration.md#expiration-date-of-the-application) for more details |

### Expiration date of the application

When the expiration date is reached, the application will be shutdown. Mainly because the SSL certificate needs to be renewed. It requires a new deployment because of our implement security measures to garantee zero trust environment.

If the plan is `free` then the expiration date will be overwritten to the value inherited from this plan: **1  day**. 

In case the SSL certificate is provided by the app owner, this value should be lower than the expiration date of the certificate.

If no `expiration_date` is specified in the configuration file, the expiration date of the application is the expiration date of the certificate if some. Otherwise, it takes the value inherited from the chosen plan. 

In dev mode, the expiration date is infinite.

## The code section

|         Keys          | Mandatory | Types |                                             Description                                              |
| :-------------------: | :-------: | :---: | :--------------------------------------------------------------------------------------------------: |
|       location        |     ✔️     |  str  | The path (absolue or relative from the config file location) where to find the application to deploy |
|  python_application   |     ✔️     |  str  |                                   module_name:flask_variable_name                                    |
| health_check_endpoint |     ✔️     |  str  |          An endpoint `mse-ctl` can request to determine if the application is up and ready           |

## The SSL section

For more information about the SSL information. See [Scenarii](scenarii.md).

|    Keys     | Mandatory | Types |                                        Description                                         |
| :---------: | :-------: | :---: | :----------------------------------------------------------------------------------------: |
| domain_name |     ✔️     |  str  | The chosen domain name for your application. It should be the same than in the certificate |
| private_key |     ✔️     |  str  |                     The private key (PEM format) of the SSL connection                     |
| certificate |     ✔️     |  str  |                    The full chain certificate  (PEM format) of the SSL                     |

Find below the procedure to generate the certificate with *LetsEncrypt* for your own mse app domain name (here: *example.domain.com*).

1. In your DNS provider interface, register a `A` field *example.domain.com* for the cosmian proxy ip address: `57.128.36.109`. This registration must be effective before running any `mse-ctl deploy`.
2. To generate a certificate, the DNS-001 challenge will be used. With `certbot` run:
```console
# apt install certbot
# certbot certonly -d example.domain.com --manual --preferred-challenges dns -m tech@domain.com  --agree-tos
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
3. As you can see in the `stdout`, a DNS `TXT` record should be registered under a given name in your DNS provider interface. After doing that, the certificate will be generated. Delete this record at the end of the process.
4. Read the two pem files and create your own `ssl` section in the mse configuration file. You are now ready to deploy your app using: `mse-ctl deploy`.