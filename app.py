from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd

from feature_extraction import extract_features


app = Flask(__name__)


# ==========================================
# LOAD TRAINED MODEL
# ==========================================

with open("model.pkl", "rb") as f:
    model = pickle.load(f)


# ==========================================
# LOAD FEATURE COLUMNS
# ==========================================

with open("model_columns.pkl", "rb") as f:
    feature_columns = pickle.load(f)


print("Model loaded successfully!")
print("Features:", feature_columns)


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# PREDICTION API
# ==========================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        # Get JSON data
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No data received."
            }), 400


        # Get URL
        url = data.get("url", "").strip()


        if not url:

            return jsonify({
                "error": "Please enter a URL."
            }), 400


        # Add HTTPS if protocol is missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url


        print("\n================================")
        print("Analyzing:", url)
        print("================================")


        # ==========================================
        # EXTRACT FEATURES
        # ==========================================

        features = extract_features(url)


        print("Extracted features:")
        print(features)

        print("Feature count:", len(features))


        # ==========================================
        # CHECK FEATURES
        # ==========================================

        if len(features) != len(feature_columns):

            return jsonify({
                "error": (
                    f"Feature mismatch. "
                    f"Expected {len(feature_columns)}, "
                    f"got {len(features)}."
                )
            }), 500


        # ==========================================
        # CREATE DATAFRAME
        # ==========================================

        X = pd.DataFrame([features])

        # Make sure feature order matches training
        X = X[feature_columns]


        # ==========================================
        # MODEL PREDICTION
        # ==========================================

        prediction = model.predict(X)[0]


        probabilities = model.predict_proba(X)[0]


        legitimate_probability = float(
            probabilities[0]
        )

        phishing_probability = float(
            probabilities[1]
        )


        # ==========================================
        # RESULT
        # ==========================================

        if prediction == 1:

            result = "Phishing"

            confidence = (
                phishing_probability * 100
            )

        else:

            result = "Legitimate"

            confidence = (
                legitimate_probability * 100
            )


        print("Result:", result)
        print(
            f"Confidence: {confidence:.2f}%"
        )


        # ==========================================
        # RETURN JSON
        # ==========================================

        return jsonify({

            "url": url,

            "prediction": result,

            "confidence": round(
                confidence,
                2
            ),

            "phishing_probability": round(
                phishing_probability * 100,
                2
            ),

            "legitimate_probability": round(
                legitimate_probability * 100,
                2
            ),

            "features": features

        })


    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )

        return jsonify({
            "error": str(e)
        }), 500


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    print("\n================================")
    print("   PHISHING WEBSITE DETECTOR")
    print("================================")
    print("Server running at:")
    print("http://127.0.0.1:5000")
    print("================================\n")


    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )