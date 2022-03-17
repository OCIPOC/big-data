#!/bin/bash

NAMESPACE=big-data

# Responsible for executing commands inside a given pod and container
function podexec () {
	local pod=$1
	local container=$2
    local cmd=$3

	kubectl exec -it $pod -c $container -n $NAMESPACE -- $cmd
}

# Check if the pod /etc/hosts file has a host
function has_host() {
	local host=$1
	local pod=$2
	local container=$3
	local ret=0
	if [[ $container ]]; then
		# Return true if a container inside a pod has host $host 
		if [[ $(podexec $pod $container 'cat /etc/hosts' | grep $host) ]]; then
			ret=1	
		fi
	else
		# Return true if the only container in the pod has host $host
		if [[ $(podexec $pod $pod  'cat /etc/hosts' | grep $host) ]]; then
			ret=1
		fi
	fi
	return "$ret"

}

# This section is supposed to add all datanodes names to /etc/hosts of resourcemanager pod.
# WIP solution. Refer to issue #4 on https://github.com/hrchlhck/k8s-bigdata
function add_host() {
	local pod_name=$1
	local datanodes=($(kubectl get pods -n $NAMESPACE -o wide --no-headers | awk '{if ($1 ~ /datanode/) {print ($1","$6)};}'))

	for datanode in "${datanodes[@]}"; do
		name=$(echo $datanode | awk '{split($1, a, ","); print a[1]}')
		ip=$(echo $datanode | awk '{split($1, a, ","); print a[2]}')

		
		if [[ $pod_name == "datanodes" ]]; then
			for _datanode in "${datanodes[@]}"; do
				_name=$(echo $_datanode | awk '{split($1, a, ","); print a[1]}')
				has_host $name $_name nodemanager
				ret1=$?
				has_host $name $_name datanode
				ret2=$?
				if [[ $ret1 == 0 || $ret2 == 0 ]]; then
					echo "Adding $ip $name to $_name"
					kubectl exec -it $_name -c datanode -n $NAMESPACE -- /bin/bash -c "echo -e ${ip} ${name} >> /etc/hosts"
					kubectl exec -it $_name -c nodemanager -n $NAMESPACE -- /bin/bash -c "echo -e ${ip} ${name} >> /etc/hosts"
				else
					echo "$_name already contains $ip $name"
				fi
			done
		else
			has_host $name $pod_name
			ret=$?
			if [[ $ret == 0 ]]; then
				echo "Adding $ip $name to $pod_name"
				kubectl exec -it $pod_name -n $NAMESPACE -- /bin/bash -c "echo -e ${ip} ${name} >> /etc/hosts"
			else
				echo "$pod_name already contains $ip $name"
			fi
		fi
	done
}

# Wait for pod to be ready
function wait_pods() {
	local pods=($(kubectl get pods -n $NAMESPACE --no-headers | awk '{print $1};'))
	for pod in "${pods[@]}"; do
		echo "Waiting for pod $pod"
		while [ "$(kubectl get pods $pod -n $NAMESPACE -o jsonpath='{.status.phase}')" != "Running" ]; do
			echo "waiting"
			sleep 3
		done
	done

}

# Used to trap ctrl+c and/or when the program ends
function finish() {
	echo -e "Ending"
	# clear_hdfs
}


################
kubectl apply -f k8s/cluster-hdfs.yml
add_host namenode
add_host historyserver
add_host datanodes
add_host resourcemanager
