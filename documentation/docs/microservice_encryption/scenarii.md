
|           | Cosmian | App owner |
| :-------: | :-----: | :-------: |
| Zerotrust |    ❌    |     ❌     |
| Apptrust  |    ❌    |     ✅     |
| Anytrust  |    ✅    |     ✅     |

## Zerotrust approach: collaborative computation

|                    Specification                     |        |
| :--------------------------------------------------: | :----: |
|         Is the code encrypted when sending?          | ✅  (*) |
| Is the code encrypted when running (on disk/on ram)? |   ✅    |
| App owner can verify the mse instance when deploying |   ✅    |
|       User can verify the mse instance on use        |   ✅    |
|       Are the queries/data encrypted when send       |   ✅    |
|           App is working on a web browser            |   ❌    |


## Apptrust approach: fully encrypted SaaS

|                    Specification                     |             |
| :--------------------------------------------------: | :---------: |
|          Is the code encrypted when sending          |   ✅  (*)    |
| Is the code encrypted when running (on disk/on ram)  |      ✅      |
| App owner can verify the mse instance when deploying |      ✅      |
|       User can verify the mse instance on use        |      ❌      |
|       Are the queries/data encrypted when send       | 👁️ App Owner |
|           App is working on a web browser            |      ✅      |


## Anytrust approach: quick start dev

|                    Specification                     |           |
| :--------------------------------------------------: | :-------: |
|          Is the code encrypted when sending          |  ✅  (*)   |
| Is the code encrypted when running (on disk/on ram)  |     ✅     |
| App owner can verify the mse instance when deploying |     ✅     |
|       User can verify the mse instance on use        |     ❌     |
|       Are the queries/data encrypted when send       | 👁️ Cosmian |
|           App is working on a web browser            |     ✅     |
