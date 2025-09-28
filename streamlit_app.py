import streamlit as st
import requests
from snowflake.snowpark.functions import col
from snowflake.snowpark.context import get_active_session

# Title & Intro
st.title("🍓 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Your name for the order:")
if name_on_order:
    st.write("Smoothie will be prepared for:", name_on_order)

try:
    # Snowflake session
    session = get_active_session()

    # Load fruit names
    fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME")).to_pandas()
    fruit_names = fruit_df["FRUIT_NAME"].tolist()

    # Select fruits
    selected_fruits = st.multiselect(
        "Choose up to 5 ingredients:",
        fruit_names,
        max_selections=5
    )

    # Display info from Fruityvice for each selected fruit
    if selected_fruits:
        for fruit in selected_fruits:
            try:
                response = requests.get(f"https://fruityvice.com/api/fruit/{fruit}")
                response.raise_for_status()
                fruit_data = response.json()
                st.write(f"**Nutritional info for {fruit.capitalize()}:**")
                st.json(fruit_data)
            except requests.exceptions.RequestException as e:
                st.warning(f"Could not load data for {fruit}: {str(e)}")

    # Button to submit order
    if st.button("Blend My Smoothie!"):
        if selected_fruits and name_on_order:
            ingredients_string = ', '.join(selected_fruits)
            insert_stmt = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            session.sql(insert_stmt).collect()
            st.success(f"Smoothie for **{name_on_order}** is ordered! ✅")
        elif not name_on_order:
            st.info("Please enter your name before submitting.")
        elif not selected_fruits:
            st.info("Please select at least one fruit to create your smoothie.")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")

# Link
st.write("Check out the repo: [GitHub](https://github.com/appuv)")
