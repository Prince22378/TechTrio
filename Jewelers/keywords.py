# nan checks
# category
# sku naming
# keywords
# final_structure

import pandas as pd
import random

# 1) Read your data
df = pd.read_csv('v2.csv')

# 2) Define your updated keyword templates
primary_templates = [
    'lab grown diamonds Kolkata',
    'diamond {category}',
    'buy {category} in india',
    'diamond price in india',
    'diamond {category} india',
    'buy diamond jewelry online',
    'certified diamond jewelry',
    'buy diamond {category}',
    'designer {category} jewelry',
]

secondary_templates = [
    'lab grown diamonds Kolkata',
    'diamond jewelry price in india',
    'buy {category} in india',
    'luxury diamond {category}',
    'affordable {category} jewelry',
    'high quality {category}',
    'best diamond deals',
    'sustainable diamond jewelry',
    'lab diamonds',
    'premium diamonds',
]

# 3) Helper to format + sample n keywords
def make_keywords(row, templates, n=6):
    all_phrases = [tpl.format(category=row['Category']) 
                   for tpl in templates]
    chosen = random.sample(all_phrases, n)
    return ', '.join(chosen)

random.seed(123)

# 4) Generate the two new columns
df['Primary keywords'] = df.apply(lambda r: make_keywords(r, primary_templates, 6), axis=1)
df['Secondary keywords'] = df.apply(lambda r: make_keywords(r, secondary_templates, 4), axis=1)

# 5) Write out
df.to_csv('v3.csv', index=False)

print("Generated 'primary_keywords' and 'secondary_keywords' with 6 varied SEO phrases each.")
