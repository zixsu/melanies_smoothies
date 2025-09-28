import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session

# App Title
st.title("🍺 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Get name on order
name_on_order = st.text_input("Your name for the order:")
if name_on_order:
    st.write("The smoothie is ordered by:", name_on_order)

try:
    # Get Snowflake session from st.secrets (already configured)
    session = get_active_session()

    # Load fruit options from Snowflake table
    fruit_df = session.table("smoothies.public.fruit_options").to_pandas()
    fruit_names = fruit_df['FRUIT_NAME'].tolist()

    # Show fruit options table (optional)
    st.dataframe(fruit_df, use_container_width=True)

    # Multiselect input
    ind = st.multiselect(
        'Choose up to 5 ingredients:',
        fruit_names,
        max_selections=5
    )

    # Show fruityvice nutritional info for selected fruits
    if ind:
        st.subheader("🔍 Nutritional Info")
        for fruit in ind:
            try:
                # Format name for API (lowercase and replace spaces with hyphens)
                formatted_name = fruit.lower().replace(" ", "-")
                url = f"https://fruityvice.com/api/fruit/{formatted_name}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                st.write(f"**{fruit}**")
                st.json(data)
            except requests.exceptions.RequestException:
                st.warning(f"Could not load data for {fruit}")

    # Button to place the smoothie order
    if st.button("Blend My Smoothie!"):
        if ind and name_on_order:
            ingredients_string = ', '.join(ind)

            # Insert SQL
            insert_sql = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            session.sql(insert_sql).collect()
            st.success(f"Smoothie for **{name_on_order}** is ordered! ✅")

        elif not ind:
            st.info("Please select at least one ingredient!")
        elif not name_on_order:
            st.info("Please enter a name for the order before submitting!")

except Exception as e:
    st.error(f"An error occurred: {e}")

# GitHub link (optional)
st.write("Check out the repo: [GitHub](https://github.com/appuv)")
