import tkinter as tk
from tkinter import Listbox, Button
import sqlite3

def update_display(listboxes):
    """ Update the listboxes with data from the database """
    conn = sqlite3.connect('school_management.db')
    cursor = conn.cursor()

    student_listbox, instructor_listbox, course_listbox = listboxes

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
        course_listbox.insert(tk.END, f"{course[1]} (ID: {course[0]})")

    conn.close()

def create_tkinter_frame():
    """ Create the Tkinter window and return the root and listboxes """
    root = tk.Tk()
    root.title("Database Records")
    root.geometry("400x400")

    student_listbox = Listbox(root, height=6, width=40)
    instructor_listbox = Listbox(root, height=6, width=40)
    course_listbox = Listbox(root, height=6, width=40)

    student_listbox.pack(pady=5)
    instructor_listbox.pack(pady=5)
    course_listbox.pack(pady=5)

    refresh_button = Button(root, text="Refresh", command=lambda: update_display((student_listbox, instructor_listbox, course_listbox)))
    refresh_button.pack(pady=10)

    return root, (student_listbox, instructor_listbox, course_listbox)
