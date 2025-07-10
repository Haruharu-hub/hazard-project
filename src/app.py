import streamlit as st
import os
from PIL import Image
from openai import OpenAI
import base64
from io import BytesIO
import ast
from json_repair import repair_json
import re
from custom_rules import rule_description

DATA_DIR = 'data/processed_images/'
client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")
temperature = 0
max_length = 3000
llm = 'llama3.1'

def get_all_hazards():
    return sorted({'_'.join(f.split('_')[:-1]) for f in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, f))})

def get_labels(hazard_type):
    return [d.split('_')[-1] for d in os.listdir(DATA_DIR) if d.startswith(hazard_type)]

def get_image_files(hazard_type, label):
    folder = f"{hazard_type}_{label}"
    path = os.path.join(DATA_DIR, folder)
    image_files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    return sorted(image_files), path

def image_to_base64_data_uri(file_path):
    with open(file_path, "rb") as img_file:
        base64_data = base64.b64encode(img_file.read()).decode('utf-8')
        return f"data:image/jpg;base64,{base64_data}"

def get_text_response(system_prompt, user_prompt, chat_history=[]):
    response = client.chat.completions.create(
            model=llm, 
            temperature=temperature,
            max_tokens=max_length,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                *chat_history
            ],
        )
    
    return response.choices[0].message.content

def get_image_response(system_prompt, file_path, chat_history):

    data_uri = image_to_base64_data_uri(file_path)

    response = client.chat.completions.create(
        model='llava',
        temperature=temperature,
        max_tokens=max_length,
        messages=[{
            "role":
            "user",
            "content": [
                {
                    "type": "text",
                    "text": system_prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": data_uri
                    },
                },
            ],
            
        }, 
        *chat_history
        ],
       
    )

    response = response.choices[0].message.content

    return response

def get_single_llava_output(image_path, hazard_rule):

    system_prompt = f"""Determine whether the situation in the image follows or violates: "{hazard_rule}". Provide your answer in JSON format as follows:
    
    {{
        "rationale": "A concise explanation that describes the visible content of the image and clearly explains whether each safety rule is being followed, violated, or not applicable based solely on the image. Justify the overall status (Hazard/Safe only) based on visual evidence and rule relevance. Classify 'hazard' status if any one of the applicable rule is not followed.",
        "compliance": "Answer Followed/Violated/Not Applicable for each safety rule category: {{"Rule 1: ..." : "Followed" | "Violated" | "Not Applicable", "Rule 2: ...": "Followed" | "Violated" | "Not Applicable", "Rule 3: ...": "Followed" | "Violated" | "Not Applicable", "Rule 4: ...": "Followed" | "Violated" | "Not Applicable", "Rule 5: ...": "Followed" | "Violated" | "Not Applicable"}}",
        "status": "Hazard" | "Safe"
    }}

"""

    response = get_image_response(system_prompt, image_path, chat_history=[])
    # print(response)
   
    return response

def get_multi_llava_output(image_path, hazard_rule):

    chat_history = []
    chat_history.append({"role": "user", "content": f'You will be asked to perform a safety rule assessment task.'})

    # system_prompt1 = """Describe the image stating who the main person are, what activity or task they are performing, the exact posture of each hand and leg, the height and positions of key objects directly or indirectly attached to the main person, background objects, and any visible next-step hazards based on the main activity in the image."""
    system_prompt1 = """Describe the image stating any visible hazards based on the main activity in the image."""

    chat_history.append({"role": "user", "content": system_prompt1})
    response1 = get_image_response(system_prompt1, image_path, chat_history).replace('\n\n', ' ')
    chat_history.append({"role": "assistant", "content": response1})

    st.write('### Step 1 Describe Image \n', response1)

    qa_prompt = """Given a list of workplace safety rules, generate a list of visual hazard inspection questions related to the main activity in the image. Do not try to introduce new safety rules or assumptions. Focus only on what can be visually verified in the image solely based on the given rules and image description. 

Questions:
    1. ...
    2. ...
"""
    qa = get_text_response(qa_prompt, f'Safety Rule: "{hazard_rule}" \n\nImage Description: {response1}')

    st.write('\n\n ### Step 2 Assess Criteria \n')

    response2 = ''
    for i, q in enumerate(re.findall(r"\d+\.\s*(.+)", qa), start=1):

        st.write(i, '. ', q)
        response2 += f'{i}. {q} \n'

        # system_prompt2 = f"""Answer the question: {q} based on the given image and image description: {response1} \nLet's think step by step."""
        system_prompt2 = f"""Answer the question: {q} \n\nEvaluate whether the rule applies based on the visible evidence. Respond with clear and confident reasoning that justifies your conclusion. \n\nContext: \n{response1}."""
        tmp = [{"role": "user", "content": system_prompt2}]
        r = get_image_response(system_prompt2, image_path, tmp).replace('\n\n', ' ')
        st.write('\n ',r)
        response2 += f'{r} \n'
    chat_history.append({"role": "assistant", "content": response2})

    system_prompt3 = f"""Determine whether the situation in the image follows or violates: "{hazard_rule}" \n\nContext: \n{response2}.

Rule Assessment:
    Rule 1: [Followed/Violated – Reason]
    Rule 2: [Followed/Violated – Reason]
    ...
"""

    chat_history.append({"role": "user", "content": system_prompt3})
    response3 = get_image_response(system_prompt3, image_path, chat_history)
    chat_history.append({"role": "assistant", "content": response3})

    st.write('\n\n ### Step 3 Evaluate Safety Rule and Hazard \n',response3)

    system_prompt4 = f"""Provide your answer in JSON format as follows:
    
    {{
        "rationale": "A concise explanation that describes the visible content of the image and clearly explains whether each safety rule is being followed, violated, or not applicable based solely on the image. Justify the overall status (Hazard/Safe only) based on visual evidence and rule relevance. Classify 'hazard' status if any one of the applicable rule is not followed.",
        "compliance": "Answer Followed/Violated/Not Applicable for each safety rule category: {{"Rule 1: ..." : "Followed" | "Violated" | "Not Applicable", "Rule 2: ...": "Followed" | "Violated" | "Not Applicable", "Rule 3: ...": "Followed" | "Violated" | "Not Applicable", "Rule 4: ...": "Followed" | "Violated" | "Not Applicable", "Rule 5: ...": "Followed" | "Violated" | "Not Applicable"}}",
        "status": "Hazard" | "Safe"
    }}

"""

    chat_history.append({"role": "user", "content": system_prompt4})
    response4 = get_image_response(system_prompt4, image_path, chat_history)
    output_dict = ast.literal_eval(repair_json(response4.replace('```', '')))
    status = output_dict['status']
    st.write('\n\n ### Step 4 Final Decision \n **Hazard** :', status)
    st.write('**Safety Rule Compliance**: ', output_dict['compliance'])
    st.write('**Rationale**: ', output_dict['rationale'])

    return [response1, response2, response3, response4]

st.set_page_config(layout="centered")
st.sidebar.title("Hazard Detection System")
domain = st.sidebar.selectbox("Select Domain", ["Warehouse", "Construction", "Traffic"])
st.title(f"{domain} Hazard Detection")

base_dir = f"{DATA_DIR}{domain.lower()}"

image_data = []
for rule_dir in sorted(os.listdir(base_dir)):
    rule_path = os.path.join(base_dir, rule_dir)
    if os.path.isdir(rule_path):
        try:
            rule_name, label = rule_dir.rsplit("_", 1)
        except ValueError:
            rule_name, label = rule_dir, "unknown"
        for fname in os.listdir(rule_path):
            if fname.lower().endswith(("jpg", "jpeg", "png")):
                image_data.append({
                    "path": os.path.join(rule_path, fname),
                    "rule": rule_name.replace("_", " "),  
                    "raw_rule": rule_name,  
                    "label": label,
                    "filename": fname
                })

st.sidebar.subheader("Filter Options")

rule_options = sorted(set(img["rule"] for img in image_data))
rule_filter = st.sidebar.multiselect("Filter by Testing Scenario", rule_options, default=rule_options)

label_options = sorted(set(img["label"] for img in image_data))
label_filter = st.sidebar.multiselect("Filter by Label", label_options, default=label_options, placeholder='1')

filename_filter = st.sidebar.text_input("Filter by Image ID / Filename")

filtered_images = [
    img for img in image_data
    if img["rule"] in rule_filter
    and img["label"] in label_filter
    and filename_filter.lower() in img["filename"].lower()
]

if "prev_filter_count" not in st.session_state:
    st.session_state.prev_filter_count = len(filtered_images)

if st.session_state.prev_filter_count != len(filtered_images):
    st.session_state.image_index = 0
    st.session_state.prev_filter_count = len(filtered_images)

if "image_index" not in st.session_state or st.session_state.image_index >= len(filtered_images):
    st.session_state.image_index = 0


st.subheader("Input Hazard Detection Rules")
hazard_rule = st.text_area("Describe the hazard rules for this domain", rule_description.get(domain.lower(), ""), height=200)

col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    if st.button("Previous") and st.session_state.image_index > 0:
        st.session_state.image_index -= 1
with col3:
    if st.button("Next") and st.session_state.image_index < len(filtered_images) - 1:
        st.session_state.image_index += 1

if filtered_images:

    current = filtered_images[st.session_state.image_index]
    image = Image.open(current["path"])
    # image = image.resize((336, 336), Image.Resampling.LANCZOS)

    col4, col5, col6 = st.columns([1, 2, 1]) 

    with col5:
        st.image(image, caption=current["filename"])

        st.markdown(f"""
        **Rule Name:** `{current["rule"]}`  
        **Label (ground truth):** `{current["label"]}`  
        **Filename:** `{current["filename"]}`
        """)

else:
    st.warning("No images match the selected filters.")

tab1, tab2 = st.tabs(['Multi-step Reasoning', 'Single-step Reasoning'])

if "multi_output" not in st.session_state:
    st.session_state.multi_output = {}

if "single_output" not in st.session_state:
    st.session_state.single_output = {}

with tab1:
    if st.button("Run Multi-step"):
        with st.status("Running") as status:
            output = get_multi_llava_output(current["path"], hazard_rule)
            status.update(label="Completed", state="complete", expanded=False)
        output_dict = ast.literal_eval(repair_json(output[-1].replace('```', '')))
        st.session_state.multi_output[current["path"]] = output_dict

    if current["path"] in st.session_state.multi_output:
        output_dict = st.session_state.multi_output[current["path"]]
        status = output_dict['status']
        st.markdown("### Status:")
        if status == "Hazard":
            st.error("🔴 Hazard")
        else:
            st.success("🟢 Safe")

        st.markdown("### Rationale:")
        st.info(output_dict['rationale'])

        st.markdown("### Safety Rule Compliance:")
        st.write(output_dict['compliance'])


with tab2:
    
    if st.button("Run Single-step"):
        with st.status("Running") as status:
            output = get_single_llava_output(current["path"], hazard_rule)
            status.update(label="Completed", state="complete", expanded=False)

        output_dict = ast.literal_eval(repair_json(output.replace('```', '')))
        print(output_dict)
        st.session_state.single_output[current["path"]] = output_dict

    if current["path"] in st.session_state.single_output:
        output_dict = st.session_state.single_output[current["path"]]
        status = output_dict['status']
        st.markdown("### Status:")
        if status == "Hazard":
            st.error("🔴 Hazard")
        else:
            st.success("🟢 Safe")
            
        st.markdown("### Rationale:")
        st.info(output_dict['rationale'])

        st.markdown("### Safety Rule Compliance:")
        st.write(output_dict['compliance'])


