#!/bin/sh

nic_ifcfg=/etc/sysconfig/network-scripts/

nic_names=`ls /sys/class/net`
nic_name_arr=(${nic_names// /})
len=${#nic_name_arr[*]}
unset nic_name_arr[${len}-1]

for ((i=0; i<${len}-1; i++))
do
    sed -i 's/DEVICE=${nic_name_arr[${i}]}/DEVICE=eth${i}/g' ${nic_ifcfg}ifcfg-${nic_name_arr[${i}]}
    sed -i 's/NAME=${nic_name_arr[${i}]}/NAME=eth${i}/g' /etc/udev/rules.d/70-persistent-net.rules
    mv ${nic_ifcfg}ifcfg-${nic_name_arr[${i}]} ${nic_ifcfg}ifcfg-eth${i}
done