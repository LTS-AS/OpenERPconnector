import json
from os import environ, name

class Connection:
  def __init__(self):
    if name == 'nt':
      config_path = environ['HOMEDRIVE']+environ['HOMEPATH']+"/config/api-server.json"
    else:
      config_path = environ['HOMEPATH']+"/config/api-server.json"

    with open(config_path, "r") as f:
      file_buffer = f.read()
      f.close()

    self.params = json.loads(file_buffer)

#Test-code for module
if __name__ == '__main__':
  con = Connection()
  print(Connection().params)