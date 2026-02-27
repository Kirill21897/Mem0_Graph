from mem0 import Memory
from mem0_graph.config import MEM0_CONFIG
import os
from dotenv import load_dotenv

load_dotenv()

try:
    memory = Memory.from_config(MEM0_CONFIG)
    user_id = "user_1"
    
    # Add a dummy memory first if needed, but search might return empty list
    print("Adding memory...")
    memory.add("My name is Test", user_id=user_id)
    
    print("Searching...")
    relevant = memory.search("Hello", user_id=user_id)
    print(f"Type of relevant: {type(relevant)}")
    print(f"Content of relevant: {relevant}")
    
    if isinstance(relevant, list) and len(relevant) > 0:
        first_item = relevant[0]
        print(f"Type of first item: {type(first_item)}")
        print(f"Content of first item: {first_item}")

    print("Getting all memories...")
    all_memories = memory.get_all(user_id=user_id)
    print(f"Type of all_memories: {type(all_memories)}")
    print(f"Content of all_memories: {all_memories}")

except Exception as e:
    print(f"Error: {e}")

