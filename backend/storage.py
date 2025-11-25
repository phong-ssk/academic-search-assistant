"""
Storage service để lưu và quản lý kết quả tìm kiếm
"""
import json
import os
from datetime import datetime
from typing import List, Dict

class StorageService:
    """Class xử lý lưu trữ kết quả"""

    def __init__(self, output_folder: str = "results"):
        self.output_folder = output_folder
        self._ensure_folder_exists()

    def _ensure_folder_exists(self):
        """Đảm bảo folder output tồn tại"""
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def save_results(self, articles: List[Dict], query: str, source: str = "PubMed") -> str:
        """
        Lưu kết quả tìm kiếm vào file JSON

        Args:
            articles: Danh sách bài báo
            query: Query tìm kiếm
            source: Nguồn tìm kiếm (PubMed, Scopus, etc.)

        Returns:
            Đường dẫn file đã lưu
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_folder}/{source.lower()}_{timestamp}.json"

        data = {
            "query": query,
            "source": source,
            "timestamp": timestamp,
            "total_results": len(articles),
            "articles": articles
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filename

    def load_results(self, filename: str) -> Dict:
        """
        Đọc kết quả từ file JSON

        Args:
            filename: Đường dẫn file

        Returns:
            Dictionary chứa kết quả
        """
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_saved_results(self) -> List[str]:
        """
        Liệt kê tất cả file kết quả đã lưu

        Returns:
            Danh sách đường dẫn file
        """
        if not os.path.exists(self.output_folder):
            return []

        files = [
            os.path.join(self.output_folder, f)
            for f in os.listdir(self.output_folder)
            if f.endswith('.json')
        ]
        return sorted(files, reverse=True)
