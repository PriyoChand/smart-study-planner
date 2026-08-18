import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import os

print("Loading dataset...")
# Load the data we just generated
df = pd.read_csv('data/final_student_data.csv')

# Define features (X) and target (y)
X = df[['Subject', 'Study_Hours', 'Sleep_Hours', 'Attendance_Pct', 'Assignments_Completed', 'Daily_Consistency', 'Study_Days_Remaining', 'Previous_Marks']]
y = df['Final_Marks']

# Split into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Building AI Model Pipeline...")
# We use OneHotEncoder to turn the text 'Subject' into numbers the AI can understand
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['Subject'])
    ], remainder='passthrough'
)

# Create a pipeline that preprocesses the data, then runs the Random Forest model
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])

print("Training the AI (This might take a few seconds)...")
model_pipeline.fit(X_train, y_train)

# Test the model's accuracy
predictions = model_pipeline.predict(X_test)
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(f"🎯 Model Accuracy Details:")
print(f"Mean Absolute Error: {mae:.2f} marks (Predictions are usually within this many marks)")
print(f"R-Squared Score: {r2:.2f} (1.0 is perfect)")

# Save the trained model to be used by the Streamlit app
os.makedirs('model', exist_ok=True)
with open('model/marks_predictor.pkl', 'wb') as file:
    pickle.dump(model_pipeline, file)
    
print("✅ AI Model saved successfully to 'model/marks_predictor.pkl'!")
