
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "password123"

driver = GraphDatabase.driver(uri, auth=(user, password))

def check_labels_type():
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN labels(n) as labels LIMIT 1")
        for record in result:
            print(f"Type of labels in Record: {type(record['labels'])}")
            print(f"Value: {record['labels']}")
            
        result = session.run("MATCH (n) RETURN labels(n) as labels LIMIT 1")
        data = [r.data() for r in result]
        if data:
            print(f"Type of labels in data(): {type(data[0]['labels'])}")
            print(f"Value: {data[0]['labels']}")

try:
    check_labels_type()
finally:
    driver.close()
