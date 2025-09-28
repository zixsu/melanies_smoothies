import streamlit as st
import requests
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col

# 🍓 App Title & Intro
st.title("🍓 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# 🧑‍🍳 Get user's name
name_on_order = st.text_input("Your name for the order:")
if name_on_order:
    st.write("Smoothie will be prepared for:", name_on_order)

# ✅ Setup Snowflake session (cached)
@st.cache_resource
def create_session():
    connection_parameters = {
        "account": st.secrets["snowflake"]["account"],
        "user": st.secrets["snowflake"]["user"],
        "password": st.secrets["snowflake"]["password"],
        "role": st.secrets["snowflake"]["role"],
        "warehouse": st.secrets["snowflake"]["warehouse"],
        "database": st.secrets["snowflake"]["database"],
        "schema": st.secrets["snowflake"]["schema"],
        "client_session_keep_alive": st.secrets["snowflake"].get("client_session_keep_alive", True),
    }
    return Session.builder.configs(connection_parameters).create()

try:
    session = create_session()

    # 🍍 Load fruit names from Snowflake
    fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME")).to_pandas()
    fruit_names = fruit_df["FRUIT_NAME"].tolist()

    # 🥝 Let user select fruits
    selected_fruits = st.multiselect(
        "Choose up to 5 ingredients:",
        fruit_names,
        max_selections=5
    )

    # 🧠 Map for Fruityvice API name compatibility
    fruit_name_map = {
        "Blueberries": "blueberry",
        "Dragon Fruit": "pitaya",
        "Passion Fruit": "passionfruit",
        "Blackberries": "blackberry",
        "Starfruit": "carambola",
        # Add more mappings as needed
    }

    # 🍊 Show nutrition info for selected fruits
    if selected_fruits:
        for fruit in selected_fruits:
            try:
                fruit_api_name = fruit_name_map.get(fruit, fruit.lower().replace(" ", ""))
                response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_api_name}")
                response.raise_for_status()
                fruit_data = response.json()
                st.write(f"**Nutritional info for {fruit}:**")
                st.json(fruit_data)
            except requests.exceptions.RequestException as e:
                st.warning(f"Could not load data for {fruit}: {str(e)}")

    # 🧃 Submit smoothie order
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

# 🔗 GitHub Repo Link
st.write("Check out the repo: [GitHub](https://github.com/appuv)")
