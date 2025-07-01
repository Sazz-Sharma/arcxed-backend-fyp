"""
HTTP client for communicating with the AI/ML service
"""

import httpx
import json
from typing import Dict, List, Any, Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AIServiceClient:
    """Client for communicating with the separated AI/ML FastAPI service"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip('/')
        self.timeout = 300.0  # 5 minutes timeout for AI operations
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make HTTP request to AI service"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "POST":
                    response = await client.post(url, json=data)
                elif method.upper() == "GET":
                    response = await client.get(url, params=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logger.error(f"Timeout when calling AI service: {url}")
            raise Exception("AI service request timed out")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from AI service: {e.response.status_code} - {e.response.text}")
            raise Exception(f"AI service error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error calling AI service: {str(e)}")
            raise Exception(f"Failed to communicate with AI service: {str(e)}")
    
    async def generate_questions(self, current_level: List[Dict], syllabus: Optional[List[Dict]] = None) -> Dict:
        """Generate questions using AI service"""
        data = {
            "current_level": current_level,
            "syllabus": syllabus
        }
        
        return await self._make_request("POST", "/api/v1/agents/generate-questions", data)
    
    async def explain_answer(self, question: str, options: List[str], correct_answer: str, user_answer: Optional[str] = None) -> Dict:
        """Get answer explanation from AI service"""
        data = {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "user_answer": user_answer
        }
        
        return await self._make_request("POST", "/api/v1/agents/explain-answer", data)
    
    async def evaluate_user(self, evaluation_type: str, performance_data: List[Dict]) -> Dict:
        """Evaluate user performance using AI service"""
        data = {
            "evaluation_type": evaluation_type,
            "performance_data": performance_data
        }
        
        return await self._make_request("POST", "/api/v1/agents/evaluate-user", data)
    
    async def make_study_plan(self, current_level: List[Dict], target_exam: Optional[str] = None, available_time: Optional[int] = None) -> Dict:
        """Create study plan using AI service"""
        data = {
            "current_level": current_level,
            "target_exam": target_exam,
            "available_time": available_time
        }
        
        return await self._make_request("POST", "/api/v1/agents/make-study-plan", data)
    
    async def create_embeddings(self, texts: List[str], normalize: bool = True) -> Dict:
        """Create text embeddings using AI service"""
        data = {
            "texts": texts,
            "normalize": normalize
        }
        
        return await self._make_request("POST", "/api/v1/embeddings/embed", data)
    
    async def semantic_search(self, query: str, top_k: int = 5, use_reranking: bool = True) -> Dict:
        """Perform semantic search using AI service"""
        data = {
            "query": query,
            "top_k": top_k,
            "use_reranking": use_reranking
        }
        
        return await self._make_request("POST", "/api/v1/embeddings/search", data)
    
    async def health_check(self) -> Dict:
        """Check if AI service is healthy"""
        return await self._make_request("GET", "/health")

# Global client instance
ai_client = AIServiceClient()
