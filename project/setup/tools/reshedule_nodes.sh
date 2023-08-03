
for node in $(kubectl --kubeconfig ~/.kube/admin.conf get nodes -o jsonpath='{.items[*].metadata.name}' | tr " " "\n" | grep -v "heydar20.labs.hpecorp.net")
do
  kubectl --kubeconfig ~/.kube/admin.conf uncordon "$node"
done
