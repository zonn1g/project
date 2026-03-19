import tkinter as tk
from tkinter import messagebox
import json
import os

USERS_FILE = "data/users.json"
TASKS_FILE = "data/tasks.json"

current_user = None
users = {}
tasks = []

def load_data():
    global users, tasks
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    else:
        users = {}

    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)
    else:
        tasks = []

def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def save_tasks():
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def register():
    login = entry_login.get()
    password = entry_password.get()

    if len(password) < 4:
        messagebox.showwarning("Ошибка", "Слишком короткий пароль")
        return

    users[login] = password
    save_users()
    messagebox.showinfo("Успех", "Пользователь зарегистрирован")

def login():
    global current_user
    login = entry_login.get()
    password = entry_password.get()

    if login in users and users[login] == password:
        current_user = login
        messagebox.showinfo("Успех", "Вход выполнен")
        refresh_tasks()
    else:
        messagebox.showerror("Ошибка", "Неверный логин или пароль")

def add_task():
    if not current_user:
        messagebox.showerror("Ошибка", "Сначала войдите")
        return

    title = entry_task.get()
    task = {"user": current_user, "title": title, "done": False}
    tasks.append(task)
    save_tasks()
    refresh_tasks()
    entry_task.delete(0, tk.END)

def delete_task():
    index = listbox.curselection()[0]
    del tasks[index]
    save_tasks()
    refresh_tasks()

def mark_done():
    index = listbox.curselection()[0]
    tasks[index]["done"] = True
    save_tasks()
    refresh_tasks()

def refresh_tasks():
    listbox.delete(0, tk.END)
    for task in tasks:
        status = "[x]" if task["done"] else "[ ]"
        listbox.insert(tk.END, f"{status} {task['user']}: {task['title']}")

root = tk.Tk()
root.title("TaskTracker")
root.geometry("500x400")

load_data()

tk.Label(root, text="Логин").pack()
entry_login = tk.Entry(root)
entry_login.pack()

tk.Label(root, text="Пароль").pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()

tk.Button(root, text="Регистрация", command=register).pack(pady=5)
tk.Button(root, text="Вход", command=login).pack(pady=5)

tk.Label(root, text="Новая задача").pack()
entry_task = tk.Entry(root, width=40)
entry_task.pack()

tk.Button(root, text="Добавить задачу", command=add_task).pack(pady=5)
tk.Button(root, text="Отметить выполненной", command=mark_done).pack(pady=5)
tk.Button(root, text="Удалить задачу", command=delete_task).pack(pady=5)

listbox = tk.Listbox(root, width=60, height=10)
listbox.pack(pady=10)

refresh_tasks()

root.mainloop()
