# CHANGELOG

## \[1.1\] - 2023-07-31

### Added

* [MSE Home] Support of Microsoft Azure attestation

### Updated

* [MSE Home] Fix hardcoded localhost occurences
* [MSE Home] Fix explicit usage of host, subject and subject alternative name

## \[1.0.1\] - 2023-07-19

### Updated

* Fix obsolete subcommands in the documentation
* Add a timeout option when using `deploy` subcommand (default is 1440 minutes)
* New args for localtest: `--no-tests`

## \[1.0.0\] - 2023-07-18

### Added

* New command `mse home` to run a microservice on your localhost SGX
* New subcommand `mse test` & `mse localtest` to run test for cloud environment
* Add a `Dockerfile` to use `mse` through a docker

### Updated

* Context and application configuration files have changed (breaking changed)

## \[0.12.0\] - 2023-04-14

### Updated

* Support MSE backend 0.5.2: changing user api

## \[0.11.0\] - 2023-04-03

### Added

* Display application metrics using `mse status`
* New option `--color` to enable/disable color for stdout/stderr

### Updated

* Field `resouce` has been renamed into `hardware`
* Complete documentation about hardware booked/bought
* `mse list` does not required the project name. It's optional.
* Use `get_server_certificate` from `intel-sgx-ra`
* Support refresh token expiration
* Take the default configuration values from the backend 

## \[0.10.2\] - 2023-03-01

### Updated

* Doc: fixing several typos and misleading information
* Scaffold: Return "Ok" to be more user-friendly
* Update documentation using new dockers

## \[0.10.1\] - 2023-02-21

### Added

* Doc: Add a paragraph concerning memory size limitations
* Doc: Add a paragraph concerning opened port for `test` and `login`
* Allow stopping several apps at once (`mse stop`)

### Updated

* Support gramine 1.4 when parsing stdout to get mr_enclave

### Fixed

* Various stdout formatting 
* Error when local image contains '/' 
* Return `1` if an error occurs for every subcommands. Remove error stacktrace

## \[0.10.0\] - 2023-02-13

### Added

* Add a spinner when computing the code fingerprint
* Add timeout when waiting for backend status
* Add a `.mseignore` to enable the app owner to not send some files in the enclave

### Updated

* Support mse-backend 0.4.1:
  * Pagination for listing apps and projects
* Bump `mse-lib-crypto` to 1.0 and `intel-sgx-ra` to 1.0

### Fixed

* Some bad urls in the `README.md` and the documentation

## \[0.9.0\] - 2023-02-01

### Added

* First release on pypi