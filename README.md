# Artifact
Artifact for: P4DDG: Data-Dependent Grammars for Packet Specification and Parsing in P4

Latest version: 
## Usage
To clone this repository use:
```
git clone --recurse-submodules 
```
The code expects two Docker images. 
<!-- These are published, so **there should be no need to build them**. However, if you want to, they can be built from `submodules/bmv2` and `submodules/p4c`. -->
To built them, from the root directory run:
```
cd submodules/bmv2 && docker build . -t bmv2
```
and 
```
cd submodules/p4c && docker build . -t p4c-with-fix
```

# Reproduce the images in the paper
To generate the images shown in the paper 
run the included python scripts.
<!-- run:
```
sudo python3 main.py
``` -->

## Submodules
- P4ddgC: A compiler from P4ddg, a variant of the P4 language that uses data-dependent grammars (DDGs) to specify parsers (https://github.com/tommanis1/P4DDG)
- bmv2: A fork of the behavioral model v2 with a minimal tweak to timestamp generation
- p4c: A version of the reference P4 compiler with a fix applied for reading from header stacks
- p4app: A fork of p4app; a utility to run P4 code using mininet

## Scripts
- `check_correctness.py`: Establish runtime equivalence between DDG-generated and hand-written parsers 
<!-- - `main.py`: Generates figure  -->
- `run_eval_stack_usage.py`: Generates figure 14
- `plot_equiv_delays.py`: Generates figure 13
- `python gen_programs.py` : Generate P4 code from the DDGs in programs/programs_with_equivalent_ddgs using submodules/P4ddgC

