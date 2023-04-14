#!/usr/bin/env bash

NAME=BTProfileApplet

DST_NAME1=org.mate.panel.${NAME}.mate-panel-applet
DST_DIR1=/usr/share/mate-panel/applets

DST_NAME2=org.mate.panel.applet.${NAME}Factory.service
DST_DIR2=/usr/share/dbus-1/services

DST_NAME3=${NAME}.py
DST_DIR3=/usr/share/mate-applets/btprofile-applet

TARGET1="${DST_DIR1:?}/${DST_NAME1:?}"
TARGET2="${DST_DIR2:?}/${DST_NAME2:?}"
TARGET3="${DST_DIR3:?}/${DST_NAME3:?}"

rm -f "${TARGET1:?}"
rm -f "${TARGET2:?}"
rm -f "${TARGET3:?}"

rm -rf "${DST_DIR3:?}"
