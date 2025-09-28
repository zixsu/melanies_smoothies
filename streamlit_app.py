import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Title
st.title("🍺 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Your name for the order:")
if name_on_order:
    st.write("The smoothie is ordered by:", name_on_order)

try:
    # ✅ Connect to Snowflake using Streamlit Secrets
    cnx = st.connection("snowflake", type="snowflake")
    session = cnx.session()

    # Get fruit options
    fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME")).to_pandas()
    fruit_names = fruit_df["FRUIT_NAME"].tolist()

    # Show fruit table (optional)
    st.dataframe(fruit_df, use_container_width=True)

    # User selection
    ind = st.multiselect("Choose up to 5 ingredients:", fruit_names, max_selections=5)

    # Fruityvice API info
    if ind:
        st.subheader("🔍 Nutritional Info")
        for fruit in ind:
            try:
                formatted_name = fruit.lower().replace(" ", "-")
                url = f"https://fruityvice.com/api/fruit/{formatted_name}"
                response = requests.get(url)
                response.raise_for_status()
                st.write(f"**{fruit}**")
                st.json(response.json())
            except requests.exceptions.RequestException:
                st.warning(f"Could not load data for {fruit}")

    # Submit button
    if st.button("Blend My Smoothie!"):
        if ind and name_on_order:
            ingredients_string = ', '.join(ind)
            insert_sql = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            session.sql(insert_sql).collect()
            st.success(f"Smoothie for **{name_on_order}** is ordered! ✅")
        elif not name_on_order:
            st.info("Please enter your name before submitting.")
        elif not ind:
            st.info("Please select at least one fruit.")

except Exception as e:
    st.error(f"An error occurred: {e}")

st.write("Check out the repo: [GitHub](https://github.com/appuv)")
