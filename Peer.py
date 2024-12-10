import time

class Peer:
  def __init__(self, name = '', host = '', port = 0, id = None):
    self.name = name
    self.host = host
    self.port = port
    self.id = id
    self.last_seen = time.time()
        
  def update_last_seen(self):
    self.last_seen = time.time()
  
  def is_inactive(self):
    return (time.time() - self.last_seen) >  60
  