import os
import json
import time
import pandas as pd
import networkx as nx
from pathlib import Path
from dotenv import load_dotenv
from kg_gen import KGGen

# Load environment variables
load_dotenv()

# Load dataset
df = pd.read_csv("Datasets/Custom_test_dataset_original.csv")
rows = df.iloc[:, 0].tolist()  # adjust column index if needed

# Initialize KG generator
kg = KGGen(
    model="ollama_chat/llama3",       # set the downloaded model
    api_base=os.getenv("http://localhost:11434")
)

# Directed knowledge graph
G = nx.DiGraph()

# Tracking variables
total_time = 0
completed_count = 0
total_relations = 0

# Process each passage synchronously
for idx, passage in enumerate(rows):
    print(f"\n📄 Processing entry {idx + 1}")
    temp_start_time = time.time()

    try:
        graph = kg.generate(input_data=passage, context="Scientific passage")
        temp_end_time = time.time()
        elapsed = temp_end_time - temp_start_time

        total_time += elapsed
        completed_count += 1
        print(f"✅ Completed {completed_count} of {len(rows)} | ⏱️ Time taken: {elapsed:.2f}s | Total time so far: {total_time:.2f}s")

        if not graph.relations:
            print("⚠️  No relations extracted.")
            continue

        for subj, rel, obj in graph.relations:
            print(f"  ➤ ({subj}) -[{rel}]-> ({obj})")
            G.add_node(subj)
            G.add_node(obj)
            G.add_edge(subj, obj, label=rel)
            total_relations += 1

    except Exception as e:
        completed_count += 1
        print(f"❌ Error in entry {idx + 1}: {e}")
        print(f"✅ Completed {completed_count} of {len(rows)} (with errors)")

# Serialize graph to JSON
graph_data = {
    "nodes": [{"id": str(n)} for n in G.nodes()],
    "links": [
        {"source": str(u), "target": str(v), "label": d.get("label", "")}
        for u, v, d in G.edges(data=True)
    ]
}

output_path = Path("outputs/KG_Output_from_ollama.json")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w") as f:
    json.dump(graph_data, f, indent=2)

print(f"\n✅ Extracted {total_relations} relations from {len(rows)} entries.")
print(f"✅ Knowledge Graph saved to: {output_path.resolve()}")
print(f"\n⏱️ Total wall-clock runtime: {total_time:.2f} seconds")
