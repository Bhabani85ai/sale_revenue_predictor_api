
# Import necessary libraries
import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize Flask application
sale_revenue_predictor_api = Flask("Sale Revenue Predictor")

# Load the trained machine learning model
model = joblib.load("superkart_model.joblib")

# =========================================================
# Health Check
# =========================================================

@sale_revenue_predictor_api.get('/')
def home():
    """
    Health check endpoint.
    """
    return "Welcome to the SuperKart Sale Revenue Prediction API!"


# =========================================================
# Single Prediction
# =========================================================

@sale_revenue_predictor_api.post('/v1/revenue')
def revenue_sales_price():
    """
    Predict Product_Store_Sales_Total for one product/store.
    """

    try:

        # Get JSON data from request
        property_data = request.get_json()

        # Extract predictor variables used during model training
        sample = {
            'Product_Id_char': property_data['Product_Id_char'],
            'Product_Weight': property_data['Product_Weight'],
            'Product_Sugar_Content': property_data['Product_Sugar_Content'],
            'Product_Allocated_Area': property_data['Product_Allocated_Area'],
            'Product_Type_Category': property_data['Product_Type_Category'],
            'Product_MRP': property_data['Product_MRP'],
            'Store_Age_Years': property_data['Store_Age_Years'],
            'Store_Size': property_data['Store_Size'],
            'Store_Location_City_Type': property_data['Store_Location_City_Type'],
            'Store_Type': property_data['Store_Type']
        }

        # Convert input into DataFrame
        input_data = pd.DataFrame([sample])

        # Make prediction
        predicted_sales = model.predict(input_data)[0]

        # Convert prediction to Python float
        predicted_sales = round(float(predicted_sales), 2)

        # Return prediction
        return jsonify({
            'Predicted Product Store Sales Total': predicted_sales
        })

    except Exception as e:

        return jsonify({
            'error': str(e)
        }), 500


# =========================================================
# Batch Prediction
# =========================================================

@sale_revenue_predictor_api.post('/v1/revenuebatch')
def revenue_sales_price_batch():
    """
    Predict Product_Store_Sales_Total for multiple records.
    """

    try:

        # Get uploaded CSV file
        file = request.files['file']

        # Read CSV
        input_data = pd.read_csv(file)

        # Features used during model training
        feature_columns = [
            'Product_Id_char',
            'Product_Weight',
            'Product_Sugar_Content',
            'Product_Allocated_Area',
            'Product_Type_Category',
            'Product_MRP',
            'Store_Age_Years',
            'Store_Size',
            'Store_Location_City_Type',
            'Store_Type'
        ]

        # Check whether all required columns are present
        missing_columns = [
            column for column in feature_columns
            if column not in input_data.columns
        ]

        if missing_columns:

            return jsonify({
                'error': f"Missing required columns: {missing_columns}"
            }), 400

        # Select only the features used by the model
        model_input = input_data[feature_columns]

        # Make predictions
        predicted_sales = model.predict(model_input)

        # Convert predictions to Python floats
        predicted_sales = [
            round(float(value), 2)
            for value in predicted_sales
        ]

        # Add predictions to original DataFrame
        input_data['Predicted_Product_Store_Sales_Total'] = predicted_sales

        # Return results
        return jsonify(
            input_data.to_dict(orient='records')
        )

    except Exception as e:

        return jsonify({
            'error': str(e)
        }), 500


# =========================================================
# Run Flask Application
# =========================================================

if __name__ == '__main__':

    sale_revenue_predictor_api.run(
        host='0.0.0.0',
        port=7860,
        debug=True
    )
