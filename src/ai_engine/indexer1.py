import os
import torch
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def build_index():
    # Kiểm tra GPU và khả năng tương thích
    device = "cpu"
    print(f"🚀 Đang chạy Indexer trên: {device.upper()}")

    # 1. Cấu hình Model Embedding (BGE-Base)
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",
        model_kwargs={'device': device},
        encode_kwargs={'normalize_embeddings': True}
    )

    # 2. Loader: SỬA LỖI TẠI ĐÂY - Dùng from_filesystem thay vì from_custom_extractors
    # Chỉ quét thư mục src, bỏ qua các file rác
    loader = GenericLoader.from_filesystem(
        "./src",
        glob="**/*.py",
        suffixes=[".py"],
        parser=LanguageParser(language=Language.PYTHON, parser_threshold=500)
    )
    
    print("📂 Đang đọc mã nguồn và phân tích cấu trúc...")
    docs = loader.load()

    if not docs:
        print("❌ Không tìm thấy file .py nào trong thư mục ./src")
        return

    # 3. Splitter: Cắt theo logic Python
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, 
        chunk_size=1500, 
        chunk_overlap=200
    )
    texts = splitter.split_documents(docs)
    print(f"✂️ Đã chia thành {len(texts)} mảnh logic chuyên sâu.")

    # 4. Lưu trữ vào FAISS
    vector_db = FAISS.from_documents(texts, embeddings)
    
    # Đảm bảo thư mục tồn tại
    os.makedirs("./src/ai_engine/stores/code_idx_v2", exist_ok=True)
    vector_db.save_local("./src/ai_engine/stores/code_idx_v2")
    print("✅ Đã cập nhật 'Bộ nhớ thông minh' tại code_idx_v2")

if __name__ == "__main__":
    build_index()