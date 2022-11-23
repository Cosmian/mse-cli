You can create, in a interactive way, a new configuration file for your app as follow:

```console
$ mse-ctl init
We need you to fill in the following fields

App name: test
App version: 1.0.0
Project name [default]: 
Plan id [free]: 
Enable dev mode (yes/[no]): 
Code location: .
Python application [app:app]: 
Health check endpoint [/]: 
Your app configuration has been saved in: /home/user/app/mse.toml
```

The configuration file for the previous example would be:

```toml
name = "test"
version = "1.0.0"
project = "default"
plan = "free"

[code]
location = "."
python_application = "app:app"
health_check_endpoint = "/"
```