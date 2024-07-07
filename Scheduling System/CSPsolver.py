import collections
from ortools.sat.python import cp_model
import tkinter as tk
from tkinter import ttk
from ctypes import windll

# Create the model
model = cp_model.CpModel()

# Constants--------------------------------------------------------------------------------------------------------------------------------------------
num_courses = 8
num_days = 5
num_groups = 6
num_slots_per_day = {0: 5, 1: 5, 2: 3, 3: 5, 4: 5} 
num_sessions_per_course = [2, 2, 2, 1, 2, 2, 3, 3]
days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
courses =["Security", "FM","NA","Entrepreneurship","OR2",
"DA&IC","Networks2","AI"]
sessions=["Lecture","Recitation","Lab"]
num_teachers = 14

teacher_availability = {
    0: {0: ["Djebari"], 1: ["Djennane", "Kassa"], "Color": "#FF9999"},  # Light red
    1: {0: ["Zedek"], 1: ["Zedek"], "Color": "#99FF99"},  # Light green
    2: {0: ["Alkama"], 1: ["Alkama"], "Color": "#9999FF"},  # Light blue
    3: {0: ["Kaci"], "Color": "#FFFF99"},  # Light yellow
    4: {0: ["Issaadi"], 1: ["Issaadi"], "Color": "#99FFFF"},  # Light cyan
    5: {0: ["Djenadi"], 1: ["Djenadi"], "Color": "#FF99FF"},  # Light magenta
    6: {0: ["Zenadji"], 1: ["Zenadji", "Sahli"], 2: ["Zaidi"], "Color": "#FFCC99"},  # Light orange
    7: {0: ["Lekehali"], 1: ["Lekehali"], 2: ["Hamma", "Bechar","Abbas & Ladlani"], "Color": "#CC99FF"}  # Light purple
}

# Variables----------------------------------------------------------------------------------------------------------------------------------
X = {} # e.g: { (c,s,d,t) : "X_c_s_d_t" == [0 or 1] } whether a session of a given course is scheduled on a given day at a given time.
Z = {} # e.g: { (c,s,d,t,g) : "X_c_s_d_t_g" == [0 or 1] } whether a group is attending the session "X_c_s_d_t".

# Create the variables with the domain being [0..1] (Boolean)
for c in range(num_courses):
    for s in range(num_sessions_per_course[c]):
        for d in range(num_days):
            for t in range(num_slots_per_day[d]):
                X[(c, s, d, t)] = model.NewBoolVar(f'X_{c}_{s}_{d}_{t}') # e.g: X:{ (0,0,0,0) : "X_0_0_0_0" = [0..1] }
                for g in range(num_groups):
                    Z[(c, s, d, t, g)] = model.NewBoolVar(f'Z_{c}_{s}_{d}_{t}_{g}') 

# Constraints -------------------------------------------------------------------------------------------------------------------------------
# Each session must be scheduled exactly once:
for c in range(num_courses):
    for s in range(1,num_sessions_per_course[c]):
        model.Add(sum(X[(c, s, d, t)] 
                      for d in range(num_days) 
                      for t in range(num_slots_per_day[d])) >= 1) # e.g. : X[(7,2,0,0)] + X[(7,2,1,4)] + ...  == 1

# Each group must attend all sessions of each course
for g in range(num_groups):
    for c in range(num_courses):
        for s in range(num_sessions_per_course[c]):
            model.Add(sum(Z[(c, s, d, t, g)] for d in range(num_days) for t in range(num_slots_per_day[d])) == 1)

# Add constraints to ensure each day has at least one recitation and one lab
for d in range(num_days):
    # Recitation constraint
    model.Add(sum(X[(c, s, d, t)] 
                  for c in range(num_courses) 
                  for t in range(num_slots_per_day[d]) 
                  for s in range(1,num_sessions_per_course[c])) >= 1)

# A group can only attend one session at a time
for g in range(num_groups):
    for d in range(num_days):
        for t in range(num_slots_per_day[d]):
            model.Add(sum(Z[(c, s, d, t, g)] 
                          for c in range(num_courses) 
                          for s in range(num_sessions_per_course[c])) <= 1)

# Each session must be scheduled exactly once for each group
for c in range(num_courses):
    for s in range(num_sessions_per_course[c]):
        for g in range(num_groups):
            model.Add(sum(Z[(c, s, d, t, g)] 
                          for d in range(num_days) 
                          for t in range(num_slots_per_day[d])) == 1)

# Non-lecture sessions must be attended by only one group
for c in range(num_courses):
    for s in range(1, num_sessions_per_course[c]):  # start from 1 to exclude lecture session 0
        for d in range(num_days):
            for t in range(num_slots_per_day[d]):
                # Ensure that for each non-lecture session, it is scheduled without requiring all groups to attend
                model.Add(sum(Z[(c, s, d, t, g)] for g in range(num_groups)) <= 1)

# Lecture sessions (session 0) must be attended by all groups simultaneously
for c in range(num_courses):
    for d in range(num_days):
        for t in range(num_slots_per_day[d]):
            lecture = X[(c, 0, d, t)]
            for g in range(num_groups):
                model.Add(Z[(c, 0, d, t, g)] == lecture)

# Ensure no group studies for more than 3 consecutive slots
for g in range(num_groups):
    for d in range(num_days):
        for t in range(num_slots_per_day[d] - 2):
            # Sum up sessions in 3 consecutive slots for group g on day d starting at slot t
            consecutive_sessions = sum(Z[(c, s, d, t + i, g)] 
                                       for c in range(num_courses) 
                                       for s in range(num_sessions_per_course[c]) 
                                       for i in range(3))
            model.Add(consecutive_sessions <= 3)
        if num_slots_per_day[d] > 4:
            for t in range(num_slots_per_day[d] - 3):
                consecutive_sessions = sum(Z[(c, s, d, t + i, g)] 
                                           for c in range(num_courses) 
                                           for s in range(num_sessions_per_course[c]) 
                                           for i in range(4))
                model.Add(consecutive_sessions <= 3)

# Maximize the number of slots used
slot_usage = []
for d in range(num_days):
    for t in range(num_slots_per_day[d]):
        slot_usage.append(sum(X[(c, s, d, t)] 
                              for c in range(num_courses) 
                              for s in range(num_sessions_per_course[c] ) 
                              if sessions[s] != "Lecture"))
model.Maximize(sum(slot_usage))

# Solver---------------------------------------------------------------------------------------------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

def format_timetable(solver,X,Z):
        timetable = {}
        for d in range(num_days):
            for t in range(num_slots_per_day[d]):
                timetable[(d, t)] = []
                for c in range(num_courses):
                    for s in range(num_sessions_per_course[c]):
                        if solver.Value(X[(c, s, d, t)]):
                            for g in range(num_groups):
                                if solver.Value(Z[(c, s, d, t, g)]):
                                    timetable[(d, t)].append((f'{courses[c]} {sessions[s]}', f'Group {g+1}'))                                    
        return timetable
def present_solution(timetable, teacher_assignment):
    #This is used to enable high DPI (Dot Per Inch) support for the Tkinter GUI on Windows systems.
    if windll.shcore: 
        windll.shcore.SetProcessDpiAwareness(1) 

    # Create the main Tkinter window
    root = tk.Tk()
    root.title("Timetable")

    # Create a frame to hold the timetable grid
    frame = ttk.Frame(root, padding=10)
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S)) # type: ignore
    
    # Create headers for days
    for d in range(num_days):
        tk.Label(frame, text=days[d], font=("Helvetica", 10, "bold"),
                 relief=tk.RAISED, padx=10, pady=5).grid(row=0, column=(d * 7) + 2, columnspan=7, sticky='nsew')

    # Create headers for time slots
    for t in range(max(num_slots_per_day.values())):
        slot_label = f"Slot {t + 1}"
        tk.Label(frame, text=slot_label, font=("Helvetica", 10, "bold"),
                 relief=tk.RAISED, padx=10, pady=5).grid(row=(t * 7) + 1, column=0, rowspan=7, sticky='nsew')

        for line in range(6):
            group_number = str(line + 1)
            tk.Label(frame, text=group_number, font=("Helvetica", 10, "bold"),
                     relief=tk.RAISED, padx=10, pady=5).grid(row=(t * 7) + line + 2, column=1, sticky='nsew')
            
    # Populate timetable data into the grid
    for d in range(num_days):
        for t in range(num_slots_per_day[d]):
            groups_sessions = timetable[(d, t)]
            groups_sessions = sorted(groups_sessions , key = lambda i: i[1][6])
             # Create a mapping of group index to session
            group_to_session = {int(group[6]) - 1: (course_session, group) for (course_session, group) in groups_sessions}
            
            for line in range(6):
                content = " "
                if line in group_to_session:
                    (course_session, group) = group_to_session[line]
                                
                    course, session = course_session.split(" ")
                    course_idx = courses.index(course)
                    color=teacher_availability[course_idx]["Color"]
                    if session == "Lecture":
                        content = "\n".join([f"{course_session} - (Teacher: {teacher_availability[courses.index(course)][0][0]})"])
                        lecture_frame = tk.Frame(frame, relief=tk.RAISED)
                        lecture_frame.grid(row=(t * 7) + 2, column=(d * 7) + 2, rowspan=6, columnspan=7, sticky='nsew')
                        tk.Label(lecture_frame, text=content,relief=tk.RAISED, font=("Helvetica", 9), bg=color,padx=10, pady=6).pack(fill=tk.BOTH, expand=True)
                    else:
                        content = "\n".join([f"{course_session} - (Teacher: {teacher_assignment[(d, t, course_session, group)]})"])
                        label = tk.Label(frame, text=content, relief=tk.RAISED,  pady=5,
                                            font=("Helvetica", 9), bg=color)
                        label.grid(row=(t * 7) + line + 2, column=(d * 7) + 2, columnspan=7, rowspan=1, sticky='nsew',  pady=0)
                else:
                    color = "white"
                    label = tk.Label(frame, text=content, relief=tk.RAISED, padx=10, pady=5,
                                        font=("Helvetica", 9), bg=color)
                    label.grid(row=(t * 7) + line + 2, column=(d * 7) + 2, columnspan=7, rowspan=1, sticky='nsew',  pady=0)
                
                
    # Make the grid cells auto-expandable
    for i in range((num_days * 7) + 2):  # Adjusted for new column structure
        frame.columnconfigure(i, weight=1)
    for i in range((max(num_slots_per_day.values()) * 7) + 2):  # Adjusted for new row structure
        frame.rowconfigure(i, weight=1)
    

    # Run the Tkinter main loop
    root.mainloop()
def assign_teachers(timetable):
        teacher_assignment = collections.defaultdict(list)
        teacher_load = collections.defaultdict(int)
        for d in range(num_days):
            for t in range(num_slots_per_day[d]):
                if (d, t) in timetable:
                    for (course_session, group) in timetable[(d, t)]:
                        course, session = course_session.split(" ")
                        course_idx = courses.index(course)
                        session_idx = sessions.index(session)
                        
                        if session_idx in teacher_availability[course_idx]:
                            available_teachers = teacher_availability[course_idx][session_idx]
                        else:
                            available_teachers = [teacher_availability[course_idx][0]]

                        # Assign the teacher with the least load (to balance the assignment)
                        assigned_teacher = min(available_teachers, key=lambda teacher: teacher_load[teacher])
                        teacher_load[assigned_teacher] += 1 # e.g. teacher_load["Djennane"] += 1 
                        teacher_assignment[(d, t, course_session, group)] = assigned_teacher
        return teacher_assignment

# Getting the solution and presenting it using Tkinter---------------------------------------------------------------------------------------------
if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
    
    # Creating the timetable dictionary
    timetable = format_timetable(solver,X,Z)    
    # Assign teachers based on their specialties
    teacher_assignment = assign_teachers(timetable)
    # Representing the solution using Tkinter
    present_solution(timetable, teacher_assignment)

else:
    print('No feasible solution found.')