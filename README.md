# ⚠️ Hazard Detection Project
 
This is a hazard detection project that combines LLaVA's multimodal vision-language capabilities with user-defined **hazard rules**. Images are preloaded, and users define what constitutes a hazard by specifying rules or keywords. For the purpose of this project, the rules are derived from real-world safety regulations and are intended to test the model's ability to reason based on context-dependent hazard definitions rather than general/common-sense notions.

## 🔍 What It Does

- Users define **custom hazard rules** (e.g., "no helmet", "fire", "driving distraction").
- Preloaded images are analyzed using [LLaVA](https://github.com/haotian-liu/LLaVA), a large vision-language model, through a multi-step reasoning framework.
- LLaVA generates a descriptive caption for each image, assesses and highlights possible hazards according to those rules.

## ‼️ Data Availability
Due to copyright restrictions, the data are not publicly available. Access may be granted upon reasonable request.
Contact: Stephanie, szng@deakin.edu.au

## ⚙️ Setup Instructions

### 1. Clone this repository and navigate to main folder
```
git clone https://github.com/Haruharu-hub/hazard-project.git
cd hazard-project
```

### 2. Install Package
```
conda create -n llava python=3.11.11 -y
conda activate llava
pip install --upgrade pip
pip install -e .
conda install -c conda-forge cairosvg
```

### 3. Install Ollama
Install from https://ollama.com/download

Or install via terminal for Linux:
```
curl -fsSL https://ollama.com/install.sh | sh
```

See [Manual Install Instruction](https://github.com/ollama/ollama/blob/main/docs/linux.md) for more info.

Pull Required models.
```
ollama pull llava
ollama pull llama3.1
```

Run model
```
ollama run llava
```

### 4. Download and Preprocess Images
```
python src/download_images.py
python src/process_images.py

```

### 5. Launch Streamlit App
```
streamlit run src/app.py
```
The app will open in your default browser at: http://localhost:8501

If it doesn't open automatically, just copy and paste the link into your browser.

## 🖼 Data Collection

### 1. Rule Definition

- Rules are defined in `custom_rules.py` for three domains: `construction`, `warehouse`, and `traffic`.
- Each domain includes **5 rules**:
- Derived from **OSHA**, **Victorian Road Safety Rules**, and other policy sources.

### 2. Image Collection
Images are collected and organized via URL links, stored under the `images_link` folder in this structure: `[domain_name]/[rule_name]_[label].txt`.

- `label = 0`: Rule is **complied with**
- `label = 1`: Rule is **violated**

### 3. Current Dataset Statistics

#### Images Statistics

| Domain      | Rule                   | Downloaded | Processed | Matched | Label Distribution | Total |
|-------------|------------------------|------------|-----------|---------|--------------------|-------|
| Traffic     | Driving Distraction    | 207        | 207       | ✅     | 0: 100, 1: 107              | 1007  |
|             | Pedestrian Crossing    | 200        | 200       | ✅     | 0: 100, 1: 100              |       |
|             | Road Condition         | 200        | 200       | ✅     | 0: 100, 1: 100              |       |
|             | Traffic Rules          | 200        | 200       | ✅     | 0: 100, 1: 100              |       |
|             | Vehicle Load           | 200        | 200       | ✅     | 0: 100, 1: 100              |       |
| Construction| Crane Use              | 200        | 200       | ✅     | 0: 100, 1: 100              | 999   |
|             | Fire Risk              | 200        | 200       | ✅     | 0: 100, 1: 100              |       |
|             | Ladder Use             | 200        | 199       | ❌     | 0: 100, 1: 99               |       |
|             | Protective Equipment   | 200        | 200       | ✅     | 0: 100, 1: 100              |       |
|             | Scaffolding Risk       | 200        | 200       | ✅     | 0: 100, 1: 100              |       |
| Warehouse   | Ergonomic Lifting      | 200        | 200       | ✅     | 0: 100, 1: 100              | 1000  |
|             | Forklift Use           | 200        | 200       | ✅     | 0: 100, 1: 100              |       |
|             | Ladder Use             | 200        | 200       | ✅     | 0: 100, 1: 100              |       |
|             | Protective Equipment   | 200        | 200       | ✅     | 0: 100, 1: 100              |       |
|             | Surface Condition      | 200        | 200       | ✅     | 0: 100, 1: 100              |       |

**Total images**: 3006

#### Annotation Statistics

| Domain  | Rule                | Complied | Not Applicable | Violated | Total |
|---------|---------------------|----------|----------------|----------|-------|
| Construction | Crane Use            |   127    |      763       |   109    |  999  |
|         | Fire Risk            |   121    |      771       |   107    |  999  |
|         | Ladder Use           |   105    |      795       |    99    |  999  |
|         | Protective Equipment |   430    |      282       |   287    |  999  |
|         | Scaffolding Risk     |   128    |      733       |   138    |  999  |
| Traffic | Driving Distraction  |   112    |      788       |   107    | 1007  |
|         | Pedestrian Crossing  |   136    |      760       |   111    | 1007  |
|         | Road Condition       |   642    |      211       |   154    | 1007  |
|         | Traffic Rules        |   385    |      453       |   169    | 1007  |
|         | Vehicle Load         |   169    |      735       |   103    | 1007  |
| Warehouse | Ergonomic Lifting    |   137    |      717       |   146    | 1000  |
|         | Forklift Use         |   124    |      775       |   101    | 1000  |
|         | Ladder Use           |   102    |      788       |   110    | 1000  |
|         | Protective Equipment |   319    |      211       |   470    | 1000  |
|         | Surface Condition    |   530    |      288       |   182    | 1000  |
| **Total** |                     |   3567   |      9070      |   2393   | 15030 |

#### Current Annotation:
- Per-rule binary label based on image link filename as described above
- Assumes **each image maps to a single rule**

#### Planned Annotation:
- **Multi-rule, image-centric annotations** (to support real-world overlaps)
- For each image, annotate status for **all 5 rules** in its domain:
  - `"complied"`, `"violated"`, `"not applicable"`

#### Example Annotation Formats in CSV:

image_dir = data/downloaded_images/traffic/Driving_Distraction_1/0000004.jpg

| Domain  | Image Link                                                                 | Rule             | Label          |
|---------|-----------------------------------------------------------------------------|---------------------|----------------|
| traffic | [Link](https://cdn.hswstatic.com/gif/driving-dogs-lap.jpg)                 | Driving Distraction | violated        |
| traffic | [Link](https://cdn.hswstatic.com/gif/driving-dogs-lap.jpg)                 | Pedestrian Crossing | not applicable |
| traffic | [Link](https://cdn.hswstatic.com/gif/driving-dogs-lap.jpg)                 | Road Condition      | not applicable |
| traffic | [Link](https://cdn.hswstatic.com/gif/driving-dogs-lap.jpg)                 | Traffic Rules       | not applicable |
| traffic | [Link](https://cdn.hswstatic.com/gif/driving-dogs-lap.jpg)                 | Vehicle Load        | not applicable |


Example of multiple rules applicable to a single image:

image_dir = data/downloaded_images/warehouse/Ergonomic_Lifting_1/0000002.jpg

| Domain    | Image Link                                                                                   | Rule             | Label          |
|-----------|-----------------------------------------------------------------------------------------------|---------------------|----------------|
| warehouse | [Link](https://images.cisco-eagle.com/blog/wp-content/uploads/2020/05/Lifting-Boxes-Rack.jpg) | Ergonomic Lifting   | violated        |
| warehouse | [Link](https://images.cisco-eagle.com/blog/wp-content/uploads/2020/05/Lifting-Boxes-Rack.jpg) | Forklift Use        | not applicable |
| warehouse | [Link](https://images.cisco-eagle.com/blog/wp-content/uploads/2020/05/Lifting-Boxes-Rack.jpg) | Ladder Use          | not applicable |
| warehouse | [Link](https://images.cisco-eagle.com/blog/wp-content/uploads/2020/05/Lifting-Boxes-Rack.jpg) | Protective Equipment | violated       |
| warehouse | [Link](https://images.cisco-eagle.com/blog/wp-content/uploads/2020/05/Lifting-Boxes-Rack.jpg) | Surface Condition   | complied        |

