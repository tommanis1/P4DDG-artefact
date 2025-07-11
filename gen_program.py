import os
import argparse
import sys
import subprocess

def find_file(dir_path, ending=".ddg"):
    """
    This function searches for a file in the specified directory.
    If found, it returns the absolute path to the file.
    """
    try:
        for root, _, files in os.walk(dir_path):
            for file in files:
                print(f"Checking file: {file}")
                if file.endswith(ending):
                    return os.path.abspath(os.path.join(root, file))
        print(f"No {ending} file found in the directory: {dir_path}")
    except Exception as e:
        print(f"An error occurred while searching for {ending} files: {e}")
    
        sys.exit(1)

def find_files(dir_path, ending=".ddg"):
    """
    This function searches for all files with the specified ending in the directory.
    Returns a list of absolute paths to the files found.
    """
    files_found = []
    try:
        print(f"walking: {dir_path}")
        for root, _, files in os.walk(dir_path):
            for file in files:
                print(f"Checking file: {file}")
                if file.endswith(ending):
                    files_found.append(os.path.abspath(os.path.join(root, file)))
        if not files_found:
            print(f"No {ending} files found in the directory: {dir_path}")
        return files_found
    except Exception as e:
        print(f"An error occurred while searching for {ending} files: {e}")
        sys.exit(1)

def update(ddg, file_to_edit, backend="continuations", num=0, exec_path="null"):
    subprocess.run(f"cd {exec_path} && cabal build exe:P4DDG", shell=True, capture_output=True,text=True)

    p4_code = subprocess.run(f"cd {exec_path} && cabal exec P4DDG -- --opt -i {ddg} -b {backend}", shell=True, capture_output=True,text=True)

    # print(p4_code)


    if p4_code.returncode != 0:
        print(f"\033[91mError: Failed to run P4DDG on {ddg}.\033[0m")
        subprocess.run(f"cd {exec_path} && cabal exec P4DDG -- --debug --opt -i {ddg} -b {backend}", shell=True)

    else:
    #     preamble,parser_body = parse(p4_code.stdout)
    #     print(preamble)
    #     print(parser_body)

    # modied_file_path = file_to_edit.replace("-ddg.p4f", f"-ddg{num}.p4")
    # print(f"Modifying file: {modied_file_path}")
    # # Replace "#Preamble" with preamble in file_to_edit
    # with open(file_to_edit, "r") as f:
    #     file_content = f.read()
    # file_content = file_content.replace("#Preamble", preamble)

    # # Replace "#Parser" with preamble in file_to_edit

    # file_content = file_content.replace("#Parser", parser_body)
    # with open(modied_file_path, "w") as f:
    #     f.write(file_content)
        modied_file_path = file_to_edit.replace("-ddg.p4f", f"-ddg{num}.p4")
        if os.path.exists(modied_file_path):
            os.remove(modied_file_path)
        # print(p4_code.stdout)

        parser = p4_code.stdout
        with open(file_to_edit, "r") as f:
            file_content = f.read()
        file_content = file_content.replace("#Parser", parser)
        with open(modied_file_path, "w") as f:
            f.write(file_content)



def parse(p4_code):
    pre, post = "", ""
    a = False
    b = False
    for line in p4_code.splitlines():
        if not b:
            if "// Place this header definition outside of your parser" in line: a = True
        if "// Make these global variables of the parser" in line: b = True

        if b: post += line + "\n"
        if a and not b : pre += line + "\n"

    return pre, post
        

def main(dir_path, exec_path):
    ddg_files = find_files(dir_path, ".ddg")
    file_to_edit = find_file(dir_path, "-ddg.p4f")
    print(f"Found ddg files: {ddg_files} and file to edit: {file_to_edit}")
    
    # Process each DDG file with its corresponding number
    for ddg_file in enumerate(ddg_files):
        filename = ddg_file[1]
        base = filename.split('.ddg')[0][::-1]
        digits = ""
        for char in base:
            if char.isdigit():
                digits += char
            else:
                break
        if digits == "":
            i = len(ddg_files)
        else: 
            i = int(digits[::-1])
        print(f"Processing DDG file {i}: {filename}")
        update(filename, file_to_edit, num=i, backend="continuations", exec_path=exec_path)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Process a directory path.")
#     parser.add_argument(
#         "dir_path",
#         type=str,
#         help="Path to the directory to be processed"
#     )
#     args = parser.parse_args()

#     if not os.path.isdir(args.dir_path):
#         print(f"Error: The path '{args.dir_path}' is not a valid directory.")
#         sys.exit(1)
    
#     main(args.dir_path)