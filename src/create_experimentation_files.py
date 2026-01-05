import pandas as pd
from sklearn.model_selection import train_test_split

def create_experimentation_files(seed = 42):
    
    domains = ['Traffic', 'Construction', 'Warehouse']
    ANNOTATION_FILE = 'data/annotations/hazard-project-annotation.xlsb.xlsm'

    df = pd.DataFrame()
    for domain in domains:
        tmp = pd.read_excel(ANNOTATION_FILE, sheet_name= f'{domain} Domain')
        df = pd.concat([df,tmp])

    df.to_excel('data/experimentation/hazard-project-annotation-cleaned.xlsx', index = False)

    print('Domain Train Val Test Remaining')

    for domain in domains:
        unique_ids = df[df['Domain'] == domain]['Image ID'].unique()[:50]
        extra_ids = df[df['Domain'] == domain]['Image ID'].unique()[50:]
        train_img_ids, test_img_ids = train_test_split(unique_ids, test_size=0.2, random_state=seed)
        train_img_ids, val_img_ids = train_test_split(train_img_ids, test_size=0.25, random_state=seed)

        train_df = df[(df['Domain'] == domain) & (df['Image ID'].isin(train_img_ids))]
        val_df = df[(df['Domain'] == domain) & (df['Image ID'].isin(val_img_ids))]
        test_df = df[(df['Domain'] == domain) & (df['Image ID'].isin(test_img_ids))]
        if list(extra_ids):
            train_more_df= df[(df['Domain'] == domain) & (df['Image ID'].isin(extra_ids))]

        train_df.to_json(f"data/experimentation/{domain.lower()}-train.jsonl", orient="records", lines=True, force_ascii=False)
        val_df.to_json(f"data/experimentation/{domain.lower()}-val.jsonl", orient="records", lines=True, force_ascii=False)
        test_df.to_json(f"data/experimentation/{domain.lower()}-test.jsonl", orient="records", lines=True, force_ascii=False)
        train_more_df.to_json(f"data/experimentation/{domain.lower()}-train-more.jsonl", orient="records", lines=True, force_ascii=False)

        print(f'{domain}: ', len(train_df), len(val_df), len(test_df), len(train_more_df))

if __name__ == '__main__':
    create_experimentation_files()
