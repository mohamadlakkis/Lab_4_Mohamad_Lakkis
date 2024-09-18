import threading
import sys
import json
import sqlite3
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMessageBox, QListWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QFormLayout, QHBoxLayout, QGridLayout, QFileDialog, QFrame, QWidget
from PyQt5.QtGui import QWindow
from PyQt5 import QtCore
from tkinter_display import create_tkinter_frame, update_display
from tkinter import TclError

class SchoolManagementApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect('school_management.db')
        self.create_tables()

        self.setWindowTitle("School Management System")
        self.setGeometry(100, 100, 1200, 600)
        self.main_layout = QGridLayout(self)

        self.create_search_frame()
        self.create_student_form()
        self.create_course_form()
        self.create_instructor_form()
        self.create_delete_form()
        self.create_clear_all_form()
        self.create_save_load_buttons()

        self.embed_tkinter_display()

        self.setLayout(self.main_layout)

    def create_tables(self):
        self.conn.execute("PRAGMA foreign_keys = ON")
        try:
            cursor = self.conn.cursor()
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
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")

    def embed_tkinter_display(self):
        self.tk_container = QFrame(self)
        self.tk_container_layout = QVBoxLayout()
        self.tk_container.setLayout(self.tk_container_layout)
        self.main_layout.addWidget(self.tk_container, 1, 2, 4, 1)

        def run_tkinter():
            root, listboxes = create_tkinter_frame()
            try:
                update_display(listboxes)
                root.mainloop()
            except TclError as e:
                print(f"Error with Tkinter: {e}")

        tkinter_thread = threading.Thread(target=run_tkinter)
        tkinter_thread.daemon = True
        tkinter_thread.start()

    def create_search_frame(self):
        search_frame = QtWidgets.QWidget()
        search_layout = QHBoxLayout()

        search_label = QLabel("Search:", self)
        search_layout.addWidget(search_label)

        self.search_entry = QLineEdit()
        search_layout.addWidget(self.search_entry)

        self.search_criteria = QComboBox()
        self.search_criteria.addItems(["Select Criteria", "Name", "ID", "Course"])
        search_layout.addWidget(self.search_criteria)

        self.search_listbox = QListWidget()
        search_layout.addWidget(self.search_listbox)

        search_button = QPushButton("Search", self)
        search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(search_button)

        search_frame.setLayout(search_layout)
        self.main_layout.addWidget(search_frame, 0, 0, 1, 2)

    def perform_search(self):
        query = self.search_entry.text().lower()
        criteria = self.search_criteria.currentText()
        cursor = self.conn.cursor()

        search_results = []
        if criteria == "Name":
            cursor.execute("SELECT * FROM students WHERE LOWER(name) LIKE ?", ('%' + query + '%',))
            students = cursor.fetchall()
            search_results += [f"Student: {s[1]}, ID: {s[0]}" for s in students]

            cursor.execute("SELECT * FROM instructors WHERE LOWER(name) LIKE ?", ('%' + query + '%',))
            instructors = cursor.fetchall()
            search_results += [f"Instructor: {i[1]}, ID: {i[0]}" for i in instructors]

        elif criteria == "ID":
            cursor.execute("SELECT * FROM students WHERE LOWER(student_id) LIKE ?", ('%' + query + '%',))
            students = cursor.fetchall()
            search_results += [f"Student: {s[1]}, ID: {s[0]}" for s in students]

            cursor.execute("SELECT * FROM instructors WHERE LOWER(instructor_id) LIKE ?", ('%' + query + '%',))
            instructors = cursor.fetchall()
            search_results += [f"Instructor: {i[1]}, ID: {i[0]}" for i in instructors]

        elif criteria == "Course":
            cursor.execute("SELECT * FROM courses WHERE LOWER(course_name) LIKE ? OR LOWER(course_id) LIKE ?",
                           ('%' + query + '%', '%' + query + '%'))
            courses = cursor.fetchall()
            for course in courses:
                course_info = f"Course: {course[1]} (ID: {course[0]}), Instructor: {course[2]}"
                search_results.append(course_info)

                cursor.execute("SELECT s.name, s.student_id FROM enrollments e JOIN students s ON e.student_id = s.student_id WHERE e.course_id = ?", (course[0],))
                enrolled_students = cursor.fetchall()
                for student in enrolled_students:
                    search_results.append(f" - Student: {student[0]}, ID: {student[1]}")
        else:
            self.show_message("Error", "Please select a valid search criterion!")
            return

        self.search_listbox.clear()
        if search_results:
            self.search_listbox.addItems(search_results)
        else:
            self.search_listbox.addItem("No matching results found.")

    def create_student_form(self):
        student_form_frame = QtWidgets.QWidget()
        student_form_layout = QFormLayout()

        self.name_entry = QLineEdit()
        self.age_entry = QLineEdit()
        self.id_entry = QLineEdit()
        self.email_entry = QLineEdit()

        self.course_listbox = QListWidget()
        self.course_listbox.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        self.update_course_listbox()

        student_form_layout.addRow("Student Name:", self.name_entry)
        student_form_layout.addRow("Student Age:", self.age_entry)
        student_form_layout.addRow("Student ID:", self.id_entry)
        student_form_layout.addRow("Email:", self.email_entry)
        student_form_layout.addRow("Select Courses:", self.course_listbox)

        submit_button = QPushButton("Register Student")
        submit_button.clicked.connect(self.create_student)
        student_form_layout.addRow(submit_button)

        student_form_frame.setLayout(student_form_layout)
        self.main_layout.addWidget(student_form_frame, 1, 0)

    def update_course_listbox(self):
        self.course_listbox.clear()
        cursor = self.conn.cursor()
        cursor.execute("SELECT course_name, course_id FROM courses")
        courses = cursor.fetchall()
        for course in courses:
            course_name, course_id = course
            self.course_listbox.addItem(f"{course_name} (ID: {course_id})")

    def create_student(self):
        name = self.name_entry.text()
        age = self.age_entry.text()
        student_id = self.id_entry.text()
        email = self.email_entry.text()

        try:
            age = int(age)
        except ValueError:
            self.show_message("Error", "Age must be a valid number!")
            return

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        if cursor.fetchone():
            self.show_message("Error", "A student with this ID already exists!")
            return

        selected_courses = [self.course_listbox.item(i).text().split(' (ID:')[1][:-1] for i in range(self.course_listbox.count()) if self.course_listbox.item(i).isSelected()]

        if name and student_id and email and selected_courses:
            try:
                cursor.execute("INSERT INTO students (student_id, name, age, email) VALUES (?, ?, ?, ?)", 
                            (student_id, name, age, email))
                self.conn.commit()

                for course_id in selected_courses:
                    cursor.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
                self.conn.commit()

                self.show_message("Success", f"Student {name} has been registered!")
                self.name_entry.clear()
                self.age_entry.clear()
                self.id_entry.clear()
                self.email_entry.clear()
                self.course_listbox.clearSelection()

            except sqlite3.Error as e:
                self.show_message("Error", f"Failed to add student to the database: {e}")
        else:
            self.show_message("Error", "All fields are required!")

    def create_course_form(self):
        course_form_frame = QtWidgets.QWidget()
        course_form_layout = QFormLayout()

        self.course_entry = QLineEdit()
        self.course_id_entry = QLineEdit()
        self.course_instructor_combobox = QComboBox()

        self.update_instructor_combobox()

        course_form_layout.addRow("Course Name:", self.course_entry)
        course_form_layout.addRow("Course ID:", self.course_id_entry)
        course_form_layout.addRow("Select Instructor:", self.course_instructor_combobox)

        submit_button = QPushButton("Add Course")
        submit_button.clicked.connect(self.create_course)
        course_form_layout.addRow(submit_button)

        course_form_frame.setLayout(course_form_layout)
        self.main_layout.addWidget(course_form_frame, 2, 0)

    def update_instructor_combobox(self):
        self.course_instructor_combobox.clear()
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, instructor_id FROM instructors")
        instructors = cursor.fetchall()
        for instructor in instructors:
            instructor_name, instructor_id = instructor
            self.course_instructor_combobox.addItem(f"{instructor_name} (ID: {instructor_id})")

    def create_course(self):
        course_name = self.course_entry.text()
        course_id = self.course_id_entry.text()
        selected_instructor_name = self.course_instructor_combobox.currentText()

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM instructors WHERE name = ?", (selected_instructor_name,))
        instructor = cursor.fetchone()

        cursor.execute("SELECT * FROM courses WHERE course_id = ?", (course_id,))
        if cursor.fetchone():
            self.show_message("Error", "A course with this ID already exists!")
            return

        if course_name and course_id and instructor:
            try:
                cursor.execute("INSERT INTO courses (course_id, course_name, instructor_id) VALUES (?, ?, ?)", 
                            (course_id, course_name, instructor[0]))
                self.conn.commit()

                self.show_message("Success", f"Course {course_name} has been added!")
                self.course_entry.clear()
                self.course_id_entry.clear()
                self.course_instructor_combobox.setCurrentIndex(0)

                self.update_course_listbox()
            except sqlite3.Error as e:
                self.show_message("Error", f"Failed to add course to the database: {e}")
        else:
            self.show_message("Error", "All fields are required!")

    def create_instructor_form(self):
        instructor_form_frame = QtWidgets.QWidget()
        instructor_form_layout = QFormLayout()

        self.instructor_name_entry = QLineEdit()
        self.instructor_age_entry = QLineEdit()
        self.instructor_id_entry = QLineEdit()
        self.instructor_email_entry = QLineEdit()

        instructor_form_layout.addRow("Instructor Name:", self.instructor_name_entry)
        instructor_form_layout.addRow("Instructor Age:", self.instructor_age_entry)
        instructor_form_layout.addRow("Instructor ID:", self.instructor_id_entry)
        instructor_form_layout.addRow("Email:", self.instructor_email_entry)

        submit_button = QPushButton("Add Instructor")
        submit_button.clicked.connect(self.create_instructor)
        instructor_form_layout.addRow(submit_button)

        instructor_form_frame.setLayout(instructor_form_layout)
        self.main_layout.addWidget(instructor_form_frame, 3, 0)

    def create_instructor(self):
        name = self.instructor_name_entry.text()
        age = self.instructor_age_entry.text()
        instructor_id = self.instructor_id_entry.text()
        email = self.instructor_email_entry.text()

        try:
            age = int(age)
        except ValueError:
            self.show_message("Error", "Age must be a valid number!")
            return

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM instructors WHERE instructor_id = ?", (instructor_id,))
        if cursor.fetchone():
            self.show_message("Error", "An instructor with this ID already exists!")
            return

        if name and instructor_id and email:
            try:
                cursor.execute("INSERT INTO instructors (instructor_id, name, age, email) VALUES (?, ?, ?, ?)", 
                            (instructor_id, name, age, email))
                self.conn.commit()

                self.show_message("Success", f"Instructor {name} has been added!")
                self.instructor_name_entry.clear()
                self.instructor_age_entry.clear()
                self.instructor_id_entry.clear()
                self.instructor_email_entry.clear()

                self.update_instructor_combobox()
            except sqlite3.Error as e:
                self.show_message("Error", f"Failed to add instructor to the database: {e}")
        else:
            self.show_message("Error", "All fields are required!")

    def create_delete_form(self):
        delete_frame = QtWidgets.QWidget()
        delete_layout = QVBoxLayout()

        self.category_combobox = QComboBox()
        self.category_combobox.addItems(["Select Category", "Students", "Instructors", "Courses"])

        self.record_listbox = QListWidget()

        delete_button = QPushButton("Delete Selected Record")
        delete_button.clicked.connect(self.delete_record)

        delete_layout.addWidget(QLabel("Select Category to Delete:"))
        delete_layout.addWidget(self.category_combobox)
        delete_layout.addWidget(self.record_listbox)
        delete_layout.addWidget(delete_button)

        self.category_combobox.currentIndexChanged.connect(self.update_record_listbox)
        delete_frame.setLayout(delete_layout)
        self.main_layout.addWidget(delete_frame, 4, 0)

    def update_record_listbox(self):
        selected_category = self.category_combobox.currentText()
        self.record_listbox.clear()
        cursor = self.conn.cursor()

        if selected_category == "Students":
            cursor.execute("SELECT * FROM students")
            students = cursor.fetchall()
            for student in students:
                self.record_listbox.addItem(f"{student[1]} (ID: {student[0]})")

        elif selected_category == "Instructors":
            cursor.execute("SELECT * FROM instructors")
            instructors = cursor.fetchall()
            for instructor in instructors:
                self.record_listbox.addItem(f"{instructor[1]} (ID: {instructor[0]})")

        elif selected_category == "Courses":
            cursor.execute("SELECT * FROM courses")
            courses = cursor.fetchall()
            for course in courses:
                self.record_listbox.addItem(f"{course[1]} (ID: {course[0]}) - Instructor: {course[2]}")

    def delete_record(self):
        selected_category = self.category_combobox.currentText()
        selected_item = self.record_listbox.currentItem()

        if selected_item:
            selected_text = selected_item.text()
            cursor = self.conn.cursor()

            if selected_category == "Students":
                student_id = selected_text.split('(ID: ')[1][:-1]
                cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
                cursor.execute("DELETE FROM enrollments WHERE student_id = ?", (student_id,))
                self.conn.commit()

                self.show_message("Success", f"Student (ID: {student_id}) has been deleted.")

            elif selected_category == "Instructors":
                instructor_id = selected_text.split('(ID: ')[1][:-1]
                cursor.execute("DELETE FROM courses WHERE instructor_id = ?", (instructor_id,))
                cursor.execute("DELETE FROM instructors WHERE instructor_id = ?", (instructor_id,))
                self.conn.commit()

                self.show_message("Success", f"Instructor (ID: {instructor_id}) has been deleted.")

            elif selected_category == "Courses":
                course_id = selected_text.split('(ID: ')[1].split(')')[0]
                cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
                cursor.execute("DELETE FROM enrollments WHERE course_id = ?", (course_id,))
                self.conn.commit()

                self.show_message("Success", f"Course (ID: {course_id}) has been deleted.")

            self.update_record_listbox()
            self.update_course_listbox()
            self.update_instructor_combobox()
        else:
            self.show_message("Error", "Please select a record to delete!")

    def create_clear_all_form(self):
        clear_frame = QtWidgets.QWidget()
        clear_layout = QVBoxLayout()

        clear_all_button = QPushButton("Clear All Records")
        clear_all_button.clicked.connect(self.clear_all_records)

        clear_layout.addWidget(clear_all_button)
        clear_frame.setLayout(clear_layout)
        self.main_layout.addWidget(clear_frame, 5, 0)

    def clear_all_records(self):
        if QMessageBox.question(self, "Confirm", "Are you sure you want to delete all records? This action cannot be undone!",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            cursor = self.conn.cursor()
            
            try:
                cursor.execute("DELETE FROM enrollments")
                cursor.execute("DELETE FROM courses")
                cursor.execute("DELETE FROM students")
                cursor.execute("DELETE FROM instructors")
                self.conn.commit()

                self.update_course_listbox()
                self.update_instructor_combobox()
                self.update_record_listbox()

                self.update_search_criteria()
                self.update_category_combobox()

                self.show_message("Success", "All records have been cleared!")
            except sqlite3.Error as e:
                self.show_message("Error", f"Failed to clear records: {e}")

    def update_search_criteria(self):
        self.search_entry.clear()
        self.search_listbox.clear()
        self.search_criteria.setCurrentIndex(0)

    def update_category_combobox(self):
        self.category_combobox.setCurrentIndex(0)
        self.record_listbox.clear()

    def create_save_load_buttons(self):
        save_load_frame = QtWidgets.QWidget()
        save_load_layout = QHBoxLayout()

        save_button = QPushButton("Save Data")
        save_button.clicked.connect(self.save_data)
        save_load_layout.addWidget(save_button)

        load_button = QPushButton("Load Data")
        load_button.clicked.connect(self.load_data)
        save_load_layout.addWidget(load_button)

        save_load_frame.setLayout(save_load_layout)
        self.main_layout.addWidget(save_load_frame, 6, 0, 1, 2)

    def save_data(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "JSON Files (*.json);;All Files (*)")
        if filename:
            data = {
                "students": [],
                "instructors": [],
                "courses": []
            }
            cursor = self.conn.cursor()

            cursor.execute("SELECT * FROM students")
            students = cursor.fetchall()
            for student in students:
                data["students"].append({
                    "student_id": student[0],
                    "name": student[1],
                    "age": student[2],
                    "email": student[3]
                })

            cursor.execute("SELECT * FROM instructors")
            instructors = cursor.fetchall()
            for instructor in instructors:
                data["instructors"].append({
                    "instructor_id": instructor[0],
                    "name": instructor[1],
                    "age": instructor[2],
                    "email": instructor[3]
                })

            cursor.execute("SELECT * FROM courses")
            courses = cursor.fetchall()
            for course in courses:
                data["courses"].append({
                    "course_id": course[0],
                    "course_name": course[1],
                    "instructor_id": course[2]
                })

            with open(filename, 'w') as file:
                json.dump(data, file)

            self.show_message("Success", "Data has been saved!")

    def load_data(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load File", "", "JSON Files (*.json);;All Files (*)")
        if filename:
            with open(filename, 'r') as file:
                data = json.load(file)

            cursor = self.conn.cursor()

            try:
                cursor.execute("DELETE FROM enrollments")
                cursor.execute("DELETE FROM courses")
                cursor.execute("DELETE FROM students")
                cursor.execute("DELETE FROM instructors")
                self.conn.commit()

                for student in data["students"]:
                    cursor.execute("INSERT INTO students (student_id, name, age, email) VALUES (?, ?, ?, ?)",
                                (student["student_id"], student["name"], student["age"], student["email"]))

                for instructor in data["instructors"]:
                    cursor.execute("INSERT INTO instructors (instructor_id, name, age, email) VALUES (?, ?, ?, ?)",
                                (instructor["instructor_id"], instructor["name"], instructor["age"], instructor["email"]))

                for course in data["courses"]:
                    cursor.execute("INSERT INTO courses (course_id, course_name, instructor_id) VALUES (?, ?, ?)",
                                (course["course_id"], course["course_name"], course["instructor_id"]))

                self.conn.commit()

                self.update_course_listbox()
                self.update_instructor_combobox()

                self.show_message("Success", "Data has been loaded!")
            
            except sqlite3.Error as e:
                self.show_message("Error", f"Failed to load data: {e}")

    def update_instructor_combobox(self):
        self.course_instructor_combobox.clear()
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM instructors")
        instructors = cursor.fetchall()
        instructor_names = [instructor[0] for instructor in instructors]
        self.course_instructor_combobox.addItems(instructor_names)

    def show_message(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SchoolManagementApp()
    window.show()
    sys.exit(app.exec_())
