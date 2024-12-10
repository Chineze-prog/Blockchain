import json
import time
import socket


class Event:
  def __init__(self, task, interval):
    self.task = task
    self.interval = interval
    self.replay_time = time.time() + interval
        
  def do_task(self):
    self.task()
    self.replay_time += self.interval


class EventHandler:
  def __init__(self, main_peer):
    self.events = []
    self.main_peer = main_peer
    
    
  def add_event(self, event, repeat_once = False):
    self.events.append((event, repeat_once))


  def remove_event(self, event, repeat_once):
    for an_event, repeat_once in self.events:
      if an_event == event:
        self.events.remove((event, repeat_once))
        print("An Event was Removed.")
        break
      
    
  def start_running(self, server_socket):
    try:
      while True:
        current_time = time.time()
        
        for event, repeat_once in self.events:
          if current_time >= event.replay_time:
            event.do_task()
          
            if repeat_once == True:
              self.remove_event(event, repeat_once)
               
        try:
          command_bytes, from_peer = server_socket.recvfrom(1024)

          if command_bytes and from_peer: 
            message = json.loads(command_bytes.decode())
            self.main_peer.handle_message_recieved(message, from_peer)
        
        except socket.timeout:
          pass
        except json.JSONDecodeError:
          print(f"Bad JSON Message: {command_bytes}")
        except Exception as e:
          print(f"An error has occurred when recieving a message: {e}")
        
        time.sleep(0.01) # sleep a little
              
    except Exception as e:
      print(f"An error occurred: {e}")
      