import pandas as pd
import numpy as np
import os

os.makedirs('data', exist_ok=True)
np.random.seed(42)

num_students = 500
subjects = ['Python Programming', 'DBMS', 'Data Analytics', 'Operating Systems', 'Algorithms']
data = []

print("Generating perfectly aligned student data...")

for student_id in range(1, num_students + 1):
    # Student baselines
    base_attendance = np.clip(np.random.normal(80, 10), 40, 100)
    base_sleep = np.clip(np.random.normal(7, 1.5), 4, 10)
    consistency = np.random.randint(2, 8) 
    
    # NEW: Added Assignments Completed (Percentage)
    assignments_completed = np.clip(np.random.normal(75, 15), 0, 100)
    
    # NEW: Added Study Days Remaining before exam
    days_remaining = np.random.randint(5, 45)
    
    for subject in subjects:
        study_hours = np.round(np.random.uniform(1.0, 8.0), 1) 
        previous_marks = np.round(np.random.uniform(40.0, 95.0), 1)
        
        # Updated Logic: Including Assignments and Days Remaining
        # If they have few days remaining but high study hours, they cram well. 
        # High assignments completed boosts marks.
        calculated_marks = (
            (study_hours * 3.0) + 
            (previous_marks * 0.35) + 
            (base_attendance * 0.10) + 
            (assignments_completed * 0.15) + # New weight
            (consistency * 1.5) +
            ((base_sleep - 6) * 1.5) + 
            np.random.normal(0, 5) 
        )
        
        # Minor penalty if exam is close (days_remaining < 10) and consistency is low
        if days_remaining < 10 and consistency < 4:
            calculated_marks -= 5
            
        final_marks = np.clip(calculated_marks, 0, 100)
        
        data.append([
            student_id, subject, study_hours, np.round(base_sleep, 1),
            np.round(base_attendance, 1), np.round(assignments_completed, 1), 
            consistency, days_remaining, previous_marks, np.round(final_marks, 1)
        ])

df = pd.DataFrame(data, columns=[
    'Student_ID', 'Subject', 'Study_Hours', 'Sleep_Hours', 
    'Attendance_Pct', 'Assignments_Completed', 'Daily_Consistency', 
    'Study_Days_Remaining', 'Previous_Marks', 'Final_Marks'
])

df.to_csv('data/final_student_data.csv', index=False)
print(f"✅ Generated data with ALL requested features for {num_students} students!")