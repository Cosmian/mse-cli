!!! info User

    This command is designed to be used by the **SGX operator**


You can get information about a given application as follow:

```console
$ msehome status <app_name>
```

The status could have the following values:

- `initializing`: the status of an app when the configuration server or the application server is starting
- `waiting secret keys`: the status of an app waiting for the key to decrypt the code or other secrets needed to be successfully run
- `running`: the status of app running successfully  
- `on_error`: the application has stopped with an error and it's probably bugged