import json
import csv
from collections import defaultdict                        # defaultdict is used to create a dictionary that returns a default value for non-existing keys

# Load the dataset
json_path = "data/raw/students_dataset.json"               # Path to the JSON file (Put your JSON file in the same directory as this script) 
csv_output_path = "data/processed/student_summary.csv" 

with open(json_path, "r") as file:                         # "r" mode is used to read the file
    students_data = json.load(file)

# Calculate total and mean age
total_students = len(students_data)
total_age = sum(student["Age"] for student in students_data)
mean_age = round(total_age / total_students, 2)
print (f"Total Students: {total_students}, Mean Age: {mean_age}")

# Calculate Mean Score
total_score = sum(student["Score"] for student in students_data)
mean_score = round(total_score / total_students, 2)
print (f"Total Students: {total_students}, Mean Age: {mean_age}, Mean Score: {mean_score}")

# Count students per type
student_type_counts = defaultdict(int)
for student in students_data:
    stype = student["Student Type"]                         # stype = Abreviation for Student Type
    student_type_counts[stype] += 1                         # Count students per type += 1 is used to increment the count for each student type
print (f"Student Type Counts: {dict(student_type_counts)}")

# Count Age Students per Type
age_student_type_counts = defaultdict(lambda: defaultdict(int))
for student in students_data:
    stype = student["Student Type"]
    age_student_type_counts[stype][student["Age"]] += 1
print("Age Student Type Counts:")

for stype, ages in age_student_type_counts.items():
    sorted_ages = dict(sorted(ages.items()))

    print(f"  {stype}: {sorted_ages}")
    age_student_type_counts[stype] = sorted_ages              # update to sorted dict for later use

# Prepare summary rows
summary_rows = [
    {"Metric": "Total Students", "Value": total_students},
    {"Metric": "Mean Age", "Value": mean_age}
]
# Add Mean Score to summary after Mean Age
summary_rows.insert(1, {
    "Metric": "Mean Score",
    "Value": mean_score
})

# Add student type counts
for stype, count in student_type_counts.items():
    summary_rows.append({
        "Metric": f"Total {stype}",
        "Value": count
    })
    
# Add age student type counts
for stype, ages in age_student_type_counts.items():
    for age, count in ages.items():
        summary_rows.append({
            "Metric": f"Total {stype} Age {age}",
            "Value": count
        })
# Export summary to CSV
with open(csv_output_path, "w", newline='') as csvfile:                # "w" mode is used to write to the file
    writer = csv.DictWriter(csvfile, fieldnames=["Metric", "Value"])
    writer.writeheader()
    writer.writerows(summary_rows)

print(f"✅ Summary exported to CSV at: {csv_output_path}")