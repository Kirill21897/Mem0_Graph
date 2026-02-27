from neo4j import GraphDatabase
from pyvis.network import Network


class Neo4jGraphViz:
    """Визуализация нативного графа знаний из Neo4j"""
    
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password123"):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Закрыть соединение с базой"""
        if self.driver:
            self.driver.close()

    def get_graph_data(self, user_id="user_1"):
        """
        Запрашивает узлы и связи из Neo4j.
        Mem0 создаёт узлы с лейблами: User, Memory, Entity
        """
        query = """
        MATCH (n)-[r]->(m)
        WHERE n.user_id = $user_id OR m.user_id = $user_id OR 
              n.user_id IS NULL OR m.user_id IS NULL
        RETURN 
            toString(id(n)) as source,
            toString(id(m)) as target,
            type(r) as relation,
            labels(n) as n_labels,
            labels(m) as m_labels,
            n.memory as n_memory,
            m.memory as m_memory,
            n.value as n_value,
            m.value as m_value,
            n.name as n_name,
            m.name as m_name,
            n.text as n_text,
            m.text as m_text,
            n.id as n_id,
            m.id as m_id
        LIMIT 1000
        """
        
        with self.driver.session() as session:
            result = session.run(query, user_id=user_id)
            return [record.data() for record in result]

    def build_pyvis_graph(self, data):
        """Строит интерактивный граф PyVis из данных Neo4j"""
        net = Network(
            height="650px", 
            width="100%", 
            bgcolor="#1a1a2e", 
            font_color="#ffffff",
            select_menu=True, 
            filter_menu=True,
            cdn_resources="remote"
        )
        net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=250)

        nodes = {}
        
        for record in data:
            src = str(record['source'])
            tgt = str(record['target'])
            rel = record['relation'] if record['relation'] else 'related'
            
            # Получаем читаемые подписи
            def get_label(record, prefix):
                return (record.get(f'{prefix}_name') or 
                        record.get(f'{prefix}_memory') or 
                        record.get(f'{prefix}_value') or 
                        record.get(f'{prefix}_text') or 
                        record.get(f'{prefix}_id') or 
                        (record[f'{prefix}_labels'][-1] if record[f'{prefix}_labels'] else 'Node'))

            src_label = get_label(record, 'n')
            tgt_label = get_label(record, 'm')
            
            # Цвета по типу узла
            def get_color(labels):
                if not labels:
                    return "#94a3b8"
                
                # Приводим все метки к нижнему регистру для проверки
                lower_labels = [l.lower() for l in labels]
                
                if 'user' in lower_labels or '__user__' in lower_labels:
                    return "#6366f1"  # Indigo
                elif 'entity' in lower_labels:
                    return "#f97316"  # Orange
                elif 'memory' in lower_labels:
                    return "#22c55e"  # Green
                elif 'person' in lower_labels:
                    return "#e11d48"  # Red
                elif 'location' in lower_labels:
                    return "#0ea5e9"  # Sky
                elif 'organization' in lower_labels:
                    return "#8b5cf6"  # Violet
                else:
                    return "#94a3b8"  # Slate

            
            # Добавляем узлы
            if src not in nodes:
                net.add_node(
                    src, 
                    label=str(src_label)[:35], 
                    title=f"{src_label}\nТип: {record['n_labels']}",
                    color=get_color(record['n_labels']),
                    size=25 if (record['n_labels'] and 'User' in record['n_labels']) else 20
                )
                nodes[src] = True
                
            if tgt not in nodes:
                net.add_node(
                    tgt,
                    label=str(tgt_label)[:35],
                    title=f"{tgt_label}\nТип: {record['m_labels']}",
                    color=get_color(record['m_labels']),
                    size=25 if (record['m_labels'] and 'User' in record['m_labels']) else 20
                )
                nodes[tgt] = True
            
            # Добавляем связь
            net.add_edge(src, tgt, label=rel, title=rel, color="#64748b")

        return net

    def save_graph(self, user_id="user_1", filename="knowledge_graph.html"):
        """Полный цикл: запрос → построение → сохранение HTML"""
        data = self.get_graph_data(user_id)
        
        if not data:
            return None
        
        net = self.build_pyvis_graph(data)
        
        # Настройки визуализации
        net.set_options("""
        var options = {
          "nodes": { "font": { "size": 14, "face": "Arial" }},
          "edges": { 
            "font": { "size": 10, "align": "middle", "face": "Arial" },
            "smooth": { "type": "continuous", "roundness": 0.3 }
          },
          "physics": { 
            "enabled": true,
            "barnesHut": { "gravitationalConstant": -80000, "springLength": 250 },
            "stabilization": { "enabled": true, "iterations": 100 }
          },
          "interaction": { "hover": true, "tooltipDelay": 200 }
        }
        """)
        
        net.save_graph(filename)
        return filename

    def test_connection(self):
        """Проверка подключения к Neo4j"""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 'OK' as status")
                record = result.single()
                return record['status'] == 'OK'
        except Exception as e:
            print(f"Connection error: {e}")
            return False

