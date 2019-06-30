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

kubectl apply -n canary -f k8s

kubectl set image -n canary deployment/notification-controller-deployment silence=mikemcgarry/canary-silence:$SHA
kubectl set image -n canary deployment/notification-controller-deployment feathers=mikemcgarry/canary-feathers:$SHA
kubectl set image -n canary deployment/subscription-controller-deployment chirp=mikemcgarry/canary-chirp:$SHA
kubectl set image -n canary deployment/view-deployment bird_cage=mikemcgarry/canary-bird_cage:$SHA
