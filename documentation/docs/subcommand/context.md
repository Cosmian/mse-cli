
`mse-ctl` uses various directories to save information about the deployed applications. 

## Login

The user login information is stored in: `$HOME/.config/mse-ctl/login.toml` on Linux/Darwin and `%APPDATA%\mse-ctl\login.toml` on Windows. 

## Workspace

Any files created during the deployment process are stored in `/tmp/uniqueName/` such as:

- The encrypted files
- The code tarball
- The certificates
- and so on.

## Context

`mse-ctl` also creates a directory `$HOME/.config/mse-ctl/context/uuid/` when a deployment is sucessfully completed. This directory contains:

- The tarball of the encrypted code
- A toml file with the details required for a user to verify the trustworthiness of the app


=== "Enclave certificate"

    ```toml
    version = "1.0"

    [config]
    name = "helloworld"
    version = "1.0.0"
    project = "default"
    python_application = "app:app"

    [instance]
    id = "0b41c2a4-470e-4602-99e2-58a6bf7b123d"
    config_domain_name = "demo.cosmian.app"
    enclave_size = 1
    expires_at = "2022-11-19 09:47:26.931077+00:00"
    docker_version = "e1d88756"
    ssl_certificate_origin = "self"
    ```

=== "App owner SSL certificate"

    ```toml
    version = "1.0"

    [config]
    name = "helloworld"
    version = "1.0.0"
    project = "default"
    python_application = "app:app"
    code_sealed_key = "a389f8baf2e03cebd445d99f03600b29ca259faa9a3964e529c03effef206135"
    ssl_app_certificate = "-----BEGIN CERTIFICATE[...]"

    [instance]
    id = "d17a9cbd-e2ff-4f77-ba03-e9d8ea58ca2e"
    config_domain_name = "demo.cosmian.app"
    enclave_size = 1
    expires_at = "2022-11-18 16:22:11.516125"
    docker_version = "11d789bf"
    ssl_certificate_origin = "owner"
    ```

=== "Dev mode"

    ```toml
    version = "1.0"

    [config]
    name = "helloworld"
    version = "1.0.0"
    project = "default"
    python_application = "app:app"
    code_sealed_key = "23a143da6cdabadfba914e2bfc29272dbb90e8346f2bde9fab4c7b3f135ed4ad"

    [instance]
    id = "c54a6b71-257e-4b24-bd63-cbbb38429beb"
    config_domain_name = "demo.cosmian.app"
    enclave_size = 1
    expires_at = "2022-11-18 16:00:43.352980"
    docker_version = "e1d88756"
    ssl_certificate_origin = "operator"
    ```

This directory is designed to be shared with any app users wishing to verify the trustworthiness of the app. 

### List

You can list the context saved on your local host using:

```console
$ mse-ctl context --list
852a4256-fffa-457a-80ed-329166a652af -> helloworld-1.0.0 (2022-11-23 16:22:34.621387)
[...]
```

### Clean

You can remove the context directory of an app using:

```console
$ mse-ctl context --clean 852a4256-fffa-457a-80ed-329166a652af 
[...]
```

!!! warning "If you do that, you will lost the configuration and the tar code. Which make you unable to share these information and make your app user unable to verify the trustworthiness of your app"


### Purge

You can also remove all your context direcotries:

```console
$ mse-ctl context --purge
[...]
```

!!! warning "If you do that, you will lost the configuration and the tar code. Which make you unable to share these information and make your app user unable to verify the trustworthiness of your apps"


### Export

If you want an app user to verify the trustworthiness of your apps, they will need this context directory which can be exported as a tarball doing:

```console
$ mse-ctl context --export 852a4256-fffa-457a-80ed-329166a652af
Exporting 852a4256-fffa-457a-80ed-329166a652af context in context.tar...
You can now transfer this file to your app user.
```

You can now share this tarball with the users.
