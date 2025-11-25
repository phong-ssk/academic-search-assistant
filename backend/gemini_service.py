"""
Gemini AI Service
"""
from google import genai
from google.genai import types
from typing import List, Dict, Optional
import json

class GeminiService:
    """Class xử lý Gemini AI"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def optimize_query(self, user_input: str) -> Dict[str, str]:
        """
        Tối ưu hóa câu truy vấn của người dùng
        Trả về JSON: {
            "english_query": "...",
            "vietnamese_query": "...",
            "strategy": "..."
        }
        """
        if not self.client:
            return {"english_query": user_input, "vietnamese_query": user_input, "strategy": "No API Key"}

        prompt = f"""
        Bạn là một chuyên gia tìm kiếm y văn.
        Người dùng muốn tìm kiếm về: "{user_input}"
        
        Hãy giúp tôi:
        1. Tạo một câu truy vấn tiếng Anh tối ưu cho PubMed/Scopus (dùng MeSH terms nếu cần).
        2. Tạo một câu truy vấn tiếng Việt tối ưu cho Semantic Scholar.
        3. Đưa ra chiến lược tìm kiếm ngắn gọn.
        
        Trả về kết quả dưới dạng JSON KHÔNG có markdown formatting:
        {{
            "english_query": "...",
            "vietnamese_query": "...",
            "strategy": "..."
        }}
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash', # Using latest flash model as requested implicitly by "newest lib"
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json'
                )
            )
            
            # With response_mime_type='application/json', the text should be valid JSON
            text = response.text.strip()
            return json.loads(text)
        except Exception as e:
            print(f"Gemini optimize error: {e}")
            # Fallback if JSON parsing fails or other error
            return {"english_query": user_input, "vietnamese_query": user_input, "strategy": "Error optimizing query"}

    def consult_search(self, user_input: str) -> str:
        """
        Tư vấn chiến lược tìm kiếm
        """
        if not self.client:
            return "Vui lòng nhập API Key để nhận tư vấn."

        prompt = f"""
        Người dùng muốn tìm kiếm y văn về: "{user_input}"
        Hãy đóng vai trò là một thủ thư y khoa chuyên nghiệp và tư vấn cho họ:
        1. Các từ khóa (keywords) nên dùng (tiếng Anh và Việt).
        2. Cấu trúc PICO (Population, Intervention, Comparison, Outcome) nếu áp dụng được.
        3. Các toán tử tìm kiếm (AND, OR, NOT) nên phối hợp thế nào.
        4. Gợi ý các nguồn dữ liệu nên tìm.
        
        Trả lời ngắn gọn, súc tích, dùng định dạng Markdown.
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Lỗi khi gọi Gemini: {str(e)}"

