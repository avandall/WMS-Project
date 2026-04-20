#!/usr/bin/env python3
"""
Câu hỏi test AI WMS dựa trên data từ seed.py
"""

# Dựa trên data seed.py, đây là các câu hỏi test AI WMS:

TEST_QUESTIONS = {
    "inventory_queries": [
        # Basic inventory queries
        "Tồn kho hiện tại của sản phẩm 'Máy hàn thiếc Quick 936A' là bao nhiêu?",
        "Sản phẩm 'Đồng hồ vạn năng Fluke' còn bao nhiêu trong kho?",
        "Kiểm tra tồn kho cho mã 'Keo dán gỗ chuyên dụng'",
        
        # Stock level analysis
        "Những sản phẩm nào đang có tồn kho dưới 100 đơn vị?",
        "Danh sách các sản phẩm có quantity <= safety stock",
        "Sản phẩm nào cần nhập hàng gấp (quantity <= reorder_point)?",
        
        # Location-based queries
        "Sản phẩm 'Máy bào gỗ Makita' đang được lưu ở kho nào?",
        "Kiểm tra tồn kho tại 'Kho Miền Bắc'",
        "Tất cả các sản phẩm trong 'Kho Miền Trung'",
    ],
    
    "transaction_analysis": [
        # Transaction history
        "Lịch sử biến đổi tồn kho của sản phẩm 'Máy mài cầm tay Bosch' trong 7 ngày qua",
        "Ai đã thực hiện điều chỉnh tồn kho cho 'Kính hiển vi soi mạch' hôm nay?",
        "Thống kê các giao dịch của user 'banhang@wms.com' trong tháng này",
        
        # Movement tracking
        "Lịch di chuyển hàng giữa các kho trong tuần qua",
        "Sản phẩm 'Bo mạch chủ Asus H510' đã được di chuyển đi đâu?",
        "Tất cả các di chuyển hàng của user 'thukho@wms.com'",
    ],
    
    "warehouse_operations": [
        # Location management
        "Kiểm tra xem 'Kho Miền Bắc' còn trống không?",
        "Vị trí 'Zone A-01-01' trong 'Kho Miền Nam' có bao nhiêu sản phẩm?",
        "Dung tích kho 'Kho Miền Tây' đã sử dụng bao nhiêu %?",
        
        # Stock movements
        "Chuyển 50 đơn vị 'Máy hàn thiếc Quick 936A' từ 'Kho Miền Bắc' sang 'Kho Miền Trung'",
        "Kiểm tra xem có thể chuyển 'Cuộn vải thun Cotton' vào 'Zone B-02-03' không?",
        
        # Low stock alerts
        "Báo cáo các sản phẩm sắp hết hàng trong toàn bộ hệ thống",
        "Những mặt hàng nào đang dưới mức safety stock tại 'Kho Miền Trung'?",
    ],
    
    "abc_analysis": [
        # ABC classification
        "Phân tích ABC cho toàn bộ kho hàng",
        "Sản phẩm nào thuộc nhóm A (high frequency)?",
        "Giá trị tồn kho theo từng nhóm ABC",
        
        # Slotting optimization
        "Tối ưu vị trí lưu trữ cho sản phẩm nhóm A",
        "Đề xuất vị trí lý tưởng cho 'Thước kẹp điện tử Mitutoyo'",
        "Phân tích lại vị trí lưu trữ hiện tại có tối ưu chưa?",
    ],
    
    "user_management": [
        # User activity
        "Thống kê hoạt động của user 'ketoan@wms.com' trong 30 ngày qua",
        "Ai là người tích cực nhất trong hệ thống?",
        "Kiểm tra quyền truy cập của user 'khach@wms.com'",
        
        # Role-based queries
        "User 'admin@wms.com' có thể làm gì trong hệ thống?",
        "Phân công giữa các role trong WMS",
    ],
    
    "document_management": [
        # Document tracking
        "Tìm chứng từ IMPORT sản phẩm 'Điện tử' ngày 15/04/2025",
        "Lịch xuất hàng trong tuần qua",
        "Kiểm tra trạng thái chứng từ 'EXPORT-2025-001'",
        
        # Document analysis
        "Tổng giá trị các chứng từ IMPORT trong tháng",
        "Sản phẩm nào xuất khẩu nhiều nhất?",
        "Đối tác thương mại chính trong các chứng từ",
    ],
    
    "advanced_scenarios": [
        # Complex multi-step scenarios
        "Tạo báo cáo tồn kho tổng hợp cho tất cả các kho",
        "Phân tích hiệu suất sử dụng kho (turnover rate)",
        "Dự báo nhu cầu nhập hàng dựa trên lịch sử dụng 3 tháng qua",
        
        # Integration queries
        "Kết nối dữ liệu tồn kho với thông tin khách hàng",
        "Tìm các sản phẩm bán chạy nhất kết hợp với data khách hàng",
        "Phân tích xu hướng nhập xuất hàng theo ngành hàng",
    ],
    
    "alert_management": [
        # System alerts
        "Tạo cảnh báo cho các sản phẩm hết hàng",
        "Kiểm tra các cảnh báo chưa xử lý",
        "Thống kê loại cảnh báo theo mức độ ưu tiên",
        
        # Alert responses
        "Xử lý cảnh báo tồn kho thấp cho ngành 'Điện tử'",
        "Tự động tạo cảnh báo khi quantity <= safety stock",
    ]
}

# Các câu hỏi test theo cấp độ khó:
EASY_QUESTIONS = [
    "Tồn kho của 'Máy hàn thiếc Quick 936A'?",
    "Có bao nhiêu sản phẩm trong 'Kho Miền Bắc'?",
    "Ai đã điều chỉnh tồn kho hôm nay?",
]

MEDIUM_QUESTIONS = [
    "Những sản phẩm nào cần nhập hàng gấp?",
    "Lịch sử biến đổi tồn kho 7 ngày qua",
    "Chuyển hàng từ 'Kho Miền Bắc' sang 'Kho Miền Trung'",
    "Phân tích ABC cho ngành hàng 'Điện tử'",
]

HARD_QUESTIONS = [
    "Tạo báo cáo tồn kho tổng hợp tất cả các kho",
    "Phân tích hiệu suất sử dụng kho kết hợp customer data",
    "Dự báo nhu cầu nhập hàng dựa trên trend 3 tháng qua",
    "Tối ưu vị trí lưu trữ cho sản phẩm nhóm A kết hợp constraint analysis",
]

def get_test_questions(difficulty="all"):
    """Lấy câu hỏi test theo độ khó"""
    if difficulty == "easy":
        return EASY_QUESTIONS
    elif difficulty == "medium":
        return MEDIUM_QUESTIONS  
    elif difficulty == "hard":
        return HARD_QUESTIONS
    else:  # all
        all_questions = []
        for category in TEST_QUESTIONS.values():
            all_questions.extend(category)
        return all_questions

def get_questions_by_category(category):
    """Lấy câu hỏi theo danh mục"""
    return TEST_QUESTIONS.get(category, [])

if __name__ == "__main__":
    print("📋 Câu hỏi test AI WMS (dựa trên data seed.py)")
    print("=" * 60)
    
    print("\n🎯 CÁCH SỬ DỤNG:")
    print("1. Copy câu hỏi vào dashboard AI")
    print("2. Chọn độ khó: easy/medium/hard") 
    print("3. Kiểm tra response của AI có:")
    print("   - Chính xác về data")
    print("   - Sử dụng đúng tools")
    print("   - Format response rõ ràng")
    print("4. Kiểm tra performance và accuracy")
    
    print(f"\n📊 TỔNG QUAN: {len(get_test_questions('all'))} câu hỏi")
    print(f"   - Easy: {len(EASY_QUESTIONS)} câu")
    print(f"   - Medium: {len(MEDIUM_QUESTIONS)} câu") 
    print(f"   - Hard: {len(HARD_QUESTIONS)} câu")
    
    print("\n📝 Categories:")
    for category, questions in TEST_QUESTIONS.items():
        print(f"   - {category}: {len(questions)} câu hỏi")
    
    print("\n" + "=" * 60)
    print("✅ Ready để test AI WMS!")
