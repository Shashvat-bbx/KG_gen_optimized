import { useEffect, useState, useCallback, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import "./App.css";




export default function App() {
  const fgRef = useRef();
  const miniMapRef = useRef();
  const [data, setData] = useState(null);
  const [selected, setSelected] = useState(null);
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());

  const [searchTerm, setSearchTerm] = useState("");
  const getNodeColor = (node) => {
    return highlightNodes.has(node.id) ? "#2a4d6f" : node.originalColor;
  };


  const getLinkColor = (link) => {
    return highlightLinks.has(link) ? "#2a4d6f" : link.originalColor;
  };




  useEffect(() => {
    fetch("/cleaned_shashvat_dataset_flash_lite.json")
      .then((res) => res.json())
      .then((json) => {
        json.nodes.forEach(node => {
          node.originalColor = "#4682B4"; // soft blue
          node.color = "#4682B4";
        });
        json.links.forEach(link => {
          link.originalColor = "#cce5f6"; // pale blue
          link.color = "#cce5f6";
        });
        setData(json);
      })
      .catch((err) => console.error("Failed to load graph", err));
  }, []);

  // ↓ find this in App.jsx:
const handleNodeClick = useCallback((node) => {
  // ADD THESE LINES at the top of the function:
  console.log(" Node clicked:", node);
  console.log("→ setting selected.type to 'node'");
  
  setSelected({ type: "node", data: node });

  const neighbors = new Set();
  const links = new Set();

    data.links.forEach((link) => {
      if (link.source.id === node.id || link.source === node.id || link.target.id === node.id || link.target === node.id) {
        neighbors.add(link.source.id || link.source);
        neighbors.add(link.target.id || link.target);
        links.add(link);
      }
    });

  setHighlightNodes(neighbors);
  setHighlightLinks(links);
}, [data]);


  // ↓ and similarly here:
const handleLinkClick = useCallback((link) => {
  // ADD THESE LINES:
  console.log("📌 Link clicked:", link);
  console.log("→ setting selected.type to 'link'");
  
  setSelected({ type: "link", data: link });
}, []);


  const handleSearch = useCallback((term) => {
    if (!data) return;

    const node = data.nodes.find((n) => n.id.toLowerCase() === term.toLowerCase());
    if (node) {
      fgRef.current.centerAt(node.x, node.y, 1000);
      fgRef.current.zoom(4, 1000);
      setSelected({ type: "node", data: node });
    } else {
      alert("Node not found!");
    }
  }, [data]);



  const suggestions = data
    ? data.nodes
        .map((n) => n.id)
        .filter((id) =>
          id.toLowerCase().includes(searchTerm.toLowerCase()) &&
          searchTerm.length > 1
        )
        .slice(0, 10) // show top 10 suggestions
    : [];



  return (
    <div className="app-container">
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search node..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSearch(searchTerm);
          }}

          // onKeyDown={(e) => e.key === "Enter" && handleSearch()}
        />

        <button onClick={() => handleSearch(searchTerm)}>Go</button>


        {suggestions.length > 0 && (
          <ul className="suggestions">
            {suggestions.map((s, idx) => (
              <li key={idx} onClick={() => {
                setSearchTerm(s);
                handleSearch(s); 
              }}>
                {s}
              </li>
            ))}
          </ul>
        )}
        {/* <button onClick={handleSearch}>Go</button> */}
      </div>

      <div className="graph-pane">
        

        {data ? (
          <ForceGraph2D
            ref={fgRef}
            style={{ width: "100%", height: "100%" }}  // ← make it fill
            graphData={data}
            nodeLabel="id"
            linkLabel="label"
            linkDirectionalArrowLength={4}
            linkDirectionalArrowRelPos={1}
            nodeAutoColorBy="group"
            onNodeClick={handleNodeClick}
            onLinkClick={handleLinkClick}
            nodeColor={getNodeColor}
            linkColor={getLinkColor}
            onNodeDrag={handleNodeClick}
            linkCanvasObjectMode={() => "after"}
            linkCanvasObject={(link, ctx, globalScale) => {
              if (globalScale < 2 || !link.label) return;

              const fontSize = Math.min(30, 12 / globalScale); // Slightly larger for heading
              ctx.font = `${fontSize}px Sans-Serif`;
              ctx.fillStyle = "#1a1a1a";
              ctx.textAlign = "center";
              ctx.textBaseline = "middle";

              const start = typeof link.source === "object" ? link.source : { x: 0, y: 0 };
              const end = typeof link.target === "object" ? link.target : { x: 0, y: 0 };

              const midX = (start.x + end.x) / 2;
              const midY = (start.y + end.y) / 2;

              ctx.fillText(link.label, midX, midY);
            }}
            nodeCanvasObjectMode={() => "after"}
            nodeCanvasObject={(node, ctx, globalScale) => {
              const label = node.id;
              const fontSize = 12 / globalScale;

              if (globalScale < 1.5) return;  // Only show if zoomed in enough
              ctx.font = ` bold ${fontSize}px Sans-Serif`;
              ctx.fillStyle = "black";
              ctx.fillText(label, node.x + 6, node.y + 6);
            }}

            
          
          />
          
          
        ) : (
          <p style={{ padding: "1rem", color: "#666" }}>Loading graph…</p>
        )}
      </div>
        {selected && (
  <div className="side-pane">
    <button className="close-btn" onClick={() => setSelected(null)}>
      ✕
    </button>
    
    {/* NODE DETAILS */}
    {selected.type === "node" && (
      <>
        <h2>Node</h2>
        <p><strong>ID:</strong> {selected.data?.id ?? "N/A"}</p>
      </>
    )}

    {/* LINK/EDGE DETAILS */}
    {selected.type === "link" && (
      <>
        <h2>Edge</h2>
        <p>
          <strong>Source:</strong>{" "}
          {typeof selected.data.source === "object"
            ? selected.data.source.id
            : selected.data.source}
        </p>
        <p>
          <strong>Target:</strong>{" "}
          {typeof selected.data.target === "object"
            ? selected.data.target.id
            : selected.data.target}
        </p>
        {selected.data.label && (
          <p><strong>Label:</strong> {selected.data.label}</p>
        )}
      </>
    )}

    {/* FALLBACK MESSAGE */}
    {!["node", "link"].includes(selected.type) && (
      <p>No details available for this selection.</p>
    )}
  </div>
)}

    </div>
  );
}
