You can create, in an interactive way, a new configuration file for your app as follow:

```console
$ mse init
We need you to fill in the following fields

App name: test
Project name [default]: 
Hardware name [512m-eu-001]: 
Docker url [ghcr.io/cosmian/mse-flask:20230228091325]: 
Code location: .
Python application [app:app]: 
Health check endpoint [/]: 
Your app configuration has been saved in: /home/user/app/mse.toml
```

The configuration file for the previous example would be:

```toml
name = "test"
project = "default"
hardware = "512m-eu-001"

[code]
location = "."
python_application = "app:app"
healthcheck_endpoint = "/"
docker = "ghcr.io/cosmian/mse-flask:20230228091325"
```