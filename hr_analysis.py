import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

df = pd.read_csv("toy_hr_data.csv")

print("=== DATASET OVERVIEW ===")
print(df.describe())
print("\nDepartments:", df["department"].value_counts().to_dict())

print("\n=== FINDING 1: Tenure vs Satisfaction ===")
print(df[["tenure_years", "satisfaction_score"]].corr())
bins = [0, 2, 5, 8, 20]
labels = ["0-2 yrs", "2-5 yrs", "5-8 yrs", "8+ yrs"]
df["tenure_band"] = pd.cut(df["tenure_years"], bins=bins, labels=labels)
print(df.groupby("tenure_band", observed=True)["satisfaction_score"].mean().round(2))

print("\n=== FINDING 2: High performers by dept ===")
print("Performance rating distribution:")
print(df["performance_rating"].value_counts().sort_index())
high_perf = df[df["performance_rating"] == 5]
print("\nHigh performers (rating=5) count by dept:")
print(high_perf["department"].value_counts())
print("\nHigh performers avg satisfaction:", high_perf["satisfaction_score"].mean().round(2))
print("Overall avg satisfaction:", df["satisfaction_score"].mean().round(2))

print("\n=== FINDING 3: Salary equity across departments ===")
dept_salary = df.groupby("department")["salary"].agg(["mean", "median", "min", "max"]).round(0)
print(dept_salary)
print("\nSalary std by dept:")
print(df.groupby("department")["salary"].std().round(0))

# Tenure band satisfaction detail
print("\n=== Veteran flight-risk detail ===")
veterans = df[df["tenure_years"] >= 8]
print(f"Employees with 8+ years tenure: {len(veterans)}")
print(veterans[["employee_id", "department", "tenure_years", "salary", "satisfaction_score", "performance_rating"]])
