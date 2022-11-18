The configuration of an MSE app is written in a TOML file. This file is read in the current directory when using `deploy` subcommand if a `mse.toml` exists. Otherwise use `--path` to specify its location.

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
   8   │ encrypted = true
   9   │ python_application = "app:app"
  10   │ health_check_endpoint = "/"
───────┴──────────────────────────────
```

Find below the description of this configuration file. 

## The main section

|      Keys       | Mandatory |            Types            |                                              Description                                               |
| :-------------: | :-------: | :-------------------------: | :----------------------------------------------------------------------------------------------------: |
|      name       |     ✅     |             str             |                      The name of the app. It should be unique in a given project                       |
|     version     |     ✅     |             str             |         The version of the app. An app can exist with various version number in a same project         |
|     project     |     ✅     |             str             |                                     The project the app belongs to                                     |
|      plan       |     ✅     | `free` or other plans names |                             The name of the plan your project is linked to                             |
|       dev       |           | `True` / `False` (default)  |       Whether you want to start your app in dev mode. See <TODO> for more details about dev mode       |  |
| expiration_date |           |      YY-MM-DD HH/mm/ss      | The expiration date of your app once deploy. See <TODO> for more information about the expiration date |

## The code section

|         Keys          | Mandatory |      Types       |                                             Description                                              |
| :-------------------: | :-------: | :--------------: | :--------------------------------------------------------------------------------------------------: |
|       location        |     ✅     |       str        | The path (absolue or relative from the config file location) where to find the application to deploy |
|       encrypted       |     ✅     | `True` / `False` |                   Wheter the application should be sent encrypted to the mse node                    |
|  python_application   |     ✅     |       str        |                                   module_name:flask_variable_name                                    |
| health_check_endpoint |     ✅     |       str        |          An endpoint `mse-ctl` can request to determine if the application is up and ready           |

## The ssl section

For more information about the ssl information. See <TODO>

|    Keys     | Mandatory | Types |                                        Description                                         |
| :---------: | :-------: | :---: | :----------------------------------------------------------------------------------------: |
| domain_name |     ✅     |  str  | The chosen domain name for your application. It should be the same than in the certificate |
| private_key |     ✅     |  str  |                     The private key (PEM format) of the SSL connection                     |
| certificate |     ✅     |  str  |                    The full chain certificate  (PEM format) of the SSL                     |
