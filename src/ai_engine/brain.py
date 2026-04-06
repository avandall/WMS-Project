import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def get_line_number(doc):
    """Hàm phụ trợ để ước tính số dòng từ start_index"""
    content = doc.page_content
    # Đây là logic ước tính, thực tế LangChain sẽ lưu start_index trong metadata
    return doc.metadata.get('start_index', 0) // 40 # Ước tính trung bình 40 ký tự/dòng

def ask_my_code_v3(question: str):
    # Khớp 100% với Indexer
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5",
        model_kwargs={'device': 'cpu'}
    )

    # Load kho tri thức mới v3
    vector_db = FAISS.load_local(
        "./src/ai_engine/stores/code_idx_v3", 
        embeddings, 
        allow_dangerous_deserialization=True
    )

    # Chỉ lấy 5 đoạn code chất lượng nhất
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})

    llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0)

    template = """
    VAI TRÒ: Bạn là Senior Developer am hiểu dự án WMS này.
    NGỮ CẢNH CODE:
    {context}
    
    CÂU HỎI: {question}
    
    YÊU CẦU:
    1. Trả lời chính xác logic nằm ở file nào.
    2. Trích dẫn đoạn code ngắn gọn liên quan.
    3. Nếu không có trong code, hãy nói "Tôi không tìm thấy logic này trong src/".
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt | llm | StrOutputParser()
    )

    print("\n" + "="*50)
    print(f"🤖 AI ĐANG PHÂN TÍCH V3...")
    print(chain.invoke(question))

if __name__ == "__main__":
    query = input("Hỏi về logic WMS: ")
    ask_my_code_v3(query)