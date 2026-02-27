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

    def _normalize_results(self, result):
        """Приводит ответы Mem0 (list/dict) к единому формату."""
        if not result:
            return []

        if isinstance(result, dict):
            items = result.get("results") or result.get("data") or []
        else:
            items = result

        normalized = []
        for item in items:
            if isinstance(item, dict):
                memory_text = (
                    item.get("memory")
                    or item.get("text")
                    or item.get("content")
                    or item.get("value")
                )
                score = item.get("score")
                metadata = item.get("metadata") or item.get("meta")
                mem_id = item.get("id") or item.get("_id")
            else:
                memory_text = str(item)
                score = None
                metadata = None
                mem_id = None

            normalized.append(
                {
                    "id": mem_id,
                    "memory": memory_text,
                    "score": score,
                    "metadata": metadata,
                    "raw": item,
                }
            )

        return normalized

    def _chunk_text(self, text, max_chunk_size=2000):
        """Грубое разбиение длинного текста на части для более удобной индексации."""
        if not text:
            return []

        paragraphs = text.split("\n\n")
        chunks = []
        current = ""

        for paragraph in paragraphs:
            p = paragraph.strip()
            if not p:
                continue

            # если текущий чанк ещё помещается — добавляем
            if current and len(current) + len(p) + 2 <= max_chunk_size:
                current = f"{current}\n\n{p}"
            elif not current and len(p) <= max_chunk_size:
                current = p
            else:
                # сохраняем текущий и начинаем новый / дробим слишком длинный абзац
                if current:
                    chunks.append(current)
                    current = ""

                if len(p) <= max_chunk_size:
                    current = p
                else:
                    # очень длинный абзац режем по длине
                    for i in range(0, len(p), max_chunk_size):
                        chunks.append(p[i : i + max_chunk_size])

        if current:
            chunks.append(current)

        return chunks

    def chat(self, message):
        """Диалог с агентом"""
        try:
            raw_relevant = self.memory.search(message, user_id=self.user_id)
            relevant = self._normalize_results(raw_relevant)
        except Exception as e:
            print(f"[Mem0Agent.chat] search error: {e}")
            relevant = []

        context_parts = []
        for m in relevant:
            text = m.get("memory")
            if not text:
                continue
            meta = m.get("metadata") or {}
            source = meta.get("source")
            prefix = f"[source: {source}] " if source else ""
            context_parts.append(f"- {prefix}{text}")

        # ограничиваем количество воспоминаний в контексте
        context = "\n".join(context_parts[:10])

        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты умный ассистент. "
                            "Используй контекст воспоминаний пользователя, если он релевантен.\n\n"
                            f"Контекст:\n{context}"
                        ),
                    },
                    {"role": "user", "content": message},
                ],
            )
            answer = response.choices[0].message.content
        except Exception as e:
            print(f"[Mem0Agent.chat] llm error: {e}")
            return f"Произошла ошибка при обращении к модели: {e}"

        # сохраняем диалог в память
        try:
            self.memory.add(message, user_id=self.user_id)
            self.memory.add(answer, user_id=self.user_id)
        except Exception as e:
            print(f"[Mem0Agent.chat] add error: {e}")

        return answer

    def get_all_memories(self):
        try:
            raw = self.memory.get_all(user_id=self.user_id)
        except Exception as e:
            print(f"[Mem0Agent.get_all_memories] get_all error: {e}")
            return []
        return self._normalize_results(raw)

    def clear_memory(self):
        """Очистка всей памяти пользователя"""
        try:
            self.memory.delete_all(user_id=self.user_id)
        except Exception as e:
            print(f"[Mem0Agent.clear_memory] delete_all error: {e}")

    def add_memory(self, text, metadata=None, max_chunk_size=2000):
        """Добавить воспоминание вручную (например, из документа) с разбиением текста на части."""
        chunks = self._chunk_text(text, max_chunk_size=max_chunk_size)
        results = []
        for chunk in chunks:
            try:
                res = self.memory.add(chunk, user_id=self.user_id, metadata=metadata)
                results.append(res)
            except Exception as e:
                print(f"[Mem0Agent.add_memory] add error: {e}")
        return results