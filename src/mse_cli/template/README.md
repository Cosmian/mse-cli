# Example application

A basic example of an MSE application containing:
- A simple helloworld Flask application
- An MSE app config file
- Unit tests

You should edit the following files:
- `mse_src/` with your own webservice code
- `Dockerfile` to run your webservice code into a Docker
- `mse.toml` to specify some details for the person who will run your code through the `mse home` cli
- `tests` with the tests code which can be run against your webservice
- `secrets_to_seal.json` and `secrets.json` if necessary to specify your app secrets (when using `mse home`)
  
## MSE HOME

### Test your app, your Docker and your mse home configuration

```console
$ mse home localtest --code mse_src/ \
                     --dockerfile Dockerfile \
                     --config mse.toml \
                     --test tests/
```

### Create the MSE package with the code and the Docker image

```console
$ mse home package --code mse_src/ \
                   --dockerfile Dockerfile \
                   --config mse.toml \
                   --test tests/ \
                   --output code_provider
```
The generated package can now be sent to the SGX operator.

## MSE CLOUD

### Test it locally

```console
$ # From your project directory
$ mse cloud localtest
```

### Deploy your application

```console
$ # From your project directory
$ mse cloud deploy 
```

Your application is now ready to be used

### Test it remotely

```console
$ # From your project directory
$ mse cloud test <APP_ID>
```

### Use it 

You can get the certificate and check it using:

```console
$ mse cloud verify "<app_domain_name>"
```

You can now query your microservice:

```sh
$ curl https://<app_domain_name>/ --cacert cert.pem
```