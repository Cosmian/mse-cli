# Overview

The application has been developped by the app owner. Therefore, how to use it depends on its own API. 
However, there are some specificity depending on the mse configuration namely the scenarii chosen by the app owner. 

Schéma

The TLS connection is specific to each scenario:


|                          |                        P1                         |                 P2                  |
| :----------------------: | :-----------------------------------------------: | :---------------------------------: |
|   Zero trust approach    |  TLS using enclave SSL certificate (passthrough)  |  TLS using enclave SSL certificate  |
| App owner trust approach | TLS using app owner SSL certificate (passthrough) | TLS using app owner SSL certificate |
|    Any trust approach    |         TLS using Cosmian SSL certificate         |                HTTP                 |

In *App owner trust approach* and *Any trust approach* the user trusts the app owner. Therefore, the user does not need to verify the mse app. So, the user can use the app as if it is running inside a classic cloud. 

```console
$ curl https://my_app.cosmian.app/
```

In *Zero trust approach* the user has to verify the mse app and the SSL certificate before querying the app. The following diagram explains how it works: 

# Use process

Schéma

## MSE instance verification

The app user should verify the mse app, that is to say:

- Check that the code is running inside an enclave
- Check that this enclave belongs to Cosmian
- Check that the code is exactly the same as provided by the app owner

If not, the app owner shouldn't query further the application. 

Otherwise, the app user should use this certificate to proceed the next queries.

```console
$ curl https://my_app.cosmian.app/ --cacert verified_cert.pem
```

For more details about this step, read [security](security.md).

This verification can be done using: `mse-ctl verify`: 

- if the user doesn't want to verify the code fingerprint, he can use the option `--skip-fingerprint`
- if the user wants to verify the code fingerprint against a fingerprint the app ower gives, they can use the option `--fingerprint FINGERPRINT`
- if the user wants to compute on their own the code fingerprint, they can use the option `--context` and `--code`. The context file and the encrypted code tarbal should be provided by the app owner on its own way. 

```console
$ mse-ctl verify my_app.cosmian.app
Checking your app...
Code fingerprint check skipped!
Verification: success
The verified certificate has been saved at: ./cert.pem
```