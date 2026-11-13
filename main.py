
from dataclasses import dataclass
from drafter import *
from bakery import assert_equal


@dataclass
class Assignment:
    """Store the name and grade for one assignment."""
    name: str
    grade: float


@dataclass
class State:
    """Store information that the website needs between pages."""
    assignments: list[Assignment]
    course_name: str
    current_grade: float
    target_grade: float
    needed_grade: float
    message: str


def average_grades(assignments: list[Assignment]) -> float:
    """Calculate the average of all assignment grades."""
    if len(assignments) == 0:
        return 0.0

    total = 0.0
    for assignment in assignments:
        total = total + assignment.grade

    return total / len(assignments)


def required_next_grade(assignments: list[Assignment],
                        target: float) -> float:
    """Calculate the grade needed on the next assignment."""
    total = 0.0

    for assignment in assignments:
        total = total + assignment.grade

    number_of_assignments = len(assignments) + 1
    needed = target * number_of_assignments - total

    return needed


def valid_grade(grade: float) -> bool:
    """Check whether a grade is between 0 and 100."""
    return grade >= 0 and grade <= 100


@route
def index(state: State) -> Page:
    """Display the home page and main navigation."""
    return Page(state, [
        "COLLEGE GRADE CALCULATOR",
        "Welcome! Use this website to keep track of your grades.",
        "Course name: " + state.course_name,
        TextBox("course_name", state.course_name),
        Button("Save Course Name", "save_course"),
        " ",
        Button("Add Assignment", "add_assignment"),
        Button("View Assignments", "view_assignments"),
        Button("Calculate Current Grade", "calculate_grade"),
        Button("Set Desired Grade", "target_grade_page"),
        Button("Help", "help_page"),
        state.message
    ])


@route
def save_course(state: State, course_name: str) -> Page:
    """Save the course name entered by the student."""
    if course_name.strip() == "":
        state.message = "Please enter a course name."
    else:
        state.course_name = course_name
        state.message = "Course name saved."

    return index(state)


@route
def add_assignment(state: State) -> Page:
    """Display the form for entering a new assignment."""
    return Page(state, [
        "ADD AN ASSIGNMENT",
        "Enter the assignment name:",
        TextBox("assignment_name"),
        "Enter the assignment grade (0-100):",
        TextBox("grade", 0.0, "number"),
        Button("Save Assignment", "save_assignment"),
        Button("Home", "index")
    ])


@route
def save_assignment(state: State, assignment_name: str,
                    grade: float) -> Page:
    """Check and save a new assignment."""
    if assignment_name.strip() == "":
        state.message = "Please enter an assignment name."
    elif not valid_grade(grade):
        state.message = "Grade must be between 0 and 100."
    else:
        new_assignment = Assignment(assignment_name, grade)
        state.assignments.append(new_assignment)
        state.current_grade = average_grades(state.assignments)
        state.message = "Assignment successfully added."

    return view_assignments(state)


@route
def view_assignments(state: State) -> Page:
    """Display all assignments currently saved."""
    content = ["YOUR ASSIGNMENTS"]

    if len(state.assignments) == 0:
        content.append("You have not entered any assignments yet.")
    else:
        for assignment in state.assignments:
            content.append(
                assignment.name + ": " + str(assignment.grade) + "%"
            )

    content.append(" ")
    content.append("Current average: " +
                   str(round(average_grades(state.assignments), 2)) + "%")
    content.append(state.message)
    content.append(Button("Add Another Assignment", "add_assignment"))
    content.append(Button("Calculate Current Grade", "calculate_grade"))
    content.append(Button("Home", "index"))

    return Page(state, content)


@route
def calculate_grade(state: State) -> Page:
    """Calculate and display the student's current grade."""
    if len(state.assignments) == 0:
        state.message = "Add assignments before calculating your grade."
        state.current_grade = 0.0
    else:
        state.current_grade = average_grades(state.assignments)
        state.message = "Your current grade has been calculated."

    return Page(state, [
        "YOUR CURRENT GRADE",
        "Course: " + state.course_name,
        "Current average: " + str(round(state.current_grade, 2)) + "%",
        state.message,
        Button("View Assignments", "view_assignments"),
        Button("Set Desired Grade", "target_grade_page"),
        Button("Home", "index")
    ])


@route
def target_grade_page(state: State) -> Page:
    """Display the form for entering a desired grade."""
    return Page(state, [
        "DESIRED GRADE CALCULATOR",
        "What grade would you like to achieve?",
        "Enter a target grade between 0 and 100:",
        TextBox("target_grade", state.target_grade, "number"),
        Button("Calculate Needed Grade", "save_target_grade"),
        Button("Home", "index")
    ])


@route
def save_target_grade(state: State, target_grade: float) -> Page:
    """Check and save the student's desired grade."""
    if not valid_grade(target_grade):
        state.message = "Your desired grade must be between 0 and 100."
        return target_grade_page(state)

    state.target_grade = target_grade
    return calculate_needed_grade(state)


@route
def calculate_needed_grade(state: State) -> Page:
    """Display the grade needed on the next assignment."""
    state.needed_grade = required_next_grade(
        state.assignments, state.target_grade
    )

    if state.needed_grade > 100:
        result = "You would need more than 100% on the next assignment."
    elif state.needed_grade < 0:
        result = "You have already reached your desired grade."
    else:
        result = (
            "You need at least " +
            str(round(state.needed_grade, 2)) +
            "% on your next assignment."
        )

    return Page(state, [
        "YOUR TARGET GRADE RESULT",
        "Current average: " +
        str(round(average_grades(state.assignments), 2)) + "%",
        "Desired grade: " + str(state.target_grade) + "%",
        result,
        "This calculation assumes all assignments count equally.",
        Button("Try Another Target", "target_grade_page"),
        Button("View Assignments", "view_assignments"),
        Button("Home", "index")
    ])


@route
def help_page(state: State) -> Page:
    """Explain how to use the grade calculator."""
    return Page(state, [
        "HELP",
        "1. Enter your course name on the home page.",
        "2. Select Add Assignment.",
        "3. Enter the assignment name and grade.",
        "4. View your assignments or calculate your current average.",
        "5. Select Set Desired Grade to enter your goal.",
        "6. The calculator estimates the grade needed on your next assignment.",
        "All assignments count equally toward your average.",
        "Grades must be between 0 and 100.",
        Button("Home", "index")
    ])


# Tests for the calculation and validation functions
test_assignments = [
    Assignment("Homework 1", 80.0),
    Assignment("Quiz 1", 90.0),
    Assignment("Exam 1", 70.0)
]

assert_equal(average_grades(test_assignments), 80.0)
assert_equal(average_grades([]), 0.0)
assert_equal(required_next_grade(test_assignments, 85.0), 100.0)
assert_equal(required_next_grade([], 90.0), 90.0)
assert_equal(valid_grade(75.0), True)
assert_equal(valid_grade(105.0), False)
assert_equal(valid_grade(-5.0), False)


start_server(State([], "", 0.0, 90.0, 0.0, ""))
