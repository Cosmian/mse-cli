
You can get information about a given application as follow:

```console
$ mse status 4e3f9969-0fb3-45dd-a230-ef7b82d1f283

Microservice
        Name         = float_average
        Version      = 1.0.0
        Domain name  = demo.cosmian.app
        Billing plan = free
        Application  = app:app
        MSE docker   = ghcr.io/cosmian/mse-flask:20230124182826
        Healthcheck  = /

Deployement status
        UUID               = 4e3f9969-0fb3-45dd-a230-ef7b82d1f283
        Certificate origin = self
        Enclave size       = 1024M
        Cores amount       = 1
        Created at         = 2022-11-17 09:04:17.414325+00:00
        Expires at         = 2022-11-18 09:04:17.414190+00:00 (-1 days remaining)
        Status             = running
        Online since       = 2022-11-17 09:04:34.043340+00:00
```

The status could have the following values:
- `spawning`: the first status of a deploying app
- `initializing`: the status of an app waiting for the key to decrypt the code or other secrets needed to be successfully run
- `running`: the status of app running successfully 
- `on_error`: the status of an app stopped with a failure. It's a terminal state.
- `stopped`: the status of an app stopped without any errors. For example: when the expiration date is reached. It's a terminal state.