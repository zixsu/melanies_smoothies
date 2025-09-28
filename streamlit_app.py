import streamlit as st
import requests
from snowflake.snowpark.functions import col
from snowflake.snowpark.session import Session

# Title & intro
st.title("🍺 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# ✅ Display API response from SmoothieFroot
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response.json())

sf_df = pd.json_normalize(smoothiefroot_response.json())

st.dataframe(sf_df)

name_on_order = st.text_input("Your name for the order:")
if name_on_order:
    st.write("The smoothie is ordered by:", name_on_order)

# Load session configuration from Streamlit secrets
@st.cache_resource
def create_session():
    connection_parameters = {
        "account": st.secrets["snowflake"]["account"],
        "user": st.secrets["snowflake"]["user"],
        "password": st.secrets["snowflake"]["password"],
        "role": st.secrets["snowflake"]["role"],
        "warehouse": st.secrets["snowflake"]["warehouse"],
        "database": st.secrets["snowflake"]["database"],
        "schema": st.secrets["snowflake"]["schema"]
    }
    return Session.builder.configs(connection_parameters).create()

try:
    session = create_session()

    # Load fruit names
    fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME")).to_pandas()
    fruit_names = fruit_df["FRUIT_NAME"].tolist()

    # Select fruits
    selected_fruits = st.multiselect(
        "Choose up to 5 ingredients:",
        fruit_names,
        max_selections=5
    )

    # 🧃 Blend button to submit order
    if st.button("Blend My Smoothie!"):
        if selected_fruits and name_on_order:
            ingredients_string = ', '.join(selected_fruits)

            insert_sql = f"""
                INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                VALUES ('{ingredients_string}', '{name_on_order}')
            """
            session.sql(insert_sql).collect()

            st.success(f"Smoothie for **{name_on_order}** is ordered! ✅")

        elif not selected_fruits:
            st.info("Please select at least one ingredient to see your smoothie!")
        elif not name_on_order:
            st.info("Please enter a name for the order before submitting!")

except Exception as e:
    st.error(f"An error occurred: {e}")

# Footer
st.write("Check out the repo: [GitHub](https://github.com/zixsu)")
