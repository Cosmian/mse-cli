
You can run your tests (specified when deployed the application) against a deployed app by simply run the `test` subcommand.

```{.console}
$ mse cloud test 
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: intel-sgx-ra in /home/seb/.local/lib/python3.10/site-packages (2.0a11)
Requirement already satisfied: requests<3.0.0,>=2.31.0 in /home/seb/.local/lib/python3.10/site-packages (from intel-sgx-ra) (2.31.0)
Requirement already satisfied: cryptography<42.0.0,>=41.0.1 in /home/seb/.local/lib/python3.10/site-packages (from intel-sgx-ra) (41.0.1)
Requirement already satisfied: cffi>=1.12 in /home/seb/.local/lib/python3.10/site-packages (from cryptography<42.0.0,>=41.0.1->intel-sgx-ra) (1.15.0)
Requirement already satisfied: charset-normalizer<4,>=2 in /home/seb/.local/lib/python3.10/site-packages (from requests<3.0.0,>=2.31.0->intel-sgx-ra) (2.0.12)
Requirement already satisfied: idna<4,>=2.5 in /usr/lib/python3/dist-packages (from requests<3.0.0,>=2.31.0->intel-sgx-ra) (3.3)
Requirement already satisfied: urllib3<3,>=1.21.1 in /home/seb/.local/lib/python3.10/site-packages (from requests<3.0.0,>=2.31.0->intel-sgx-ra) (1.26.15)
Requirement already satisfied: certifi>=2017.4.17 in /home/seb/.local/lib/python3.10/site-packages (from requests<3.0.0,>=2.31.0->intel-sgx-ra) (2022.9.24)
Requirement already satisfied: pycparser in /home/seb/.local/lib/python3.10/site-packages (from cffi>=1.12->cryptography<42.0.0,>=41.0.1->intel-sgx-ra) (2.21)
Defaulting to user installation because normal site-packages is not writeable
Requirement already satisfied: pytest==7.2.0 in /home/seb/.local/lib/python3.10/site-packages (7.2.0)
Requirement already satisfied: attrs>=19.2.0 in /usr/lib/python3/dist-packages (from pytest==7.2.0) (21.2.0)
Requirement already satisfied: iniconfig in /home/seb/.local/lib/python3.10/site-packages (from pytest==7.2.0) (1.1.1)
Requirement already satisfied: packaging in /home/seb/.local/lib/python3.10/site-packages (from pytest==7.2.0) (23.0)
Requirement already satisfied: pluggy<2.0,>=0.12 in /home/seb/.local/lib/python3.10/site-packages (from pytest==7.2.0) (1.0.0)
Requirement already satisfied: exceptiongroup>=1.0.0rc8 in /home/seb/.local/lib/python3.10/site-packages (from pytest==7.2.0) (1.0.1)
Requirement already satisfied: tomli>=1.0.0 in /home/seb/.local/lib/python3.10/site-packages (from pytest==7.2.0) (2.0.1)
===================================================== test session starts =====================================================
platform linux -- Python 3.10.6, pytest-7.2.0, pluggy-1.0.0
rootdir: /home/seb/dev/microservice_encryption/mse-app-examples, configfile: setup.cfg
plugins: anyio-3.6.1
collected 2 items                                                                                                             

test_app.py ..                                                                                                          [100%]

====================================================== 2 passed in 0.75s ======================================================
```


!!! warning "Update tests"

    If you need to change the test parameters after a deployement, you can edit the context file of the corresponding application. The context file is read when you run the `test` command. 

