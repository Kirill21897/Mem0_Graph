# app.py
import streamlit as st
from mem0_graph.agent import Mem0Agent
from mem0_graph.graph_viz import Neo4jGraphViz
import os
import PyPDF2
from io import StringIO

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

# === Функции ===
def process_uploaded_file(uploaded_file):
    """Обработка загруженного файла"""
    try:
        text = ""
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif uploaded_file.type == "text/plain":
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            text = stringio.read()
        
        if text:
            with st.spinner("Добавляю содержимое документа в память..."):
                st.session_state.agent.add_memory(text, metadata={"source": uploaded_file.name})
            st.success(f"✅ Файл '{uploaded_file.name}' успешно обработан!")
        else:
            st.warning("Файл пуст или не удалось извлечь текст.")
            
    except Exception as e:
        st.error(f"Ошибка при обработке файла: {e}")

# === Боковая панель ===
with st.sidebar:
    st.header("⚙️ Управление")
    
    # Загрузка документов
    st.subheader("📂 Загрузка документов")
    uploaded_file = st.file_uploader("Загрузить файл (TXT, PDF)", type=["txt", "pdf"])
    if uploaded_file is not None:
        if st.button("Обработать файл"):
            process_uploaded_file(uploaded_file)
            
    st.divider()
    
    # Статистика
    st.subheader("📊 Статистика")
    memories = st.session_state.agent.get_all_memories()
    count = len(memories) if memories else 0
    st.metric("Воспоминаний", count)
    
    # Статус подключения
    try:
        is_connected = st.session_state.graph_viz.test_connection()
        status_color = "🟢" if is_connected else "🔴"
        st.metric("Neo4j", f"{status_color} {'Подключено' if is_connected else 'Ошибка'}")
    except:
        st.metric("Neo4j", "🔴 Ошибка")
        
    st.divider()
    
    # Очистка
    if st.button("🗑️ Очистить память", type="secondary", use_container_width=True):
        st.session_state.show_confirm = True

    if st.session_state.get('show_confirm', False):
        st.warning("Вы уверены? Это действие необратимо.")
        if st.button("Да, удалить всё", type="primary"):
            st.session_state.agent.clear_memory()
            st.session_state.messages = []
            st.session_state.show_confirm = False
            st.success("Память очищена!")
            st.rerun()
        if st.button("Отмена"):
            st.session_state.show_confirm = False
            st.rerun()

# === Основная область: Вкладки ===
tab_chat, tab_graph = st.tabs(["💬 Чат с агентом", "🕸️ Граф знаний"])

# --- Вкладка 1: Чат ---
with tab_chat:
    st.header("Диалог")
    
    # Вывод истории сообщений
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # Ввод нового сообщения
    if prompt := st.chat_input("Напишите сообщение..."):
        # Добавляем сообщение пользователя
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
            
        # Получаем ответ агента
        with st.chat_message("assistant"):
            with st.spinner("Думаю и обновляю граф..."):
                response = st.session_state.agent.chat(prompt)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# --- Вкладка 2: Граф ---
with tab_graph:
    col_ctrl, col_view = st.columns([1, 4])
    
    with col_ctrl:
        st.subheader("Управление графом")
        if st.button("🔄 Обновить граф", type="primary", use_container_width=True):
            st.session_state.graph_updated = True
            
        st.info("""
        **Легенда:**
        - 🔵 **User**: Пользователь
        - 🟠 **Entity**: Сущности
        - 🟢 **Memory**: Воспоминания
        """)
            
    with col_view:
        if st.session_state.get('graph_updated', False) or st.button("Показать граф"):
            with st.spinner("Строю граф..."):
                try:
                    filename = st.session_state.graph_viz.save_graph(
                        user_id="user_1", 
                        filename="knowledge_graph.html"
                    )
                    
                    if filename and os.path.exists(filename):
                        with open(filename, "r", encoding="utf-8") as f:
                            st.components.v1.html(f.read(), height=700)
                    else:
                        st.warning("Граф пока пуст.")
                except Exception as e:
                    st.error(f"Ошибка визуализации: {e}")
            st.session_state.graph_updated = False

# === Нижняя панель: отладка ===
with st.expander("🗄️ Сырые данные из Mem0"):
    memories = st.session_state.agent.get_all_memories()
    if memories:
        preview = []
        for m in memories[:10]:
            if isinstance(m, dict):
                preview.append(
                    {
                        "id": m.get("id"),
                        "text": m.get("memory"),
                        "score": m.get("score"),
                        "metadata": m.get("metadata"),
                    }
                )
            else:
                preview.append({"text": str(m)})

        st.json(preview)
    else:
        st.text("Нет данных")

# === Футер ===
st.markdown("---")
st.caption(" **Mem0Graph** | Графовая визуализация памяти | Neo4j + Mem0 + ChromaDB")