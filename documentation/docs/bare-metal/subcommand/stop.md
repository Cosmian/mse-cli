!!! info "User"

    This command is designed to be used by the **SGX operator**


You can stop a running application as follow:

```console
$ mse home stop [--remove] <app_name>
```

If you stop an app without the parameter `--remove`, you can restart it later by recovering the last app state. However you can't spawn a new app on the same port and with the same name: remove it before.
