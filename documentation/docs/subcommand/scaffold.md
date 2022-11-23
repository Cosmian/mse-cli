
Use the subcommand `scaffold` to bootstrap your `Flask` app
with all the required configuration to be launched in Microservice Encryption.

This scaffold command prepares a fresh lite Flask app, with one endpoint on `/` answering
`GET` requests with an `Hello world` response.

```{.bash}
$ mse-ctl scaffold my_new_hello_world
$ tree my_new_hello_world            
my_new_hello_world
├── code
│   ├── app.py
│   └── requirements.txt
└── mse.toml

1 directory, 3 files
```

## Configuration of your microservice

Take a look at the configuration file:

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

The `mse.toml` file contains all the configuration for your microservice.
