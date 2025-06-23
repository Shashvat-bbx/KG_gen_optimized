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
df= pd.read_csv("Datasets/kg_dataset_small.csv")
# df = pd.read_parquet("Datasets/train-00000-of-00001.parquet" )
rows = df.iloc[:, 0].tolist() # update the column according to the dataset csv

# Initialize KG generator
kg = KGGen(
    model="gemini/gemini-2.0-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY")
)

# Directed knowledge graph
G = nx.DiGraph()

# Semaphore to limit concurrency to 100 tasks at a time
semaphore = asyncio.Semaphore(100)


async def process_passage(idx, passage, G, kg):
    async with semaphore:
        print(f"\n📄 Processing entry {idx + 1}")
        print("📖 Text Snippet:", passage[:])

        try:
            graph = await asyncio.to_thread(
                kg.generate, input_data=passage, context="Scientific passage"
            )

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
            print(f"❌ Error in entry {idx + 1}: {e}")
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

    output_path = Path("outputs/kg_result_gemini_flash_lite.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(graph_data, f, indent=2)

    print(f"✅ Knowledge Graph saved to: {output_path.resolve()}")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main_async(rows, G, kg))
    end_time = time.time()

    duration = end_time - start_time
    print(f"\n⏱️ Total runtime: {duration:.2f} seconds")