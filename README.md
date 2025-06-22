
# Knowledge Graph Generator & Visualizer

This project consists of two main components:

1. **Python Backend** – Responsible for generating the Knowledge Graph from a dataset.
2. **React Frontend** – Visualizes the generated Knowledge Graph.

---

## 🗂️ Project Structure

```
.
├── kg-visualizer-react-frontend/   # React-based frontend for visualization
├── kg_gen_main.py                  # Main KG generation script
├── entity_aggregation.py           # Entity cleanup & alias grouping
├── requirements.txt                # Python dependencies
└── outputs/                        # Folder where KG JSON files are saved
```

---

## 🚀 Frontend Setup (Visualization)

Navigate to the frontend folder:

```bash
cd kg-visualizer-react-frontend
```

Then install dependencies and run the development server:

```bash
npm install
npm run dev
```

### 📌 Important:
In the frontend source file `App.jsx`, make sure to update the path to the KG JSON file you want to visualize:

```jsx
import graphData from './path/to/your/final/json';
```

---

## 🧠 Backend Setup (Knowledge Graph Generation)

### Prerequisite:
Install [**uv**](https://github.com/astral-sh/uv) – a fast Python package manager.

Then install Python dependencies:

```bash
uv pip install -r requirements.txt
```

### Step 1: Generate the Raw KG

Update the pandas dataset link in `kg_gen_main.py`, then run:

```bash
python kg_gen_main.py
```

This will generate the raw KG JSON and save it to the `outputs/` folder.

### Step 2: Aggregate and Clean Entities

Run the entity aggregation step:

```bash
python entity_aggregation.py
```

This will produce the final cleaned KG file:

```
outputs/cleaned_aggregated_final_dataset_flash_lite.json
```

---

## 📊 Visualize the Graph

Once you have the final JSON file, place it in the frontend directory and reference it in `App.jsx` to visualize it in the browser.

---

## ✅ Summary

| Task                    | Command / Action                              |
|-------------------------|-----------------------------------------------|
| Install frontend deps   | `npm install` inside `kg-visualizer-react-frontend/` |
| Run frontend            | `npm run dev`                                 |
| Install backend deps    | `uv pip install -r requirements.txt`          |
| Generate raw KG         | `python kg_gen_main.py`                       |
| Clean & aggregate KG    | `python entity_aggregation.py`               |
| Visualize               | Update JSON path in frontend `App.jsx`       |

---

