import os

def compile_book():
    output_file = "d:/ci lang/docs/THE_BOOK_OF_CHAOS.md"
    base_dir = "d:/ci lang/docs"
    
    # Define the exact order of files
    order = [
        "Book_TOC.md",
        "Book_Chapter_1.md",
        "Book_Chapter_2.md",
        "Book_Chapter_3.md",
        "Book_Chapter_4.md",
        "Book_Chapter_5.md",
        "Book_Chapter_6.md",
        "Book_Chapter_7.md",
        "Book_Chapter_8.md",
        "Book_Chapter_9.md",
        "Book_Chapter_10.md",
        "Book_Chapter_11.md",
        "Book_Chapter_12.md",
        "Book_Chapter_13.md",
        "Book_PartV.md",  # Covers Ch 14-16
        "Book_PartVI.md", # Covers Ch 17-20
        "Book_Chapter_20_Integration.md", # Covers 20.5 - 20.6
        "Book_PartVII.md" # Covers Ch 21-23
    ]
    
    print(f"Compiling {len(order)} files into THE_BOOK_OF_CHAOS.md...")
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in order:
            path = os.path.join(base_dir, filename)
            if os.path.exists(path):
                print(f"Processing {filename}...")
                with open(path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)
                    outfile.write("\n\n---\n\n") # Page break/Separator
            else:
                print(f"WARNING: Missing file {filename}")
                
    print("Compilation Complete.")

if __name__ == "__main__":
    compile_book()
