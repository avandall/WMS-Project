import os
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def index_codebase():
    print("🚀 Đang bắt đầu quét mã nguồn...")

    #1. Load codebase
    loader = GenericLoader.from_filesystem(
        "./src",
        glob="**/*.py",
        suffixes=[".py"],
        parser=LanguageParser(language=Language.PYTHON,parser_threshold=200)
    )
    docs=loader.load()
    print(f"📂 Đã quét {len(docs)} tài liệu mã nguồn")
    
    #2. Split code into chunks
    splitter = RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON, chunk_size=1500, chunk_overlap=200)
    texts= splitter.split_documents(docs)

    print(f"✂️ Đã chia mã nguồn thành {len(texts)} đoạn")

    #3. Create embeddings
    print("🔍 Đang tạo embeddings...")
    embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    #4. Store in FAISS
    vector_db = FAISS.from_documents(texts, embeddings)
    vector_db.save_local("./ai_engine/stores/code_idx")
    print("✅ Quá trình quét và lưu trữ hoàn tất!")

if __name__ == "__main__":
    index_codebase()