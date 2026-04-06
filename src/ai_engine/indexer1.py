import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def build_index_v3():
    # Ép dùng CPU cho ổn định với GTX 1060
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",
        model_kwargs={'device': 'cpu'}
    )

    all_docs = []
    # Quét thủ công để lấy chính xác số dòng
    source_dir = "./src/app"
    for root, dirs, files in os.walk(source_dir):
        # Bỏ qua các thư mục rác
        if any(x in root for x in ['seed', 'data', '__pycache__', 'stores']):
            continue
            
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                # Dùng TextLoader để nạp từng file
                loader = TextLoader(file_path, encoding='utf-8')
                file_docs = loader.load()
                
                # Thêm metadata về file cho từng doc
                for doc in file_docs:
                    doc.metadata["source"] = file_path
                all_docs.extend(file_docs)

    # Splitter thông minh hơn
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        add_start_index=True # Lưu vị trí ký tự để sau này tính ra số dòng
    )
    
    final_texts = splitter.split_documents(all_docs)
    
    # Lưu vào kho mới
    vector_db = FAISS.from_documents(final_texts, embeddings)
    vector_db.save_local("./src/ai_engine/stores/code_idx_v3")
    print(f"✅ Đã index {len(final_texts)} đoạn code từ các file logic thực tế!")

if __name__ == "__main__":
    build_index_v3()