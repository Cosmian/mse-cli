!!! info "Pre-requisites"

    Before testing the app, verify that Docker service is up and your current user can use the Docker client without privilege


You can run your application inside the same Docker as MSE environment:

```{.console}
$ mse cloud localtest 
Starting the docker: ghcr.io/cosmian/mse-flask:8bb7598ee7f975e9ab4d72b326361fd40ecc6a03...
Installing tests requirements...
Running tests...
========================================================================================================================= test session starts ==========================================================================================================================
platform linux -- Python 3.10.6, pytest-7.2.0, pluggy-1.0.0
rootdir: /home/seb/dev/microservice_encryption/mse-app-examples, configfile: setup.cfg
plugins: anyio-3.6.1
collected 2 items                                                                                                                                                                                                                                                      

test_app.py ..                                                                                                                                                                                                                                                   [100%]

========================================================================================================================== 2 passed in 0.04s ===========================================================================================================================
Tests successful
```

The docker will start your Flask server. Once started, the tests will be run based on the information provided in the configuration file when deployed it. 

We recommend to run this test before any deployment.
It ensures that the Docker contains all the dependencies needed for your own application.


!!! warning "Opened port"

    The `test` subcommand required the port 5000 to be opened and available on `localhost`

