import pickle
import sys

def dump(filename):
    with open(filename, 'rb') as f:
        code = pickle.load(f)
    for i, instr in enumerate(code):
        print(f"{i:03}: {instr}")

if __name__ == "__main__":
    dump(sys.argv[1])
