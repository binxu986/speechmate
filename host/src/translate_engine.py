import os
from typing import Dict, Optional
import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer


class TranslationEngine:
    LANG_CODE_MAP = {
        "zh": "zh",
        "en": "en",
        "chinese": "zh",
        "english": "en",
    }
    
    def __init__(self, model_name: str = "m2m100-418M", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        if self.model is None:
            cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "m2m100")
            self.tokenizer = M2M100Tokenizer.from_pretrained(
                self.model_name,
                cache_dir=cache_dir if os.path.exists(cache_dir) else None
            )
            self.model = M2M100ForConditionalGeneration.from_pretrained(
                self.model_name,
                cache_dir=cache_dir if os.path.exists(cache_dir) else None
            )
            self.model = self.model.to(self.device)
            self.model.eval()
        return self.model
    
    def _normalize_lang_code(self, lang: str) -> str:
        lang_lower = lang.lower()
        return self.LANG_CODE_MAP.get(lang_lower, lang_lower)
    
    def translate(self, text: str, src_lang: str = "zh", tgt_lang: str = "en") -> str:
        if not text or not text.strip():
            return ""
        
        model = self.load_model()
        
        src_lang = self._normalize_lang_code(src_lang)
        tgt_lang = self._normalize_lang_code(tgt_lang)
        
        self.tokenizer.src_lang = src_lang
        encoded = self.tokenizer(text, return_tensors="pt").to(self.device)
        
        generated_tokens = model.generate(
            **encoded,
            forced_bos_token_id=self.tokenizer.get_lang_id(tgt_lang),
            max_length=512
        )
        
        result = self.tokenizer.batch_decode(
            generated_tokens, skip_special_tokens=True
        )[0]
        return result
    
    def translate_batch(self, texts: list, src_lang: str = "zh", tgt_lang: str = "en") -> list:
        if not texts:
            return []
        
        model = self.load_model()
        
        src_lang = self._normalize_lang_code(src_lang)
        tgt_lang = self._normalize_lang_code(tgt_lang)
        
        self.tokenizer.src_lang = src_lang
        encoded = self.tokenizer(texts, return_tensors="pt", padding=True).to(self.device)
        
        generated_tokens = model.generate(
            **encoded,
            forced_bos_token_id=self.tokenizer.get_lang_id(tgt_lang),
            max_length=512
        )
        
        results = self.tokenizer.batch_decode(
            generated_tokens, skip_special_tokens=True
        )
        return results
    
    def translate_audio_to_text(self, audio_path: str, src_lang: str = "zh", tgt_lang: str = "en") -> str:
        from .asr_engine import ASREngine
        asr = ASREngine()
        asr_result = asr.transcribe(audio_path, language=src_lang)
        text = asr_result["text"]
        return self.translate(text, src_lang, tgt_lang)
    
    def unload_model(self):
        if self.model:
            del self.model
            self.model = None
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def get_model_info(self) -> Dict:
        return {
            "model_name": self.model_name,
            "device": self.device
        }
