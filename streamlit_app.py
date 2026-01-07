# Import python packages
import streamlit as st
import requests
import pandas as pd
import numpy as np

from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f"Example Streamlit App :cup_with_straw: {st.__version__}")
st.write(
    """Replace this example with your own code!
    **And if you're new to Streamlit,** check
    out our easy-to-follow guides at
    [docs.streamlit.io](https://docs.streamlit.io).
    """
)

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be', name_on_order)

# Snowflake connection (Streamlit Cloud / SniS)
cnx = st.connection("snowflake", type="snowflake")
session = cnx.session()

# Get fruit options
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col("FRUIT_NAME"))

# Convert Snowpark DF → Python list
fruit_list = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Multiselect with limit
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)

# Build ingredients string
if ingredients_list and name_on_order:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    insert_stmt = (
        "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (ingredients, name_on_order) "
        "VALUES ('" + ingredients_string.strip() + "', '" + name_on_order + "')"
    )

    if st.button("Submit Order"):
        session.sql(insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")

# SmoothieFroot nutrition info (correct placement)
smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)

st.dataframe(
    data=smoothiefroot_response.json(),
    use_container_width=True
)
