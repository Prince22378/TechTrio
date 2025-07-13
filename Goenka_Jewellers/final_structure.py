import pandas as pd

# === File paths ===
input_file = 'v3.csv'
output_file = 'output_transformed.csv'

# === Read CSV and clean column names ===
df = pd.read_csv(input_file)
df.columns = df.columns.str.strip()

# === Output structure ===
base_columns = [
    "SKU", "Cost", "Mrp", "Price", "Quantity", "Inventory Location",
    "Primary keywords", "Secondary keywords", "Copy Attribute From SKU",
    "Attr-STATUS", "Attr-COLOUR STONE", "Attr-GRADE", "Attr-Shape",
    "Attr-Dia Wt(CT)", "Attr-Dia Pc", "Attr-Age group", "Attr-Case color",
    "Attr-Material", "Attr-Target gender", "Attr-Jewelry type",
    "Attr-Color", "Attr-Band color", "Attr-Ring Size", "Attr-GOLD WEIGHT-14K",
    "Attr-DIAMOND WEIGHT", "Attr-GOLD WEIGHT-18K", "Attr-Type",
    "Attr-GOLD WEIGHT", "Attr-IGI CERTIFICATE", "Attr-COLOUR & PURITY",
    "Attr-Gr.Wt(GM)", "Attr-N.Wt(GM)", "Option1-Name", "Option1-Value",
    "Option2-Name", "Option2-Value", "Option3-Name", "Option3-Value",
    "Variant-sku", "Image-1", "Image-2", "Image-3", "Image-4", "Image-5",
    "Image-6", "Folder"
]
output_columns = ["URL", "Product Name"] + base_columns

# === Build output rows ===
rows = []
grouped = df.groupby("Product Name", sort=False)

for _, group in grouped:
    for idx, (_, r) in enumerate(group.iterrows()):
        new_row = {col: "" for col in output_columns}

        # Basic product info
        new_row["URL"] = r.get("URL", "")
        new_row["Product Name"] = r.get("Product Name", "")
        new_row["Mrp"] = r.get("MRP", "")
        new_row["Price"] = r.get("Price", "")
        new_row["Quantity"] = 1
        new_row["Primary keywords"] = r.get("Primary keywords", "")
        new_row["Secondary keywords"] = r.get("Secondary keywords", "")

        # SKU logic
        if idx == 0:
            new_row["SKU"] = r.get("newSKU", "")
            new_row["Variant-sku"] = ""
        else:
            new_row["SKU"] = ""
            new_row["Variant-sku"] = r.get("newSKU", "")

        # Attributes
        new_row["Attr-Shape"] = r.get("type", "")
        new_row["Attr-Dia Wt(CT)"] = r.get("Total Diamond Weight", "")
        new_row["Attr-Dia Pc"] = r.get("Total Diamond Count", "")
        new_row["Attr-Gr.Wt(GM)"] = r.get("Gross Weight", "")
        new_row["Attr-N.Wt(GM)"] = r.get("Net Weight(Gold Wt)", "")
        new_row["Attr-Jewelry type"] = r.get("type", "")
        new_row["Attr-Type"] = ""  # leave empty as instructed
        new_row["Attr-Color"] = ""  # leave empty as instructed

        # Options
        new_row["Option1-Name"] = "Purity"
        new_row["Option1-Value"] = r.get("type", "")
        new_row["Option2-Name"] = "Color"
        new_row["Option2-Value"] = r.get("color", "")

        # Category/folder
        new_row["Folder"] = r.get("Category", "")

        # Images
        new_row["Image-1"] = r.get("image_1", "")
        new_row["Image-2"] = r.get("image_2", "")
        new_row["Image-3"] = r.get("image_3", "")
        new_row["Image-4"] = r.get("image_4", "")
        new_row["Image-5"] = r.get("image_5", "")
        new_row["Image-6"] = r.get("image_6", "")

        rows.append(new_row)

# === Write output ===
df_out = pd.DataFrame(rows, columns=output_columns)
df_out.to_csv(output_file, index=False)

print(f"✅ Done! Transformed variant-friendly file saved as '{output_file}'.")
