import os
import psycopg2
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="warehouse_db",
        user="wms_user",
        password="wms_password",
        port="5433"
    )

def ask_warehouse_data(question: str):
    # Cập nhật Schema Context đầy đủ và chuyên nghiệp hơn
    schema_context = """
    CẤU TRÚC DATABASE WMS:
    1. Bảng 'products': 
       - Cột: product_id (PK), name (với index btree), description, price.
    2. Bảng 'inventory': 
       - Cột: product_id (PK, FK tham chiếu products.product_id), quantity.
    3. Bảng 'warehouses': 
       - Cột: warehouse_id (PK), location (Unique index).
    
    LƯU Ý QUAN TRỌNG:
    - Để lấy tên sản phẩm và số lượng, hãy JOIN 'products' và 'inventory' qua 'product_id'.
    - Sử dụng 'ILIKE' cho tìm kiếm văn bản để không phân biệt hoa thường.
    """


    # 2. Khởi tạo LLM
    llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0, api_key=os.getenv("GROQ_API_KEY"))

    # 3. Prompt để sinh SQL
    system_prompt = f"""
    Bạn là một chuyên gia SQL cho hệ thống WMS. 
    Dựa trên Schema sau: {schema_context}
    
    NHIỆM VỤ: 
    - Chuyển câu hỏi của người dùng thành câu lệnh PostgreSQL chuẩn.
    - CHỈ TRẢ VỀ CÂU LỆNH SQL, không giải thích gì thêm.
    - Nếu câu hỏi không liên quan đến dữ liệu, hãy trả về 'NONE'.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}")
    ])

    # 4. Sinh lệnh SQL
    chain = prompt | llm
    sql_query = chain.invoke({"question": question}).content.strip()

    if "SELECT" not in sql_query.upper():
        print(f"🤖 AI: {sql_query}")
        return

    print(f"⚙️ SQL Generated: {sql_query}")

    # 5. Thực thi và trả kết quả
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql_query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        print(f"📊 KẾT QUẢ: {rows}")
    except Exception as e:
        print(f"❌ Lỗi thực thi SQL: {e}")

if __name__ == "__main__":
    q = input("Hỏi về dữ liệu kho (VD: Sản phẩm đắt nhất là gì?): ")
    ask_warehouse_data(q)