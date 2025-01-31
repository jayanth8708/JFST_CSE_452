import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

// Abstract Class: Student
abstract class Student {
    protected String studentID;
    protected String name;
    protected List<Double> grades;

    public Student(String studentID, String name) {
        this.studentID = studentID;
        this.name = name;
        this.grades = new ArrayList<>();
    }

    public String getStudentID() {
        return studentID;
    }

    public String getName() {
        return name;
    }

    public List<Double> getGrades() {
        return grades;
    }

    public void addGrade(double grade) {
        grades.add(grade);
    }

    public double calculateAverage() {
        double sum = 0;
        for (double grade : grades) {
            sum += grade;
        }
        return sum / grades.size();
    }
}

// Concrete Class: GradingSystem
class GradingSystem extends Student implements GradingOperations {
    public GradingSystem(String studentID, String name) {
        super(studentID, name);
    }

    @Override
    public void addGrade(double grade) {
        super.addGrade(grade);
    }

    @Override
    public void viewGrades() {
        System.out.println("Student ID: " + getStudentID());
        System.out.println("Name: " + getName());
        System.out.println("Grades: " + getGrades());
    }

    @Override
    public double calculateAverage() {
        return super.calculateAverage();
    }
}

// Interface: GradingOperations
interface GradingOperations {
    void addGrade(double grade);
    void viewGrades();
    double calculateAverage();
}

// Main Class: Menu-driven program
public class Main {
    private static List<GradingSystem> students = new ArrayList<>();
    private static Scanner scanner = new Scanner(System.in);

    public static void main(String[] args) {
        while (true) {
            System.out.println("1. Add Student");
            System.out.println("2. Add Grade");
            System.out.println("3. View Grades");
            System.out.println("4. Calculate Average");
            System.out.println("5. Exit");
            System.out.print("Choose an option: ");
            int option = scanner.nextInt();
            scanner.nextLine(); // Consume newline left-over

            switch (option) {
                case 1:
                    addStudent();
                    break;
                case 2:
                    addGrade();
                    break;
                case 3:
                    viewGrades();
                    break;
                case 4:
                    calculateAverage();
                    break;
                case 5:
                    System.exit(0);
                    break;
                default:
                    System.out.println("Invalid option. Please choose again.");
            }
        }
    }

    private static void addStudent() {
        System.out.print("Enter student ID: ");
        String studentID = scanner.nextLine();
        System.out.print("Enter student name: ");
        String name = scanner.nextLine();
        students.add(new GradingSystem(studentID, name));
        System.out.println("Student added successfully.");
    }

    private static void addGrade() {
        System.out.print("Enter student ID: ");
        String studentID = scanner.nextLine();
        for (GradingSystem student : students) {
            if (student.getStudentID().equals(studentID)) {
                System.out.print("Enter grade: ");
                double grade = scanner.nextDouble();
                scanner.nextLine(); // Consume newline left-over
                student.addGrade(grade);
                System.out.println("Grade added successfully.");
                return;
            }
        }
        System.out.println("Student not found.");
    }

    private static void viewGrades() {
        System.out.print("Enter student ID: ");
        String studentID = scanner.nextLine();
        for (GradingSystem student : students) {
            if (student.getStudentID().equals(studentID)) {
                student.viewGrades();
                return;
            }
        }
        System.out.println("Student not found.");
    }

    private static void calculateAverage() {
        System.out.print("Enter student ID: ");
        String studentID = scanner.nextLine();
        for (GradingSystem student : students) {
            if (student.getStudentID().equals(studentID)) {
                System.out.println("Average grade: " + student.calculateAverage());
                return;
            }
        }
        System.out.println("Student not found.");
    }
}