import streamlit as st
from snowflake.snowpark.functions import col

st.title("🍺 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Get name on order
name_on_order = st.text_input("Your name for the order:")
if name_on_order:
    st.write("The smoothie is ordered by:", name_on_order)

try:
    # Connect to Snowflake via Streamlit connection
    cnx = st.connection("snowflake")
    session = cnx.session()

    # Load fruit options
    fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME")).to_pandas()
    fruit_names = fruit_df["FRUIT_NAME"].tolist()

    # Show fruits table (optional)
    st.dataframe(fruit_df, use_container_width=True)

    # Select fruits (limit to 5 max)
    selected_fruits = st.multiselect(
        "Choose up to 5 ingredients:",
        fruit_names,
        max_selections=5
    )

    # On button click, insert order
    if st.button("Blend My Smoothie!"):
        if selected_fruits and name_on_order:
            ingredients_string = ', '.join(selected_fruits)

            st.write("### 🥤 Your Smoothie Will Include:")
            st.write(ingredients_string)

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

st.write("Check out the repo: [GitHub](https://github.com/appuv)")
