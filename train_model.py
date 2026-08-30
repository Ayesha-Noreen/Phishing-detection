import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier

# ==========================================
# LOAD DATASET
# ==========================================

data = pd.read_csv("DataFiles/5.urldata.csv")

print("Dataset loaded!")
print("Dataset shape:", data.shape)

# ==========================================
# USE ALL 16 FEATURES
# ==========================================

feature_columns = [
    "Have_IP",
    "Have_At",
    "URL_Length",
    "URL_Depth",
    "Redirection",
    "https_Domain",
    "TinyURL",
    "Prefix/Suffix",
    "DNS_Record",
    "Web_Traffic",
    "Domain_Age",
    "Domain_End",
    "iFrame",
    "Mouse_Over",
    "Right_Click",
    "Web_Forwards"
]

X = data[feature_columns]
y = data["Label"]

print("Features:", len(feature_columns))
print("Training data:", X.shape)

# ==========================================
# TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# ==========================================
# XGBOOST MODEL
# ==========================================

model = XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric="logloss"
)

print("\nTraining model...")

model.fit(X_train, y_train)

# ==========================================
# EVALUATION
# ==========================================

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n==============================")
print("MODEL TRAINING COMPLETE")
print("==============================")
print("Accuracy:", round(accuracy, 4))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# ==========================================
# SAVE MODEL
# ==========================================

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("model_columns.pkl", "wb") as f:
    pickle.dump(feature_columns, f)

print("\nModel saved as model.pkl")
print("Feature columns saved as model_columns.pkl")