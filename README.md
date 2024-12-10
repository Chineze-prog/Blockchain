## How to start my peer

- To start/run my peer enter: (ip-address and port number of a known peer)
    
        python main.py  IP-ADDRESS  PORT-NUMBER

- My peer prints out what state the peer is in, whether its responding to a request, sending a request, gossiping, or doing consensus so that it is easy to keep track of what is going on.
- When the blockchain was at size 2173, it took my peer about 3mins and 12 seconds to synchronize, ie. get all the blocks and validate the chain.
- As the peer is adding blocks, it prits out which block its adding and when the peer is validating the chain, it prints out which block in the chain its currently validating.
- Once the chain is validated, a "THE BLOCKCHAIN IS VALID" message will be printed to the terminal.

## Location of my consensus code

- My consensus code starts at line 284 of the main.py file
- The part that chooses which chain to synchronize to starts at line 299 of the main.py file
- At the beginning of the consensus, my peer sends out STATS requests and waits 10 seconds. During the 10 seconds my peer accepts STATS REPLIES and groups the peers based on hash and height. Then, after the 10 seconds, it finds which group has the most members and choosed that chain the synchronize with. My peer then ask for blocks from random members in the group every 10 seconds for blocks that are missing from the my chain. When the chain is full, the chain is validated and if the chain is not valid, it's discarded and waits for the next consensus time.

## How I clean up peers

- I clean up my peers by keeping track of how long it has been since i last got a gossip or gossip reply from them (can be found at line 11 of the Peer.py file). And when i get a gossip or gossip reply from them i update the last time i saw them (can be seen at line 167 and 208 of main.py file) and also check for any other peer that has exceeded their limit (can be seen at line 14 of Peer.py file).