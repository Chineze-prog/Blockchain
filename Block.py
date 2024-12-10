import time
import hashlib

DIFFICULTY = 8

class Block:
  def __init__(self, miner = '', messages = [], nonce = '', block_hash = '', height = 0, timestamp = int(time.time())):
    self.miner = str(miner)
    self.prev_hash = '' 
    self.height = int(height)
    self.nonce = str(nonce) 
    self.hash = str(block_hash) 
    self.timestamp = int(timestamp)
    
    if isinstance(messages, list):
      self.messages = messages
    else:
      if isinstance(messages, str) and messages.startswith("[") and messages.endswith("]"):
        self.messages = [str(item) for item in messages[1:-1].split(",")]
      else:
        self.messages = str(messages)

    
  def compute_hash(self):
    comp_hash = ''
    hash_base = hashlib.sha256()
    
    if self.prev_hash:
      hash_base.update(self.prev_hash.encode())
      
    hash_base.update(self.miner.encode())
    
    for msg in self.messages:
      hash_base.update(msg.encode())
      
    hash_base.update(self.timestamp.to_bytes(8, 'big'))
    hash_base.update(self.nonce.encode())
    
    comp_hash = hash_base.hexdigest()
    
    if comp_hash[-1 * DIFFICULTY:] < '0' * DIFFICULTY:
      print(f"Block was not difficult enough: {comp_hash}")
      
    return comp_hash
  
  
  def is_valid(self, prevHash):
    self.prev_hash = str(prevHash)
    calculated_hash = self.compute_hash()
    return self.hash == calculated_hash
