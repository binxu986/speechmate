import uuid
import hashlib
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class KeyManager:
    def __init__(self, config: Dict):
        self.config = config
        self.keys = config.get("api_keys", [])
        
    def generate_key(self, name: str = "default") -> str:
        key = f"sk-{uuid.uuid4().hex}{uuid.uuid4().hex[:8]}"
        key_info = {
            "key": key,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "usage": {
                "daily": {},
                "weekly": {},
                "monthly": {}
            }
        }
        self.keys.append(key_info)
        self._save()
        return key
    
    def validate_key(self, key: str) -> bool:
        if not key:
            return False
        return any(k.get("key") == key for k in self.keys)
    
    def delete_key(self, key: str) -> bool:
        self.keys = [k for k in self.keys if k.get("key") != key]
        self._save()
        return True
    
    def get_all_keys(self) -> List[Dict]:
        return [
            {
                "key": k.get("key", ""),
                "name": k.get("name", ""),
                "created_at": k.get("created_at", "")
            }
            for k in self.keys
        ]
    
    def record_usage(self, key: str, endpoint: str):
        today = datetime.now().strftime("%Y-%m-%d")
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%W")
        month = datetime.now().strftime("%Y-%m")
        
        for k in self.keys:
            if k.get("key") == key:
                usage = k.get("usage", {})
                
                daily = usage.get("daily", {})
                daily[endpoint] = daily.get(endpoint, 0) + 1
                usage["daily"] = daily
                
                weekly = usage.get("weekly", {})
                weekly[endpoint] = weekly.get(endpoint, 0) + 1
                usage["weekly"] = weekly
                
                monthly = usage.get("monthly", {})
                monthly[endpoint] = monthly.get(endpoint, 0) + 1
                usage["monthly"] = monthly
                
                k["usage"] = usage
                self._save()
                break
    
    def get_stats(self, key: Optional[str] = None) -> Dict:
        if key:
            for k in self.keys:
                if k.get("key") == key:
                    return k.get("usage", {})
            return {}
        
        total = {
            "daily": {},
            "weekly": {},
            "monthly": {}
        }
        
        for k in self.keys:
            usage = k.get("usage", {})
            for period in total:
                period_data = usage.get(period, {})
                for endpoint, count in period_data.items():
                    total[period][endpoint] = total[period].get(endpoint, 0) + count
        
        return total
    
    def get_total_calls(self, period: str = "daily") -> int:
        stats = self.get_stats()
        return sum(stats.get(period, {}).values())
    
    def _save(self):
        self.config["api_keys"] = self.keys
        from ..config import save_config
        save_config(self.config)
