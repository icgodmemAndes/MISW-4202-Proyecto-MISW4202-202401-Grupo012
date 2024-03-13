#!/bin/bash

docker rm autorizador-experiment usuarios-experiment nginx-experiment

docker rmi experimento_seguridad-autorizador experimento_seguridad-usuarios

docker-compose -f docker-compose.yaml up