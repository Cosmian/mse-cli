You can run your application inside the same docker as MSE environment:

```{.console}
$ mse-ctl test --path mse-app-demo/helloworld/config/zero_trust.toml
```

The docker will start your Flask server. At this point, you can interact with the endpoints or run local unit tests.

```{.console}
$ curl http://localhost:5000/
$ pytest
```

We recommand to run this test before any deployment. It ensures that the docker contains all the dependencies needed for your own application.

