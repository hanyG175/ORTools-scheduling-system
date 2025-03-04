# Course Scheduling Solver

This project is a course scheduling application built in Python using the `ortools` library for constraint programming and `tkinter` for a graphical user interface (GUI). It generates an optimized timetable for multiple courses, groups, and teachers across a 5-day week, ensuring constraints such as group availability, session requirements, and teacher assignments are met.

## Features
- Schedules 8 courses across 5 days (Sunday to Thursday) with varying time slots per day.
- Supports multiple session types: Lectures, Recitations, and Labs.
- Assigns sessions to 6 student groups and 14 teachers with specific availability.
- Ensures constraints like no more than 3 consecutive slots per group and balanced teacher loads.
- Visualizes the timetable in a color-coded GUI using `tkinter`.

## Prerequisites
To run this project, you’ll need the following installed:
- **Python 3.x** (tested with Python 3.9+)
- **Required Libraries**:
  - `ortools` (`pip install ortools`)
  - `tkinter` (usually included with Python; if not, install via your package manager, e.g., `sudo apt-get install python3-tk` on Linux)
- **Windows-specific**: The script uses `ctypes` for high DPI support, so it’s optimized for Windows, though it may work on other OSes with minor adjustments.

## Installation
1. Clone or download this repository to your local machine:
  ``git clone <repository-url>``
  ``cd <repository-folder>``

2. Install the required dependencies:
   ``pip install ortools``

## Usage
1. Run the script:Ensure `tkinter` is available. On Windows, it’s typically pre-installed with Python. On Linux, you may need:
    `CSPSolver.py`
   
2. The script will:
- Solve the scheduling problem using the CP-SAT solver from `ortools`.
- Assign teachers to sessions based on availability and workload balance.
- Display the timetable in a GUI window, with days as columns, time slots as rows, and group assignments shown in color-coded cells.

## Project Structure
- **`CSPSolver.py`**: Main script containing the scheduling logic, constraints, and GUI code.
- **Model Setup**: Defines courses, days, groups, slots, and teacher availability.
- **Constraints**: Ensures session scheduling, group attendance, and teacher assignments.
- **Solver**: Uses `ortools` to maximize slot usage and find a feasible solution.
- **GUI**: Displays the timetable using `tkinter`.

## Customization
- **Courses and Sessions**: Modify `courses`, `num_sessions_per_course`, and `sessions` to change the course list or session types.
- **Days and Slots**: Adjust `num_days`, `days`, and `num_slots_per_day` for a different week structure.
- **Teachers**: Update `teacher_availability` to reflect different teachers or availability.
- **Constraints**: Edit the constraint section to enforce additional rules (e.g., specific teacher preferences).

## Example Output
The GUI shows a grid where:
- Rows represent time slots (e.g., Slot 1, Slot 2, etc.).
- Columns represent days (Sunday to Thursday).
- Cells display course sessions (e.g., "Security Lecture"), group numbers, and assigned teachers, with colors indicating different courses.

## Limitations
- The script assumes a feasible solution exists; if not, it outputs "No feasible solution found."
- Non-lecture sessions (Recitations, Labs) are limited to one group at a time.
- Optimized for Windows due to DPI settings; may require tweaks for other OSes.

## Contributing
Feel free to submit issues or pull requests to improve the solver, add features, or fix bugs!

## License
This project is open-source and available under the [MIT License](LICENSE).
