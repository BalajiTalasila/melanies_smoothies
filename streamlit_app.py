# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# App header
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# Customer name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fruit options from Snowflake
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col("FRUIT_NAME"))

# Convert Snowpark DF → Python list
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Multiselect (limit 5)
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# If fruits selected
if ingredients_list and name_on_order:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # SmoothieFroot API call
        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen.lower()
        )

        # ✅ Handle fruits NOT in database (like Ximenia)
        if response.status_code == 200:
            data = response.json()

            # If API returns an error message
            if "error" in data:
                st.dataframe(
                    [{"error": data["error"]}],
                    use_container_width=True
                )
            else:
                st.dataframe(
                    data,
                    use_container_width=True
                )
        else:
            st.dataframe(
                [{"error": "Sorry, that fruit is not in our database."}],
                use_container_width=True
            )

    # Insert order into Snowflake
    insert_stmt = (
        "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER) "
        "VALUES ('" + ingredients_string.strip() + "', '" + name_on_order + "')"
    )

    if st.button("Submit Order"):
        session.sql(insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")
