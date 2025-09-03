import os
import re
from collections import defaultdict
import pandas as pd

DOWNLOADED_DIR = "data/downloaded_images"
PROCESSED_DIR = "data/processed_images"
ANNOTATION_FILE = 'data/experimentation/hazard-project-annotation-cleaned.xlsx'
README_PATH = "README.md"
SECTION_HEADER = "#### Images Statistics"
ANNOTATION_SECTION_HEADER = "#### Annotation Statistics"
LABELS = {0: "Complied", 1: "Violated", 2: "Not Applicable"} 

def normalize_rule(rule_label):
    *rule_parts, label = rule_label.split('_')
    rule = ' '.join(rule_parts).replace('-', ' ').title()
    return rule, int(label)

from collections import defaultdict
import os

def count_images_by_domain_and_rule(root_dir):
    counts = defaultdict(lambda: defaultdict(int))

    for domain in os.listdir(root_dir):
        domain_path = os.path.join(root_dir, domain)
        if not os.path.isdir(domain_path):
            continue

        for rule_folder in os.listdir(domain_path):
            rule_path = os.path.join(domain_path, rule_folder)
            if not os.path.isdir(rule_path):
                continue

            rule_parts = rule_folder.split('_')
            if rule_parts[-1].isdigit():
                rule_name = '_'.join(rule_parts[:-1])
            else:
                rule_name = rule_folder

            count = len([
                f for f in os.listdir(rule_path)
                if os.path.isfile(os.path.join(rule_path, f)) and f.lower().startswith('000')
            ])

            counts[domain][rule_name] += count

    return counts


def collect_stats():
    stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    total_images = 0
    total_images_per_domain = dict()

    for domain in os.listdir(PROCESSED_DIR):
        total_images_per_domain[domain] = 0
        domain_path = os.path.join(PROCESSED_DIR, domain)
        if not os.path.isdir(domain_path):
            continue

        for rule_label in os.listdir(domain_path):
            rule_path = os.path.join(domain_path, rule_label)
            if not os.path.isdir(rule_path):
                continue

            rule_name, label = normalize_rule(rule_label)
            image_count = len([
                f for f in os.listdir(rule_path)
                if os.path.isfile(os.path.join(rule_path, f))
            ])
            stats[domain][rule_name][label] += image_count
            total_images_per_domain[domain] += image_count
            total_images += image_count

    return stats, total_images_per_domain, total_images

def format_table(stats, total_images_per_domain):

    processed_counts = count_images_by_domain_and_rule(PROCESSED_DIR)
    downloaded_counts = count_images_by_domain_and_rule(DOWNLOADED_DIR)

    lines = [
        "| Domain      | Rule                   | Downloaded | Processed | Matched | Label Distribution | Total |",
        "|-------------|------------------------|------------|-----------|---------|--------------------|-------|"
    ]

    for domain, rules in stats.items():
        first = True

        domain_total = 0

        for rule, label_dist in sorted(rules.items()):
            rule_label = f"{rule.replace(' ', '_')}"  
            domain_total += processed_counts[domain].get(rule_label, 0)

        for rule, label_dist in sorted(rules.items()):

            rule_label = f"{rule.replace(' ', '_')}"  
            downloaded = downloaded_counts[domain].get(rule_label, 0)
            processed = processed_counts[domain].get(rule_label, 0)
            match = "✅" if downloaded == processed else "❌"

            dist_str = ", ".join(f"{lbl}: {cnt}" for lbl, cnt in sorted(label_dist.items()))
            
            domain_total_str = domain_total if first else ""

            domain_str = domain.capitalize() if first else ""
            line = f"| {domain_str:<12}| {rule:<23}| {downloaded:<10} | {processed:<9} | {match:<5} | {dist_str:<27} | {domain_total_str:<5} |"
            lines.append(line)
            first = False

    return "\n".join(lines)

def create_annotation_table():

    # df = pd.read_csv('data/hazard-project-annotation-cleaned.csv')
    # df = df[df['Note'].isna()].copy()
    df = pd.read_excel(ANNOTATION_FILE)
    grouped = df.groupby(['Domain', 'Rule'])['Label'].value_counts().unstack(fill_value=0)

    grouped['Total'] = grouped.sum(axis=1)
    grouped = grouped.reset_index()

    label_cols = ['Complied', 'Not Applicable', 'Violated']
    for col in label_cols:
        if col not in grouped.columns:
            grouped[col] = 0
    grouped = grouped[['Domain', 'Rule'] + label_cols + ['Total']]

    lines = [
        "| Domain  | Rule                | Complied | Not Applicable | Violated | Total |",
        "|---------|---------------------|----------|----------------|----------|-------|"
    ]

    last_domain = None
    for _, row in grouped.iterrows():
        domain = row['Domain']
        rule = row['Rule']
        comp, na, viol, total = row['Complied'], row['Not Applicable'], row['Violated'], row['Total']

        domain_display = domain if domain != last_domain else ""

        lines.append(f"| {domain_display:<7} | {rule:<20} | {comp:^8} | {na:^14} | {viol:^8} | {total:^5} |")
        last_domain = domain

    total_row = grouped[label_cols + ['Total']].sum().astype(int)
    lines.append(f"| **Total** |                     | {total_row['Complied']:^8} | {total_row['Not Applicable']:^14} | {total_row['Violated']:^8} | {total_row['Total']:^5} |")

    return "\n".join(lines)


def update_readme(table_md, total_images):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        rf"({re.escape(SECTION_HEADER)}\n)(.*?)(\*\*Total images\*\*: \d+)",
        re.DOTALL,
    )

    new_section = f"{SECTION_HEADER}\n\n{table_md}\n\n**Total images**: {total_images}"
    updated_content = re.sub(pattern, new_section, content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)

def update_annotation_section(table_md):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        rf"({re.escape(ANNOTATION_SECTION_HEADER)}\n)(.*?)(\n\n|$)",
        re.DOTALL
    )

    new_section = f"{ANNOTATION_SECTION_HEADER}\n\n{table_md}\n\n"

    if pattern.search(content):
        updated_content = pattern.sub(new_section, content)
    else:
        updated_content = content.strip() + "\n\n" + new_section

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)

def main():
    stats, total_images_per_domain, total_images = collect_stats()
    table_md = format_table(stats, total_images_per_domain)
    update_readme(table_md, total_images)
    table_md = create_annotation_table()
    update_annotation_section(table_md)

if __name__ == "__main__":
    main()
