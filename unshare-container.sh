#!/bin/bash

ROTFS=$PWD/container
INIT=init.sh

gcc tjener.c -o /home/lloyd/da-nan3000/eksempler/container/bin/tjener -static


if [ ! -d $ROTFS ];then

    mkdir -p $ROTFS/{bin,proc,var}
    mkdir $ROTFS/var/www
    mkdir $ROTFS/var/log

    touch $ROTFS/var/log/debug.log

    cd       $ROTFS/bin/
    cp       /bin/busybox .
    cp       /bin/dumb-init .
    for P in $(./busybox --list); do ln busybox $P; done;

    cat <<EOF  > $INIT
#!bin/sh
mount -t proc none /proc
exec /bin/sh
EOF

    chmod +x init.sh
fi

cd $ROTFS
sudo PATH=/bin unshare --fork --pid /usr/sbin/chroot . bin/dumb-init bin/init.sh
