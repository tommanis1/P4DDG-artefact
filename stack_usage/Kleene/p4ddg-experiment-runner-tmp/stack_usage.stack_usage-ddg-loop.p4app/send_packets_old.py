# Send a bunch of packets using scapy and log the timestamps
# Input:
#  packets.txt
#  output file
import argparse
import os
from scapy.all import *
import time
# NUMBER_OF_TIMES_TO_SEND_EACH_PACKET = 20

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--packets", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--repeat", type=int, required=True)
    args = parser.parse_args()
    p = None
    print("reading packets")
    with open(args.packets, "r") as f: 
        packets = f.readlines()[1:]
        p = packets 
    if (not packets): print(f"failed to read packets from {args.packets}")
    
    accepted_file = f"{args.packets}_ACCEPTED"
    rejected_file = f"{args.packets}_REJECTED"
    
    # Clear the files if they exist
    if os.path.exists(accepted_file):
        os.remove(accepted_file)
    if os.path.exists(rejected_file):
        os.remove(rejected_file)
        
    with open(args.output, "a") as f:
        with open(accepted_file, "a") as accept:
            with open(rejected_file, "a") as reject:
                f.write("testing")
                for i, packet in enumerate(packets):
                        f.write(f"START: Iterating for packet {i}\nPacket: {packet}")
                        for n in range(args.repeat):
                            f.write(f"BEFORE: {time.time()}\n")
                            try:
                                sendp(packet)
                                accept.write(packet)
                            except Exception as e:
                                t = time.time()
                                print(f"Exception: {e}")
                                f.write(f"Exception: {e}")
                                f.write(f"AFTER: {t}")
                                reject.write(packet)
                            f.write(f"AFTER: {time.time()}\n")
                        f.write(f"END: Finished sending {args.repeat} packets\n")

if __name__ == "__main__": main()