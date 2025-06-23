import os
import json
import asyncio
import pandas as pd
import networkx as nx
from pathlib import Path
from dotenv import load_dotenv
from kg_gen import KGGen
import time

# Load environment variables
load_dotenv()

# Load dataset
df = pd.read_parquet("Datasets/train-00000-of-00001.parquet")
rows = df.iloc[:, 1].tolist()  # adjust column index as needed

# Initialize KG generator
kg = KGGen(
    model="gemini/gemini-2.0-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY")
)

# Directed knowledge graph
G = nx.DiGraph()

# Shared tracking variables
total_time = 0
completed_count = 0
lock = asyncio.Lock()  # For thread-safe updates


async def process_passage(idx, passage, G, kg):
    global total_time, completed_count
    print(f"\n📄 Processing entry {idx + 1}")
    temp_start_time = time.time()

    try:
        graph = await asyncio.to_thread(
            kg.generate, input_data=passage, context="Scientific passage"
        )
        temp_end_time = time.time()
        elapsed = temp_end_time - temp_start_time

        async with lock:
            total_time += elapsed
            completed_count += 1
            print(f"✅ Completed {completed_count} of {len(rows)} | ⏱️ Time taken: {elapsed:.2f}s | Total time so far: {total_time:.2f}s")

        if not graph.relations:
            print("⚠️  No relations extracted.")
            return 0

        local_count = 0
        for subj, rel, obj in graph.relations:
            print(f"  ➤ ({subj}) -[{rel}]-> ({obj})")
            G.add_node(subj)
            G.add_node(obj)
            G.add_edge(subj, obj, label=rel)
            local_count += 1

        return local_count

    except Exception as e:
        async with lock:
            completed_count += 1
            print(f"❌ Error in entry {idx + 1}: {e}")
            print(f"✅ Completed {completed_count} of {len(rows)} (with errors)")
        return 0


async def main_async(rows, G, kg):
    tasks = [
        process_passage(idx, passage, G, kg)
        for idx, passage in enumerate(rows)
    ]
    results = await asyncio.gather(*tasks)
    total_relations = sum(results)

    print(f"\n✅ Extracted {total_relations} relations from {len(rows)} entries.")

    # Serialize graph to JSON
    graph_data = {
        "nodes": [{"id": str(n)} for n in G.nodes()],
        "links": [
            {"source": str(u), "target": str(v), "label": d.get("label", "")}
            for u, v, d in G.edges(data=True)
        ]
    }

    output_path = Path("outputs/shashvat_dataset_flash_lite.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(graph_data, f, indent=2)

    print(f"✅ Knowledge Graph saved to: {output_path.resolve()}")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main_async(rows, G, kg))
    end_time = time.time()

    duration = end_time - start_time
    print(f"\n⏱️ Total wall-clock runtime: {duration:.2f} seconds")
