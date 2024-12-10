import random
import time
from Block import Block

class Blockchain:
  def __init__(self):
    self.chain = []
    self.nonce = 0


  def empty_and_resize_chain(self, new_size):
    self.chain = [None] * new_size
    
    
  def add_block(self, block):    
    self.chain[block.height] = block
    

  def get_block(self, height):
    block_height = int(height)
    
    if block_height >= 0 and block_height < len(self.chain):
      return self.chain[block_height]
    
    else:
      return None
    
    
  def get_height(self):
    return len(self.chain) 
  
  
  def get_empty_chain_entries(self):
    return [index for index, block in enumerate(self.chain) if block is None]
  
  
  def get_last_block(self):
    last_block = None
    
    if len(self.chain) >= 1:
      for block in self.chain:
        if block != None:
          last_block = block
          
    return last_block
  
  
  def get_chain_hash(self):
    last_block = self.get_last_block()
    chain_hash = None
    
    if last_block is not None:
      chain_hash = last_block.hash
    
    return chain_hash
  
  
  def is_valid_chain(self, chain_height, chain_hash):
    if len(self.chain) == chain_height:
      print("validating block 0...")
      
      if self.chain[0].is_valid(''):
        for i in range(1, len(self.chain)):
          print(f"validating block {i}...")
          prev_block_hash = self.chain[i-1].hash

          if not self.chain[i].is_valid(prev_block_hash):
            print("Chain validation was unsuccessfull.")
            return False
        
        if self.get_last_block().hash != chain_hash:
          print("Chain validation was unsuccessfull.")
          return False
          
      else: 
        return False
      
    return True
  

  def mine_a_block(self):
    difficulty = 8
    start_time = time.time()
    
    print("Mining a block...")
    last_block = self.get_last_block()
    try:
      if last_block != None:
        while (time.time() - start_time) <= 60:
          list_of_messages = ['test', 'hello world', 'blockchains', 'mining', 'comp 3010', 'peer 2 peer']
          messages = random.sample(list_of_messages, 3)
          new_block = Block("Chineze's Peer", messages, self.nonce, height = self.get_height())
          new_block.prev_hash = last_block.hash
          new_block.hash = new_block.compute_hash()
          if new_block.hash.endswith('0' * difficulty):
            print(f"Block successfully mined. Nonce: {new_block.nonce}, Hash: {new_block.hash}")
            self.add_block(new_block)
            return new_block
          
          self.nonce += 1
          
      print("Couldn't mine a block within a minuite. Will try again in 7 mins.")
      return None
    
    except Exception as e:
      print("The issue is here")
