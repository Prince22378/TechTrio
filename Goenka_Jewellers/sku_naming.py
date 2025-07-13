import pandas as pd
import re

# Mappings with lowercase keys
Category_MAP = {
    'bracelets': 'BL',
    'pendants': 'PD',
    'earrings': 'ER',
    'nosepin': 'NP',
    'rings': 'RI',
    'necklaces': 'NK',
    'mangalsutra': 'MS',
    'bangles': 'BG',
    'brooch': 'BR',
    'kids': 'KD',
    'cufflinks': 'CF',
    'anklets': 'AK',
    'charms': 'CM',
    'noserings': 'NR',
    'watch accessories': 'WA',
    'drops': 'DR',
    'ear cuffs': 'EC',
    'sui dhaga': 'SD',
    'jhumkas': 'JK',
    'sets': 'SE',
    'stud': 'ST',
    'hoops': 'HP',
    'band': 'BD'
}

COLOR_MAP = {
    'yellow': 'Y',
    'rose': 'R',
    'white': 'W',
    'platinum': 'P'
}

# === Extract category code from category name ===
def extract_Category_code(name):
    name = str(name).lower()
    for key in Category_MAP:
        if key in name:
            return Category_MAP[key]
    return 'XX'

# === Extract purity (gold type) from metal field like '18K Rose Gold' ===
def extract_gold_type(type_str):
    match = re.search(r'(\d{2})', str(type_str))
    return match.group(1) if match else '00'

# === Extract color code from metal field like '18K Rose Gold' or separate Color column ===
def extract_color_code(color_str):
    if not isinstance(color_str, str):
        return 'X'
    for color, code in COLOR_MAP.items():
        if color in color_str.lower():
            return code
    return 'X'

# === SKU generation logic ===
def generate_newsku_column(df):
    # Step 1: Category code
    df['__CategoryCode'] = df['Category'].apply(extract_Category_code)

    # Step 2: Product Key = category + product name
    df['__ProductKey'] = df['__CategoryCode'] + '||' + df['Product Name']

    # Step 3: Unique sequence number per category
    unique_products = df.drop_duplicates(subset='__ProductKey').copy()
    unique_products['__ProductSeq'] = unique_products.groupby('__CategoryCode').cumcount() + 1

    # Step 4: Padding width for SKU sequence
    counts = unique_products['__CategoryCode'].value_counts().to_dict()
    pad_width = {cat: len(str(count)) for cat, count in counts.items()}

    # Step 5: Merge sequence numbers back
    seq_map = dict(zip(unique_products['__ProductKey'], unique_products['__ProductSeq']))
    df['__SeqNum'] = df['__ProductKey'].map(seq_map)
    df['__PadLen'] = df['__CategoryCode'].map(pad_width)

    # Step 6: Build SKU
    df['newSKU'] = df.apply(lambda row: (
        'GS' +
        row['__CategoryCode'] +
        str(row['__SeqNum']).zfill(row['__PadLen']) +
        extract_gold_type(row['Metal']) + 'K' +
        extract_color_code(row['Color'])
    ), axis=1)

    # Clean temp columns
    df.drop(columns=['__CategoryCode', '__ProductKey', '__SeqNum', '__PadLen'], inplace=True)
    return df

# === Main Execution ===
input_file = 'with_category.csv'
output_file = 'v2.csv'

df = pd.read_csv(input_file)
df = generate_newsku_column(df)
df.to_csv(output_file, index=False)

print(f"✅ 'newSKU' column added and saved to {output_file}")
