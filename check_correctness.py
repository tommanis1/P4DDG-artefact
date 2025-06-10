# Check behavioral equivalence by comparing ONLY the parsed headers, nothing else 
import subprocess
import re
import os
REPEAT_EACH_PACKET_N_TIMES = 1
MAX_PACKETS_P4PKTGEN = 75
PROGRAMS_DIR = "programs/programs_with_equivalent_ddgs"
manual_pairs = [
    # The first element is the file that is used for packet generation
    ("programs/running_example/basic_tunnel.p4", "programs/running_example/basic_tunnel.p4", "programs/running_example/basic_tunnel-ddg.p4")
    ]

equiv_pairs = []

for root, _, files in os.walk(PROGRAMS_DIR):
    # First collect all original .p4 files
    original_files = [f for f in files if f.endswith(".p4") and not f.endswith("-ddg.p4") and not re.search(r"-ddg\d+\.p4$", f)]
    
    for original_file in original_files:
        abs_original = os.path.abspath(os.path.join(root, original_file))
        base_name = os.path.splitext(original_file)[0]
        
        # # Check for single -ddg.p4 file
        # single_ddg = abs_original.replace(".p4", "-ddg.p4")
        # if os.path.exists(single_ddg):
        #     equiv_pairs.append((abs_original, abs_original, single_ddg))
        
        # Check for numbered -ddg{num}.p4 files
        dir_path = os.path.dirname(abs_original)
        for file in os.listdir(dir_path):
            if file.startswith(base_name) and re.search(r"-ddg\d+\.p4$", file):
                numbered_ddg = os.path.abspath(os.path.join(dir_path, file))
                equiv_pairs.append((abs_original, abs_original, numbered_ddg))

pairs = manual_pairs + equiv_pairs


import sim
import sys
import os

def filter_out_short_packets(p):
    return [packet for packet in p if len(packet) > 32]

def get_trace(r):
    traces = []
    for per_packer in r:
        try:
            log = per_packer[1][0][1] # -- 0th iteration as repeat = 1
        except Exception as e:
            print(e)
            # print(f"occured for {r}")
            # sys.exit(1)
        packet = per_packer[0]
        # for line in log: print(line)
        # print()
        trace = []
        extract_pattern = r"Extracting header '([^']+)'"

        for line in log:
            # header 
            if "Extracting header" in line:
        
                match = re.search(extract_pattern, line)
                if match:
                    trace.append(match.group(1))
            # TODO exclude scalars but include sie effects 
            # if "Parser set" in line:
            #     trace.append(line.split("Parser set:")[-1])


        traces.append((packet, trace, log))
    return traces



subprocess.call("mkdir -p correctness_results", shell=True)
subprocess.call("rm -rf correctness_results", shell=True)
subprocess.call("mkdir -p correctness_results", shell=True)
s = 0
results = []
for f_gen, f_original, f_ddg in pairs:
    try:
        base_name = os.path.splitext(os.path.basename(f_gen))[0]
        print(f"Testing {f_original} and {f_ddg}")
        suc, packets_from_p4f = sim.prepare_run(f_gen, None, MAX_PACKETS_P4PKTGEN, REPEAT_EACH_PACKET_N_TIMES, None)

        if not suc:
            print(f"P4TestGen failed for {f_gen}, this should be a normal P4 file, with modifications to not crash p4testgen")
            sys.exit(1)
        else:
            packets = filter_out_short_packets(list(set(packets_from_p4f)))
        
        if len(packets) < 5:
            print(f"Not enough packets, only {len(packets)}, to test {f_original} and {f_ddg}, skipping")
            continue
        with open(f"correctness_results/{base_name}.packets", "w") as packet_file:
            for packet in packets:
                packet_file.write(f"{packet}\n")
        try:
            r_original = sim.run_bmv2(f_original, packets, len(packets), REPEAT_EACH_PACKET_N_TIMES, None)
        except Exception as e:
            print(f"ERROR: {e} for {f_original}")
            continue
        try:
            r_ddg = sim.run_bmv2(f_ddg, packets, len(packets), REPEAT_EACH_PACKET_N_TIMES, None)
        except Exception as e:
            print(f"ERROR: {e} for {f_ddg}")
            continue
        subprocess.call(f"cp /tmp/p4ddg-experiment-runner-log.txt correctness_results/{base_name}-p4app.log", shell=True)

        trace_og = get_trace(r_original)
        trace_ddg = get_trace(r_ddg)
        with open(f"correctness_results/{base_name}.log", "w") as out:

            out.write("Logs for each packet for: {f_original}:\n")
            for packet, trace, log in trace_og:
                out.write(f"Packet: {packet}\n")
                out.write(f"Trace: {trace}\n")
                out.write(f"Log: {log}\n")


            out.write("Logs for each packet for: {f_ddg}:\n")
            for packet, trace, log in trace_ddg:
                out.write(f"Packet: {packet}\n")
                out.write(f"Trace: {trace}\n")
                out.write(f"Log: {log}\n")
        error = False
        for (( packet_og, trace_og, _), ( packet_ddg, trace_ddg, _)) in zip(trace_og, trace_ddg):
            if packet_og != packet_ddg:
                print(f"ERROR: found two traces that should have the same input packet, but don't ")
                error = True

            elif trace_og != trace_ddg:
                print(f"ERROR: found a packet where the two traces are not equal \n packet: {packet_og} \n trace original p4 program {trace_og} \n trace ddg {trace_ddg}\n\n")
                error = True
        
        if not error:
            print(f"SUCCESS: {f_original} and {f_ddg} are equivalent for {len(packets)} packets")
            s += 1
            results.append((True, (f_gen, f_original, f_ddg)))

    except Exception as e:
        print(f"ERROR: {e} for {f_original} and {f_ddg}")
        # print(f"{trace_og} {trace_ddg}")
print(f"Success for {s} out of {len(pairs)} pairs")

print("Passed tests:")
print(f"pairs = [")
for result in results:
    f_gen, f_original, f_ddg = result[1]
    if result[0]:
        print(f"    (\"{f_original}\", \"{f_ddg}\"),")
print("]")
