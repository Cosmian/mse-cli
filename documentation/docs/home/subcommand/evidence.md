The evidence are collected when you run the `spawn` command. You can also retrieve them using the `evidence` command. 


!!! info User

    This command is designed to be used by the **SGX operator**


```console
$ msehome evidence --output workspace/sgx_operator/ \
                   app_name
```

This command collects cryptographic proofs related to the enclave and serialize them as a file named `evidence.json`.

This command will determine your pccs url by parsing the aesmd service configuration file: `/etc/sgx_default_qcnl.conf`. You can choose another pccs by specifying the `--pccs` parameter.

The file `workspace/sgx_operator/evidence.json` can now be shared with other participants.