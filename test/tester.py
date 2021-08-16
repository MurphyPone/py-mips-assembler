#!/usr/bin/env python3
import sys
import os

def main(argc, argv):
    multiple = False

    if argc < 2:
        print("Missing input file, invoke with ./testery.py <xyz_output.o>")
        return 1 
    elif argc == 2:
        input_file = argv[1]
        solution_file = f"{input_file[:input_file.index('_output')]}_solution.o"

        print(f"input_file: {input_file}, solution_file: {solution_file}")
    
    elif argc == 3 and argv[1] == "-f":
        folder = argv[2]
        multiple = True
        print(f"folder: {folder}")

    if multiple:
        scores = []
        for entry in os.listdir(folder):
            if entry.endswith("_output.o"): # find a given file
                input_file = f"{folder}{entry}"
                solution_file = f"{input_file[:input_file.index('_output')]}_solution.o"

                with open(input_file, "r") as f:
                    raw_lines = f.readlines()
                    lines = []
                    for line in raw_lines:
                        if not line.strip() == "":
                            lines.append(line.strip())
                
                with open(solution_file, "r") as f:
                    raw_lines = f.readlines()

                    solution_lines = []
                    for line in raw_lines:
                        if not line.strip() == "":
                            solution_lines.append(line.strip())

                if len(lines) != len(solution_lines):
                    print(f"length of output files are not the same. len(lines): {len(lines)}, len(solution_lines) {len(solution_lines)}")
                    return

                your_line = "your line:".ljust(12)
                solution_line = "solution:".ljust(12)
                
                current_score = {
                    "name": entry,
                    "earned": 0,
                    "total": len(lines)
                }

                for i, (l, s) in enumerate(zip(lines, solution_lines)):
                    idx = "{0:02d}".format(i)
                    print(f"{idx} {your_line}{l.strip()}\n{idx} {solution_line}{s.strip()}", end=" ")
                    if l == s:
                        current_score["earned"] += 1
                        print("✅\n")
                    else:
                        print("❌\n")

                scores.append(current_score)
                print(f"matched {current_score['earned']} / {current_score['total']} lines")
                print("---------------------------------------\n")
        
        for score in scores:
            earned = "{0:2d}".format(score['earned'])
            total = "{0:2d}".format(score['total'])
            print(f"{score['name']}\t{earned} / {total}")
    
    else: # process single
        with open(input_file, "r") as f:
            raw_lines = f.readlines()
            lines = []
            for line in raw_lines:
                if not line.strip() == "":
                    lines.append(line.strip())

        
        with open(solution_file, "r") as f:
            raw_lines = f.readlines()

            solution_lines = []
            for line in raw_lines:
                if not line.strip() == "":
                    solution_lines.append(line.strip())

        if len(lines) != len(solution_lines):
            print(f"length of output files are not the same. len(lines): {len(lines)}, len(solution_lines) {len(solution_lines)}")
            return

        your_line = "your line:".ljust(12)
        solution_line = "solution:".ljust(12)
        
        score = 0
        total = len(lines)

        for i, (l, s) in enumerate(zip(lines, solution_lines)):
            idx = "{:02d}".format(i+1)
            print(f"{idx} {your_line}{l.strip()}\n{idx} {solution_line}{s.strip()}", end=" ")
            if l == s:
                score += 1
                print("✅\n")
            else:
                print("❌\n")

        print(f"matched {score} / {total} lines")



if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
    
