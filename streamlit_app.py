# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched

# --------------------------------------------------
# Page Title
# --------------------------------------------------
st.title("🥤 Customize your own smoothie")

st.write("Choose the fruits you want for your custom smoothie")

# --------------------------------------------------
# Get Snowflake session (SiS / SniS compatible)
# --------------------------------------------------
session = get_active_session()

# --------------------------------------------------
# Load Orders that are NOT NULL
# --------------------------------------------------
orders_df = (
    session
    .table("SMOOTHIES.PUBLIC.ORDERS")
    .select(
        col("ORDER_UID"),
        col("ORDER_FILLED"),
        col("NAME_ON_ORDER"),
        col("INGREDIENTS")
    )
    .order_by(col("ORDER_UID"))
)

# Convert to Pandas for editing
orders_pd = orders_df.to_pandas()

# --------------------------------------------------
# Editable table
# --------------------------------------------------
edited_df = st.data_editor(
    orders_pd,
    disabled=["ORDER_UID", "NAME_ON_ORDER", "INGREDIENTS"],
    use_container_width=True
)

# --------------------------------------------------
# Submit button
# --------------------------------------------------
submitted = st.button("Submit")

if submitted:
    try:
        og_dataset = session.table("SMOOTHIES.PUBLIC.ORDERS")
        edited_dataset = session.create_dataframe(edited_df)

        og_dataset.merge(
            edited_dataset,
            og_dataset["ORDER_UID"] == edited_dataset["ORDER_UID"],
            [
                when_matched().update(
                    {"ORDER_FILLED": edited_dataset["ORDER_FILLED"]}
                )
            ]
        )

        st.success("Order(s) updated!")

    except Exception as e:
        st.error("Something went wrong while updating orders.")
