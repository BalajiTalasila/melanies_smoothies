# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# --------------------------------------------------
# Page Title
# --------------------------------------------------
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# --------------------------------------------------
# Name on Order
# --------------------------------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# --------------------------------------------------
# Snowflake Connection (SniS)
# --------------------------------------------------
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# --------------------------------------------------
# Get Fruit Options from Snowflake
# --------------------------------------------------
fruit_df = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col("FRUIT_NAME"))
fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# --------------------------------------------------
# Ingredient Selection (Max 5)
# --------------------------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# --------------------------------------------------
# SmoothieFroot Nutrition Section
# --------------------------------------------------
if ingredients_list:

    for fruit_chosen in ingredients_list:

        st.subheader(f"{fruit_chosen} Nutrition Information")

        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}"
        )

        if response.status_code == 200:
            st.dataframe(
                response.json(),
                use_container_width=True
            )
        else:
            st.warning("Sorry, that fruit is not in our database.")

# --------------------------------------------------
# Submit Order
# --------------------------------------------------
if ingredients_list and name_on_order:

    ingredients_string = " ".join(ingredients_list)

    insert_stmt = (
        "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (ingredients, name_on_order) "
        f"VALUES ('{ingredients_string}', '{name_on_order}')"
    )

    if st.button("Submit Order"):
        session.sql(insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")
