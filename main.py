"""
Student Performance Analysis
-----------------------------
This program loads a dataset of 100 students, checks that the data is
valid, calculates useful statistics (averages, rankings, categories),
creates charts, and prints a summary of what was found.

How to run:
    python main.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------------------

# Path to the dataset. Using os.path.join keeps this working on both
# Windows and Linux/Mac.
DATA_PATH = os.path.join("data", "student_performance_100_students.csv")

# Folder where charts will be saved.
VISUALIZATION_FOLDER = "visualization"

# The 5 subjects and 4 assessments used in this dataset.
# The original columns are named like "Mathematics - Unit Test 1", so we
# build the exact column name by combining a subject and an assessment.
SUBJECTS = ["Mathematics", "Science", "English", "Computer Science", "Social Science"]
ASSESSMENTS = ["Unit Test 1", "Midterm 1", "Unit Test 2", "Midterm 3"]

# The score column names, built from the subjects and assessments above.
SCORE_COLUMNS = [f"{subject} - {assessment}" for subject in SUBJECTS for assessment in ASSESSMENTS]

# This project is designed around a dataset of 100 students.
EXPECTED_STUDENTS = 100

# Performance category thresholds (based on a student's overall average).
# These ranges are documented again in the README.
def get_performance_category(average_score):
    """Turn a numeric average into an easy-to-understand category."""
    if average_score >= 90:
        return "Excellent"
    elif average_score >= 75:
        return "Very Good"
    elif average_score >= 60:
        return "Good"
    elif average_score >= 45:
        return "Needs Improvement"
    else:
        return "At Risk"


# ---------------------------------------------------------------------------
# STEP 1: LOAD DATA
# ---------------------------------------------------------------------------

def load_data(path):
    """Load the student data from a CSV file. Returns a DataFrame, or None
    if the file could not be loaded."""

    print(f"Looking for dataset at: {path}")

    if not os.path.exists(path):
        print("ERROR: The dataset file was not found at that path.")
        return None

    try:
        data = pd.read_csv(path)
    except Exception as error:
        print(f"ERROR: Could not read the CSV file. Details: {error}")
        return None

    print("Dataset loaded successfully.\n")
    return data


# ---------------------------------------------------------------------------
# STEP 2: VALIDATE DATA
# ---------------------------------------------------------------------------

def validate_data(data):
    """Run simple checks on the dataset. Prints any problems found.
    Returns True if the data looks usable, False if there is a serious
    problem that should stop the program."""

    print("Running data validation checks...")

    # Check the dataset is not empty.
    if data.empty:
        print("ERROR: The dataset is empty.")
        return False

    # Check that the "Student Name" column exists.
    if "Student Name" not in data.columns:
        print("ERROR: The dataset is missing a 'Student Name' column.")
        return False

    # Check that all expected score columns exist.
    missing_columns = [column for column in SCORE_COLUMNS if column not in data.columns]
    if missing_columns:
        print(f"ERROR: The dataset is missing these expected columns: {missing_columns}")
        return False

    # Check for missing student names.
    missing_names = data["Student Name"].isnull().sum()
    if missing_names > 0:
        print(f"WARNING: {missing_names} row(s) have a missing student name.")

    # Check for duplicate student names.
    duplicate_names = data["Student Name"].duplicated().sum()
    if duplicate_names > 0:
        print(f"WARNING: {duplicate_names} duplicate student name(s) found.")

    # Check for missing scores.
    missing_scores = data[SCORE_COLUMNS].isnull().sum().sum()
    if missing_scores > 0:
        print(f"WARNING: {missing_scores} missing score value(s) found.")

    # Check that score columns are numeric.
    non_numeric_columns = []
    for column in SCORE_COLUMNS:
        if not pd.api.types.is_numeric_dtype(data[column]):
            non_numeric_columns.append(column)
    if non_numeric_columns:
        print(f"WARNING: These columns contain non-numeric values: {non_numeric_columns}")

    # Check that scores fall within the expected 0-100 range.
    # (Only checking columns that are actually numeric.)
    numeric_score_columns = [column for column in SCORE_COLUMNS if column not in non_numeric_columns]
    out_of_range_count = 0
    for column in numeric_score_columns:
        out_of_range_count += ((data[column] < 0) | (data[column] > 100)).sum()
    if out_of_range_count > 0:
        print(f"WARNING: {out_of_range_count} score value(s) are outside the 0-100 range.")

    # Check the dataset has the expected number of students for this project.
    number_of_students = len(data)
    print(f"Expected number of students: {EXPECTED_STUDENTS}")
    print(f"Actual number of students:   {number_of_students}")
    if number_of_students != EXPECTED_STUDENTS:
        print(f"WARNING: This project expects exactly {EXPECTED_STUDENTS} students.")

    print("Validation checks complete.\n")
    return True


# ---------------------------------------------------------------------------
# STEP 3: EXPLORE DATA
# ---------------------------------------------------------------------------

def explore_data(data):
    """Print some basic information about the dataset so we understand
    what we are working with."""

    print("=" * 60)
    print("DATA EXPLORATION")
    print("=" * 60)

    print(f"\nNumber of students: {len(data)}")
    print(f"Number of subjects: {len(SUBJECTS)}")
    print(f"Number of assessments per subject: {len(ASSESSMENTS)}")
    print(f"Dataset shape (rows, columns): {data.shape}")

    print("\nFirst 5 rows of the dataset:")
    print(data.head())

    print("\nColumn data types:")
    print(data.dtypes)

    print("\nMissing values per column (showing only columns with missing values):")
    missing_counts = data.isnull().sum()
    missing_counts = missing_counts[missing_counts > 0]
    if len(missing_counts) > 0:
        print(missing_counts)
    else:
        print("No missing values found.")

    print("\nNumber of duplicate student names:", data["Student Name"].duplicated().sum())

    print("\nBasic statistics for the score columns:")
    print(data[SCORE_COLUMNS].describe())
    print()


# ---------------------------------------------------------------------------
# STEP 4: CLEAN DATA
# ---------------------------------------------------------------------------

def clean_data(data):
    """Fix reasonable data-quality problems. Only makes changes when
    something is actually wrong, and explains what was done."""

    cleaned_data = data.copy()
    original_row_count = len(cleaned_data)

    # Remove rows with a missing student name, since we cannot analyze
    # a student we cannot identify.
    cleaned_data = cleaned_data.dropna(subset=["Student Name"])

    # Remove duplicate student names, keeping the first occurrence.
    cleaned_data = cleaned_data.drop_duplicates(subset=["Student Name"], keep="first")

    # Convert score columns to numbers. If a value cannot be converted,
    # Pandas changes it to NaN so we can handle it below.
    for column in SCORE_COLUMNS:
        cleaned_data[column] = pd.to_numeric(cleaned_data[column], errors="coerce")

    # Fill missing scores with the average of that score column.
    # This keeps the example simple and avoids losing an entire student row.
    for column in SCORE_COLUMNS:
        if cleaned_data[column].isnull().sum() > 0:
            column_average = cleaned_data[column].mean()
            cleaned_data[column] = cleaned_data[column].fillna(column_average)
            print(f"Filled missing values in '{column}' with the column average ({column_average:.2f}).")

    # Clip scores that are outside the valid 0-100 range.
    for column in SCORE_COLUMNS:
        out_of_range = ((cleaned_data[column] < 0) |
                        (cleaned_data[column] > 100)).sum()
        if out_of_range > 0:
            cleaned_data[column] = cleaned_data[column].clip(lower=0, upper=100)
            print(f"Clipped {out_of_range} out-of-range value(s) in '{column}' to fit 0-100.")


    rows_removed = original_row_count - len(cleaned_data)
    if rows_removed > 0:
        print(f"Removed {rows_removed} row(s) during cleaning (missing name or duplicate).")
    else:
        print("No cleaning was necessary — the dataset was already in good shape.")

    print()
    return cleaned_data


# ---------------------------------------------------------------------------
# STEP 5 & 6 & 7: CALCULATE PERFORMANCE (STUDENT, SUBJECT, ASSESSMENT)
# ---------------------------------------------------------------------------

def calculate_student_averages(data):
    """Calculate each student's average score per subject, plus one
    overall average across everything. Returns a new DataFrame."""

    student_averages = pd.DataFrame()
    student_averages["Student Name"] = data["Student Name"]

    # For each subject, average that subject's 4 assessment columns.
    for subject in SUBJECTS:
        subject_columns = [f"{subject} - {assessment}" for assessment in ASSESSMENTS]
        student_averages[subject] = data[subject_columns].mean(axis=1)

    # The overall average is the mean of all 20 score columns for that student.
    student_averages["Overall Average"] = data[SCORE_COLUMNS].mean(axis=1)

    return student_averages


def calculate_subject_performance(student_averages):
    """Calculate the average score for each subject, across all students."""

    subject_performance = student_averages[SUBJECTS].mean()
    subject_performance = subject_performance.sort_values(ascending=False)
    return subject_performance


def calculate_assessment_performance(data):
    """Calculate the average score for each assessment (Unit Test 1,
    Midterm 1, etc.), combining all 5 subjects together."""

    assessment_performance = {}
    for assessment in ASSESSMENTS:
        # Gather the columns for this assessment across all subjects,
        # e.g. "Mathematics - Unit Test 1", "Science - Unit Test 1", etc.
        assessment_columns = [f"{subject} - {assessment}" for subject in SUBJECTS]
        assessment_performance[assessment] = data[assessment_columns].mean(axis=1).mean()

    # Keep the assessments in their natural order (not sorted), since
    # this represents a timeline.
    assessment_performance = pd.Series(assessment_performance)
    return assessment_performance


# ---------------------------------------------------------------------------
# STEP 8: PERFORMANCE CATEGORIES
# ---------------------------------------------------------------------------

def add_performance_categories(student_averages):
    """Add a 'Category' column to the student averages table, based on
    each student's overall average."""

    student_averages = student_averages.copy()
    student_averages["Category"] = student_averages["Overall Average"].apply(get_performance_category)
    return student_averages


# ---------------------------------------------------------------------------
# STEP 9: TOP STUDENTS
# ---------------------------------------------------------------------------

def get_top_students(student_averages, number_of_students=10):
    """Return the top N students, ranked by overall average (highest first)."""

    top_students = student_averages.sort_values(by="Overall Average", ascending=False)
    top_students = top_students.head(number_of_students).reset_index(drop=True)

    # Add a "Rank" column, starting at 1.
    top_students.insert(0, "Rank", range(1, len(top_students) + 1))

    return top_students


# ---------------------------------------------------------------------------
# STEP 10: IMPROVEMENT ANALYSIS
# ---------------------------------------------------------------------------

def calculate_improvement(assessment_performance):
    """Compare the first assessment (Unit Test 1) to the final assessment
    (Midterm 3) to see whether performance went up or down overall."""

    first_assessment_score = assessment_performance["Unit Test 1"]
    final_assessment_score = assessment_performance["Midterm 3"]
    improvement = final_assessment_score - first_assessment_score
    return improvement


def calculate_subject_improvement(data):
    """Compare Unit Test 1 to Midterm 3 for each subject individually."""

    subject_improvement = {}
    for subject in SUBJECTS:
        first_score = data[f"{subject} - Unit Test 1"].mean()
        final_score = data[f"{subject} - Midterm 3"].mean()
        subject_improvement[subject] = final_score - first_score

    return pd.Series(subject_improvement)


# ---------------------------------------------------------------------------
# VISUALIZATIONS
# ---------------------------------------------------------------------------

def create_subject_performance_chart(subject_performance):
    """Bar chart showing the average score for each subject."""

    plt.figure(figsize=(9, 6))
    plt.bar(subject_performance.index, subject_performance.values, color="steelblue")

    plt.title("Average Score by Subject", fontsize=14)
    plt.xlabel("Subject")
    plt.ylabel("Average Score")
    plt.ylim(0, 100)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()

    output_path = os.path.join(VISUALIZATION_FOLDER, "subject_performance.png")
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def create_assessment_trend_chart(assessment_performance):
    """Line chart showing how the average score changed across the
    4 assessments, from Unit Test 1 through Midterm 3."""

    plt.figure(figsize=(9, 6))
    plt.plot(assessment_performance.index, assessment_performance.values,
             marker="o", color="darkorange", linewidth=2)

    plt.title("Average Score Trend Across Assessments", fontsize=14)
    plt.xlabel("Assessment")
    plt.ylabel("Average Score")
    plt.ylim(0, 100)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()

    output_path = os.path.join(VISUALIZATION_FOLDER, "assessment_trend.png")
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def create_performance_distribution_chart(student_averages):
    """Pie chart showing what percentage of students fall into each
    performance category."""

    # Count how many students are in each category.
    category_order = ["Excellent", "Very Good", "Good", "Needs Improvement", "At Risk"]
    category_counts = student_averages["Category"].value_counts().reindex(category_order, fill_value=0)

    # Put the categories in a sensible order (best to worst) so the
    # chart is easy to read.
    category_order = ["Excellent", "Very Good", "Good", "Needs Improvement", "At Risk"]
    category_counts = category_counts.reindex(category_order).fillna(0)

    plt.figure(figsize=(8, 8))
    plt.pie(category_counts.values, labels=category_counts.index, autopct="%1.1f%%", startangle=90)

    plt.title("Distribution of Students by Performance Category", fontsize=14)
    plt.tight_layout()

    output_path = os.path.join(VISUALIZATION_FOLDER, "performance_distribution.png")
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def create_top_students_chart(top_students):
    """Horizontal bar chart showing the top 10 students and their
    overall average. Horizontal bars work well here because student
    names can be long."""

    # Reverse the order so the #1 student appears at the top of the chart.
    chart_data = top_students.iloc[::-1]

    plt.figure(figsize=(9, 7))
    plt.barh(chart_data["Student Name"], chart_data["Overall Average"], color="seagreen")

    plt.title("Top 10 Students by Overall Average", fontsize=14)
    plt.xlabel("Overall Average")
    plt.ylabel("Student Name")
    plt.xlim(0, 100)
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()

    output_path = os.path.join(VISUALIZATION_FOLDER, "top_10_students.png")
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


# ---------------------------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------------------------

def main():
    # Step 1: Load the data.
    data = load_data(DATA_PATH)
    if data is None:
        print("Stopping the program because the dataset could not be loaded.")
        return

    # Step 2: Validate the data.
    is_valid = validate_data(data)
    if not is_valid:
        print("Stopping the program because the dataset failed validation.")
        return

    # Step 3: Explore the data.
    explore_data(data)

    # Step 4: Clean the data.
    print("=" * 60)
    print("DATA CLEANING")
    print("=" * 60)
    data = clean_data(data)

    # Make sure the visualization folder exists before saving charts.
    os.makedirs(VISUALIZATION_FOLDER, exist_ok=True)

    # Steps 5-7: Calculate student, subject, and assessment performance.
    student_averages = calculate_student_averages(data)
    subject_performance = calculate_subject_performance(student_averages)
    assessment_performance = calculate_assessment_performance(data)

    # Step 8: Add performance categories.
    student_averages = add_performance_categories(student_averages)
    category_order = ["Excellent", "Very Good", "Good", "Needs Improvement", "At Risk"]
    category_counts = student_averages["Category"].value_counts().reindex(category_order, fill_value=0)

    # Step 9: Find the top 10 students.
    top_students = get_top_students(student_averages, number_of_students=10)

    # Step 10: Improvement analysis.
    overall_improvement = calculate_improvement(assessment_performance)
    subject_improvement = calculate_subject_improvement(data)

    # Create all 4 visualizations.
    print("\n" + "=" * 60)
    print("CREATING VISUALIZATIONS")
    print("=" * 60)
    create_subject_performance_chart(subject_performance)
    create_assessment_trend_chart(assessment_performance)
    create_performance_distribution_chart(student_averages)
    create_top_students_chart(top_students)

    # Print a summary of the key findings.
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    print(f"\nBest-performing subject: {subject_performance.index[0]} "
          f"(average: {subject_performance.iloc[0]:.2f})")
    print(f"Lowest-performing subject: {subject_performance.index[-1]} "
          f"(average: {subject_performance.iloc[-1]:.2f})")

    print("\nAverage score by subject:")
    print(subject_performance.round(2))

    print("\nAverage score by assessment:")
    print(assessment_performance.round(2))

    if overall_improvement > 0:
        print(f"\nOverall trend: scores IMPROVED by {overall_improvement:.2f} points "
              f"from Unit Test 1 to Midterm 3.")
    elif overall_improvement < 0:
        print(f"\nOverall trend: scores DECLINED by {abs(overall_improvement):.2f} points "
              f"from Unit Test 1 to Midterm 3.")
    else:
        print("\nOverall trend: scores stayed the same from Unit Test 1 to Midterm 3.")

    print("\nSubject-level improvement (Midterm 3 minus Unit Test 1):")
    print(subject_improvement.round(2))

    print("\nNumber of students in each performance category:")
    print(category_counts)

    print("\nTop 10 students:")
    print(top_students[["Rank", "Student Name", "Overall Average"]].to_string(index=False))

    print("\nAll visualizations were saved in the 'visualization' folder.")
    print("Program finished successfully.")


if __name__ == "__main__":
    main()
