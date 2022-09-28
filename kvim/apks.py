#!/usr/bin/env python
import sys
import os
import json
import urllib.request
import hashlib
import shutil

#usage apks.py preinstall_dir jsonfile

template = """include $(CLEAR_VARS)
LOCAL_MODULE := %s
LOCAL_MODULE_CLASS := APPS
LOCAL_MODULE_PATH := $(TARGET_OUT)%s
LOCAL_SRC_FILES := $(LOCAL_MODULE)$(COMMON_ANDROID_PACKAGE_SUFFIX)
LOCAL_CERTIFICATE := PRESIGNED
LOCAL_DEX_PREOPT := false
LOCAL_MODULE_TAGS := optional
LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)
include $(BUILD_PREBUILT)

"""

def parseJson(jsonfile):
    f = open(jsonfile)
    return json.load(f)["apks"]

def getChecksum(filename):
    checksum = None

    with open(filename, 'rb') as file_to_check:
        # read contents of the file
        data = file_to_check.read()
        # pipe contents of the file through
        checksum = hashlib.md5(data).hexdigest()
    return checksum

def download(url, filename, path, remote_checksum = None):
    fullpath = path + "/" + filename
    localfile, headers = urllib.request.urlretrieve(url)

    local_checksum = getChecksum(localfile)
    if (remote_checksum and local_checksum == remote_checksum) or not remote_checksum:
        os.remove(fullpath)
        shutil.move(localfile, fullpath)
    else:
        raise Exception("invalid checksum")

def main(argv):

    preinstall_dir = argv[1]
    apks = parseJson(argv[2])

    if os.path.exists(preinstall_dir):
        #Use to define modules for install
        makefile_path = preinstall_dir + '/Android.mk'
        #Use to include modules
        include_path = preinstall_dir + '/preinstall.mk'

        if os.path.exists(makefile_path):
            os.remove(makefile_path)
        if os.path.exists(include_path):
            os.remove(include_path)

        makefile = open(makefile_path, 'w')
        includefile = open(include_path, 'w')

        makefile.write("LOCAL_PATH := $(my-dir)\n\n")
        for apk in apks:
            filename = apk["file"]
            url = apk["url"]
            name = apk["name"]
            md5 = apk["md5"]
            path = apk["path"]

            download(url, filename, path, md5)

            makefile.write(template %(name, path))
            includefile.write('PRODUCT_PACKAGES += %s\n' % name)
        makefile.close()
        includefile.close()

if __name__=="__main__":
  main(sys.argv)
