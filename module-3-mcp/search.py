import zipfile
import os
import sys
import pickle
from pathlib import Path
from minsearch import Index


def extract_md_files_from_zip(zip_path):
    """
    Extract and read all .md and .mdx files from a zip file.
    Returns a list of documents with 'content' and 'filename' fields.
    The first part of the path is removed from filenames.
    """
    documents = []

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.filelist:
            filename = file_info.filename

            # Check if it's a .md or .mdx file
            if filename.endswith('.md') or filename.endswith('.mdx'):
                # Skip directories
                if not file_info.is_dir():
                    try:
                        # Read the file content
                        with zip_ref.open(filename) as file:
                            content = file.read().decode('utf-8')

                        # Remove the first part of the path
                        # e.g., "fastmcp-main/docs/getting-started/welcome.mdx" -> "docs/getting-started/welcome.mdx"
                        path_parts = filename.split('/', 1)
                        if len(path_parts) > 1:
                            clean_filename = path_parts[1]
                        else:
                            clean_filename = filename

                        documents.append({
                            'content': content,
                            'filename': clean_filename
                        })

                    except Exception as e:
                        print(f"Error reading {filename}: {e}")

    return documents


def create_search_index(documents):
    """
    Create a minsearch index from documents.
    """
    index = Index(
        text_fields=['content', 'filename'],
        keyword_fields=[]
    )
    index.fit(documents)
    return index


def save_index(index, documents, filepath='search_index.pkl'):
    """
    Save the index and documents to a file.
    """
    data = {
        'index': index,
        'documents': documents
    }
    with open(filepath, 'wb') as f:
        pickle.dump(data, f)
    print(f"Index saved to {filepath}")


def load_index(filepath='search_index.pkl'):
    """
    Load the index and documents from a file.
    Returns (index, documents) or (None, None) if file doesn't exist.
    """
    if not os.path.exists(filepath):
        return None, None

    with open(filepath, 'rb') as f:
        data = pickle.load(f)

    print(f"Index loaded from {filepath}")
    return data['index'], data['documents']


def need_reindex(zip_path, index_path='search_index.pkl'):
    """
    Check if reindexing is needed by comparing file modification times.
    """
    if not os.path.exists(index_path):
        return True

    zip_mtime = os.path.getmtime(zip_path)
    index_mtime = os.path.getmtime(index_path)

    return zip_mtime > index_mtime


def search(index, query, num_results=5):
    """
    Search for documents using the query.
    Returns the top num_results most relevant documents.
    """
    boost_dict = {
        'filename': 2,
        'content': 1
    }

    results = index.search(
        query,
        boost_dict=boost_dict,
        num_results=num_results
    )

    return results


def main():
    # Path to the downloaded zip file
    zip_path = 'fastmcp-main.zip'
    index_path = 'search_index.pkl'

    # Get query from command line argument or use default
    if len(sys.argv) > 1:
        query = sys.argv[1]
    else:
        query = 'demo'

    if not os.path.exists(zip_path):
        print(f"Error: {zip_path} not found!")
        return

    # Check if we need to reindex
    if need_reindex(zip_path, index_path):
        print("Extracting and reading md/mdx files from zip...")
        documents = extract_md_files_from_zip(zip_path)
        print(f"Found {len(documents)} md/mdx files")

        print("\nIndexing documents with minsearch...")
        index = create_search_index(documents)
        print("Indexing complete!")

        # Save index for future use
        save_index(index, documents, index_path)
    else:
        print("Loading cached index...")
        index, documents = load_index(index_path)

    print(f"\nSearching with query: '{query}'")
    results = search(index, query, num_results=5)

    print(f"\nTop 5 results for '{query}':")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc['filename']}")
        print(f"   Preview: {doc['content'][:100]}...")
        print()

    if results:
        print(f"The first file returned is: {results[0]['filename']}")
    else:
        print("No results found!")


if __name__ == '__main__':
    main()
