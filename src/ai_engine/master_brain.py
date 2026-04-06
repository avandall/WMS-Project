import os
from brain2 import ask_warehouse_data  
from brain import ask_my_code_v3        
from langchain_groq import ChatGroq

def master_agent(user_query: str):
    llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0, api_key=os.getenv("GROQ_API_KEY"))
    
    # 1. AI đóng vai trò phân loại (Router)
    router_prompt = f"""
    Bạn là bộ điều hướng yêu cầu cho dự án WMS.
    Dựa trên câu hỏi: "{user_query}"
    
    Hãy chọn 1 trong 2 nhãn sau:
    - 'CODE': Nếu câu hỏi liên quan đến cấu trúc file, logic lập trình, hàm, line code.
    - 'DATA': Nếu câu hỏi liên quan đến dữ liệu thực tế trong kho, giá cả, số lượng sản phẩm.
    
    CHỈ TRẢ VỀ ĐÚNG 1 TỪ 'CODE' HOẶC 'DATA'.
    """
    
    decision = llm.invoke(router_prompt).content.strip().upper()
    
    if 'CODE' in decision:
        print("⚡ [System]: Đang tìm kiếm trong Source Code (FAISS)...")
        ask_my_code_v3(user_query)
    else:
        print("📊 [System]: Đang truy vấn dữ liệu thực tế (PostgreSQL)...")
        ask_warehouse_data(user_query)

if __name__ == "__main__":
    while True:
        q = input("\nHỏi bất cứ điều gì về WMS (Code hoặc Dữ liệu): ")
        if q.lower() in ['exit', 'quit']: break
        master_agent(q)