You can create, in an interactive way, a new configuration file for your app as follow:

```console
$ mse cloud init
We need you to fill in the following fields

App name: test
Project name [default]: 
Hardware name [4g-eu-001]: 
Docker url [ghcr.io/cosmian/mse-flask:20230710125733]: 
Code location [mse_src]: .
Tests location [tests]: .
Python application [app:app]: 
Health check endpoint [/]: 
Your app configuration has been saved in: /home/user/app/mse.toml
```

The configuration file for the previous example would be:

```toml
name = "test"
python_application = "app:app"
healthcheck_endpoint = "/"
tests_cmd = "pytest"
tests_requirements = [ "intel-sgx-ra>=1.0.1,<1.1", "pytest==7.2.0",]

[cloud]
code = "mse_src"
tests = "tests"
docker = "ghcr.io/cosmian/mse-flask:20230710125733"
project = "default"
hardware = "4g-eu-001"
```