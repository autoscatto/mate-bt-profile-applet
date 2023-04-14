#!/usr/bin/env bash

NAME=BTProfileApplet
SRC_FOLDER=$(dirname "$BASH_SOURCE")

SRC_NAME1=org.mate.panel.${NAME}.mate-panel-applet
DST_NAME1=org.mate.panel.${NAME}.mate-panel-applet
DST_DIR1=/usr/share/mate-panel/applets

SRC_NAME2=org.mate.panel.applet.${NAME}Factory.service
DST_NAME2=org.mate.panel.applet.${NAME}Factory.service
DST_DIR2=/usr/share/dbus-1/services

SRC_NAME3=${NAME}.py
DST_NAME3=${NAME}.py
DST_DIR3=/usr/share/mate-applets/btprofile-applet

TARGET1="${DST_DIR1:?}/${DST_NAME1:?}"
TARGET2="${DST_DIR2:?}/${DST_NAME2:?}"
TARGET3="${DST_DIR3:?}/${DST_NAME3:?}"

rm -rf "${TARGET1:?}"
rm -rf "${TARGET2:?}"
rm -rf "${TARGET3:?}"

mkdir -p "${DST_DIR3:?}"

cp "${SRC_FOLDER}/${SRC_NAME1}" "${TARGET1:?}"
cp "${SRC_FOLDER}/services/${SRC_NAME2}" "${TARGET2?}"
cp "${SRC_FOLDER}/${SRC_NAME3}" "${TARGET3:?}"
