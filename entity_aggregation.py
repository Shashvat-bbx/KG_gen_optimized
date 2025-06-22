from google import genai
from pydantic import BaseModel
import json
import os

     

# ---------------------- SETUP ----------------------
# Initialize the Gemini client with your API key
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))  # Replace with your actual API key

# Schema for the Gemini JSON output
class EntityGroup(BaseModel):
    canonical: str
    aliases: list[str]

# ---------------------- ENTITY GROUPING ----------------------
def process_entity_batch(batch: list[str], alias_to_canonical: dict):
    """
    Send a batch of entity names to Gemini to detect alias groups.
    Updates the alias_to_canonical dictionary in place.
    """
    
    prompt = (
    '''
    You are cleaning up entity names in a noisy knowledge graph.

    Here is a list of entity names:
    ''' + "\n".join(f"- {e}" for e in batch) + '''

    Your task is to identify and group names that clearly refer to the **same real-world entity**. Only do this if you are **absolutely confident** that the names refer to the **exact same thing** — not just similar or related entities.

    ### Output Format:
    Return your result in JSON using the following structure:
    [
    {
        "canonical": "<a clear, common DETAILED name you choose for the group>",
        "aliases": ["<variant1>", "<variant2>", ...]
    },
    ...
    ]

    ### Rules:
    - Only include entries where **multiple names refer to the same exact entity**.
    - Use any **one of the names** as the canonical name — choose the most complete, common, or widely accepted one.
    - **Do not** output singleton entities (i.e., names with no matching variants).
    - **Do not** group entities that are different in meaning, even if they are similar in wording (e.g., "male rats" vs "female rats", or "Amazon" vs "Amazon River").
    - Be extremely strict — only group names if you are **fully certain** they refer to the same real-world concept or entity.

    ### Examples:
    ✅ Group: ["Albert Einstein", "A. Einstein", "Al. Einstein"]
    ```json
    [
    {
        "canonical": "Albert Einstein",
        "aliases": ["A. Einstein", "Al. Einstein"]
    }
]'''
    ) 


    try:
        response = client.models.generate_content(
            model="models/gemini-2.0-flash-lite",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": list[EntityGroup],
                "temperature":0,
                "top_p":0.95
            },
            
        )

        print(response.text)  # Optional: log raw response

        groups: list[EntityGroup] = response.parsed
        for group in groups:
            for alias in group.aliases:
                alias_to_canonical[alias] = group.canonical

    except Exception as e:
        print(f"⚠️ Failed to process batch: {e}")

# ---------------------- GRAPH REWRITING ----------------------
def apply_alias_mapping(data, alias_to_canonical):
    """
    Renames nodes and updates links using alias_to_canonical mapping.
    Also prints before/after stats.
    """
    num_nodes_before = len(data["nodes"])
    num_links_before = len(data["links"])

    # Deduplicate nodes
    unique_ids = set()
    for node in data["nodes"]:
        canonical = alias_to_canonical.get(node["id"], node["id"])
        unique_ids.add(canonical)
    new_nodes = [{"id": eid} for eid in sorted(unique_ids)]
    num_nodes_after = len(new_nodes)

    # Update links
    new_links = []
    for link in data["links"]:
        src = alias_to_canonical.get(link["source"], link["source"])
        tgt = alias_to_canonical.get(link["target"], link["target"])
        if src != tgt:  # Avoid self-links if merged
            new_links.append({"source": src, "target": tgt, "label": link["label"]})
    num_links_after = len(new_links)

    # Print comparison
    print(f"🔢 Nodes: {num_nodes_before} → {num_nodes_after}")
    print(f"🔗 Links: {num_links_before} → {num_links_after}")

    return {"nodes": new_nodes, "links": new_links}

# ---------------------- MAIN WORKFLOW ----------------------
def main():
    # Load input JSON graph
    with open("outputs/chem_dataset_first_100_rows.json") as f:
        data = json.load(f)

    # Split entities into batches of 100
    node_ids = [node["id"] for node in data["nodes"]]
    batches = [node_ids[i:i + 100] for i in range(0, len(node_ids), 100)]

    # Build alias-to-canonical mapping
    alias_map = {}
    for batch in batches:
        process_entity_batch(batch, alias_map)

    # Save alias mapping
    with open("outputs/alias_to_canonical.json", "w") as f:
        json.dump(alias_map, f, indent=2)
    print("✅ Saved outputs/alias_to_canonical.json")

    # Apply mapping to knowledge graph
    cleaned_data = apply_alias_mapping(data, alias_map)

    # Save cleaned knowledge graph
    with open("outputs/cleaned_Aggregated_dataset_flash_lite.json", "w") as f:
        json.dump(cleaned_data, f, indent=2)
    print("✅ Saved cleaned knowledge graph to outputs/cleaned_shashvat_dataset_flash_lite.json")

# ---------------------- ENTRY POINT ----------------------
if __name__ == "__main__":
    main()
