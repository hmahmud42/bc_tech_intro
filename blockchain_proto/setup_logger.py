"""
Copyright 2022 M. M. Hassan Mahmud

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.


Setup the parameters for the logger.
"""
import coloredlogs 

field_style = {
      'asctime': {'color': 206},
     'hostname': {'color': 'magenta'},
     'levelname': {'color': 'blue', 'bold': True},
     'name': {'color': 'blue'},
     'programname': {'color': 'cyan'},
     'username': {'color': 'yellow'}
     }


coloredlogs.install(
    level='DEBUG',
    fmt='%(asctime)s %(levelname)s: %(message)s',
    field_styles=field_style)



