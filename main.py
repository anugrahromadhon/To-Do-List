import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
import sqlite3

# Database management
class TaskDatabase:
    def __init__(self, db_name="tasks.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        self.connection.commit()

    def add_task(self, description):
        self.cursor.execute(
            "INSERT INTO tasks (description, completed) VALUES (?, ?)",
            (description, 0)
        )
        self.connection.commit()

    def get_tasks(self):
        self.cursor.execute("SELECT * FROM tasks")
        return self.cursor.fetchall()

    def update_task_status(self, task_id, completed):
        self.cursor.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?", (completed, task_id)
        )
        self.connection.commit()

    def delete_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.connection.commit()

    def close(self):
        self.connection.close()

# Main application UI
class ToDoListApp(App):
    def build(self):
        self.db = TaskDatabase()
        self.title = "To-Do List"
        
        self.root = BoxLayout(orientation='vertical')

        # Input field for new tasks
        self.input_box = BoxLayout(orientation='horizontal', size_hint_y=0.1, padding=5, spacing=5)
        self.task_input = TextInput(hint_text="Enter a new task", multiline=False)
        self.add_button = Button(text="Add", on_press=self.add_task, background_color=(0.2, 0.6, 0.8, 1))
        self.input_box.add_widget(self.task_input)
        self.input_box.add_widget(self.add_button)
        
        # Task list with scroll view
        self.scroll_view = ScrollView(size_hint=(1, 0.9))
        self.task_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        self.scroll_view.add_widget(self.task_list)

        self.refresh_task_list()

        self.root.add_widget(self.input_box)
        self.root.add_widget(self.scroll_view)
        
        return self.root

    def refresh_task_list(self):
        self.task_list.clear_widgets()
        tasks = self.db.get_tasks()
        for task in tasks:
            task_item = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=5, spacing=5)
            
            with task_item.canvas.before:
                Color(1, 0.8, 1) if task[2] else Color(1, 0.8, 0.8, 1)
                self.rect = Rectangle(size=task_item.size, pos=task_item.pos)
            task_item.bind(size=lambda instance, value: self._update_rect(task_item),
                           pos=lambda instance, value: self._update_rect(task_item))

            checkbox = CheckBox(active=bool(task[2]), size_hint_x=0.1)
            checkbox.bind(active=lambda instance, value, task_id=task[0]: self.toggle_task_status(task_id, value))

            task_label = Label(text=task[1], size_hint_x=0.7, halign="left", valign="middle")
            task_label.bind(size=task_label.setter('text_size'))

            delete_button = Button(text="Delete", size_hint_x=0.2, background_color=(1, 0.3, 0.3, 1), on_press=lambda x, task_id=task[0]: self.delete_task(task_id))

            task_item.add_widget(checkbox)
            task_item.add_widget(task_label)
            task_item.add_widget(delete_button)

            self.task_list.add_widget(task_item)

    def _update_rect(self, widget):
        widget.canvas.before.clear()
        with widget.canvas.before:
            if isinstance(widget.children[0], CheckBox):
                Color(0.8, 1, 0.8, 1) if widget.children[0].active else Color(1, 0.8, 0.8, 1)
            else:
                Color(0.5, 0.3, 0.3, 1)
            Rectangle(size=widget.size, pos=widget.pos)

    def toggle_task_status(self, task_id, completed):
        self.db.update_task_status(task_id, int(completed))
        self.refresh_task_list()

    def add_task(self, instance):
        task_description = self.task_input.text.strip()
        if task_description:
            self.db.add_task(task_description)
            self.task_input.text = ""
            self.refresh_task_list()

    def delete_task(self, task_id):
        self.db.delete_task(task_id)
        self.refresh_task_list()

    def on_stop(self):
        self.db.close()

if __name__ == "__main__":
    ToDoListApp().run()
