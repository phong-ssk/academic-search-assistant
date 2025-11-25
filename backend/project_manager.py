"""
Project Manager for Academic Search
Quản lý các dự án tìm kiếm, lưu kết quả, và history
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import hashlib


class ProjectManager:
    """Quản lý dự án tìm kiếm"""
    
    def __init__(self, base_dir: str = "projects"):
        self.base_dir = base_dir
        self.registry_file = os.path.join(base_dir, "projects_registry.json")
        self._ensure_base_dir()
    
    def _ensure_base_dir(self):
        """Tạo thư mục base nếu chưa có"""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        
        # Create registry nếu chưa có
        if not os.path.exists(self.registry_file):
            self._save_registry({})
    
    def _load_registry(self) -> Dict:
        """Load registry từ file"""
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_registry(self, registry: Dict):
        """Save registry vào file"""
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    
    def create_project(self, project_name: str, user_query: str, 
                      description: str = "") -> str:
        """
        Tạo project mới
        
        Returns:
            project_id: ID của project
        """
        # Generate project ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_part = hashlib.md5(user_query.encode()).hexdigest()[:8]
        project_id = f"{timestamp}_{hash_part}"
        
        # Create project folder
        project_dir = os.path.join(self.base_dir, project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        # Create subfolders
        os.makedirs(os.path.join(project_dir, "results"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "history"), exist_ok=True)
        
        # Project metadata
        metadata = {
            "project_id": project_id,
            "project_name": project_name,
            "user_query": user_query,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "search_count": 0,
            "total_articles": 0
        }
        
        # Save metadata
        metadata_file = os.path.join(project_dir, "metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Update registry
        registry = self._load_registry()
        registry[project_id] = {
            "project_name": project_name,
            "created_at": metadata["created_at"],
            "user_query": user_query,
            "path": project_dir
        }
        self._save_registry(registry)
        
        # Create history file
        self._add_history(project_id, "Project created", {
            "query": user_query,
            "description": description
        })
        
        return project_id
    
    def save_search_results(self, project_id: str, search_results: Dict, 
                           selected_articles: List[Dict] = None):
        """
        Lưu kết quả tìm kiếm vào project
        
        Args:
            project_id: ID của project
            search_results: Kết quả từ LangGraph
            selected_articles: Danh sách articles đã chọn (nếu None thì lưu tất cả)
        """
        project_dir = os.path.join(self.base_dir, project_id)
        
        if not os.path.exists(project_dir):
            raise ValueError(f"Project {project_id} không tồn tại")
        
        # Determine articles to save
        articles = selected_articles if selected_articles is not None else search_results.get('final_results', [])
        
        # Generate search ID
        search_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        search_id = f"search_{search_timestamp}"
        
        # Save results
        results_file = os.path.join(project_dir, "results", f"{search_id}.json")
        
        save_data = {
            "search_id": search_id,
            "timestamp": datetime.now().isoformat(),
            "user_query": search_results.get('user_query', ''),
            "quality_score": search_results.get('quality_score', 0.0),
            "refinement_count": search_results.get('refinement_count', 0),
            "metadata": search_results.get('metadata', {}),
            "total_found": len(search_results.get('final_results', [])),
            "saved_count": len(articles),
            "articles": articles
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        # Update metadata
        metadata_file = os.path.join(project_dir, "metadata.json")
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        metadata['search_count'] += 1
        metadata['total_articles'] += len(articles)
        metadata['updated_at'] = datetime.now().isoformat()
        metadata['last_search_id'] = search_id
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Add history
        self._add_history(project_id, "Search results saved", {
            "search_id": search_id,
            "articles_count": len(articles),
            "quality_score": search_results.get('quality_score', 0.0)
        })
        
        return search_id
    
    def _add_history(self, project_id: str, action: str, details: Dict):
        """Thêm entry vào history"""
        project_dir = os.path.join(self.base_dir, project_id)
        history_file = os.path.join(project_dir, "history", "history.jsonl")
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        
        # Append to JSONL file
        with open(history_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def get_project_history(self, project_id: str) -> List[Dict]:
        """Lấy history của project"""
        project_dir = os.path.join(self.base_dir, project_id)
        history_file = os.path.join(project_dir, "history", "history.jsonl")
        
        if not os.path.exists(history_file):
            return []
        
        history = []
        with open(history_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    history.append(json.loads(line))
        
        return history
    
    def get_all_projects(self) -> List[Dict]:
        """Lấy danh sách tất cả projects"""
        registry = self._load_registry()
        
        projects = []
        for project_id, info in registry.items():
            # Load metadata
            metadata_file = os.path.join(info['path'], "metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                projects.append(metadata)
        
        # Sort by updated_at descending
        projects.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return projects
    
    def get_project_metadata(self, project_id: str) -> Optional[Dict]:
        """Lấy metadata của project"""
        project_dir = os.path.join(self.base_dir, project_id)
        metadata_file = os.path.join(project_dir, "metadata.json")
        
        if not os.path.exists(metadata_file):
            return None
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_project_searches(self, project_id: str) -> List[Dict]:
        """Lấy tất cả searches của project"""
        project_dir = os.path.join(self.base_dir, project_id)
        results_dir = os.path.join(project_dir, "results")
        
        if not os.path.exists(results_dir):
            return []
        
        searches = []
        for filename in os.listdir(results_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(results_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    search_data = json.load(f)
                    searches.append({
                        'search_id': search_data.get('search_id'),
                        'timestamp': search_data.get('timestamp'),
                        'query': search_data.get('user_query'),
                        'saved_count': search_data.get('saved_count'),
                        'quality_score': search_data.get('quality_score')
                    })
        
        # Sort by timestamp descending
        searches.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return searches
    
    def load_search_results(self, project_id: str, search_id: str) -> Optional[Dict]:
        """Load kết quả của 1 search cụ thể"""
        project_dir = os.path.join(self.base_dir, project_id)
        results_file = os.path.join(project_dir, "results", f"{search_id}.json")
        
        if not os.path.exists(results_file):
            return None
        
        with open(results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def delete_project(self, project_id: str):
        """Xóa project"""
        import shutil
        
        project_dir = os.path.join(self.base_dir, project_id)
        
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        
        # Remove from registry
        registry = self._load_registry()
        if project_id in registry:
            del registry[project_id]
            self._save_registry(registry)
    
    def export_project_summary(self, project_id: str) -> str:
        """Export tóm tắt project dạng markdown"""
        metadata = self.get_project_metadata(project_id)
        if not metadata:
            return "Project not found"
        
        history = self.get_project_history(project_id)
        searches = self.get_project_searches(project_id)
        
        md = f"""# 📊 Project: {metadata['project_name']}

## 📝 Thông tin cơ bản

- **Project ID:** `{metadata['project_id']}`
- **Query:** {metadata['user_query']}
- **Description:** {metadata.get('description', 'N/A')}
- **Created:** {metadata['created_at']}
- **Last Updated:** {metadata['updated_at']}

## 📈 Thống kê

- **Số lần tìm kiếm:** {metadata['search_count']}
- **Tổng bài báo đã lưu:** {metadata['total_articles']}

## 🔍 Lịch sử tìm kiếm

"""
        
        for search in searches:
            md += f"""### {search['search_id']}
- **Time:** {search['timestamp']}
- **Query:** {search['query']}
- **Articles saved:** {search['saved_count']}
- **Quality:** {search['quality_score']:.2f}

"""
        
        md += f"""## 📜 Activity History

Total activities: {len(history)}

"""
        
        for entry in history[-10:]:  # Last 10 activities
            md += f"- **{entry['timestamp']}** - {entry['action']}\n"
        
        return md
