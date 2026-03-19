# test_tasktracker.py
import pytest
import sys
import json
import os
from unittest.mock import MagicMock, patch

# Мокаем tkinter ДО импорта приложения
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()

# Теперь импортируем приложение
import tasktracker as app


@pytest.fixture(autouse=True)
def reset_state(tmp_path, monkeypatch):
    """Сбрасывает состояние перед каждым тестом"""
    # Временные файлы
    users_file = tmp_path / "users.json"
    tasks_file = tmp_path / "tasks.json"

    # Подменяем пути
    monkeypatch.setattr(app, "USERS_FILE", str(users_file))
    monkeypatch.setattr(app, "TASKS_FILE", str(tasks_file))

    # Очищаем глобальные переменные
    app.users = {}
    app.tasks = []
    app.current_user = None

    # Мокаем виджеты
    mock_login = MagicMock()
    mock_password = MagicMock()
    mock_task = MagicMock()
    mock_listbox = MagicMock()
    mock_listbox.curselection.return_value = (0,)

    monkeypatch.setattr(app, "entry_login", mock_login)
    monkeypatch.setattr(app, "entry_password", mock_password)
    monkeypatch.setattr(app, "entry_task", mock_task)
    monkeypatch.setattr(app, "listbox", mock_listbox)

    yield


@pytest.fixture
def mock_mb():
    """Мокает messagebox"""
    with patch('tasktracker.messagebox') as m:
        yield m


# === ТЕСТЫ ===

def test_register_success(mock_mb):
    """Регистрация пользователя"""
    app.entry_login.get.return_value = "user1"
    app.entry_password.get.return_value = "123456"

    app.register()

    assert "user1" in app.users
    assert app.users["user1"] == "123456"
    mock_mb.showinfo.assert_called()


def test_register_short_password(mock_mb):
    """Короткий пароль"""
    app.entry_login.get.return_value = "user1"
    app.entry_password.get.return_value = "12"

    app.register()

    assert "user1" not in app.users
    mock_mb.showwarning.assert_called()


def test_login_success(mock_mb):
    """Успешный вход"""
    app.users["admin"] = "pass123"
    app.entry_login.get.return_value = "admin"
    app.entry_password.get.return_value = "pass123"

    app.login()

    assert app.current_user == "admin"
    mock_mb.showinfo.assert_called()


def test_login_fail(mock_mb):
    """Неверный пароль"""
    app.users["admin"] = "pass123"
    app.entry_login.get.return_value = "admin"
    app.entry_password.get.return_value = "wrong"

    app.login()

    assert app.current_user is None
    mock_mb.showerror.assert_called()


def test_add_task_success():
    """Добавление задачи"""
    app.current_user = "user1"
    app.entry_task.get.return_value = "Купить хлеб"

    app.add_task()

    assert len(app.tasks) == 1
    assert app.tasks[0]["title"] == "Купить хлеб"
    app.entry_task.delete.assert_called()


def test_add_task_no_user(mock_mb):
    """Добавление без входа"""
    app.current_user = None
    app.entry_task.get.return_value = "Задача"

    app.add_task()

    assert len(app.tasks) == 0
    mock_mb.showerror.assert_called()


def test_delete_task():
    """Удаление задачи"""
    app.tasks.append({"user": "u1", "title": "Task", "done": False})

    app.delete_task()

    assert len(app.tasks) == 0


def test_mark_done():
    """Отметить выполненной"""
    app.tasks.append({"user": "u1", "title": "Task", "done": False})

    app.mark_done()

    assert app.tasks[0]["done"] == True


def test_refresh_tasks():
    """Обновление списка"""
    app.tasks = [
        {"user": "u1", "title": "Task 1", "done": False},
        {"user": "u1", "title": "Task 2", "done": True}
    ]

    app.refresh_tasks()

    app.listbox.delete.assert_called()
    assert app.listbox.insert.call_count == 2


def test_save_load_users(tmp_path, monkeypatch):
    """Сохранение и загрузка пользователей"""
    users_file = tmp_path / "users.json"
    monkeypatch.setattr(app, "USERS_FILE", str(users_file))

    app.users = {"test": "pass"}
    app.save_users()

    app.users = {}
    app.load_data()

    assert "test" in app.users


def test_save_load_tasks(tmp_path, monkeypatch):
    """Сохранение и загрузка задач"""
    tasks_file = tmp_path / "tasks.json"
    monkeypatch.setattr(app, "TASKS_FILE", str(tasks_file))

    app.tasks = [{"user": "u1", "title": "Task", "done": False}]
    app.save_tasks()

    app.tasks = []
    app.load_data()

    assert len(app.tasks) == 1