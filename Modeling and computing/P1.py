import sys

def compute_final_grade(x, p):
    final_grade = (0.7 * x) + (0.3 * p)
    return final_grade

def main():
    # Read all input at once
    input_lines = sys.stdin.read().splitlines()
    n = int(input_lines[0])  # First line is the number of students

    for i in range(1, n + 1):  # Iterate over each student's data
        # Parse the input line
        data = input_lines[i].split()
        participation = int(data[0])  # Participation must be an integer
        homework_correct = int(data[1])  # Homework correct must be an integer
        homework_sufficient = int(data[2])  # Homework sufficient must be an integer
        exam = float(data[3])  # Exam score is a float
        project = float(data[4])  # Project score is a float

        # Compute the final grade
        final_grade = compute_final_grade(exam, project)



        # Check if the student passes
        is_pass = (
            exam >= 5.5 and
            project >= 5.5 and
            final_grade >= 5.5 and
            participation >= 8 and
            (homework_correct >= 5 or (3 <= homework_correct < 5 and homework_sufficient in [1, 2]))
        )

        # Output the result
        if is_pass:
            print("PASS", round(final_grade, 1))
        else:
            print("FAIL")

    # Flush the output buffer to ensure all output is displayed
    sys.stdout.flush()

if __name__ == "__main__":
    main()
    