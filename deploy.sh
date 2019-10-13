#!/usr/bin/env bash

if [ "$1" = "canary" ] || [ "$1" = "canary-ci" ]; then
    echo "Deploying to the $1 namespace"
else
    echo "Error! Namespace not recognised. Must be one of 'canary' or 'canary-ci'"
    exit 125
fi

docker build -t mikemcgarry/canary-bird_cage:latest -t mikemcgarry/canary-bird_cage:$SHA ./bird_cage
docker build -t mikemcgarry/canary-chirp:latest -t mikemcgarry/canary-chirp:$SHA ./chirp
docker build -t mikemcgarry/canary-feathers:latest -t mikemcgarry/canary-feathers:$SHA ./feathers
docker build -t mikemcgarry/canary-silence:latest -t mikemcgarry/canary-silence:$SHA ./silence

docker push mikemcgarry/canary-bird_cage:latest
docker push mikemcgarry/canary-bird_cage:$SHA
docker push mikemcgarry/canary-chirp:latest
docker push mikemcgarry/canary-chirp:$SHA
docker push mikemcgarry/canary-feathers:latest
docker push mikemcgarry/canary-feathers:$SHA
docker push mikemcgarry/canary-silence:latest
docker push mikemcgarry/canary-silence:$SHA

kubectl apply -n "$1" -f k8s/common

if [ "$1" = "canary" ]; then
    kubectl apply -n "$1" -f k8s/prod
elif [ "$1" = "canary-ci" ]; then
    kubectl apply -n "$1" -f k8s/ci
fi

kubectl set image -n "$1" deployment/notification-controller-deployment silence=mikemcgarry/canary-silence:$SHA
kubectl set image -n "$1" deployment/notification-controller-deployment feathers=mikemcgarry/canary-feathers:$SHA
kubectl set image -n "$1" deployment/subscription-controller-deployment chirp=mikemcgarry/canary-chirp:$SHA
kubectl set image -n "$1" deployment/view-deployment bird-cage=mikemcgarry/canary-bird_cage:$SHA
