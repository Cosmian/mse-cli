You can list all your initializing and running applications as follow: 

```console
# List the apps from project 'default'
$ mse list ---name default

              App UUID               |          Creation date           |    Status    |             App summary              
------------------------------------------------------------------------------------------------------------------------------
4e3f9969-0fb3-45dd-a230-ef7b82d1f283 | 2022-11-17 09:04:17.414325+00:00 |   running    | float_average-1.0.0 on demo.cosmian.app
594508a4-2654-4dfa-ae31-4965301bd71f | 2022-11-17 16:22:11.516959+00:00 |   running    | float_average-trusted-1.0.0 on demo.cosmian.app
0b41c2a4-470e-4602-99e2-58a6bf7b123d | 2022-11-18 09:47:26.931196+00:00 |   running    | helloworld-1.0.0 on demo.cosmian.app
```

You can use `--all` option to also display stopped applications. The status of a stopped app could be 'stopped' or 'on_error'.