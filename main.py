# Generate all figures from the paper
import subprocess
import os
import plot_equiv_delays

def main():
    print("This script generates most of the figures from the paper.")
    # subprocess.run("cd submodules/P4ddgC && cabal build P4DDG", shell=True)
    # path = os.path.abspath("programs/running_example/tunnel.ddg")
    # subprocess.run("cd submodules/P4ddgC && cabal exec P4DDG -- --debug -i {path}", shell=True)

    print("Generating Figure 13, the bar chart comparing parse delay on BMv2")
    plot_equiv_delays.main()

    

    # print("Generating the performance comparison graph")
    # import plot_equiv_delays
    # plot_equiv_delays.main()
    # print("Generating the graph comparing recursive calls to the Kleene star")


if __name__ == "__main__":
    main()