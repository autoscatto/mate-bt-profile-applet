#!/usr/bin/python3

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

# --------------------------------------------------------
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GLib", "2.0")
gi.require_version("Gio", "2.0")
gi.require_version('MatePanelApplet', '4.0')
from gi.repository import Gtk, GLib, Gio
from gi.repository import MatePanelApplet
import os
import sys
import logging
import subprocess

BUS_NAME = "org.bluez"
INTERFACE_NAME = f"{BUS_NAME}.MediaTransport1"
DEVICE = f'{BUS_NAME}.Device1'
ADAPTER_PATH = "/org/bluez/hci0"
A2DP_PROFILE = "a2dp_sink"
HSP_PROFILE = "headset_head_unit"
OBJECT_PATH = "/"
STATE_ACTIVE = 'active'
STATE_IDLE = 'idle'
STATE_LABEL = {
    STATE_ACTIVE: 'A2DP',
    STATE_IDLE: 'HSP'
}


current_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_path)


def exception_handler(exc_type, value, traceback):
    logging.exception(f"Uncaught exception occurred: {value}")
    logging.debug(f"{value}")
    sys.__excepthook__(exc_type, value, traceback)  # calls default excepthook


logger = logging.getLogger("BTProfileAppletLog")
logger.setLevel(logging.ERROR)

sys.excepthook = exception_handler

file_handler = logging.FileHandler(os.path.expanduser("/tmp/BTProfileApplet.log"))
file_handler.setFormatter(
    logging.Formatter('[%(levelname)s] %(asctime)s: %(message)s', "%Y-%m-%d %H:%M:%S")
)
logger.addHandler(file_handler)


class BTApplet:
    def __init__(self, applet, data, bus, objs, addr):
        self.version = "0.2.0"
        self.applet = applet
        self.data = data
        self.settings_path = applet.get_preferences_path()
        logger.debug(f"Settings path: {self.settings_path}, v: {self.version}")
        self.dbus = bus
        self.addr = addr
        self.objs = objs
        under_mac = '_'.join(addr.split('_')[-6:])
        self.card = f"bluez_card.{under_mac}"
        self.sink = f"bluez_sink.{under_mac}"
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.switch = Gtk.Switch()
        if self.addr:
            state = STATE_IDLE
            for path in self.objs:
                transport = self.objs[path].get(INTERFACE_NAME, {})
                if transport.get('Device') == self.addr:
                    state = transport.get('State', STATE_IDLE)
            self.label = Gtk.Label(label="No connected devices")
            self.set_switch_by_state(state)
        else:
            self.label = Gtk.Label(label="No connected devices")
        self.vbox.pack_start(self.label, True, True, 0)
        self.vbox.pack_start(self.switch, True, True, 0)
        self.switch.connect("notify::active", self.on_switch_active_notify)
        self.applet.add(self.vbox)
        self.applet.show_all()

    def on_switch_active_notify(self, switch, active_property, *args):
        state = STATE_ACTIVE if switch.get_active() else STATE_IDLE
        self.set_device_profile(state)

    def set_switch_by_state(self, state):
        self.switch.set_sensitive(True)
        is_active = state == STATE_ACTIVE
        self.label.set_markup(f"<small>{STATE_LABEL.get(state, STATE_IDLE)}</small>")
        self.switch.set_active(is_active)

    def set_device_profile(self, state):
        profile = HSP_PROFILE
        if state == STATE_ACTIVE:
            profile = A2DP_PROFILE
        elif state == STATE_IDLE:
            profile = HSP_PROFILE
        subprocess.check_output(["pactl", "set-card-profile", self.card, profile])
        subprocess.check_output(["pacmd", "set-default-sink", f"{self.sink}.{profile}"])
        self.label.set_markup(f"<small>{STATE_LABEL.get(state, STATE_IDLE)}</small>")

    def on_properties_changed(self, *args, **kwargs):
        (
            dbus_connection,
            sender,
            object_path,
            interface,
            signal,
            (changed_properties_interface, changed_properties, invalidated_properties),
        ) = args
        self.set_switch_by_state(changed_properties["State"])

    def on_device_removed(self, *args, **kwargs):
        (
            dbus_connection,
            sender,
            object_path,
            interface,
            signal,
            (changed_properties_interface, changed_properties),
        ) = args
        try:
            addr = "/".join(changed_properties_interface.split("/")[:-1])
            if addr == self.addr:
                logger.debug("Device disconnected!")
                self.switch.set_sensitive(False)
        except Exception:
            logger.error("Error!")

def applet_factory(applet, iid, data):
    if iid != "BTProfileApplet":
        return False
    logger.debug("Factory init")
    dbus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
    proxy = Gio.DBusProxy.new_sync(dbus,
                                   Gio.DBusProxyFlags.NONE,
                                   None,
                                   BUS_NAME, OBJECT_PATH,
                                   "org.freedesktop.DBus.ObjectManager",
                                   None)
    managed_objects = proxy.GetManagedObjects()
    device_path = None
    for path, interfaces in managed_objects.items():
        if con_state := interfaces.get(DEVICE, {}).get("Connected", False):
            device_path = path
            logger.debug(f"Found connected device: {device_path}")
    win = BTApplet(applet, data, dbus, managed_objects, device_path)
    signal_id = dbus.signal_subscribe(
        BUS_NAME,
        "org.freedesktop.DBus.Properties",
        "PropertiesChanged",
        None,
        None,
        Gio.DBusSignalFlags.NONE,
        win.on_properties_changed
    )
    dbus.signal_subscribe(
        BUS_NAME,
        'org.freedesktop.DBus.ObjectManager',
        'InterfacesRemoved',
        None,
        None,
        Gio.DBusSignalFlags.NONE,
        win.on_device_removed
    )
    logger.debug("applet constructed")
    return True


MatePanelApplet.Applet.factory_main("BTProfileAppletFactory", True,
                                    MatePanelApplet.Applet.__gtype__,
                                    applet_factory, None)
