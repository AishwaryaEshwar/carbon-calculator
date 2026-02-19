import re
import pdfplumber
import pandas as pd

def process_files(pdf_path, co2_path):
    output_excel = "outputs/PBIC_Updated.xlsx"
    final_output = "outputs/Final_CO2_Recipes.xlsx"

    data = []

    keyname_re = re.compile(r'Key Name:\s+(\d+)\s+(.*)')
    item_re = re.compile(
        r'^(.*?)\s+([\d.]+)?\s*([A-Za-z\s.]+)?\s+([\d.]+)?\s+([\d.]+)?\s+(\d{10})$'
    )

    with pdfplumber.open(pdf_path) as pdf:
        current_keynum = ''
        current_keyname = ''

        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            for line in text.split('\n'):
                line = line.strip()

                if line.startswith('Key Name:'):
                    match = keyname_re.search(line)
                    if match:
                        current_keynum = match.group(1)
                        current_keyname = match.group(2)
                else:
                    match = item_re.match(line)
                    if match:
                        ingredient = match.group(1).strip()
                        quantity = match.group(2) or ''
                        unit = match.group(3) or ''
                        net_weight = match.group(4) or ''
                        unit_cost = match.group(5) or ''
                        item_code = match.group(6) or ''

                        data.append({
                            'Key Number': current_keynum,
                            'Recipe Name': current_keyname,
                            'Ingredient': ingredient,
                            'Quantity': quantity,
                            'Unit': unit,
                            'Net Weight': net_weight,
                            'Unit Cost': unit_cost,
                            'Item Code': item_code
                        })

    df = pd.DataFrame(data)
    df.to_excel(output_excel, index=False)

    # Carbon Calculation

    df_recipe = df.copy()  
    df_co2 = pd.read_excel(co2_path)

    df_recipe['Net Weight'] = pd.to_numeric(df_recipe['Net Weight'], errors='coerce').fillna(0)
    df_co2['CO2 Value'] = pd.to_numeric(df_co2['CO2 Value'], errors='coerce').fillna(0)

    df_merged = pd.merge(df_recipe, df_co2[['Ingredient', 'CO2 Value']], on='Ingredient', how='left').fillna(0)

    df_merged['Weighted gCO2e'] = df_merged['Net Weight'] * df_merged['CO2 Value']

    total_weights = df_merged.groupby('Key Number')['Net Weight'].sum().reset_index()
    total_weights.rename(columns={'Net Weight': 'Total Weight'}, inplace=True)

    total_weighted_co2 = df_merged.groupby('Key Number')['Weighted gCO2e'].sum().reset_index()
    total_weighted_co2.rename(columns={'Weighted gCO2e': 'Total Weighted gCO2e'}, inplace=True)

    df_final = pd.merge(total_weights, total_weighted_co2, on='Key Number')

    df_final['Weighted Avg gCO2e (score)'] = df_final['Total Weighted gCO2e'] / df_final['Total Weight']

    df_names = df_recipe[['Key Number', 'Recipe Name']].drop_duplicates()
    df_final = pd.merge(df_final, df_names, on='Key Number', how='left')

    def label_carbon(score):
        if score <= 2.5:
            return 'L'
        elif score <= 5:
            return 'M'
        else:
            return 'H'

    df_final['Carbon Label'] = df_final['Weighted Avg gCO2e (score)'].apply(label_carbon)

    df_final = df_final[['Key Number', 'Recipe Name', 'Total Weight', 'Total Weighted gCO2e',
                         'Weighted Avg gCO2e (score)', 'Carbon Label']]

    df_final.to_excel(final_output, index=False)

    return final_output
