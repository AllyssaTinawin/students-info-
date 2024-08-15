from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty
import datetime
from datetime import date
from kivymd.uix.behaviors import FakeRectangularElevationBehavior
from kivy.core.window import Window
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.snackbar import Snackbar  
from kivy.metrics import dp 
from kivymd.icon_definitions import md_icons
from kivymd.uix.button import MDFloatingActionButton, MDRaisedButton,MDFlatButton
from kivymd.toast import toast
from kivymd.uix.textfield import MDTextField
import sqlite3

Window.size = (900, 600)

class QuizOne(MDApp):
    def build(self):
        self.title='TINAWIN'        
        self.icon = 'android'
        self.connect_db()
        root = Builder.load_file('QuizLayout.kv')
        self.display_student_info(root)
        return root
    
    def connect_db(self):
        self.conn = sqlite3.connect('quiz_data.db')
        self.cur = self.conn.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS students (
                                id INTEGER PRIMARY KEY,
                                student_number TEXT,
                                first_name TEXT,
                                last_name TEXT,
                                course TEXT,
                                year TEXT)''')
        self.conn.commit()

    def on_stop(self):
        self.conn.close()
    
    def display_student_info(self, root):
        self.cur.execute("SELECT * FROM students")
        students = self.cur.fetchall()

    
        table = MDGridLayout(cols=5, row_default_height=dp(40), spacing=dp(10))
        
        
        table.add_widget(MDLabel(text="Student Number", halign="center", valign="middle"))
        table.add_widget(MDLabel(text="First Name", halign="center", valign="middle"))
        table.add_widget(MDLabel(text="Last Name", halign="center", valign="middle"))
        table.add_widget(MDLabel(text="Course", halign="center", valign="middle"))
        table.add_widget(MDLabel(text="Year", halign="center", valign="middle"))

       
        for student in students:
            for data in student[1:]:
                table.add_widget(MDLabel(text=str(data), halign="center", valign="middle"))

        
        root.ids.student_info_container.add_widget(table)

    def add_student_info(self):
        student_number = self.root.ids.studentnumber.text
        first_name = self.root.ids.firstname.text
        last_name = self.root.ids.lastname.text
        course = self.root.ids.course.text
        year = self.root.ids.year.text


        self.cur.execute("SELECT * FROM students WHERE student_number = ?", (student_number,))
        existing_student = self.cur.fetchone()

        if existing_student:
            toast('Student number already exists! Duplicate entry detected.')
        elif student_number != '' and last_name != '' and first_name != '' and course != '' and year != '':
            self.cur.execute("INSERT INTO students (student_number, first_name, last_name, course, year) VALUES (?, ?, ?, ?, ?)",
                            (student_number, first_name, last_name, course, year))
            self.conn.commit()
            self.root.ids.studentnumber.text = ''
            self.root.ids.firstname.text = ''
            self.root.ids.lastname.text = ''
            self.root.ids.course.text = ''
            self.root.ids.year.text = ''
            toast('Student information added successfully!')

            self.root.ids.student_info_container.clear_widgets()
            self.display_student_info(self.root)
        else:
            toast('Blank entries detected!')
    
    def delete_student_info(self):
        student_number_to_delete = self.root.ids.studentnumber.text

        if student_number_to_delete:
            confirm_dialog = MDDialog(
                text="Are you sure you want to delete this student?",
                buttons=[
                    MDFlatButton(
                        text="Cancel", on_release=lambda *args: confirm_dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="Delete",
                        on_release=lambda *args: self.confirm_delete_student(
                            student_number_to_delete
                        ),
                    ),
                ],
            )
            confirm_dialog.open()
        else:
            toast('Please enter a student number to delete')
        
    def confirm_delete_student(self, student_number_to_delete):
        self.cur.execute(
            "DELETE FROM students WHERE student_number = ?", (student_number_to_delete,)
        )
        self.conn.commit()
        toast('Student information deleted successfully!')

        self.root.ids.student_info_container.clear_widgets()
        self.display_student_info(self.root)
        
    def edit_student_info(self):
        student_number_to_edit = self.root.ids.studentnumber.text

        if student_number_to_edit:
            self.cur.execute("SELECT * FROM students WHERE student_number = ?", (student_number_to_edit,))
            student = self.cur.fetchone()

            if student:

                edit_dialog = MDDialog(
                    title="Edit Student Information",
                    type="custom",
                    content_cls=MDGridLayout(
                        cols=2,
                        adaptive_height=True,
                        padding=dp(10),
                        spacing=dp(10)
                    ),
                    buttons=[
                        MDFlatButton(
                            text="Cancel",
                            on_release=lambda *args: edit_dialog.dismiss()
                        ),
                        MDFlatButton(
                            text="Save",
                            on_release=lambda *args: self.save_edited_student_info(
                                student_number_to_edit,
                                edit_dialog
                            )
                        ),
                    ]
                )


                for attr_name, attr_value in zip(["First Name", "Last Name", "Course", "Year"], student[2:]):
                    edit_dialog.content_cls.add_widget(MDLabel(text=attr_name))
                    edit_dialog.content_cls.add_widget(MDTextField(hint_text=attr_name, text=str(attr_value), id=f'{attr_name.lower().replace(" ", "_")}_textfield'))

                edit_dialog.open()
            else:
                toast("Student not found")
        else:
            toast("Please enter a student number to edit")

    def save_edited_student_info(self, student_number_to_edit, dialog):
        edited_attributes = {}


        for child in dialog.content_cls.children:
            if isinstance(child, MDTextField):
                attr_name = child.hint_text.lower()
                attr_value = child.text
                edited_attributes[attr_name] = attr_value

 
        self.cur.execute(
            "UPDATE students SET first_name = ?, last_name = ?, course = ?, year = ? WHERE student_number = ?", 
            (edited_attributes["first name"], edited_attributes["last name"], edited_attributes["course"], edited_attributes["year"], student_number_to_edit)
        )
        
        self.conn.commit()
        dialog.dismiss()
        toast("Student information updated successfully!")

        self.root.ids.student_info_container.clear_widgets()
        self.display_student_info(self.root)


    

QuizOne().run()
