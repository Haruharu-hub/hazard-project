import os
import re
from collections import defaultdict
import pandas as pd

DATASET_ROOT = "data/processed_images"
README_PATH = "README.md"
SECTION_HEADER = "#### Images Statistics"
ANNOTATION_SECTION_HEADER = "#### Annotation Statistics"
LABELS = {0: "Complied", 1: "Not Applicable", 2: "Violated"} 

def normalize_rule(rule_label):
    *rule_parts, label = rule_label.split('_')
    rule = ' '.join(rule_parts).replace('-', ' ').title()
    return rule, int(label)

def collect_stats():
    stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    total_images = 0
    total_images_per_domain = dict()

    for domain in os.listdir(DATASET_ROOT):
        total_images_per_domain[domain] = 0
        domain_path = os.path.join(DATASET_ROOT, domain)
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
    lines = [
        "| Domain      | Rule                   | Label Distribution | Total |",
        "|-------------|------------------------|--------------------|-------|"
    ]
    for domain, rules in stats.items():
        first = True
        for rule, label_dist in sorted(rules.items()):
            domain_str = domain.capitalize() if first else ""
            dist_str = f"{dict(sorted(label_dist.items()))}"
            total_str = total_images_per_domain[domain] if first else ""
            line = f"| {domain_str:<12}| {rule:<23}| {dist_str:<18} | {total_str:<6}|"
            lines.append(line)
            first = False
    return "\n".join(lines)

def create_annotation_table():

    df = pd.read_csv('data/hazard-project-annotation-cleaned.csv')
    df = df[df['Note'].isna()].copy()
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
