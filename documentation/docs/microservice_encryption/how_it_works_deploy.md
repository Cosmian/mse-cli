## Overview

The deployment step consists for the app owner in deploying their application into MSE. Basically:

- Send the code and the configuration
- Allocate the resource and spawn the app
- Check the trustworthiness of their service

The deployment is breaking down into two stages: 

- The first one consists in interacting with the Cosmian MSE backend by sending the code and the configuration
- The second one consists in interacting right with the spwaned MSE node

When you use `mse-ctl deploy` these two stages are merged into this single subcommand.

### Stage 1: spawn the MSE node

![](../images/user_flow_1.png)


### Stage 2: configure the MSE app

![](../images/user_flow_2.png)


## Deployment process

Let's describe in a deeper way what happens when the *app owner* uses: `mse-ctl deploy`.

![](../images/deploy_p1_p2.png)

### Stage 1: code encryption when dispatching

In stage 1, because the TLS connection between the app owner and Cosmian are managed by Cosmian and because the app owner wants to protect their code from Cosmian, the code is sent encrypted to Cosmian with a key only known by the app owner. 

The cryptography specifications are explained [here](security.md).

All the [scenarii](./scenarii.md) proceed that way. 

### MSE instance verification

Between stage 1 and stage 2, the app owner should verify the MSE app, that is to say:

- check that the code is **running inside an enclave**
- check that this **enclave belongs to Cosmian**
- check that the **code is exactly theirs**

If not, the app owner shouldn't proceed with stage 2 (`mse-ctl deploy` won't proceed). The stage 2 consists in sending the secret data which can be done only if we are sure the TLS connection is trusted.

For more details about this step, read [security](security.md).

### Stage 2: secret data configuration

At this point, the app owner has sent their encrypted code inside the MSE node and trusts it. 
Before the application being able to start, the MSE node needs several extra secret parameters:

- The key to decrypt the code
- The private key of the SSL certificate if the TLS connection of the app is managed by the app owner ([scenario #2](./scenarii.md#app-owner-trust-approach-fully-encrypted-saas))

Both these parameters are sent straight to the MSE node using the dedicated TLS connection managed by the enclave. Therefore, only the MSE app can decrypt the app code previously sent.

## Start the application

The app owner code is decrypted and started. 

The TLS connection used is described in the [next paragraph](./how_it_works_use.md)

