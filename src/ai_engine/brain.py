import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import dotenv
dotenv.load_dotenv()

def ask_my_code_modern(question: str):
    # 1. Khởi tạo tài nguyên
    model_kwargs={"device": "cpu"}
    encode_kwargs={"normalize_embeddings": True}
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5", 
        model_kwargs=model_kwargs, 
        encode_kwargs=encode_kwargs
    )
    
    # Load Vector DB đã index từ trước
    vector_db = FAISS.load_local(
        "./src/ai_engine/stores/code_idx_v2", 
        embeddings,
        allow_dangerous_deserialization=True
    )
    
    # Tạo Retriever (Bộ truy xuất)
    retriever = vector_db.as_retriever(search_kwargs={
        "k": 15,
        "filter": lambda metadata: all(word not in metadata["source"].lower() for word in ["seed", "load", "insert", "mock"])
        })

    # 2. Khởi tạo LLM (Groq - Llama 3)
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant", 
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0
    )

    # 3. Thiết kế Prompt hiện đại
    template ="""
        BẠN LÀ: Một AI Engineer chuyên trách Codebase WMS.
        NHIỆM VỤ: Tìm LOGIC NGHIỆP VỤ (Business Logic).

        NGỮ CẢNH:
        {context}

        CÂU HỎI: {question}

        QUY TẮC PHẢN HỒI:
        1. TUYỆT ĐỐI BỎ QUA các đoạn code chỉ làm nhiệm vụ Insert dữ liệu mẫu (Seed data/Load data).
        2. TÌM KIẾM các hàm nằm trong thư mục 'services', 'crud', 'api' hoặc 'logic'.
        3. Nếu các đoạn code được cung cấp đều là dữ liệu mẫu, hãy trả lời: "Tôi chỉ tìm thấy dữ liệu mẫu, không thấy logic nghiệp vụ liên quan. Hãy kiểm tra lại file index."
        4. Trích dẫn chính xác tên file từ metadata.
        """
    prompt = ChatPromptTemplate.from_template(template)

    # 4. THIẾT LẬP CHUỖI LCEL (ĐÂY LÀ ĐIỂM TỐI TÂN NHẤT)
    # Dấu | kết nối các bước cực kỳ minh bạch
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # 5. Thực thi
    print(f"\n🔍 Đang truy vấn cấu trúc dự án...")
    response = rag_chain.invoke(question)
    
    print("-" * 30)
    print(f"🤖 AI ENGINEER:\n{response}")

if __name__ == "__main__":
    user_query = input("Hỏi về logic dự án WMS: ")
    ask_my_code_modern(user_query)
