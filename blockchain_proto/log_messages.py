
"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Some wrappers around a logging objects that uses a global node-id 
to log messages.
"""
from blockchain_proto.consts import node_id_global


def log_debug(log_obj, msg):
    log_obj.debug(f"[{node_id_global['value']}] " + msg)


def log_info(log_obj, msg):
    log_obj.info(f"[{node_id_global['value']}] " + msg)


def log_warning(log_obj, msg):
    log_obj.warn(f"[{node_id_global['value']}] " + msg)


def log_error(log_obj, msg):
    log_obj.error(f"[{node_id_global['value']}] " + msg)


def log_critical(log_obj, msg):
    log_obj.critical(f"[{node_id_global['value']}] " + msg)
