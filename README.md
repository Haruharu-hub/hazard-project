# ⚠️ Hazard Detection Project
 
This is a hazard detection project that combines LLaVA's multimodal vision-language capabilities with user-defined **hazard rules**. Images are preloaded, and users define what constitutes a hazard by specifying rules or keywords. For the purpose of this project, the rules are derived from real-world safety regulations and are intended to test the model's ability to reason based on context-dependent hazard definitions rather than general/common-sense notions.

## 🔍 What It Does

- Users define **custom hazard rules** (e.g., "no helmet", "fire", "driving distraction").
- Preloaded images are analyzed using [LLaVA](https://github.com/haotian-liu/LLaVA), a large vision-language model, through a multi-step reasoning framework.
- LLaVA generates a descriptive caption for each image, assesses and highlights possible hazards according to those rules.

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
| Construction| Crane Use              | 101        | 101       | ✅     | 0: 51, 1: 50                | 521   |
|             | Fire Risk              | 111        | 111       | ✅     | 0: 55, 1: 56                |       |
|             | Ladder Use             | 106        | 106       | ✅     | 0: 50, 1: 56                |       |
|             | Protective Equipment   | 103        | 103       | ✅     | 0: 50, 1: 53                |       |
|             | Scaffolding Risk       | 100        | 100       | ✅     | 0: 50, 1: 50                |       |
| Warehouse   | Ergonomic Lifting      | 103        | 103       | ✅     | 0: 52, 1: 51                | 512   |
|             | Forklift Use           | 102        | 102       | ✅     | 0: 52, 1: 50                |       |
|             | Ladder Use             | 103        | 103       | ✅     | 0: 52, 1: 51                |       |
|             | Protective Equipment   | 103        | 103       | ✅     | 0: 52, 1: 51                |       |
|             | Surface Condition      | 102        | 101       | ❌     | 0: 51, 1: 50                |       |

**Total images**: 2040

#### Annotation Statistics

| Domain  | Rule                | Complied | Not Applicable | Violated | Total |
|---------|---------------------|----------|----------------|----------|-------|
| Construction | Crane Use            |    62    |      408       |    51    |  521  |
|         | Fire Risk            |    62    |      396       |    63    |  521  |
|         | Ladder Use           |    55    |      410       |    56    |  521  |
|         | Protective Equipment |   223    |      150       |   148    |  521  |
|         | Scaffolding Risk     |    65    |      397       |    59    |  521  |
| Traffic | Driving Distraction  |    55    |      409       |    57    |  521  |
|         | Pedestrian Crossing  |    58    |      405       |    58    |  521  |
|         | Road Condition       |   313    |      112       |    96    |  521  |
|         | Traffic Rules        |   190    |      245       |    86    |  521  |
|         | Vehicle Load         |    88    |      382       |    51    |  521  |
| Warehouse | Ergonomic Lifting    |    78    |      358       |    77    |  513  |
|         | Forklift Use         |    65    |      397       |    51    |  513  |
|         | Ladder Use           |    54    |      400       |    59    |  513  |
|         | Protective Equipment |   168    |       91       |   253    |  513  |
|         | Surface Condition    |   264    |      145       |   103    |  513  |
| **Total** |                     |   1800   |      4705      |   1268   | 7775  |

#### Current Annotation:
- Per-rule binary label based on image link filename as described above
- Assumes **each image maps to a single rule**

#### Planned Annotation:
- **Multi-rule, image-centric annotations** (to support real-world overlaps)
- For each image, annotate status for **all 5 rules** in its domain:
  - `"complied"`, `"violated"`, `"not applicable"`

#### Example Annotation Formats in CSV:

![Alt text](https://cdn.hswstatic.com/gif/driving-dogs-lap.jpg)

image_dir = data/downloaded_images/traffic/Driving_Distraction_1/0000004.jpg

image_url = https://cdn.hswstatic.com/gif/driving-dogs-lap.jpg

| Domain  | Image Link                                                                 | Rule             | Label          |
|---------|-----------------------------------------------------------------------------|---------------------|----------------|
| traffic | [Link](https://cdn.hswstatic.com/gif/driving-dogs-lap.jpg)                 | Driving Distraction | violated        |
| traffic | [Link](https://cdn.hswstatic.com/gif/driving-dogs-lap.jpg)                 | Pedestrian Crossing | not applicable |
| traffic | [Link](https://cdn.hswstatic.com/gif/driving-dogs-lap.jpg)                 | Road Condition      | not applicable |
| traffic | [Link](https://cdn.hswstatic.com/gif/driving-dogs-lap.jpg)                 | Traffic Rules       | not applicable |
| traffic | [Link](https://cdn.hswstatic.com/gif/driving-dogs-lap.jpg)                 | Vehicle Load        | not applicable |


Example of multiple rules applicable to a single image:

![Alt text](https://images.cisco-eagle.com/blog/wp-content/uploads/2020/05/Lifting-Boxes-Rack.jpg)

image_dir = data/downloaded_images/warehouse/Ergonomic_Lifting_1/0000002.jpg

image_url = https://images.cisco-eagle.com/blog/wp-content/uploads/2020/05/Lifting-Boxes-Rack.jpg

| Domain    | Image Link                                                                                   | Rule             | Label          |
|-----------|-----------------------------------------------------------------------------------------------|---------------------|----------------|
| warehouse | [Link](https://images.cisco-eagle.com/blog/wp-content/uploads/2020/05/Lifting-Boxes-Rack.jpg) | Ergonomic Lifting   | violated        |
| warehouse | [Link](https://images.cisco-eagle.com/blog/wp-content/uploads/2020/05/Lifting-Boxes-Rack.jpg) | Forklift Use        | not applicable |
| warehouse | [Link](https://images.cisco-eagle.com/blog/wp-content/uploads/2020/05/Lifting-Boxes-Rack.jpg) | Ladder Use          | not applicable |
| warehouse | [Link](https://images.cisco-eagle.com/blog/wp-content/uploads/2020/05/Lifting-Boxes-Rack.jpg) | Protective Equipment | violated       |
| warehouse | [Link](https://images.cisco-eagle.com/blog/wp-content/uploads/2020/05/Lifting-Boxes-Rack.jpg) | Surface Condition   | complied        |


### 5. Experimental Roadmap
#### Phase 1: Data Expansion (🔴 High Priority)
- Collect more images for each rule
- Target: 100 images per rule, equally balanced (50 complied, 50 violated)
- Ensure:
    * Clear visibility of relevant hazards
    * Objects of interest near center of image
    * High resolution (≥ 672×672)
    * Accepted formats: `.jpg`, `.jpeg`, `.png`

#### Phase 2: Multi-rule Annotation (🔴 High Priority)
- Label each image with all 5 rules from its domain in a csv file

#### Phase 3: Descriptive Annotation (⏳ Low Priority)
- Write natural language descriptions for each image for potential use in LLaVA fine-tuning

#### Phase 4: Object-Level Annotation (⏳ Low Priority)
- Label bounding boxes for key objects or hazards for potential training/evaluating object detectors like YOLO