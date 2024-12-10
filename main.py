import sys
import uuid
import json
import random
import socket
import traceback
from Peer import Peer
from Block import Block
from Blockchain import Blockchain
from Events import Event, EventHandler


GOSSIP_INTERVAL = 30 # every 30 seconds
CONSENSUS_INTERVAL = 600 # every 10 mins

known_peers = []
         
class Main_Peer:  
  def __init__(self, server_host, server_port):
    global known_peers
    
    try:      
      self.peer_port = 8576
      self.stats_responses = {}
      self.peer_name = "Chineze's Peer"
      self.blockchain = Blockchain()
      self.is_current_chain_valid = False
      
      new_peer = Peer(host = server_host, port = server_port)
      known_peers.append(new_peer)
      print(f"Added a new peer: {new_peer.host}, {new_peer.port}")
        
      print("Creating UDP socket and connecting to network...")
      self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.peer_socket.bind(('', self.peer_port))
      self.peer_socket.settimeout(10)
      
      self.peer_ipaddr = socket.gethostbyname(socket.gethostname())
      print(f"hosting on host name: {self.peer_ipaddr} and port number:{self.peer_port}")
      
      try:    
        self.gossip()
        
        self.event_handler = EventHandler(self)
        
        # creating and adding the Gossip Event
        gossip_event = Event(lambda : self.gossip(), GOSSIP_INTERVAL)
        self.event_handler.add_event(gossip_event)
        
        # creating and adding the first consensus Event that only happens once
        first_consensus_event = Event(lambda : self.perform_consensus(), 10)
        self.event_handler.add_event(first_consensus_event, repeat_once = True)

        # creating and adding the Consensus Event
        consensus_event = Event(lambda : self.perform_consensus(), CONSENSUS_INTERVAL)
        self.event_handler.add_event(consensus_event)
        
        minning_event = Event(lambda : self.mine_block(), 420)
        self.event_handler.add_event(minning_event)
      
        self.event_handler.start_running(self.peer_socket)

        try:
          if self.peer_socket is not None:
            self.peer_socket.close()
        except:
          print("Failed to close the socket!")
          self.traceback_message() 
          sys.exit(1)   
          
      except Exception as e:
        print(f"something happened: {e}") 
        self.traceback_message()  
        sys.exit(1)          
        
    except Exception as e:
      print(f"Something Really Bad Happened: {e}")  
      self.traceback_message()
      sys.exit(1)


  def traceback_message(self):
    print("-"*60)
    traceback.print_exc(file = sys.stdout)
    print("-"*60)
   
    
  def send_message(self, message, peer_addr):
    try:
      msg = json.dumps(message)
      self.peer_socket.sendto(msg.encode(), peer_addr)
      
    except Exception as e:
      print(f"Error occurred when sending message to peer: {peer_addr} => {e}")  


  def handle_message_recieved(self, message, sender_peer):
    msg_type = message.get("type")
      
    if msg_type == "GOSSIP":
      self.respond_to_gossip(message)
    
    elif msg_type == "GOSSIP_REPLY":
      self.handle_gossip_reply(message)
      
    elif msg_type == "GET_BLOCK":
      self.respond_to_block_request(message, sender_peer)
      
    elif msg_type == "GET_BLOCK_REPLY":
      self.handle_block_reply(message)
    
    elif msg_type == "STATS":
      self.respond_to_stats_request(sender_peer)
      
    elif msg_type == "STATS_REPLY":
      self.handle_stats_reply(message, sender_peer)
      
    elif msg_type == "CONSENSUS":
      self.do_consensus()
      
    elif msg_type == "ANNOUNCE":
      self.recieve_announcement(message)
      
      
  def gossip(self):
    global known_peers
    
    try:
      if not known_peers:
        print("No peers to gossip with.")
        return
      
      GOSSIP = {
        "type" : "GOSSIP",
        "host" : self.peer_ipaddr,
        "port" : self.peer_port,
        "id" : str(uuid.uuid4()),
        "name" : self.peer_name
      }
      
      for peer in known_peers:
        self.send_message(GOSSIP, (peer.host, peer.port))  
      
      print("Just Gossiped.")
      
    except Exception as e:
      print(f"Error occurred while sending gossip message: {e}")


  #if they gossip to me, send gossip reply and forward to 3 other pairs
  def respond_to_gossip(self, gossip_message): 
    global known_peers
    
    required = ['host', 'port', 'id', 'name']
    try:
      if all (field in gossip_message for field in required):
        if gossip_message['host'] != None and gossip_message['port'] != None and gossip_message['host'] != self.peer_ipaddr and gossip_message['port'] != self.peer_port and gossip_message['name'] != self.peer_name:

          GOSSIP_REPLY = {
            "type" : "GOSSIP_REPLY",
            "host" : self.peer_ipaddr,
            "port" : self.peer_port,
            "name" : self.peer_name
          }
            
          self.send_message(GOSSIP_REPLY, (gossip_message['host'], gossip_message['port']))

          found = False 
            
          for peer in known_peers:
            if peer.host == gossip_message['host'] and peer.port == gossip_message['port']:
              peer.update_last_seen()
              
              if peer.id == None:
                known_peers.remove(peer)
                print("replaced gossip-reply peer with gossip peer.")
              
              elif peer.id == gossip_message['id']:
                found = True
                
              elif peer.is_inactive():
                known_peers.remove(peer)
                print("Removed an inactive peer.")
                    
          if not found:
            selected_peers = random.sample(known_peers, min(3, len(known_peers)))
            
            for peer in selected_peers:
              self.send_message(gossip_message, (peer.host, peer.port))
                    
            new_peer = Peer(gossip_message['name'], gossip_message['host'], gossip_message['port'], gossip_message['id'] )
            known_peers.append(new_peer)
            print(f"Added a new peer: {gossip_message['host']}, {gossip_message['port']}")
            
    except Exception as e:
      print(f"Error occurred while handling gossip message recieved: {e}")      
  
  
  # handles the gossip-replies recieved  
  def handle_gossip_reply(self, gossip_message):
    global known_peers
    
    required = ['host', 'port', 'name']
    
    try:
      if all (field in gossip_message for field in required):
        if gossip_message['host'] != None and gossip_message['port'] != None:
          
          found = False
          
          for peer in known_peers:
            if peer.host == gossip_message['host'] and peer.port == gossip_message['port']:
              found = True
              peer.update_last_seen()
              
            elif peer.is_inactive():
              known_peers.remove(peer)
              print("Removed an inactive peer.")
          
          if not found: 
            new_peer = Peer(gossip_message['name'], gossip_message['host'], gossip_message['port'])
            known_peers.append(new_peer)
            print(f"Added a new peer: {gossip_message['host']}, {gossip_message['port']}")
            
    except Exception as e:
      print(f"Error occurred while handling gossip reply message recieved: {e}")          
       
       
  def get_stats(self):
    global known_peers
    
    try:
      print("Getting peers stats...")

      GET_STATS = {
        "type":"STATS"
      }
      
      for peer in known_peers:
        self.send_message(GET_STATS, (peer.host, peer.port))   
      
    except Exception as e:
      print(f"Error occurred while getting peers stats: {e}")  
      

  def respond_to_stats_request(self, sender_peer):
    global known_peers
    
    try:
      print("Responding to stats request...")
      
      STATS_REPLY = {
        "type": "STATS_REPLY",
        "height": self.blockchain.get_height(),
        "hash": self.blockchain.get_last_block().hash if self.blockchain.get_last_block() else None
      }
      
      self.send_message(STATS_REPLY, sender_peer)
      
    except Exception as e:
      print(f"Error occurred while handling stats request message: {e}")
      
    
  def handle_stats_reply(self, stats_message, sender_peer):
    global known_peers
    
    required = ['height', 'hash']
    
    try:
      print(f"Handling stats reply...")
      
      if all (field in stats_message for field in required):
        height = stats_message['height']
        chain_hash = stats_message['hash']
        
        if height != None and chain_hash != None:
          if (height, chain_hash) not in self.stats_responses:
            self.stats_responses[(height, chain_hash)] = []
          
          if sender_peer not in self.stats_responses[(height, chain_hash)]:
            self.stats_responses[(height, chain_hash)].append(sender_peer)
        
    except Exception as e:
      print(f"Error occurred while handling stats reply message: {e}")
      
      
  def perform_consensus(self):
    self.is_current_chain_valid = False
    self.get_stats()
    
    # creating and adding the do-consensus event that occurs once
    do_consensus_event = Event(lambda : self.do_consensus(), 10)
    self.event_handler.add_event(do_consensus_event, True)


  def do_consensus(self):
    try:
      if not self.stats_responses:
        print("Didn't get any stats replies, so a consensus can't be done.")
        return
      
      agreed_chain = max(self.stats_responses.items(), key = lambda x: len(x[1]))
      chain_height, chain_hash = agreed_chain[0]
      agreeing_peers = agreed_chain[1]
      
      current_chain_height = self.blockchain.get_height() 
      current_chain_hash = self.blockchain.get_chain_hash() 
      
      if current_chain_height == chain_height and current_chain_hash == chain_hash:
        self.is_current_chain_valid = True
        print("Blockchain is already up-to-date.")
        return
      
      self.blockchain.empty_and_resize_chain(chain_height)
      
      self.get_block(agreeing_peers)
            
      # creating and adding the get missed block event 
      missed_blocks_event = Event(lambda : self.get_block(agreeing_peers), 10)
      self.event_handler.add_event(missed_blocks_event)
      
      # creating and adding the validating of the chain event
      validate_chain_event = Event(lambda : self.validate_chain(chain_height, chain_hash, validate_chain_event, missed_blocks_event), 20)
      self.event_handler.add_event(validate_chain_event)
      
    except Exception as e:
      print(f"Error occurred while doing consensus: {e}")


  def validate_chain(self, chain_height, chain_hash, validate_event, missing_blocks_event):
    try:
      if not self.blockchain.get_empty_chain_entries():
        print("Blockchain is full...")
        print("Validating full chain...")
        self.event_handler.remove_event(missing_blocks_event, False)
        self.event_handler.remove_event(validate_event, False)
        
        self.is_current_chain_valid = self.blockchain.is_valid_chain(chain_height, chain_hash)
        
        if self.is_current_chain_valid:
          print("THE BLOCKCHAIN IS VALID.")
        else:
          self.blockchain.empty_and_resize_chain(chain_height)
          
    except Exception as e:
      print(f"Error occurred while validating the blockchain: {e}")
      
             
  def get_block(self, peers_list):
    try:
      empty_entries = self.blockchain.get_empty_chain_entries()
      
      if not empty_entries and not peers_list:
        return
      
      for height in empty_entries:
        peer = random.choice(peers_list)
        
        GET_BLOCK = {
          "type": "GET_BLOCK",
          "height": height
        }
        
        self.send_message(GET_BLOCK, peer)
        
    except Exception as e:
      print(f"Error occurred while getting a block: {e}")    
         
         
  def force_consensus(self):
    try:
      print("Forcing a consensus...")
      
      CONSENSUS = {
        "type": "CONSENSUS"
      }
      
      for peer in known_peers:
        self.send_message(CONSENSUS, (peer.host, peer.port))
        
    except Exception as e:
      print(f"Error occurred while forcing a consensus: {e}")
      
      
  def respond_to_block_request(self, block_message, sender_peer):
    try:
      GET_BLOCK_REPLY = {
        "type" : "GET_BLOCK_REPLY",
        "hash": None, 
        "height": None,
        "messages": None,
        "minedBy": None,
        "nonce": None,
        "timestamp" : None,
      }
      
      required = ['height']
      
      if all (field in block_message for field in required):
        
        height = block_message['height']
        
        if height != None: 
          requested_block = self.blockchain.get_block(height)
          
          if requested_block:
            print("Responding to a block request...")

            GET_BLOCK_REPLY = {
              "type" : "GET_BLOCK_REPLY",
              "hash": requested_block.hash, 
              "height": requested_block.height,
              "messages": requested_block.messages,
              "minedBy": requested_block.miner,
              "nonce": requested_block.nonce,
              "timestamp" : requested_block.timestamp,
            }
            
      self.send_message(GET_BLOCK_REPLY, sender_peer)
      
    except Exception as e:
      print(f"Error occurred while responding to a block request: {e}")    
  
  
  def handle_block_reply(self, block_message):
    required = ['minedBy', 'messages', 'nonce', 'hash', 'height', 'timestamp']
    
    try:
      if all (field in block_message for field in required):
        miner = block_message['minedBy'] 
        messages = block_message['messages'] 
        nonce = block_message['nonce'] 
        block_hash = block_message['hash']
        height = block_message['height']
        timestamp = block_message['timestamp']
        
        if miner is not None and messages is not None and nonce is not None and block_hash is not None and height is not None and timestamp is not None:
          new_block = Block(miner, messages, nonce, block_hash, height, timestamp)
          self.blockchain.add_block(new_block)
          print(f"Adding block {height}...")
          
    except Exception as e:
      print(f"Error occurred while handling a block reply: {e}")  
    
    
  def recieve_announcement(self, announcement):
    try:
      required = ['minedBy', 'messages', 'nonce', 'hash', 'height', 'timestamp']
      
      if all (field in announcement for field in required):
        height = announcement['height']
        miner = announcement['minedBy']
        nonce = announcement['nonce']
        messages = announcement['messages']
        block_hash = announcement['hash']
        timestamp = announcement['timestamp']
        
        if miner is not None and messages is not None and nonce is not None and block_hash is not None and height is not None and timestamp is not None:
          print("Handling an announcement")
          
          if self.is_current_chain_valid:
            prev_hash = self.blockchain.get_chain_hash()
            new_block = Block(miner, messages, nonce, block_hash, height, timestamp)
            
            if new_block.is_valid(prev_hash):
              self.blockchain.chain.append(new_block)
              print("ADDED THE NEW BLOCK")
            else:
              print("New Block was not valid.")
          else:
            print("Current chain is no longer valid, so announcement cannot be handled.")
            
    except Exception as e:
      print(f"Error occurred while handling announcement message: {e}")
                
                
  def mine_block(self):
    global known_peers
    
    try:
      if self.is_current_chain_valid:
        mined_block = self.blockchain.mine_a_block()
        if mined_block != None:
          ANNOUNCEMENT = {
            "type" : "ANNOUNCE",
            "hash": mined_block.hash, 
            "height": mined_block.height,
            "messages": mined_block.messages,
            "minedBy": mined_block.miner,
            "nonce": mined_block.nonce,
            "timestamp" : mined_block.timestamp,
          }
          
          for peer in known_peers:
            self.send_message(ANNOUNCEMENT, (peer.host, peer.port))
            
    except Exception as e:
      print(f"Error occurred while sending announcement message: {e}")  
                 
if __name__ == "__main__":
  try:
    if len(sys.argv) != 3:
      raise Exception("Usage: python main.py <HOST_NAME> <PORT_NUMBER>")
                  
    peer_host = sys.argv[1]
          
    try:
      peer_port = int(sys.argv[2]) 
    except:
      raise Exception("Bad port number") 
    
    Main_Peer(peer_host, peer_port)
      
  except Exception as e:
    print(e)
    sys.exit(1)
    