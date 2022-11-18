# Overview

The deployment step consists for the app owner in deploying their application into MSE. Basically:
- Send the code and the configuration
- Allocate the resource and spawn the app
- Check the trustworthiness of their service

The deployment is breaking down into two stages : 
- The first one consists in interacting with the cosmian mse backend by send the code and the configuration
- The second one consists in interacting right with the mse node

When you use `mse-ctl deploy` these two stages are merged in this single subcommand.

## Stage 1: spawn the mse node

Schéma (TODO show the orgin of this SSL cert)

## Stage 2: configure the mse app

Schéma

# Deployment process

Let's describe what happens when the *app owner* use: `mse-ctl deploy`.

Schéma

## Code encryption when dispatching

In stage 1, because the TLS connection between the app owner and Cosmian are managed by Cosmian and because the app owner wants to protect their code from Cosmian, the code is sent encrypted to Cosmian with a key only known by the app owner. 

The cryptography specifications are: TODO


All the [scenarii](./scenarii.md) proceed that way. 

## MSE instance verification

Between stage 1 and stage 2, the app owner should verify the mse app, that is to say:

- Check that the code is running inside an enclave
- Check that this enclave belongs to Cosmian
- Check that the code is exactly theirs

If not, the app owner shouldn't proceed with stage 2 (`mse-ctl deploy` won't proceed). The stage 2 consists in sending the secret data which can be done only if we are sure the TLS connection is trusted.

For more details about this step, read [security](security.md).

# Secret data configuration

At this point, the app owner has sent its code encrypted inside the mse node and trusts it. 
Before the application being able to start, the mse node needs several extra secret parameters:

- The key to decrypt the code
- The private key of the SSL certificate if the TLS connection of the app is managed by the app owner (scenario 2)

Both this parameters are sent straight to the mse node using the dedicated TLS connection managed by the enclave. Thefore, only the mse app can decrypt the app code previously sent.

# Start the application

The code is decrypted and started. 

The TLS connection used is described in the [next paragraph](./how_it_works_use.md)

