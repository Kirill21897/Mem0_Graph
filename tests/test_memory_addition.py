from mem0 import Memory
from mem0_graph.config import MEM0_CONFIG
import time


def test_addition():
    memory = Memory.from_config(MEM0_CONFIG)
    user_id = "test_user_add"
    
    # Clear previous test data
    memory.delete_all(user_id=user_id)
    
    print("Adding first memory: 'I like apples'")
    memory.add("I like apples", user_id=user_id)
    time.sleep(2)  # Allow async processing if any
    
    print("Adding second memory: 'I like oranges'")
    memory.add("I like oranges", user_id=user_id)
    time.sleep(2)
    
    print("Searching for 'What do I like?'")
    results = memory.search("What do I like?", user_id=user_id)
    
    print("Results:", results)
    
    # Check if both are present
    # results format for graph might be complex, let's print it
    
    print("Getting all memories")
    all_mem = memory.get_all(user_id=user_id)
    print("All memories:", all_mem)


if __name__ == "__main__":
    test_addition()

