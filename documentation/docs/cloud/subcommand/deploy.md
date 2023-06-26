
Basic usage examples can be found in [Getting started](../getting_started.md) page.

### Deploying the same app multiple times

The name of an application is unique in your project, so it is not possible to have twice the same named app
running at the same time in the same project.

When you deploy the same app several times in a row, you will be asked if you wish to replace your deployed app.
It means your previous app is automatically stopped and the new one deployed right after.

```{.console}
$ mse deploy --untrusted-ssl
An application with the same name in this project is already running...
Would you like to replace it [yes/no]? yes
Stopping the previous app...
Temporary workspace is: /tmp/tmpzdvizsb5
Encrypting your source code...
Deploying your app...
…
```

### About domain names

When deploying an application, a random dedicated domain name ID is given, for example:

```{.console}
…
Deploying your app...
App 04e9952c-981d-4601-a610-81152fe21315 creating for helloworld with 512M EPC memory and 0.38 CPU cores...
You can now run `mse logs 04e9952c-981d-4601-a610-81152fe21315` if necessary
✅ App created!
…
✅ It's now ready to be used on https://81152fe21315.cosmian.dev until 2023-01-10 20:30:36.860596+01:00. The application will be automatically stopped after this date.
…
```

When you deploy again the app with the same name, a new deployment ID is used,
but the domain name is kept as the previous one, so the URL doesn't change.

```{.console}
An application with the same name in this project is already running...
Would you like to replace it [yes/no]? yes
Stopping the previous app...
Temporary workspace is: /tmp/tmpzdvizsb5
Encrypting your source code...
Deploying your app...
…
App f565385d-8c69-4001-a75d-8d84c17e312b creating for helloworld with 512M EPC memory and 0.38 CPU cores...
You can now run `mse logs f565385d-8c69-4001-a75d-8d84c17e312b` if necessary
✅ App created!
…
✅ It's now ready to be used on https://81152fe21315.cosmian.dev until 2023-01-10 20:30:36.860596+01:00. The application will be automatically stopped after this date.
…
```

A new deployment ID is used: `f565385d-8c69-4001-a75d-8d84c17e312b`.
The URL of your microservice remains the same: `https://81152fe21315.cosmian.dev`

#### Domain name and SSL configuration

If the SSL configuration change, you cannot use the same URL, because the domain name is carried by the certificate.

For example, an application is running behind your own certificate ([fully encrypted SaaS](../scenarios.md#app-owner-trusted-fully-encrypted-saas) scenario), and you want to move it back in dev mode.

The public domain name (used with your own certificate) cannot be used by Cosmian with the certificate that will be created, because we don't own that domain name.
