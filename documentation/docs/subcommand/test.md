!!! info "Pre-requisites"

    Before testing the app, verify that Docker service is up and your current user can use the Docker client without privilege


You can run your application inside the same Docker as MSE environment:

```{.console}
$ mse test --path mse-app-examples/helloworld/config/zero_trust.toml
Starting the docker: ghcr.io/cosmian/mse-flask:20230110142022...
You can stop the test at any time by typing CTRL^C
From another terminal, you can now run: `curl http://localhost:5000/health` or `pytest`
Reading args: --application app:app --debug
/app/code ~
* Serving Flask app 'app:app'
* Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
* Running on http://172.17.0.2:5000
Press CTRL+C to quit
* Restarting with stat
* Debugger is active!
* Debugger PIN: 965-735-704
```

The docker will start your Flask server. At this point, you can interact with the endpoints or run local unit tests.

```{.console}
$ curl http://localhost:5000/
$ pytest
```

We recommend to run this test before any deployment.
It ensures that the Docker contains all the dependencies needed for your own application.

