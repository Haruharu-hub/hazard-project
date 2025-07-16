import os
import re
from collections import defaultdict

# Your dataset root
DATASET_ROOT = "data/processed_images"
README_PATH = "README.md"
SECTION_HEADER = "### 3. Current Dataset Statistics"

def normalize_rule(rule_label):
    *rule_parts, label = rule_label.split('_')
    rule = ' '.join(rule_parts).replace('-', ' ').title()
    return rule, int(label)

def collect_stats():
    stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    total_images = 0

    for domain in os.listdir(DATASET_ROOT):
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
            total_images += image_count

    return stats, total_images

def format_table(stats):
    lines = [
        "| Domain      | Rule                  | Label Distribution |",
        "|-------------|-----------------------|---------------------|"
    ]
    for domain, rules in stats.items():
        first = True
        for rule, label_dist in sorted(rules.items()):
            domain_str = domain.capitalize() if first else ""
            dist_str = f"{dict(sorted(label_dist.items()))}"
            line = f"| {domain_str:<11}| {rule:<23}| {dist_str:<20} |"
            lines.append(line)
            first = False
    return "\n".join(lines)

def update_readme(table_md, total_images):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        rf"(### 3\. Current Dataset Statistics\n)(.*?)(\*\*Total images\*\*: \d+)",
        re.DOTALL,
    )

    new_section = f"{SECTION_HEADER}\n\n{table_md}\n\n**Total images**: {total_images}"
    updated_content = re.sub(pattern, new_section, content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)

def main():
    stats, total_images = collect_stats()
    table_md = format_table(stats)
    update_readme(table_md, total_images)

if __name__ == "__main__":
    main()
