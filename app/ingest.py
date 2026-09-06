from pathlib import Path
from chunker import chunk_text

DOCUMENTS_PATH = Path("data/documents")


def load_documents():
  documents = []
  for file_path in DOCUMENTS_PATH.glob("*.md"):
    content = file_path.read_text(encoding="utf-8")
    documents.append(
        {
            "source": file_path.name,
            "content": content,
        }
    )
  return documents


def main():
  documents = load_documents()
  print(f"Loaded {len(documents)} documents")
  total_chunks = 0

  for document in documents:
    chunks = chunk_text(document["content"], chunk_size=500, overlap=50)
    print("\n" + "=" * 60)
    print(f"Source: {document['source']}")
    print(f"Number of chunks: {len(chunks)}")
    print("=" * 60)

    for index, chunk in enumerate(chunks, start=1):
      chunk_data = {
          "text": chunk,
          "source": document["source"],
          "chunk_id": index,
      }
      print(f"\n--- Chunk {index} ---")
      print(f"Source: {chunk_data['source']}")
      print(f"Chunk ID: {chunk_data['chunk_id']}")
      print(chunk_data["text"])

    total_chunks += len(chunks)

  print("\n" + "=" * 60)
  print(f"Total chunks created: {total_chunks}")
  print("=" * 60)


if __name__ == "__main__":
  main()