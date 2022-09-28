#!/system/bin/sh

MARK=/data/local/docker_images_installed
DOCKER_IMAGES=/system/docker_images

busybox run-parts /system/etc/init.d/
if [ ! -e $MARK ]; then
echo "booting the first time, so pre-install some APKs."

busybox find $DOCKER_IMAGES -name "*\.tar" -exec /system/bin/docker load < {} \;

# if we need to remove those tars:
# busybox rm -rf $PKGS

touch $MARK
echo "OK, docker images loading complete."
fi
