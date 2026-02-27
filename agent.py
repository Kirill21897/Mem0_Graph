# agent.py
from mem0 import Memory
from config import MEM0_CONFIG
import openai
import os
from dotenv import load_dotenv

load_dotenv()


class Mem0Agent:
    def __init__(self, user_id="user_1"):
        self.user_id = user_id
        # Mem0 подхватит OPENAI_BASE_URL и OPENROUTER_API_KEY из среды
        self.memory = Memory.from_config(MEM0_CONFIG)
        
        # Клиент для чата (явно указываем для надежности)
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        )

    def chat(self, message):
        """Диалог с агентом"""
        relevant = self.memory.search(message, user_id=self.user_id)
        
        # Handle dict response when graph store is enabled
        if isinstance(relevant, dict):
            relevant = relevant.get("results", [])
            
        context = "\n".join([m['memory'] for m in relevant]) if relevant else ""
        
        response = self.client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Ты умный ассистент. Контекст: {context}"},
                {"role": "user", "content": message}
            ]
        )
        answer = response.choices[0].message.content
        
        self.memory.add(message, user_id=self.user_id)
        self.memory.add(answer, user_id=self.user_id)
        
        return answer

    def get_all_memories(self):
        memories = self.memory.get_all(user_id=self.user_id)
        if isinstance(memories, dict):
            return memories.get("results", [])
        return memories

    def clear_memory(self):
        """Очистка всей памяти пользователя"""
        self.memory.delete_all(user_id=self.user_id)