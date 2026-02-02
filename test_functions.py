import time
import sys


# Testatataan kuinka nopeasti haut toimivat
for i in range(10000): 
        ht.insert(f"MODEL_{i}", {"category": "Test", "name": f"Model {i}", "type": "Test Type", "description": "Test Description"})
        

start_time = time.perf_counter()
ht.get_by_category("Decor")  
end_time = time.perf_counter()

print(f"Category search took: {end_time - start_time:.9f} seconds") 

start_time = time.perf_counter()
ht.get("CHAIR")  
end_time = time.perf_counter()

print(f"Search took: {end_time - start_time:.6f} seconds")


# Testataan hashtablen uudelleenskaalausta
# Aloitetaan pienella taulukoolla, jotta saadan tuloksia nopeammin
def test_rescaling():
    ht = HashTable(size=10) 

    for i in range(200): 
        
        ht.insert(f"MODEL_{i}", {"category": "Test", "name": f"Model {i}", "type": "Test Type", "description": "Test Description"})
        
        if ht.count / ht.size > 0.75:
            ht.resize_table()  
            print(f"Resizing triggered at {ht.count} items. New table size: {ht.size}")  

test_rescaling()


# Testataan muistin kayttoa ennen ja jalkeen uudelleen skaalauksen 
# tulostaa ensimmaisen taulukoon tiedot kaksi kertaa, mutta ei vaikuta lopputulokseen
ht = HashTable(size=10)

def check_memory():
    print(f"Current Hash Table Size: {ht.size *2}")
    print(f"Memory Usage: {sys.getsizeof(ht.table)} bytes")

check_memory()

for i in range(200):
    ht.insert(f"MODEL_{i}", {"category": "Test", "name": f"Model {i}", "type": "Test Type", "description": "Test Description"})
    if ht.count / ht.size > 0.75: 
        print(f"Resized at {ht.count} items!")
        check_memory() 


# Testataan DFS ja BFS funktoita
# Luodaan testipuurakenne
big_root = TreeNode("Root2")
current = big_root
for i in range(1000):
    new_node = Node(f"Node {i}")
    current.children.append(new_node)
    current = new_node  

start_time = time.perf_counter()
dfs_traverse_categories(big_root)
end_time = time.perf_counter()
print(f"DFS took: {end_time - start_time:.6f} seconds")

start_time = time.perf_counter()
find_node_bfs(big_root, "Node 999")
end_time = time.perf_counter()
print(f"BFS took: {end_time - start_time:.6f} seconds")