# app.py
import streamlit as st
from agent import Mem0Agent
from graph_viz import Neo4jGraphViz
import os

st.set_page_config(page_title="Mem0Graph", layout="wide", page_icon="🕸️")

st.title("Mem0Graph: Визуализация графа знаний")
st.caption("Neo4j + Mem0 + ChromaDB — нативные связи в графе")

# === Инициализация сессии ===
if 'agent' not in st.session_state:
    st.session_state.agent = Mem0Agent(user_id="user_1")
if 'graph_viz' not in st.session_state:
    st.session_state.graph_viz = Neo4jGraphViz()
if 'messages' not in st.session_state:
    st.session_state.messages = []

# === Боковая панель: Чат ===
with st.sidebar:
    st.header("💬 Диалог с агентом")
    
    user_input = st.chat_input("Расскажите факт о себе...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Сохраняю в граф памяти..."):
                answer = st.session_state.agent.chat(user_input)
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
    
    st.divider()
    
    with st.expander("Последние сообщения"):
        for msg in st.session_state.messages[-4:]:
            st.text(f"{msg['role']}: {msg['content'][:50]}...")
    
    st.info("""
    💡 **Попробуйте сказать:**
    - "Меня зовут Алексей"
    - "Я работаю разработчиком"
    - "Люблю Python и графы"
    - "Живу в Москве"
    """)

# === Основная область: Граф знаний ===
st.header("Карта знаний")

col_graph, col_stats = st.columns([3, 1])

with col_graph:
    if st.button("Обновить граф", type="primary", use_container_width=True):
        with st.spinner("🔍 Запрашиваю граф из Neo4j..."):
            try:
                filename = st.session_state.graph_viz.save_graph(
                    user_id="user_1", 
                    filename="knowledge_graph.html"
                )
                
                if filename and os.path.exists(filename):
                    with open(filename, "r", encoding="utf-8") as f:
                        st.components.v1.html(f.read(), height=650)
                    st.success("✅ Граф обновлён!")
                else:
                    st.warning("📭 Граф пуст. Начните диалог, чтобы создать воспоминания!")
                    
            except Exception as e:
                st.error(f"Ошибка: {e}")
                with st.expander("🔧 Детали ошибки"):
                    st.code(str(e))

with col_stats:
    memories = st.session_state.agent.get_all_memories()
    count = len(memories) if memories else 0
    
    st.metric("Воспоминаний", count)
    
    # Статус подключения к Neo4j
    try:
        is_connected = st.session_state.graph_viz.test_connection()
        if is_connected:
            st.metric("🔗 Neo4j", "🟢 Подключено")
        else:
            st.metric("🔗 Neo4j", "🔴 Ошибка")
    except Exception as e:
        st.metric("🔗 Neo4j", "🔴 Ошибка")
    
    st.divider()
    
    # Кнопка очистки памяти
    if st.button("🗑️ Очистить память", type="secondary", use_container_width=True):
        with st.spinner("Очищаю базу знаний..."):
            try:
                st.session_state.agent.clear_memory()
                st.session_state.messages = []  # Очищаем историю чата
                st.success("✅ Память полностью очищена!")
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка при очистке: {e}")

    st.markdown("### Как это работает")
    st.markdown("""
    1. Вы пишете факт
    2. Mem0 извлекает **сущности** и **связи**
    3. Данные пишутся в **Neo4j** как узлы и рёбра
    4. Визуализатор читает **нативный граф**
    """)

# === Нижняя панель: отладка ===
with st.expander("🗄️ Сырые данные из Mem0"):
    memories = st.session_state.agent.get_all_memories()
    if memories:
        # Преобразуем в список если нужно
        if isinstance(memories, dict):
            memories_list = list(memories.values())[:10]
        elif hasattr(memories, '__iter__') and not isinstance(memories, str):
            memories_list = list(memories)[:10]
        else:
            memories_list = [memories]
        
        st.json(memories_list)
    else:
        st.text("Нет данных")

# === Футер ===
st.markdown("---")
st.caption(" **Mem0Graph** | Графовая визуализация памяти | Neo4j + Mem0 + ChromaDB")