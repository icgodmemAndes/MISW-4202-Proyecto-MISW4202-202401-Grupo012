# MISW-4202-Proyecto-MISW4202-202401-Grupo012

### Delete old containers

```shell
docker rm redis-experiment queue-experiment payment-gateway-one-experiment payment-gateway-two-experiment payment-experiment recovery-payment-experiment monitor-experiment
```

### Delete old images

```shell
docker rmi misw-4202-proyecto-misw4202-202401-grupo012-payment-gateway-one misw-4202-proyecto-misw4202-202401-grupo012-payment-gateway-two misw-4202-proyecto-misw4202-202401-grupo012-payment misw-4202-proyecto-misw4202-202401-grupo012-recovery misw-4202-proyecto-misw4202-202401-grupo012-monitor 
```

### Run All Apps

```shell
docker-compose -f docker-compose.yaml up
```