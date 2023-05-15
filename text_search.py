import re
from collections import defaultdict
from pathlib import Path

# Define a set of common words to ignore during search
stop_words = set(["the", "and", "or", "an", "a", "in", "of", "to", "is", "for", "that", "it", "with", "on", "by", "this", "be", "as", "at", "from"])

# Define the path and name of the index file
index_dir = "data/index.txt"

# Index the files in the directory
def index_files(directory):
    index = defaultdict(list)
    for path in Path(directory).rglob('*.txt'):
        with open(path, "r") as file:
            contents = file.read().lower().replace("\n", " ")
            contents = re.sub(r"[^\w\s]", " ", contents)
            contents = re.sub(r"\s+", " ", contents)
            words = contents.split()
            for word in words:
                if word not in stop_words:
                    index[word].append(str(path))
    return index

# Read the index file
def read_index(directory):
    index = defaultdict(list)
    if Path(index_dir).exists():
        with open(index_dir, "r") as file:
            for line in file:
                word, paths = line.strip().split(" ", 1)
                index[word] = paths.split()
        return index
    else:
        print("Index not found.")
        choice = input("Do you want to create an index? (Y/N): ").lower()
        if choice == "y":
            create_index(directory)
            return read_index(directory)
        else:
            exit()

# Create the index file
def create_index(directory):
    index = index_files(directory)
    with open(index_dir, "w") as file:
        for word in index:
            file.write(word + " " + " ".join(index[word]) + "\n")
    print("Index created successfully!")

# Search the indexed files
def search_files(index, query):
    results = defaultdict(int)
    words = re.findall(r"\b\w+\b", query.lower())
    for word in words:
        if word not in stop_words and word in index:
            for path in index[word]:
                results[path] += 1
    matches = []
    for path, count in results.items():
        with open(path, "r") as file:
            contents = file.read().lower().replace("\n", " ")
            contents = re.sub(r"[^\w\s]", " ", contents)
            contents = re.sub(r"\s+", " ", contents)
            excerpt = ""
            score = 0
            for word in words:
                if word in contents:
                    score += 1
                    pos = contents.index(word)
                    excerpt += "... " + contents[max(0, pos-20):pos+len(word)+20] + " ..."
            if score > 0:
                matches.append((count, excerpt, path))
    matches.sort(key=lambda match: match[0], reverse=True)
    if matches:
        print("Matching files found:")
        for i, match in enumerate(matches, start=1):
            print(f"\nMatch {i}: {match[1]}\nPath: {match[2]}\n")
    else:
        print("No matches.")

# Main program loop
if __name__ == "__main__":
    directory = input("Enter the directory containing the text files: ")
    index_dir = Path(directory) / "index_data.txt"
    index = read_index(directory)
    while True:
        query = input("Enter the search query: ")
        search_files(index, query)