import httpx
import asyncio
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.timeout = 30.0
        
    async def explain_answer(self, question: str, options: List[str], correct_answer: str, user_answer: Optional[str] = None) -> Dict[str, Any]:
        """
        Call AI service to explain an answer
        """
        url = f"{self.base_url}/api/v1/agents/explain-answer"
        payload = {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "user_answer": user_answer
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Calling AI service: {url}")
                logger.info(f"Payload: {payload}")
                
                response = await client.post(url, json=payload)
                
                logger.info(f"AI service response status: {response.status_code}")
                logger.info(f"AI service response: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    return result
                else:
                    logger.error(f"AI service error: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"AI service error: {response.status_code}",
                        "details": response.text
                    }
                    
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to AI service: {e}")
            return {
                "success": False,
                "error": "Failed to connect to AI service. Please ensure the AI service is running on http://localhost:8001"
            }
        except httpx.TimeoutException as e:
            logger.error(f"AI service request timed out: {e}")
            return {
                "success": False,
                "error": "AI service request timed out"
            }
        except Exception as e:
            logger.error(f"Unexpected error calling AI service: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    async def generate_questions(self, current_level: List[Dict], syllabus: List[Dict]) -> Dict[str, Any]:
        """Call AI service to generate questions"""
        url = f"{self.base_url}/api/v1/agents/generate-questions"
        payload = {
            "current_level": current_level,
            "syllabus": syllabus
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "success": False,
                        "error": f"AI service error: {response.status_code}",
                        "details": response.text
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"AI service error: {str(e)}"
            }

    async def make_study_plan(self, current_level: List[Dict], target_exam: Optional[str] = None, available_time: Optional[int] = None) -> Dict[str, Any]:
        """Call AI service to create study plan"""
        url = f"{self.base_url}/api/v1/agents/create-study-plan"
        payload = {
            "current_level": current_level,
            "target_exam": target_exam,
            "available_time": available_time
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "success": False,
                        "error": f"AI service error: {response.status_code}",
                        "details": response.text
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"AI service error: {str(e)}"
            }

    async def evaluate_user(self, evaluation_type: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call AI service to evaluate user performance"""
        url = f"{self.base_url}/api/v1/agents/evaluate-user"
        payload = {
            "evaluation_type": evaluation_type,
            "performance_data": performance_data
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "success": False,
                        "error": f"AI service error: {response.status_code}",
                        "details": response.text
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"AI service error: {str(e)}"
            }

    async def semantic_search(self, query: str, top_k: int = 5, use_reranking: bool = True) -> Dict[str, Any]:
        """Call AI service for semantic search"""
        url = f"{self.base_url}/api/v1/embeddings/search"
        payload = {
            "query": query,
            "top_k": top_k,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "success": False,
                        "error": f"AI service error: {response.status_code}",
                        "details": response.text
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"AI service error: {str(e)}"
            }

# Create global instance
ai_client = AIClient()