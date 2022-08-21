from cProfile import label
import pandas as pd
import streamlit as st

# Datasets
df_expected = pd.read_csv(
    "https://storage.googleapis.com/mojix-devops-wildfire-bucket/analytics/bootcamp_2_0/Bootcamp_DataAnalysis_Expected.csv", encoding="latin-1", dtype=str)
df_counted = pd.read_csv(
    "https://storage.googleapis.com/mojix-devops-wildfire-bucket/analytics/bootcamp_2_0/Bootcamp_DataAnalysis_Counted.csv", encoding="latin-1", dtype=str)

my_cols_selected = ["Retail_Product_Color",
                    "Retail_Product_Level1",
                    "Retail_Product_Level1Name",
                    "Retail_Product_Level2Name",
                    "Retail_Product_Level3Name",
                    "Retail_Product_Level4Name",
                    "Retail_Product_Name",
                    "Retail_Product_SKU",
                    "Retail_Product_Size",
                    "Retail_Product_Style",
                    "Retail_SOHQTY"]


# Tratamiento del dataset counted
df_counted = df_counted.drop_duplicates("RFID")

df_B = df_counted.groupby("Retail_Product_SKU").count(
)[["RFID"]].reset_index().rename(columns={"RFID": "Retail_CCQTY"})

# Tratamiento del dataset expected
df_A = df_expected[my_cols_selected]

# Relacionar ambos datasets tratados
df_discrepancy = pd.merge(df_A, df_B, how="outer", left_on="Retail_Product_SKU",
                          right_on="Retail_Product_SKU", indicator=True)
df_discrepancy['Retail_CCQTY'] = df_discrepancy['Retail_CCQTY'].fillna(0)
df_discrepancy["Retail_CCQTY"] = df_discrepancy["Retail_CCQTY"].astype(int)
df_discrepancy["Retail_SOHQTY"] = df_discrepancy["Retail_SOHQTY"].fillna(
    0).astype(int)

df_discrepancy["Diff"] = df_discrepancy["Retail_CCQTY"] - \
    df_discrepancy["Retail_SOHQTY"]
df_discrepancy.loc[df_discrepancy["Diff"] < 0,
                   "Unders"] = df_discrepancy["Diff"] * (-1)
df_discrepancy["Unders"] = df_discrepancy["Unders"].fillna(0).astype(int)


# Cantidades totales
sqty = df_discrepancy['Retail_SOHQTY'].sum()
cqty = df_discrepancy['Retail_CCQTY'].sum()

# Diferencia total
diff = cqty-sqty

# Productos por su nombre
df_products = df_discrepancy[['Retail_Product_Level1Name',
                              'Retail_SOHQTY', 'Retail_CCQTY']].groupby(
    "Retail_Product_Level1Name").sum()


def create_chart():
    df_products = df_discrepancy[data_display].groupby(
        "Retail_Product_Level1Name").sum()
    container.bar_chart(df_products)
    data_display = ['Retail_Product_Level1Name']


# UI
container = st.container()
container.title("INVENTORY DISCREPANCY")
container.write("Relevant data")
val1, val2, val3 = container.columns(3)
val1.metric(label="SOH INVENTORY", value=sqty)
val2.metric(label="MOJIX INVENTORY", value=cqty)
val3.metric(label="DIFFERENCE", value=diff)

data_showed = container.multiselect(
    "Pick Data to be showed", ['Retail_SOHQTY', 'Retail_CCQTY'])
container.write(data_showed)
data_showed.append('Retail_Product_Level1Name')
container.write(data_showed)

#container.button(label='Create chart', on_click=create_chart)


#container.text('Columns selected:' + ' ' + options)
