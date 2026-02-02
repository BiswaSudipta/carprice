# =========================
# 1. IMPORT LIBRARIES
# =========================
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware   # 👈 ADD THIS
from pydantic import BaseModel
from typing import Union
import pandas as pd
import joblib

# =========================
# 2. LOAD MODEL PACKAGE
# =========================
model_package = joblib.load("car_purchase_predictor.pkl")

model = model_package["model"]
label_encoders = model_package["encoders"]
feature_names = model_package["features"]

# =========================
# 3. INITIALIZE FASTAPI
# =========================
app = FastAPI(
    title="Car Purchase Prediction API",
    description="Predict car purchase amount (gender: 0/1 or Male/Female)",
    version="1.0.0"
)

# =========================
# 3.1 ENABLE CORS (IMPORTANT)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow all origins (safe for dev)
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 4. INPUT SCHEMA
# =========================
class CustomerData(BaseModel):
    country: str
    gender: Union[int, str]   # accepts 0/1 OR Male/Female
    age: int
    annual_salary: float
    credit_card_debt: float
    net_worth: float

# =========================
# 5. ROOT ENDPOINT
# =========================
@app.get("/")
def home():
    return {
        "message": "Car Purchase Prediction API is running",
        "gender_rules": {
            "0": "Female",
            "1": "Male",
            "Male/Female": "Also accepted (case-insensitive)"
        }
    }

# =========================
# 6. PREDICTION ENDPOINT
# =========================
@app.post("/predict")
def predict(data: CustomerData):

    # -------- COUNTRY ENCODING --------
    country_input = data.country.strip().lower()

    country_map = {
        str(c).strip().lower(): c
        for c in label_encoders["country"].classes_
    }

    if country_input not in country_map:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown country: {data.country}"
        )

    encoded_country = label_encoders["country"].transform(
        [country_map[country_input]]
    )[0]

    # -------- GENDER HANDLING --------
    if isinstance(data.gender, int):
        if data.gender not in [0, 1]:
            raise HTTPException(
                status_code=400,
                detail="Gender must be 0 (Female) or 1 (Male)"
            )
        encoded_gender = data.gender

    elif isinstance(data.gender, str):
        gender_input = data.gender.strip().lower()
        gender_mapping = {"female": 0, "male": 1}

        if gender_input not in gender_mapping:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown gender: {data.gender}"
            )

        encoded_gender = gender_mapping[gender_input]

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid gender format"
        )

    # -------- BUILD INPUT DATAFRAME --------
    input_df = pd.DataFrame([{
        "country": encoded_country,
        "gender": encoded_gender,
        "age": data.age,
        "annual Salary": data.annual_salary,
        "credit card debt": data.credit_card_debt,
        "net worth": data.net_worth
    }])

    input_df = input_df[feature_names]

    # -------- PREDICT --------
    prediction = model.predict(input_df)[0]

    return {
        "predicted_car_purchase_amount": round(float(prediction), 2)
    }
