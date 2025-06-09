import socket
import argparse
import os
import time


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
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
    s.bind(("h1-eth0", 0))

    with open(args.output, "a") as f:
        f.write(f"Will send {len(packets)} packets")

        with open(accepted_file, "a") as accept:
            with open(rejected_file, "a") as reject:
                f.write("testing")
                for i, packet in enumerate(packets):
                        f.write(f"START: Iterating for packet {i}\nPacket: {packet}")
                        for n in range(args.repeat):
                            f.write(f"BEFORE: {time.time()}\n")
                            try:
                                s.send(bytes.fromhex(packet.strip()))
                                accept.write(packet)
                            except Exception as e:
                                t = time.time()
                                print(f"Exception: {e}")
                                f.write(f"Exception: {e}")
                                f.write(f"packet: {packet}")
                                f.write(f"hex: {bytes.fromhex(packet)}")
                                f.write(f"AFTER: {t}")
                                reject.write(packet)
                            f.write(f"AFTER: {time.time()}\n")
                            # Needed for some reason. Otherwise the simulation ends before the P4 program has received all packets 
                            time.sleep(50/1000)
                        f.write(f"END: Finished sending {args.repeat} packets\n")
    s.close()
if __name__ == "__main__": main()