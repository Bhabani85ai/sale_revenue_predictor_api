
import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend
BACKEND_URL = "http://backend:7860"

# Set the title of the Streamlit app
st.title("Product Store Sales Predictor")


# =========================================================
# Online Prediction
# =========================================================

st.subheader("Sales Revenue Prediction")


# ---------------------------------------------------------
# Product Information
# ---------------------------------------------------------

Product_Id_char = st.selectbox(
    "Product Category Code",
    [
        "FD",
        "DR",
        "NC"
    ]
)

Product_Weight = st.number_input(
    "Product Weight",
    min_value=0.0,
    value=10.0,
    step=0.1
)

Product_Sugar_Content = st.selectbox(
    "Product Sugar Content",
    [
        "Low Sugar",
        "Regular",
        "No Sugar",
        "reg"
    ]
)

Product_Allocated_Area = st.number_input(
    "Product Allocated Area",
    min_value=0.0,
    value=0.05,
    step=0.01
)

Product_Type_Category = st.selectbox(
    "Product Type Category",
    [
        "Perishables",
        "Non Perishables"
    ]
)

Product_MRP = st.number_input(
    "Product MRP",
    min_value=0.0,
    value=100.0,
    step=1.0
)


# ---------------------------------------------------------
# Store Information
# ---------------------------------------------------------

Store_Age_Years = st.number_input(
    "Store Age (Years)",
    min_value=0,
    value=17,
    step=1
)

Store_Size = st.selectbox(
    "Store Size",
    [
        "Small",
        "Medium",
        "High"
    ]
)

Store_Location_City_Type = st.selectbox(
    "Store Location City Type",
    [
        "Tier 1",
        "Tier 2",
        "Tier 3"
    ]
)

Store_Type = st.selectbox(
    "Store Type",
    [
        "Departmental Store",
        "Supermarket Type1",
        "Supermarket Type2",
        "Food Mart"
    ]
)


# =========================================================
# Convert Input into DataFrame
# =========================================================

input_data = pd.DataFrame([{

    "Product_Id_char": Product_Id_char,

    "Product_Weight": Product_Weight,

    "Product_Sugar_Content": Product_Sugar_Content,

    "Product_Allocated_Area": Product_Allocated_Area,

    "Product_Type_Category": Product_Type_Category,

    "Product_MRP": Product_MRP,

    "Store_Age_Years": Store_Age_Years,

    "Store_Size": Store_Size,

    "Store_Location_City_Type": Store_Location_City_Type,

    "Store_Type": Store_Type

}])


# =========================================================
# Single Prediction
# =========================================================

if st.button("Predict Sales Revenue", type="primary"):

    try:

        response = requests.post(
            f"{BACKEND_URL}/v1/revenue",
            json=input_data.to_dict(orient="records")[0],
            timeout=30
        )

        if response.status_code == 200:

            prediction = response.json()[
                "Predicted Product Store Sales Total"
            ]

            st.success(
                f"Predicted Product Store Sales: ₹{prediction:,.2f}"
            )

        else:

            st.error(
                f"Prediction API returned error "
                f"{response.status_code}: {response.text}"
            )

    except requests.exceptions.RequestException as e:

        st.error(
            f"Unable to connect to the prediction API: {e}"
        )


# =========================================================
# Batch Prediction
# =========================================================

st.subheader("Batch Prediction")

uploaded_file = st.file_uploader(
    "Upload CSV file for batch prediction",
    type=["csv"]
)

if uploaded_file is not None:

    if st.button("Predict Batch", type="primary"):

        try:

            response = requests.post(
                f"{BACKEND_URL}/v1/revenuebatch",
                files={"file": uploaded_file},
                timeout=60
            )

            if response.status_code == 200:

                predictions = response.json()

                st.success(
                    "Batch predictions completed!"
                )

                # Convert response to DataFrame
                predictions_df = pd.DataFrame(predictions)

                st.dataframe(
                    predictions_df,
                    use_container_width=True
                )

                # Download predictions
                csv = predictions_df.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    label="Download Predictions CSV",
                    data=csv,
                    file_name="SuperKart_Sales_Predictions.csv",
                    mime="text/csv"
                )

            else:

                st.error(
                    f"Batch prediction API returned error "
                    f"{response.status_code}: {response.text}"
                )

        except requests.exceptions.RequestException as e:

            st.error(
                f"Unable to connect to the prediction API: {e}"
            )
