import sqlite3
import json
import tkinter as tk
from tkinter import messagebox, filedialog


def create_tables():
    conn = sqlite3.connect('school_management.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT,
            age INTEGER,
            email TEXT
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS instructors (
            instructor_id TEXT PRIMARY KEY,
            name TEXT,
            age INTEGER,
            email TEXT
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            course_name TEXT,
            instructor_id TEXT,
            FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            student_id TEXT,
            course_id TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id),
            PRIMARY KEY (student_id, course_id)
        )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")
        messagebox.showerror("Database Error", f"An error occurred while creating tables: {e}")
    finally:
        conn.close()

def save_data_to_json():
    filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if filename:
        conn = sqlite3.connect('school_management.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        cursor.execute("SELECT * FROM instructors")
        instructors = cursor.fetchall()
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
        cursor.execute("SELECT * FROM enrollments")
        enrollments = cursor.fetchall()

        data = {
            "students": [{"student_id": s[0], "name": s[1], "age": s[2], "email": s[3]} for s in students],
            "instructors": [{"instructor_id": i[0], "name": i[1], "age": i[2], "email": i[3]} for i in instructors],
            "courses": [{"course_id": c[0], "course_name": c[1], "instructor_id": c[2]} for c in courses],
            "enrollments": [{"student_id": e[0], "course_id": e[1]} for e in enrollments]
        }

        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        messagebox.showinfo("Success", "Data has been saved to JSON file successfully!")
        conn.close()

def load_data_from_json():
    filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
    if filename:
        conn = sqlite3.connect('school_management.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students")
        cursor.execute("DELETE FROM instructors")
        cursor.execute("DELETE FROM courses")
        cursor.execute("DELETE FROM enrollments")
        conn.commit()

        with open(filename, 'r') as json_file:
            data = json.load(json_file)

            for student in data["students"]:
                cursor.execute("INSERT INTO students (student_id, name, age, email) VALUES (?, ?, ?, ?)",
                               (student["student_id"], student["name"], student["age"], student["email"]))

            for instructor in data["instructors"]:
                cursor.execute("INSERT INTO instructors (instructor_id, name, age, email) VALUES (?, ?, ?, ?)",
                               (instructor["instructor_id"], instructor["name"], instructor["age"], instructor["email"]))
            for course in data["courses"]:
                cursor.execute("INSERT INTO courses (course_id, course_name, instructor_id) VALUES (?, ?, ?)",
                               (course["course_id"], course["course_name"], course["instructor_id"]))
            if "enrollments" in data:
                for enrollment in data["enrollments"]:
                    cursor.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
                                   (enrollment["student_id"], enrollment["course_id"]))

        conn.commit()
        conn.close()
        update_display()
        messagebox.showinfo("Success", "Data has been loaded from JSON file successfully!")

def create_student():
    student_id = student_id_entry.get()
    name = student_name_entry.get()
    age = student_age_entry.get()
    email = student_email_entry.get()

    try:
        age = int(age)
    except ValueError:
        messagebox.showerror("Error", "Age must be a valid number!")
        return

    conn = sqlite3.connect('school_management.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    if cursor.fetchone():
        messagebox.showerror("Error", "A student with this ID already exists!")
        return

    cursor.execute("INSERT INTO students (student_id, name, age, email) VALUES (?, ?, ?, ?)",
                   (student_id, name, age, email))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Student {name} has been registered!")
    student_name_entry.delete(0, tk.END)
    student_age_entry.delete(0, tk.END)
    student_id_entry.delete(0, tk.END)
    student_email_entry.delete(0, tk.END)
    update_display()

def create_instructor():
    instructor_id = instructor_id_entry.get()
    name = instructor_name_entry.get()
    age = instructor_age_entry.get()
    email = instructor_email_entry.get()

    try:
        age = int(age)
    except ValueError:
        messagebox.showerror("Error", "Age must be a valid number!")
        return

    conn = sqlite3.connect('school_management.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM instructors WHERE instructor_id = ?", (instructor_id,))
    if cursor.fetchone():
        messagebox.showerror("Error", "An instructor with this ID already exists!")
        return

    cursor.execute("INSERT INTO instructors (instructor_id, name, age, email) VALUES (?, ?, ?, ?)",
                   (instructor_id, name, age, email))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Instructor {name} has been registered!")
    instructor_name_entry.delete(0, tk.END)
    instructor_age_entry.delete(0, tk.END)
    instructor_id_entry.delete(0, tk.END)
    instructor_email_entry.delete(0, tk.END)
    update_display()

def create_course():
    course_id = course_id_entry.get()
    course_name = course_name_entry.get()
    instructor_name = course_instructor_combobox.get()

    conn = sqlite3.connect('school_management.db')
    cursor = conn.cursor()

    cursor.execute("SELECT instructor_id FROM instructors WHERE name = ?", (instructor_name,))
    instructor = cursor.fetchone()

    cursor.execute("SELECT * FROM courses WHERE course_id = ?", (course_id,))
    if cursor.fetchone():
        messagebox.showerror("Error", "A course with this ID already exists!")
        return

    if instructor:
        cursor.execute("INSERT INTO courses (course_id, course_name, instructor_id) VALUES (?, ?, ?)",
                       (course_id, course_name, instructor[0]))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Course {course_name} has been added!")
        course_name_entry.delete(0, tk.END)
        course_id_entry.delete(0, tk.END)
        course_instructor_combobox.set('')
        update_display()
    else:
        messagebox.showerror("Error", "Selected instructor not found!")

def delete_record():
    selected_category = delete_category_combobox.get()
    selected_item = delete_record_listbox.get(tk.ACTIVE)

    conn = sqlite3.connect('school_management.db')
    cursor = conn.cursor()

    if selected_category == "Students":
        student_id = selected_item.split('(ID: ')[1][:-1]
        cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM enrollments WHERE student_id = ?", (student_id,))
        conn.commit()

        messagebox.showinfo("Success", f"Student (ID: {student_id}) has been deleted.")
    elif selected_category == "Instructors":
        instructor_id = selected_item.split('(ID: ')[1][:-1]
        cursor.execute("DELETE FROM instructors WHERE instructor_id = ?", (instructor_id,))
        cursor.execute("DELETE FROM courses WHERE instructor_id = ?", (instructor_id,))
        conn.commit()

        messagebox.showinfo("Success", f"Instructor (ID: {instructor_id}) has been deleted.")
    elif selected_category == "Courses":
        course_id = selected_item.split('(ID: ')[1].split(') -')[0]
        cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
        cursor.execute("DELETE FROM enrollments WHERE course_id = ?", (course_id,))
        conn.commit()

        messagebox.showinfo("Success", f"Course (ID: {course_id}) has been deleted.")

    update_display()
    conn.close()

def update_display():
    conn = sqlite3.connect('school_management.db')
    cursor = conn.cursor()

    # Update students list
    student_listbox.delete(0, tk.END)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    for student in students:
        student_listbox.insert(tk.END, f"{student[1]} (ID: {student[0]})")

    instructor_listbox.delete(0, tk.END)
    cursor.execute("SELECT * FROM instructors")
    instructors = cursor.fetchall()
    for instructor in instructors:
        instructor_listbox.insert(tk.END, f"{instructor[1]} (ID: {instructor[0]})")

    course_listbox.delete(0, tk.END)
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()
    for course in courses:
        course_listbox.insert(tk.END, f"{course[1]} (ID: {course[0]}) - Instructor: {course[2]}")

    conn.close()

root = tk.Tk()
root.title("School Management System")
root.geometry("1000x600")
student_frame = tk.LabelFrame(root, text="Add Student")
student_frame.grid(row=0, column=0, padx=10, pady=10)

tk.Label(student_frame, text="Student Name").grid(row=0, column=0)
student_name_entry = tk.Entry(student_frame)
student_name_entry.grid(row=0, column=1)

tk.Label(student_frame, text="Student Age").grid(row=1, column=0)
student_age_entry = tk.Entry(student_frame)
student_age_entry.grid(row=1, column=1)

tk.Label(student_frame, text="Student ID").grid(row=2, column=0)
student_id_entry = tk.Entry(student_frame)
student_id_entry.grid(row=2, column=1)

tk.Label(student_frame, text="Email").grid(row=3, column=0)
student_email_entry = tk.Entry(student_frame)
student_email_entry.grid(row=3, column=1)

tk.Button(student_frame, text="Register Student", command=create_student).grid(row=4, columnspan=2)

instructor_frame = tk.LabelFrame(root, text="Add Instructor")
instructor_frame.grid(row=1, column=0, padx=10, pady=10)

tk.Label(instructor_frame, text="Instructor Name").grid(row=0, column=0)
instructor_name_entry = tk.Entry(instructor_frame)
instructor_name_entry.grid(row=0, column=1)

tk.Label(instructor_frame, text="Instructor Age").grid(row=1, column=0)
instructor_age_entry = tk.Entry(instructor_frame)
instructor_age_entry.grid(row=1, column=1)

tk.Label(instructor_frame, text="Instructor ID").grid(row=2, column=0)
instructor_id_entry = tk.Entry(instructor_frame)
instructor_id_entry.grid(row=2, column=1)
tk.Label(instructor_frame, text="Email").grid(row=3, column=0)
instructor_email_entry = tk.Entry(instructor_frame)
instructor_email_entry.grid(row=3, column=1)

tk.Button(instructor_frame, text="Add Instructor", command=create_instructor).grid(row=4, columnspan=2)

course_frame = tk.LabelFrame(root, text="Add Course")
course_frame.grid(row=2, column=0, padx=10, pady=10)

tk.Label(course_frame, text="Course Name").grid(row=0, column=0)
course_name_entry = tk.Entry(course_frame)
course_name_entry.grid(row=0, column=1)

tk.Label(course_frame, text="Course ID").grid(row=1, column=0)
course_id_entry = tk.Entry(course_frame)
course_id_entry.grid(row=1, column=1)

tk.Label(course_frame, text="Instructor Name").grid(row=2, column=0)
course_instructor_combobox = tk.Entry(course_frame)
course_instructor_combobox.grid(row=2, column=1)

tk.Button(course_frame, text="Add Course", command=create_course).grid(row=3, columnspan=2)

display_frame = tk.LabelFrame(root, text="Current Records")
display_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=10)

tk.Label(display_frame, text="Students").grid(row=0, column=0)
student_listbox = tk.Listbox(display_frame, height=6, width=40)
student_listbox.grid(row=1, column=0)

tk.Label(display_frame, text="Instructors").grid(row=2, column=0)
instructor_listbox = tk.Listbox(display_frame, height=6, width=40)
instructor_listbox.grid(row=3, column=0)

tk.Label(display_frame, text="Courses").grid(row=4, column=0)
course_listbox = tk.Listbox(display_frame, height=6, width=40)
course_listbox.grid(row=5, column=0)

delete_frame = tk.LabelFrame(root, text="Delete Record")
delete_frame.grid(row=3, column=0, padx=10, pady=10)

tk.Label(delete_frame, text="Category").grid(row=0, column=0)
delete_category_combobox = tk.Entry(delete_frame)
delete_category_combobox.grid(row=0, column=1)

delete_record_listbox = tk.Listbox(delete_frame, height=6, width=40)
delete_record_listbox.grid(row=1, column=0, columnspan=2)

tk.Button(delete_frame, text="Delete Selected", command=delete_record).grid(row=2, columnspan=2)

save_load_frame = tk.LabelFrame(root, text="Save/Load Data")
save_load_frame.grid(row=4, column=0, padx=10, pady=10)

tk.Button(save_load_frame, text="Save to JSON", command=save_data_to_json).grid(row=0, column=0)
tk.Button(save_load_frame, text="Load from JSON", command=load_data_from_json).grid(row=0, column=1)

create_tables()
update_display()
root.mainloop()


