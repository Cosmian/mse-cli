You can run your app inside the same docker than the one MSE environement will start:

```{.console}
$ mse-ctl test --path mse-app-demo/helloworld/config/zero_trust.toml
```

The docker will start your flask server. At this point, you can interact with the endpoints or run local unit tests.

```{.console}
$ curl http://localhost:5000/
$ pytest
```

We recommand to run this test before any deployments. It assures you that the docker contains all the dependences needed for your own application.

