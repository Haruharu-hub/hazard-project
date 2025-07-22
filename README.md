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
| Traffic     | Driving Distraction    | 109        | 107       | ❌     | 0: 50, 1: 57                | 107   |
|             | Pedestrian Crossing    | 105        | 102       | ❌     | 0: 50, 1: 52                | 102   |
|             | Road Condition         | 109        | 109       | ✅     | 0: 49, 1: 60                | 109   |
|             | Traffic Rules          | 99         | 96        | ❌     | 0: 45, 1: 51                | 96    |
|             | Vehicle Load           | 101        | 100       | ❌     | 0: 51, 1: 49                | 100   |
| Construction| Crane Use              | 102        | 99        | ❌     | 0: 51, 1: 48                | 99    |
|             | Fire Risk              | 111        | 111       | ✅     | 0: 55, 1: 56                | 111   |
|             | Ladder Use             | 106        | 106       | ✅     | 0: 50, 1: 56                | 106   |
|             | Protective Equipment   | 106        | 106       | ✅     | 0: 50, 1: 56                | 106   |
|             | Scaffolding Risk       | 103        | 102       | ❌     | 0: 51, 1: 51                | 102   |
| Warehouse   | Ergonomic Lifting      | 20         | 20        | ✅     | 0: 10, 1: 10                | 20    |
|             | Forklift Use           | 20         | 20        | ✅     | 0: 10, 1: 10                | 20    |
|             | Ladder Use             | 20         | 20        | ✅     | 0: 10, 1: 10                | 20    |
|             | Protective Equipment   | 20         | 20        | ✅     | 0: 10, 1: 10                | 20    |
|             | Surface Condition      | 20         | 20        | ✅     | 0: 10, 1: 10                | 20    |

**Total images**: 1138

#### Annotation Statistics

| Domain  | Rule                | Complied | Not Applicable | Violated | Total |
|---------|---------------------|----------|----------------|----------|-------|
| Traffic | Driving Distraction  |    55    |      401       |    58    |  514  |
|         | Pedestrian Crossing  |    58    |      401       |    55    |  514  |
|         | Road Condition       |   204    |      237       |    73    |  514  |
|         | Traffic Rules        |    98    |      338       |    78    |  514  |
|         | Vehicle Load         |   186    |      277       |    51    |  514  |
| **Total** |                     |   601    |      1654      |   315    | 2570  |

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