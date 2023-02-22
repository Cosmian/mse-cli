
`mse` uses various directories to save information about the deployed applications. 

## Login

The user login information is stored in: `$HOME/.config/mse/login.toml` on Linux/MacOS and `%APPDATA%\mse\login.toml` on Windows. 

## Workspace

Any files created during the deployment process are stored in `/tmp/uniqueName/` such as:

- The encrypted files
- The code tarball
- The certificates
- and so on.

## Context

`mse` also creates a directory `$HOME/.config/mse/context/{uuid}/` when a deployment is successfully completed.

This directory contains:

- The tarball of the encrypted code
- A TOML file which contains the details required for a user to verify the trustworthiness of the app


=== "Enclave certificate"

    ```toml
    version = "1.0"

    [config]
    name = "helloworld"
    project = "default"
    python_application = "app:app"
    docker = "ghcr.io/cosmian/mse-flask:20230124182826"
    code_secret_key = "a389f8baf2e03cebd445d99f03600b29ca259faa9a3964e529c03effef206135"

    [instance]
    id = "0b41c2a4-470e-4602-99e2-58a6bf7b123d"
    config_domain_name = "demo.cosmian.app"
    enclave_size = 1024
    expires_at = "2022-11-19 09:47:26.931077+00:00"
    ssl_secret_origin = "self"

    [instance.nonces]
    "app.py" = "f33f4a1a1555660f9396aea7811b0ff7b0f19503a7485914"
    ```

=== "App owner SSL certificate"

    ```toml
    version = "1.0"

    [config]
    name = "helloworld"
    project = "default"
    python_application = "app:app"
    docker = "ghcr.io/cosmian/mse-flask:20230124182826"
    code_secret_key = "a389f8baf2e03cebd445d99f03600b29ca259faa9a3964e529c03effef206135"
    ssl_app_certificate = "-----BEGIN CERTIFICATE[...]"

    [instance]
    id = "d17a9cbd-e2ff-4f77-ba03-e9d8ea58ca2e"
    config_domain_name = "demo.cosmian.app"
    enclave_size = 1024
    expires_at = "2022-11-18 16:22:11.516125"
    ssl_certificate_origin = "owner"

    [instance.nonces]
    "app.py" = "f33f4a1a1555660f9396aea7811b0ff7b0f19503a7485914"
    ```

=== "Deploying using `--untrusted-ssl`"

    ```toml
    version = "1.0"

    [config]
    name = "helloworld"
    project = "default"
    python_application = "app:app"
    docker = "ghcr.io/cosmian/mse-flask:20230124182826"
    code_secret_key = "23a143da6cdabadfba914e2bfc29272dbb90e8346f2bde9fab4c7b3f135ed4ad"

    [instance]
    id = "c54a6b71-257e-4b24-bd63-cbbb38429beb"
    config_domain_name = "demo.cosmian.app"
    enclave_size = 1024
    expires_at = "2022-11-18 16:00:43.352980"
    ssl_certificate_origin = "operator"

    [instance.nonces]
    "app.py" = "f33f4a1a1555660f9396aea7811b0ff7b0f19503a7485914"
    ```

This directory is designed to be shared with any app users wishing to verify the trustworthiness of the app. 

### List

You can list the contexts saved on your local host using:

```console
$ mse context --list
852a4256-fffa-457a-80ed-329166a652af -> helloworld-1.0.0 (2022-11-23 16:22:34.621387)
[...]
```

### Remove

You can remove the context directory of an app using:

```console
$ mse context --remove 852a4256-fffa-457a-80ed-329166a652af
[...]
```

!!! warning "Warning"

    If you do that, you will lose the configuration and the tar code. That will make you unable to share these information, thus an app user will be unable to verify the trustworthiness of your app


### Purge

You can also remove all your context directories:

```console
$ mse context --purge
[...]
```

!!! warning "Warning" 

    If you do that, you will lose the configuration and the tar code for all apps. That will make you unable to share these information, thus an app user will be unable to verify the trustworthiness of all of your apps


### Export

If you want app users to verify the trustworthiness of your apps, they will need this context file from the context directory which can be exported using:

```console
$ mse context --export 852a4256-fffa-457a-80ed-329166a652af
Exporting 852a4256-fffa-457a-80ed-329166a652af context in context.mse...
You can now transfer this file to your app user.
```

You can now share this file with the users.
