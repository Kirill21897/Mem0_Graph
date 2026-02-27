from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "password123"

driver = GraphDatabase.driver(uri, auth=(user, password))


def print_graph_structure():
    with driver.session() as session:
        print("--- Node Labels ---")
        result = session.run("MATCH (n) RETURN DISTINCT labels(n) as labels, count(n) as count")
        for record in result:
            print(f"{record['labels']}: {record['count']}")
            
        print("\n--- Relationship Types ---")
        result = session.run("MATCH ()-[r]->() RETURN DISTINCT type(r) as type, count(r) as count")
        for record in result:
            print(f"{record['type']}: {record['count']}")
            
        print("\n--- Sample Nodes ---")
        result = session.run("MATCH (n) RETURN n LIMIT 5")
        for record in result:
            print(record['n'])

        print("\n--- Sample Relationships ---")
        result = session.run("MATCH ()-[r]->() RETURN r LIMIT 5")
        for record in result:
            print(record['r'])


if __name__ == "__main__":
    try:
        print_graph_structure()
    finally:
        driver.close()

