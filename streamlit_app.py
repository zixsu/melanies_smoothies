import streamlit as st
from snowflake.snowpark.context import get_active_session

# Title & intro
st.title("🍺 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Get name on order
name_on_order = st.text_input("Your name for the order:")
if name_on_order:
    st.write("The smoothie is ordered by:", name_on_order)

# Get Snowflake session
session = get_active_session()

# Load fruit options into pandas DataFrame
fruit_df = session.table("smoothies.public.fruit_options").to_pandas()
fruit_names = fruit_df['FRUIT_NAME'].tolist()

# Show fruit options (optional)
st.dataframe(fruit_df, use_container_width=True)

# Multiselect with max_selections to limit to 5 fruits max
ind = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,
    max_selections=5  # THIS limits selection to max 5
)

# Blend button — insert only once when clicked
if st.button("Blend My Smoothie!"):
    if ind and name_on_order:
        ingredients_string = ', '.join(ind)

        st.write("### 🥤 Your Smoothie Will Include:")
        st.write(ingredients_string)

        # Insert order into Snowflake
        insert_sql = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(insert_sql).collect()

        st.success(f"Smoothie for **{name_on_order}** is ordered! ✅")

    elif not ind:
        st.info("Please select at least one ingredient to see your smoothie!")
    elif not name_on_order:
        st.info("Please enter a name for the order before submitting!")
