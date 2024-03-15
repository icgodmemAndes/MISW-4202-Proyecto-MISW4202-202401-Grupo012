# MISW-4202-Proyecto-MISW4202-202401-Grupo012

## Security Experiment

### Delete old containers

```shell
docker rm autorizador-experiment usuarios-experiment nginx-experiment
```

### Delete old images

```shell
docker rmi experimento_seguridad-autorizador experimento_seguridad-usuarios
```

### Run All Apps

```shell
docker-compose -f docker-compose.yaml up
```

### Run with SH
```shell
sh run.sh
```

### Video example, Running Experiment

[Link](https://uniandes-my.sharepoint.com/:v:/g/personal/c_paradac_uniandes_edu_co/EUggF0kuuShNsUmRLNzQbVsBlSwuUMuNRfGNNqVR_Gjv6A?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=wuWLUF)