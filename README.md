## How to start my peer

- To start/run my peer enter: (ip-address and port number of a known peer)
    
        python main.py  IP-ADDRESS  PORT-NUMBER

- My peer prints out what state the peer is in, whether its responding to a request, sending a request, gossiping, or doing consensus so that it is easy to keep track of what is going on.
- When the blockchain was at size 2173, it took my peer about 3mins and 12 seconds to synchronize, ie. get all the blocks and validate the chain.
- As the peer is adding blocks, it prits out which block its adding and when the peer is validating the chain, it prints out which block in the chain its currently validating.
- Once the chain is validated, a "THE BLOCKCHAIN IS VALID" message will be printed to the terminal.
