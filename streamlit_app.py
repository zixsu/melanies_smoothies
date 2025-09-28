import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# App title & instructions
st.title("🍺 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Your name for the order:")
if name_on_order:
    st.write("The smoothie is ordered by:", name_on_order)

try:
    # Get Snowflake session (requires st.secrets configured)
    session = get_active_session()

    # Load fruit names from Snowflake
    fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME")).to_pandas()
    fruit_names = fruit_df["FRUIT_NAME"].tolist()

    # Fruit selection
    selected_fruits = st.multiselect("Choose up to 5 ingredients:", fruit_names, max_selections=5)

    # Show nutritional info from Fruityvice API
    if selected_fruits:
        st.subheader("🔍 Nutritional Info")
        for fruit in selected_fruits:
            try:
                # Format fruit name to match API (lowercase, hyphens for spaces)
                formatted_name = fruit.lower().replace(" ", "-")
                url = f"https://fruityvice.com/api/fruit/{formatted_name}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                st.write(f"**{fruit.capitalize()}**")
                st.json(data)
            except requests.exceptions.RequestException:
                st.warning(f"Could not load data for {fruit} (not found in Fruityvice API)")

    # Order button
    if st.button("Blend My Smoothie!"):
        if selected_fruits and name_on_order:
            ingredients_string = ", ".join(selected_fruits)
            insert_sql = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            session.sql(insert_sql).collect()
            st.success(f"Smoothie for **{name_on_order}** is ordered! ✅")
        elif not name_on_order:
            st.info("Please enter your name before submitting.")
        elif not selected_fruits:
            st.info("Please select at least one fruit.")

except Exception as e:
    st.error(f"An error occurred: {e}")

st.write("Check out the repo: [GitHub](https://github.com/appuv)")
