# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# --------------------------------------------------
# Page Title
# --------------------------------------------------
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want for your custom smoothie")

# --------------------------------------------------
# Name on Order
# --------------------------------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# --------------------------------------------------
# Snowflake Connection (Streamlit not in Snowflake)
# --------------------------------------------------
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# --------------------------------------------------
# Get FRUIT_NAME and SEARCH_ON from Snowflake
# --------------------------------------------------
# Get FRUIT_NAME and SEARCH_ON from Snowflake
my_dataframe = (
    session
    .table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Convert the Snowpark DataFrame to a Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Display it so we can verify SEARCH_ON values
st.dataframe(pd_df, use_container_width=True)

# Pause execution so we can focus on this step
st.stop()


# --------------------------------------------------
# (THIS RUNS LATER — after removing st.stop())
# --------------------------------------------------

# Convert Snowpark DF → Pandas DF
pd_df = my_dataframe.to_pandas()

# --------------------------------------------------
# Ingredient Selection (Max 5)
# --------------------------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # ✅ Get SEARCH_ON value using pandas loc / iloc
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        # ✅ This text should appear exactly like the screenshot
        st.write(
            "The search value for ",
            fruit_chosen,
            " is ",
            search_on,
            "."
        )

        # ✅ Nutrition section
        st.subheader(f"{fruit_chosen} Nutrition Information")

        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        if response.status_code == 200:
            st.dataframe(
                response.json(),
                use_container_width=True
            )
        else:
            st.warning("Sorry, that fruit is not in the SmoothieFroot database.")


# --------------------------------------------------
# Submit Order
# --------------------------------------------------
if ingredients_list and name_on_order:

    ingredients_string = ingredients_string.strip()

    insert_stmt = (
        "INSERT INTO SMOOTHIES.PUBLIC.ORDERS "
        "(ingredients, name_on_order) "
        f"VALUES ('{ingredients_string}', '{name_on_order}')"
    )

    if st.button("Submit Order"):
        session.sql(insert_stmt).collect()
        st.success("Order(s) updated!")
