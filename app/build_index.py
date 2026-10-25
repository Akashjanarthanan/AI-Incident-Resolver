from pathlib import Path
import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from chunker import chunk_text


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

DOCUMENTS_PATH = Path("data/documents")
VECTOR_STORE_PATH = Path("vector_store")

METADATA_CONFIG_PATH = Path(
    "data/documents/document_metadata.json"
)


# ---------------------------------------------------------
# Embedding model
# ---------------------------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"


# ---------------------------------------------------------
# Load documents
# ---------------------------------------------------------

def load_documents():
    documents = []

    for file_path in DOCUMENTS_PATH.glob("*.md"):

        content = file_path.read_text(
            encoding="utf-8"
        )

        documents.append(
            {
                "source": file_path.name,
                "content": content,
            }
        )

    return documents


# ---------------------------------------------------------
# Load document metadata configuration
# ---------------------------------------------------------

def load_document_metadata():
    """
    Load metadata for documents from JSON configuration.
    """

    if not METADATA_CONFIG_PATH.exists():

        raise FileNotFoundError(
            "Metadata configuration not found: "
            f"{METADATA_CONFIG_PATH}"
        )

    with open(
        METADATA_CONFIG_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ---------------------------------------------------------
# Get metadata for one document
# ---------------------------------------------------------

def get_document_metadata(
    source,
    metadata_config
):
    """
    Get metadata for a document.

    Raises an error when a document does not have
    a corresponding metadata entry.
    """

    if source not in metadata_config:

        raise ValueError(
            f"No metadata found for document: {source}"
        )

    return metadata_config[source]


# ---------------------------------------------------------
# Create chunks
# ---------------------------------------------------------

def create_chunks(
    documents,
    metadata_config
):
    """
    Split documents into chunks and attach metadata
    to every chunk.
    """

    all_chunks = []

    for document in documents:

        chunks = chunk_text(
            document["content"],
            chunk_size=500,
            overlap=50
        )

        document_metadata = get_document_metadata(
            document["source"],
            metadata_config
        )

        for chunk_id, chunk in enumerate(
            chunks,
            start=1
        ):

            chunk_metadata = {
                "text": chunk,
                "source": document["source"],
                "chunk_id": chunk_id,
                "category": document_metadata["category"],
                "technology": document_metadata["technology"],
                "document_type": document_metadata["document_type"],
                "environment": document_metadata["environment"]
            }

            all_chunks.append(
                chunk_metadata
            )

    return all_chunks


# ---------------------------------------------------------
# Build FAISS index
# ---------------------------------------------------------

def build_index(
    chunks,
    model
):
    """
    Generate embeddings and build the FAISS index.
    """

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print("\nGenerating embeddings...")

    embeddings = model.encode(
        texts,
        show_progress_bar=True
    )

    embeddings = np.array(
        embeddings
    ).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(
        dimension
    )

    index.add(embeddings)

    return index


# ---------------------------------------------------------
# Save FAISS index and metadata
# ---------------------------------------------------------

def save_index(
    index,
    chunks
):
    """
    Save the vector index and chunk metadata.
    """

    VECTOR_STORE_PATH.mkdir(
        exist_ok=True
    )

    index_path = (
        VECTOR_STORE_PATH
        / "knowledge_base.index"
    )

    metadata_path = (
        VECTOR_STORE_PATH
        / "metadata.json"
    )

    faiss.write_index(
        index,
        str(index_path)
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            indent=2
        )

    print("\nIndex saved:")
    print(index_path)

    print("\nMetadata saved:")
    print(metadata_path)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("Loading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME
    )

    print("\nLoading documents...")

    documents = load_documents()

    print(
        f"Documents loaded: "
        f"{len(documents)}"
    )

    print("\nLoading document metadata...")

    metadata_config = (
        load_document_metadata()
    )

    print(
        f"Metadata entries: "
        f"{len(metadata_config)}"
    )

    print("\nCreating chunks...")

    chunks = create_chunks(
        documents,
        metadata_config
    )

    print(
        f"Chunks created: "
        f"{len(chunks)}"
    )

    index = build_index(
        chunks,
        model
    )

    print(
        f"\nVectors stored in FAISS: "
        f"{index.ntotal}"
    )

    save_index(
        index,
        chunks
    )


if __name__ == "__main__":
    main()