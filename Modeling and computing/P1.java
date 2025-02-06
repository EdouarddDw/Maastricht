import java.util.Scanner;

public class P1 {

    // Function to read a 2D array of doubles from stdin
    public static double[][] readDoubleMatrixFromStdin() {
        Scanner sc = new Scanner(System.in);

        // Read the first line as an integer (number of lines to follow)
        int n = sc.nextInt();
        sc.nextLine();  // Consume leftover newline

        // Prepare a 2D array to hold n rows
        double[][] data = new double[n][];

        // Read each of the next n lines
        for (int i = 0; i < n; i++) {
            String line = sc.nextLine().trim();

            // Split the line by spaces
            String[] tokens = line.split("\\s+");

            // Convert to double
            double[] row = new double[tokens.length];
            for (int j = 0; j < tokens.length; j++) {
                row[j] = Double.parseDouble(tokens[j]);
            }

            // Store this row in the 2D array
            data[i] = row;
        }

        sc.close();
        return data;
    }

    public static void main(String[] args) {
        // Read the matrix from stdin
        double[][] data = readDoubleMatrixFromStdin();
        // for loop to iterate over each student
        for (double[] student : data) {
            int participation = (int) student[0];
            int homework = (int) student[1];
            int homework_sufficient = (int) student[2];
            double exam = student[3];
            double project = student[4];

            double final_grade = (0.7 * exam) + (0.3 * project);
            // passing conditions
            if (
                exam >= 5.5 
                && project >= 5.5 
                && final_grade >= 5.5 
                && participation >= 8
                && homework >= 3
                && (homework >= 5 || (3 <= homework && homework < 5  && (homework_sufficient == 1 || homework_sufficient == 2)))
            ) {

                System.out.printf("PASS %.1f%n", final_grade);
            } else {
                System.out.println("FAIL");
            }
        }
    }
}
