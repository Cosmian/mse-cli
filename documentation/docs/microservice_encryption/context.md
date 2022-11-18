
`mse-ctl` uses various directory to save information about the deployed application. 

## Login

The user login information are stored in: `$HOME/.config/mse-ctl/login.toml` on Linux/Darwin and `%APPDATA%\mse-ctl\login.toml` on Windows. 

## Workspace

Any files created during the deployment process are stored in `/tmp/<app_name-app_version>/` such as:

- The encrypted files
- The code tarball
- The certificates
- and so on.

## Context

`mse-ctl` also create a file in `$HOME/.config/mse-ctl/context/<uuid.mse>` when a deployment is sucessfully completed. This file is designed to be shared with any app users wishing to verify the trustworthiness of the app. 

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

