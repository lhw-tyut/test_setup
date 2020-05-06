#!/bin/bash

function deploy_pxeagent()
{
    echo "====================================================================="
    echo "git clone pxeagent...."

    if [[ ! -d "/tftpboot/code" ]]; then
        mkdir /tftpboot/code
    fi
        cat > /tftpboot/code/boot_pxeagent.sh << EOF
custom_image=""
if [[ \$custom_image == "" ]]; then
    cp -rf /code/pxe_agent /usr/share/pxe_agent
else
    cp -rf /code/pxe_agent_custom /usr/share/pxe_agent
fi
AGENTDIR=/usr/share/pxe_agent
sh \$AGENTDIR/install.sh
EOF
        chmod 777 /tftpboot/code/boot_pxeagent.sh

    if [[ ! -d "/tftpboot/code/pxe_agent" ]]; then

        git clone -b develop https://repos.capitalonline.net/baremetal/pxe_agent.git /tftpboot/code/pxe_agent
    fi
}

function generate_pxeconfig() {

    echo "====================================================================="
    echo "generate pxe default config...."

    if [[ ! -d "/tftpboot/pxelinux/instances/default" ]]; then
        mkdir -p /tftpboot/pxelinux/instances/default
    fi

    if [[ -f /tftpboot/deploy_image_template/deploy_ramdisk ]]; then
        cp /tftpboot/deploy_image_template/deploy_ramdisk /tftpboot/pxelinux/instances/default
        cp /tftpboot/deploy_image_template/deploy_kernel /tftpboot/pxelinux/instances/default
    else
        echo 'the template of deploy images are not in the directory of /tftpboot/deploy_image_template'
    fi

    if [[ -f /etc/baremetal-api/baremetal-api.ini ]]; then
        dhcp_ip=`cat /etc/baremetal-api/baremetal-api.ini  | grep nfs_server_ip | awk '{print $3}'`
        callback=`cat /etc/baremetal-api/baremetal-api.ini  | grep scheduler | awk '{print $3}'`
        cat > /tftpboot/pxelinux/grub.cfg << EOF
set default="0"
set timeout=3
set hidden_timeout_quiet=false

menuentry "deploy" {
        linuxefi deploy_image_template/deploy_kernel rw selinux=0 scheduler-callback=$callback user-image-nfs-path=$dhcp_ip:/tftpboot/user_images
        initrdefi deploy_image_template/deploy_ramdisk
}
EOF
        cat > /tftpboot/pxelinux/pxelinux.cfg/default << EOF
default deploy

label deploy
    kernel instances/default/deploy_kernel
    append initrd=instances/default/deploy_ramdisk  rw selinux=0 scheduler-callback=$callback user-image-nfs-path=$dhcp_ip:/tftpboot/user_images
EOF
    else
        echo "bms_api config file is not place in the directory of /etc/baremetal-api"
    fi


}

function main()
{
    deploy_pxeagent
    generate_pxeconfig
}

main
