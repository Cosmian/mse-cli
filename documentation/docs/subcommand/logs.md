
Application logs can be fetched as follow:

```console
$ mse logs bf2575d2-d3a3-4a5f-8d48-4a97a9a07c83
Fetching the logs (last 64kB) for bf2575d2-d3a3-4a5f-8d48-4a97a9a07c83...

146.59.201.214 - - [06/Jan/2023 09:51:24] "GET / HTTP/1.1" 200 -
146.59.201.214 - - [06/Jan/2023 09:51:25] "GET / HTTP/1.1" 200 -
146.59.201.214 - - [06/Jan/2023 09:51:25] "GET / HTTP/1.1" 200 -
146.59.201.214 - - [06/Jan/2023 09:51:25] "GET / HTTP/1.1" 200 -
146.59.201.214 - - [06/Jan/2023 09:51:26] "GET / HTTP/1.1" 200 -
146.59.201.214 - - [06/Jan/2023 09:51:26] "GET / HTTP/1.1" 200 -
146.59.201.214 - - [06/Jan/2023 09:51:27] "GET / HTTP/1.1" 200 -
146.59.201.214 - - [06/Jan/2023 09:51:27] "GET / HTTP/1.1" 200 -
146.59.201.214 - - [06/Jan/2023 09:51:27] "GET / HTTP/1.1" 200 -
146.59.201.214 - - [06/Jan/2023 09:51:28] "GET / HTTP/1.1" 200 -
```

Only the last 64 kBytes are displayed.