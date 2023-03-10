## \[0.10.2\] - 2023-XX-YY

### Added

*

### Updated

* Doc: fixing several typos and misleading information
* Scaffold: Return "Ok" to be more user-friendly
* Update documentation using new dockers

### Fixed

*

### Removed

* 

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

### Removed

* 


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

### Removed

* 


## \[0.9.0\] - 2023-02-01

### Added

* First release on pypi