# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# --------------------------------------------------
# App Header
# --------------------------------------------------
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# --------------------------------------------------
# Customer name
# --------------------------------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# --------------------------------------------------
# Snowflake connection (Streamlit NOT in Snowflake)
# --------------------------------------------------
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# --------------------------------------------------
# Pull fruit options (DISPLAY vs SEARCH)
# --------------------------------------------------
fruit_df = session.table(
    "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

fruit_rows = fruit_df.collect()

# Build display list and lookup dictionary
fruit_display_list = [row["FRUIT_NAME"] for row in fruit_rows]

search_lookup = {
    row["FRUIT_NAME"]: row["SEARCH_ON"]
    for row in fruit_rows
}

# --------------------------------------------------
# Ingredient selection (limit = 5)
# --------------------------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_display_list,
    max_selections=5
)

# --------------------------------------------------
# Show SmoothieFroot nutrition info per ingredient
# --------------------------------------------------
if ingredients_list:
    for fruit in ingredients_list:

        search_term = search_lookup.get(fruit)

        st.subheader(f"{fruit} Nutrition Information")

        if search_term:
            response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_term}"
            )

            if response.status_code == 200:
                st.dataframe(
                    response.json(),
                    use_container_width=True
                )
            else:
                st.warning("Sorry, that fruit is not in the SmoothieFroot database.")
        else:
            st.warning("Sorry, that fruit is not available for lookup.")

# --------------------------------------------------
# Submit Order
# --------------------------------------------------
if ingredients_list and name_on_order:

    ingredients_string = " ".join(ingredients_list)

    insert_stmt = (
        "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER) "
        f"VALUES ('{ingredients_string}', '{name_on_order}')"
    )

    if st.button("Submit Order"):
        session.sql(insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")
