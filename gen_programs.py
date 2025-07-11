import gen_program as genIndividual
import os
def gen(path="programs/programs_with_equivalent_ddgs"):
    for d in os.listdir(path):

        if os.path.isdir(os.path.join(path, d)):
            # Check if the directory contains a ddg file
            ddg_file = None
            for file in os.listdir(os.path.join(path, d)):
                if file.endswith(".ddg"):
                    ddg_file = file
                    break
            if not ddg_file:
                continue
            
            # Call the compiler to generate a P4 program from the ddg
            genIndividual.main(os.path.abspath(os.path.join(path, d)), os.path.abspath("submodules/P4ddgC"))
if __name__ == "__main__": gen()