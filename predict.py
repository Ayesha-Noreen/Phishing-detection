import pandas as pd
import pickle

from feature_extraction import extract_features


# ==============================
# LOAD MODEL
# ==============================

with open("model.pkl", "rb") as file:
    model = pickle.load(file)

with open("model_columns.pkl", "rb") as file:
    feature_columns = pickle.load(file)


print("Model loaded successfully!")


# ==============================
# GET URL
# ==============================

url = input("\nEnter website URL: ")

print("\nAnalyzing URL...")


# ==============================
# EXTRACT FEATURES
# ==============================

features = extract_features(url)

print("\nExtracted Features:")

for name, value in features.items():
    print(f"{name}: {value}")


# ==============================
# CREATE DATAFRAME
# ==============================

input_data = pd.DataFrame([features])

# Ensure exact feature order
input_data = input_data[feature_columns]


# ==============================
# PREDICTION
# ==============================

prediction = model.predict(input_data)[0]

probability = model.predict_proba(input_data)[0]


# ==============================
# RESULT
# ==============================

print("\n==============================")
print("          RESULT")
print("==============================")

print("URL:", url)

if prediction == 1:
    print("⚠️ PHISHING WEBSITE")
    confidence = probability[1] * 100
else:
    print("✅ LEGITIMATE WEBSITE")
    confidence = probability[0] * 100

print(f"Confidence: {confidence:.2f}%")

print("==============================")