You can stop a running application as follow:

```console
$ mse cloud stop 4e3f9969-0fb3-45dd-a230-ef7b82d1f283
Stopping and destroying the app...
✅ App gracefully stopped
```

Be aware that stopping a Cosmian Enclave app means that you can't resume it afterwards. All the resources are released and deallocated.

The context directory will be removed locally as well.