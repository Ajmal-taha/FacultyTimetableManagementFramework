import pandas as pd
import random

# Indian names list
indian_names = [
    "Aarav", "Aarohi", "Amit", "Amita", "Arjun", "Asha", "Deepak", "Divya", "Gaurav", "Isha",
    "Jai", "Kiran", "Meera", "Neha", "Pranav", "Priya", "Rahul", "Riya", "Rohit", "Sarika",
    "Suresh", "Swati", "Tanvi", "Vikas", "Zoya"
]

# I YEAR I SEMESTER subjects
subjects_i_year_i_semester = [
    "Matrices and Calculus", "Applied Physics", "Programming for Problem Solving",
    "Engineering Workshop", "English for Skill Enhancement",
    "Elements of Computer Science & Engineering", "Applied Physics Laboratory",
    "Programming for Problem Solving Laboratory",
    "English Language and Communication Skills Laboratory",
    "Environmental Science"
]

# Mapping preferences for each staff member
staff_preferences = {}
for name in indian_names:
    # Randomly select a few subjects for each staff member
    num_preferences = random.randint(2, 5)
    preferences = random.sample(subjects_i_year_i_semester, num_preferences)
    staff_preferences[name] = preferences

# Create DataFrame from staff preferences
df = pd.DataFrame(staff_preferences.items(), columns=["Staff Name", "Subject Preferences"])

print(df)


print(df["Subject Preferences"][0])