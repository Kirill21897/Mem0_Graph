
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "password123"
driver = GraphDatabase.driver(uri, auth=(user, password))

def test_query():
    user_id = "user_1"
    query = """
    MATCH (n)-[r]->(m)
    WHERE n.user_id = $user_id OR m.user_id = $user_id OR 
            n.user_id IS NULL OR m.user_id IS NULL
    RETURN 
        elementId(n) as source,
        elementId(m) as target,
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
    LIMIT 300
    """
    
    with driver.session() as session:
        result = session.run(query, user_id=user_id)
        data = [record.data() for record in result]
        print(f"Found {len(data)} records")
        for i, d in enumerate(data[:3]):
            print(f"Record {i}: {d}")

try:
    test_query()
except Exception as e:
    print(f"Error: {e}")
finally:
    driver.close()
