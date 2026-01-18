import numpy as np

def generate_svo_corpus():
    """
    Generates a simple Subject-Verb-Object (SVO) corpus for narrative learning.
    """
    subjects = ["cat", "dog", "man", "woman", "robot"]
    verbs = ["hunts", "chases", "watches", "seeks", "greets"]
    objects = ["mouse", "bone", "chaos", "order", "logic"]
    
    corpus = []
    for s in subjects:
        for v in verbs:
            for o in objects:
                corpus.append(f"{s} {v} {o}")
    
    return corpus

if __name__ == "__main__":
    lines = generate_svo_corpus()
    print(f"Generated {len(lines)} SVO sentences.")
    with open("d:/ci lang/research_sandbox/data/svo_corpus.txt", "w") as f:
        for line in lines:
            f.write(line + "\n")
