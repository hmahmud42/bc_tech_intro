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
