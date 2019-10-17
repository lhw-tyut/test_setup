#!/bin/bash

# for bare metal interface
# Copyright(C): zhaoercheng, capitalonline

function usage()
{
    echo "USAGE: $0 [OPTIONS] < rpm-install|crc|fio|nic-down|nic-up|system-device|data-device|final-op|kernel-update > <password>"
    echo ""
    echo "Available OPTIONS:"
    echo ""
    echo "  --ipaddr  <ipaddr>      Ip address. Such as: 10.11.11.0/24. "
    echo "  --fix-ip  <fix_ip>      Fix client ip. Such as: 10.10.10.10. "
    echo "  --ip-range  <ip_range>  Ip range. Such as: 10.10.10.10~10.10.10.20. "
    echo "  --nic-name  <nic_name>  Nic name. "
    echo "  -h, --help              Show the help message."
    echo ""
    exit 0
}


function parse_options()
{
    args=$(getopt -o h -l ipaddr:,fix-ip:,ip-range:,nic-name:,help -- "$@")

    if [[ $? -ne 0 ]];then
        usage >&2
    fi

    eval set -- "${args}"

    while true
    do
        case $1 in
            --ipaddr)
                ipaddr=$2
                shift 2
                ;;
            --fix-ip)
                fix_ip=$2
                shift 2
                ;;
            --ip-range)
                ip_range=$2
                shift 2
                ;;
            --nic-name)
                nicname=$2
                shift 2
                ;;
            -h|--help)
                usage
                ;;
            --)
                shift
                break
                ;;
            *)
                usage
                ;;
        esac
    done

    if [[ $# -ne 2 ]]; then
        usage
    fi
    action=$1
    password=$2
}


function is_valid_action()
{
    action=$1
    valid_action=("rpm-install" "crc" "fio" "nic-down" "nic-up" "system-device" "data-device" "final-op" "kernel-update")
    for val in ${valid_action[@]}; do
        if [[ "${val}" == "${action}" ]]; then
            return 0
        fi
    done
    return 1
}

parse_options $@

is_valid_action ${action} || usage


case "${action}" in
    crc)
        cdscrc=1 ;;
    fio)
        cdsfio=1 ;;
    mount)
        cdsmount=1 ;;
    nic-down)
        cdsnicdown=1 ;;
    nic-up)
        cdsnicup=1 ;;
    system-device)
        cds_system_device=1 ;;
    data-device)
        cds_data_device=1 ;;
    final-op)
        cds_final_operation=1 ;;
    rpm-install)
		cds_rpm_install=1 ;;
	kernel-update)
		cds_kernel_update=1 ;;
    *)
        echo "Unknown Action:${action}!"
        usage
        ;;
esac

scan_ip=`echo $ipaddr |cut -d '/' -f 1`
host_ips_file="/home/host_ips$scan_ip"
log_file="/home/bare_metal_project_log"
data_path="/data"
sshpass_prefix="sshpass -p $password ssh -o StrictHostKeyChecking=no"


function package_install_on_master_node()
{
	yum install expect -y >> /dev/null
	yum install sshpass -y >> /dev/null
	yum install nmap -y >> /dev/null
}


function rpm_install_all_node()
{
	host_number=`cat $host_ips_file |wc -l`

    for((n=1;n<=$host_number;n++))
    do
            host_ip=`cat $host_ips_file |sed -n "$n"p`
            $sshpass_prefix -f $host_ip  "yum install psmisc -y >> /dev/null" &
    done
}

function install_rpm_all()
{
	package_install_on_master_node
	rpm_install_all_node
	sleep 10
}

function get_host_ip()
{
	if [[ ! -f $host_ips_file ]]; then
		nmap -sn $ipaddr |grep "Nmap scan report" |awk '{print $5}' > $host_ips_file
	fi
}


function iops_test()
{
	IOPS_NUM=`$sshpass_prefix -f $1 "fio -filename=$2 -direct=1 -iodepth 128 -thread -rw=read  -ioengine=libaio -bs=128k -size=10G -numjobs=1 -runtime=60 -group_reporting -name=read |grep IOPS |cut -d '=' -f 2 |cut -d ',' -f 1"`
	if [[ $IOPS_NUM -eq 0 ]];then
	    echo "host_ip:$1 DEV:$2 IOPS:$IOPS_NUM  ERROR" >> $log_file
	else
	    echo "host_ip:$1 DEV:$2 IOPS:$IOPS_NUM  SUCCESS" >> $log_file
	fi
}

function get_ips()
{
    ip_list=()
    if [[ $ip_range =~ "~" ]];then
        start_ip=`echo $ip_range | awk -F '~' '{print $1}'`
        end_ip=`echo $ip_range | awk -F '~' '{print $2}'`
        network=`echo $start_ip | awk -F '.' '{printf "%d.%d.%d.",$1,$2,$3}'`
        start_number=`echo $start_ip | awk -F '.' '{print $4}'`
        end_number=`echo $end_ip | awk -F '.' '{print $4}'`
        ip_list=($network$start_number)
        while [ $start_number -lt $end_number ]
        do
            start_number=`expr $start_number + 1`
            ip_list+=( $network$start_number )
        done
    fi
    if [[ -n $fix_ip ]];then
        ip_list+=( $fix_ip )
    fi
    if [[ ${#ip_list[@]} -eq 0 ]];then
        echo "Could not find ip address."
        exit 1
    fi
}

function make_system_device()
{
    $sshpass_prefix $1 \
    "root_part=\`blkid -tLABEL=img-rootfs -odevice\` && \
    devname=\`lsblk -o PKNAME \$root_part | tail -n 1\` && \
    partition_count=\`lsblk -Pbi -o TYPE /dev/\$devname | grep part | wc -l\` && \
    swap_partition_number=\`expr \$partition_count + 1\` && \
    sgdisk -n \$swap_partition_number:0:+128GiB -t \$swap_partition_number:8200 /dev/\$devname > /dev/null && \
    partprobe && \
    udevadm settle && \
    mkswap /dev/\$devname\$swap_partition_number 1>/dev/null 2>&1 && \
    swapon /dev/\$devname\$swap_partition_number && \
    dev_uuid=\`blkid -ovalue /dev/\$devname\$swap_partition_number | head -n 1\` && \
    echo UUID=\$dev_uuid swap swap defaults 0 0 >> /etc/fstab && \
    data_partition_number=\`expr \$swap_partition_number + 1\` && \
    sgdisk -n \$data_partition_number:0:0 -t \$data_partition_number:8300 /dev/\$devname > /dev/null && \
    partprobe && \
    udevadm settle && \
    mkfs.ext4 /dev/\$devname\$data_partition_number -F 1>/dev/null 2>&1 && \
    if [ ! -d /data ] ;then mkdir /data ; fi && \
    mount /dev/\$devname\$data_partition_number /data && \
    dev_uuid=\`blkid -ovalue /dev/\$devname\$data_partition_number | head -n 1\` && \
    echo UUID=\$dev_uuid /data ext4 defaults 0 0 >> /etc/fstab  && echo success || echo failed
    "
}

function make_system_device_all_node()
{
    for host_ip in ${ip_list[@]}
    do
    {
        result=`make_system_device $host_ip`
        if [[ "$result" == "success" ]];then
            echo "host_ip:$host_ip make system device SUCCESS" >> $log_file
        else
            echo "host_ip:$host_ip make system device FAILED" >> $log_file
        fi
    } &
    done
}


function make_data_device()
{
    $sshpass_prefix $1 \
    "if [ ! -d /data$2 ] ;then mkdir /data$2; fi && \
    sgdisk -Z /dev/$3 > /dev/null && \
    mkfs.ext4 /dev/$3 -F 1>/dev/null 2>&1 && \
    mount /dev/$3 /data$2 && \
    dev_uuid=\`blkid -ovalue /dev/$3 | head -n 1\` && \
    echo UUID=\$dev_uuid /data$2 ext4 defaults 0 0 >> /etc/fstab && \
    echo success || echo failed
    "
}


function make_data_device_all_node()
{
	for host_ip in ${ip_list[@]}
	do
	{
        nvme_devices=`$sshpass_prefix $host_ip  "cat /proc/partitions" | grep "nvme*[^p]*$" |gawk '{print $4}' 2>>$log_file`
        let num=1
        for dev in $nvme_devices
        do
        {
            result=`make_data_device $host_ip $num $dev`
            if [[ "$result" == "success" ]];then
                echo "host_ip:$host_ip make data device /dev/$dev SUCCESS"  >> $log_file
            else
                echo "host_ip:$host_ip make data device /dev/$dev FAILED"  >> $log_file
            fi
            num=`expr $num + 1`
         }
        done
	} &
	done
}


function final_operation()
{
    $sshpass_prefix $1 "systemctl stop cloud-init && \
        systemctl stop cloud-init-local && \
        yum remove cloud-init cloud-utils-growpart -y 1>/dev/null 2>&1 && \
        sh /bin/iptables.sh && \
        echo \"su - root -c '/bin/iptables.sh'\" >> /etc/rc.d/rc.local && \
        echo 'route add -net 10.0.0.0/8 gw 10.123.1.254' >> /etc/rc.d/rc.local && \
        route add -net 10.0.0.0/8 gw 10.123.1.254 && \
        echo 'any net 10.0.0.0 netmask 255.0.0.0 gw 10.123.1.254' >>/etc/sysconfig/static-routes && \
        sed  -i 's/GRUB_CMDLINE_LINUX=\"\"/GRUB_CMDLINE_LINUX=\"intel_idle.max_cstate=0 processor.max_cstate=1\"/g' /etc/sysconfig/grub && \
        sed  -i 's/GRUB_CMDLINE_LINUX=\"\"/GRUB_CMDLINE_LINUX=\"intel_idle.max_cstate=0 processor.max_cstate=1\"/g' /etc/default/grub && \
        chmod +x /etc/rc.d/rc.local && grub2-mkconfig -o /boot/grub2/grub.cfg > /dev/null && \
        echo success || echo failed"
}


function final_operation_all_node()
{
    for host_ip in ${ip_list[@]}
    do
    {
        result=`final_operation $host_ip`
        if [[ "$result" == "success" ]];then
            echo "host_ip:$host_ip final operation SUCCESS" >> $log_file
        else
            echo "host_ip:$host_ip final operation FAILED" >> $log_file
        fi
    } &
    done
}

function update_kernel()
{
    $sshpass_prefix $1 "yum install -y wget > /dev/null 2>&1 && \
        wget -O /opt/kernel-3.10.0-514.el7.x86_64.rpm https://buildlogs.centos.org/c7.1611.01/kernel/20161117160457/3.10.0-514.el7.x86_64/kernel-3.10.0-514.el7.x86_64.rpm > /dev/null 2>&1 && \
        yum install /opt/kernel-3.10.0-514.el7.x86_64.rpm -y > /dev/null 2>&1 && \
        grub2-mkconfig -o /boot/grub2/grub.cfg > /dev/null 2>&1 && \
        cp /boot/grub2/grub.cfg /boot/grub2/grub.cfg.bk && \
        sed -i '90,104d' /boot/grub2/grub.cfg && \
        init 6 && \
        echo success || echo failed"
}

function update_kernel_all_node()
{
    for host_ip in ${ip_list[@]}
    do
    {
        result=`update_kernel $host_ip`
        if [[ "$result" == "success" ]];then
            echo "host_ip:$host_ip update kernel SUCCESS" >> $log_file
        else
            echo "host_ip:$host_ip update kernel FAILED" >> $log_file
        fi
    } &
    done
}

function disk_test()
{
	host_number=`cat  $host_ips_file |wc -l`

	for((n=1;n<=$host_number;n++))
	do
		host_ip=`cat  $host_ips_file |sed -n "$n"p`
		nvme_devs=`$sshpass_prefix -f $host_ip  "cat /proc/partitions" | grep "nvme" |gawk '{print $4}'`
		for dev in $nvme_devs
		do
			iops_test $host_ip "/dev/$dev" &
			sleep 1
		done

		sd_devs=`$sshpass_prefix -f $host_ip  "cat /proc/partitions" | grep "sd.*[^1-9]$" |gawk '{print $4}'`
		for dev in $sd_devs
		do
			iops_test $host_ip "/dev/$dev" &
			sleep 1
		done

	done
}


function kill_iperf3()
{
	host_number=`cat $host_ips_file |wc -l`

	for((n=1;n<=$host_number;n++))
	do
		host_ip=`cat $host_ips_file |sed -n "$n"p`
		$sshpass_prefix -f $host_ip  "killall iperf3" &
	done
}


function iperf3_client()
{
	n=$1
	number=$2
	client_ip=`cat  $host_ips_file |sed -n "$n"p`
	service_ip=`cat  $host_ips_file |sed -n "$number"p`
	$sshpass_prefix -f $client_ip "iperf3 -c $service_ip -t 600 -R > /dev/null"
	sleep 1
	iperf3_num=`$sshpass_prefix -f $client_ip "ps -ef" | grep "iperf3 -c $service_ip -t 600 -R" |wc -l`
	if [[ $iperf3_num -ge 2 ]]; then
		echo "host_ip:$client_ip iperf3 -c $service_ip -t 600 -R  SUCCESS" >> $log_file
	else
		echo "host_ip:$client_ip iperf3 -c $service_ip -t 600 -R  ERROR" >> $log_file
	fi
}

function client_to_service_even()
{
	host_number=`cat  $host_ips_file |wc -l`
	ip_number=`expr $host_number / 2`
	for((n=1;n<=$host_number;n++))
	do
		host_ip=`cat  $host_ips_file  |sed -n "$n"p`
		$sshpass_prefix -f $host_ip  "iperf3 -s" &
		sleep 1
	done


	for((n=1;n<=$ip_number;n++))
	do
		let number=$n+$ip_number
		iperf3_client $n $number &
	done

	for((n=$ip_number+1;n<=$host_number;n++))
	do
		let number=$n-$ip_number
		iperf3_client $n $number &
	done
}

function client_to_service_odd()
{
    host_number=`cat  $host_ips_file |wc -l`
    ip_number=`expr $host_number / 2`
    for((n=1;n<=$host_number-1;n++))
    do
            host_ip=`cat  $host_ips_file  |sed -n "$n"p`
            $sshpass_prefix -f $host_ip  "iperf3 -s > /dev/null" &
			sleep 1
    done


    for((n=1;n<=$ip_number;n++))
    do
        let number=$n+$ip_number
        iperf3_client $n $number &
    done

    for((n=$ip_number+1;n<=$host_number-1;n++))
    do
        let number=$n-$ip_number
        iperf3_client $n $number &
    done
}

function client_to_service_odd_one()
{
    host_number=`cat  $host_ips_file |wc -l`

    host_ip_service=`cat  $host_ips_file  |sed -n "$ip_number"p`
    $sshpass_prefix -f $host_ip_service  "iperf3 -s > /dev/null"

    host_ip_client=`cat  $host_ips_file  |sed -n "1p"`
    $sshpass_prefix -f $host_ip_client  "iperf3 -s > /dev/null"

    $sshpass_prefix -f $host_ip_client "iperf3 -c $host_ip_service -t 600 -R > /dev/null"
	$sshpass_prefix -f $host_ip_service "iperf3 -c $host_ip_client -t 600 -R > /dev/null"
}

function nic_down()
{
	$sshpass_prefix -f $1  "ifdown $2"
	ret=`echo $?`
	if [[ ret -eq 0 ]];then
        echo "host_ip:$1 ifdown nicname:$2  SUCCESS" >> $log_file
    else
        echo "host_ip:$1 ifdown nicname:$2  ERROR" >> $log_file
    fi
}

function all_node_nic_down()
{
    host_number=`cat  $host_ips_file |wc -l`

    for((n=1;n<=$host_number;n++))
    do
            host_ip=`cat  $host_ips_file |sed -n "$n"p`
			nic_down $host_ip $nicname &
    done
}

function nic_up()
{
	$sshpass_prefix -f $1  "ifup $2"
	ret=`echo $?`
	if [[ ret -eq 0 ]];then
        echo "host_ip:$1 ifup nicname:$2  SUCCESS" >> $log_file
    else
        echo "host_ip:$1 ifup nicname:$2  ERROR" >> $log_file
    fi

}

function all_node_nic_up()
{
        host_number=`cat  $host_ips_file |wc -l`

        for((n=1;n<=$host_number;n++))
        do
                host_ip=`cat  $host_ips_file |sed -n "$n"p`
				nic_up $host_ip $nicname &
        done
}



if [[ ${cds_rpm_install} -eq 1 ]]; then
    install_rpm_all
fi

if [[ ${cdscrc} -eq 1 ]]; then
	get_host_ip
	dateinfo=`date`
	echo "crc start test $dateinfo"  >> $log_file

	kill_iperf3
	sleep 10
	host_number=`cat $host_ips_file  |wc -l`
	if test `expr $host_number % 2` == 0 ;then
		client_to_service_even
		sleep 600
		kill_iperf3
	else
		client_to_service_odd
		sleep 600
		kill_iperf3
		sleep 10
		client_to_service_odd_one
		sleep 600
		kill_iperf3
	fi
fi

if [[ ${cdsfio} -eq 1 ]]; then
	get_host_ip
	dateinfo=`date`
	echo "fio start test $dateinfo"  >> $log_file
	disk_test
fi


if [[ ${cdsnicdown} -eq 1 ]]; then
    get_host_ip
    dateinfo=`date`
    echo "nic down start test $dateinfo"  >> $log_file
    all_node_nic_down
fi


if [[ ${cdsnicup} -eq 1 ]]; then
    get_host_ip
    dateinfo=`date`
    echo "nic up  start test $dateinfo"  >> $log_file
    all_node_nic_up
fi


if [[ ${cds_system_device} -eq 1 ]]; then
    get_ips
    dateinfo=`date`
    echo "make swap and data partition in system device: $dateinfo"  >> $log_file
    make_system_device_all_node
    exit 0
fi


if [[ ${cds_data_device} -eq 1 ]]; then
    get_ips
    dateinfo=`date`
    echo "make data device: $dateinfo"  >> $log_file
    make_data_device_all_node
    exit 0
fi

if [[ ${cds_final_operation} -eq 1 ]]; then
    get_ips
    dateinfo=`date`
    echo "final operation: $dateinfo"  >> $log_file
    final_operation_all_node
    exit 0
fi

if [[ ${cds_kernel_update} -eq 1 ]]; then
    get_ips
    dateinfo=`date`
    echo "kernel update: $dateinfo"  >> $log_file
    update_kernel_all_node
    exit 0
fi