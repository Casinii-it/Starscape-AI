import os
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings
)

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.node_parser import SentenceSplitter

# Configure models
Settings.llm = Ollama(
    model="llama3.2:3b",
    context_window=2048,
    request_timeout=300
    )

node_parser = SentenceSplitter(
    chunk_size=128,
    chunk_overlap=10
)

Settings.embed_model = OllamaEmbedding(model_name="all-minilm")


PERSIST_DIR = "./storage"

if not os.path.exists(PERSIST_DIR):
    # First run → build index
    documents = SimpleDirectoryReader("./data").load_data()

    nodes = node_parser.get_nodes_from_documents(documents)
    index = VectorStoreIndex(nodes)

    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    # Later runs → load index
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine(
    similarity_top_k=6
)

while 1:
    response = query_engine.query(input("YOU:   "))
    print(f"AI:    {response}\n")
    print("\n--- SOURCES ---")
    for node in response.source_nodes:
        print(node.text)
        print("------")
