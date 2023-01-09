# Example application

Basic example of an MSE application containing:
- A simple helloworld Flask application
- An MSE app config file
- Unit tests

## Test it locally

```console
$ # From your project directory
$ mse test
$ # From another terminal in your project directory
$ pip install -U -r requirements-dev.txt
$ pytest
```

## Deploy your application

```console
$ # From your project directory
$ mse deploy 
```

Your application is now ready to be used

## Test it remotely

```console
$ # From your project directory
$ TEST_REMOTE_URL="https://<app_domain_name>" pytest
```

## Use it 

You can get the certificate and check it using:

```console
$ mse verify --skip-fingerprint "<app_domain_name>"
```

You can now query your microservice:

```sh
$ curl https://<app_domain_name>/ --cacert cert.pem
```