import re
from collections import defaultdict
from pathlib import Path
import webbrowser

# Define a set of common words to ignore during search
stop_words = set(["the", "and", "or", "an", "a", "in", "of", "to", "is", "for", "that", "it", "with", "on", "by", "this", "be", "as", "at", "from"])

# Define the path and name of the index file
index_dir = "input_data/index.txt"

# Remove stop words from text
def remove_stop_words(text):
    words = text.split()
    return " ".join([word for word in words if word.lower() not in stop_words])

# Index the files in the directory
def index_files(directory):
    index = defaultdict(list)
    for path in Path(directory).rglob('*.txt'):
        with open(path, "r") as file:
            contents = file.read().lower().replace("\n", " ")
            contents = re.sub(r"[^\w\s]", " ", contents)
            contents = re.sub(r"\s+", " ", contents)
            contents = remove_stop_words(contents)
            words = contents.split()
            for word in words:
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
def create_index(directory, force=False):
    index = index_files(directory)
    if force or not Path(index_dir).exists():
        with open(index_dir, "w") as file:
            for word in index:
                file.write(word + " " + " ".join(index[word]) + "\n")
        print("Index created successfully!")
    else:
        print("Index file already exists. Use --force option to overwrite.")

# Search the indexed files and create the HTML page
def search_and_display_files(index, query):
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
            contents = remove_stop_words(contents)
            excerpt = ""
            score = 0
            for word in words:
                if word in contents:
                    score += 1
                    pos = contents.index(word)
                    excerpt += "... " + contents[max(0, pos-20):pos+len(word)+20] + " ..."
            if score > 0:
                # Add hyperlinks to the matched text
                contents_with_links = contents
                for word in words:
                    if word in contents_with_links:
                        pos = contents_with_links.index(word)
                        href = f"file://{path}#char={pos}"
                        contents_with_links = contents_with_links.replace(word, f"<a href='{href}'>{word}</a>")
                matches.append((count, excerpt, path, contents_with_links))
    matches.sort(key=lambda match: match[0], reverse=True)
    if matches:
        print("Matching files found:")
        html = "<html><head><title>Search Results</title></head><body>"
        for i, match in enumerate(matches, start=1):
            html += f"<p>Match {i}: {match[1]}<br>Path: <a href=\"file://{match[2]}\">{match[2]}</a></p>"
            html += f"<pre>{match[3]}</pre>"
        html += "</body></html>"
        with open("search_results.html", "w") as file:
            file.write(html)
        webbrowser.open_new_tab("search_results.html")
    else:
        print("No matches.")

# Main program loop
if __name__ == "__main__":
    directory = input("Enter the directory containing the text files: ")
    index_dir = Path(directory) / "index_data.txt"
    index = read_index(directory)
    while True:
        query = input("Enter the search query: ")
        search_and_display_files(index, query)
        choice = input("Do you want to re-index the files? (Y/N): ").lower()
        if choice == "y":
            force = input("Do you want to overwrite the existing index? (Y/N): ").lower() == "y"
            create_index(directory, force)
            index = read_index(directory)