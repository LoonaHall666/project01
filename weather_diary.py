import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import re
from datetime import datetime

# --- Конфигурация ---
FILENAME = "weather_data.json"


class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник погоды")
        self.root.geometry("700x550")

        # Данные приложения
        self.weather_records = self.load_data()
        self.filtered_records = self.weather_records.copy()

        # Создание интерфейса
        self.create_widgets()
        self.update_treeview()

    # --- Логика работы с данными (JSON) ---
    def load_data(self):
        """Загружает записи из файла JSON."""
        try:
            with open(FILENAME, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_data(self):
        """Сохраняет записи в файл JSON."""
        with open(FILENAME, 'w', encoding='utf-8') as f:
            json.dump(self.weather_records, f, ensure_ascii=False, indent=2)

    # --- Валидация ввода ---
    def is_valid_date(self, date_str):
        """Проверяет формат даты ГГГГ-ММ-ДД."""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def is_valid_temperature(self, temp_str):
        """Проверяет, что температура — это число."""
        try:
            float(temp_str)
            return True
        except ValueError:
            return False

    # --- Логика добавления и фильтрации ---
    def add_record(self):
        """Обрабатывает добавление новой записи с проверкой данных."""
        date = self.entry_date.get().strip()
        temp = self.entry_temp.get().strip()
        desc = self.entry_desc.get("1.0", tk.END).strip()
        precip = self.precip_var.get()

        # Проверка корректности ввода
        if not date or not self.is_valid_date(date):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД (например, 2026-05-04)")
            return

        if not temp or not self.is_valid_temperature(temp):
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        if not desc:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым")
            return

        # Создание словаря записи
        record = {
            "date": date,
            "temperature": float(temp),
            "description": desc,
            "precipitation": precip
        }

        # Добавление в список и сохранение
        self.weather_records.append(record)
        self.save_data()

        # Очистка полей и обновление таблицы
        self.entry_date.delete(0, tk.END)
        self.entry_temp.delete(0, tk.END)
        self.entry_desc.delete("1.0", tk.END)

        self.update_treeview()

    def filter_records(self):
        """Фильтрует записи по дате и/или температуре."""
        filter_date = self.filter_date.get().strip()
        filter_temp = self.filter_temp.get().strip()

        filtered = self.weather_records.copy()

        # Фильтр по дате (точное совпадение)
        if filter_date:
            if not self.is_valid_date(filter_date):
                messagebox.showerror("Ошибка", "Дата для фильтра должна быть в формате ГГГГ-ММ-ДД")
                return
            filtered = [r for r in filtered if r['date'] == filter_date]

        # Фильтр по температуре (больше указанного значения)
        if filter_temp and self.is_valid_temperature(filter_temp):
            temp_value = float(filter_temp)
            filtered = [r for r in filtered if r['temperature'] > temp_value]

        self.filtered_records = filtered
        self.update_treeview()

    def clear_filters(self):
        """Сбрасывает фильтры и показывает все записи."""
        self.filter_date.delete(0, tk.END)
        self.filter_temp.delete(0, tk.END)
        self.filtered_records = self.weather_records.copy()
        self.update_treeview()

    def update_treeview(self):
        """Обновляет данные в таблице (Treeview)."""
        for i in self.tree.get_children():
            self.tree.delete(i)

        for record in self.filtered_records:
            self.tree.insert("", tk.END, values=(
                record['date'],
                record['temperature'],
                record['description'],
                record['precipitation']
            ))

    # --- Создание GUI ---
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Блок 1: Ввод новых данных
        input_frame = ttk.LabelFrame(main_frame, text="Добавить новую запись", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        # Сетка для аккуратного размещения полей ввода
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.entry_date = ttk.Entry(input_frame, width=15)
        self.entry_date.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(input_frame, text="Температура:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.entry_temp = ttk.Entry(input_frame, width=10)
        self.entry_temp.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

        ttk.Label(input_frame, text="Осадки:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=2)
        self.precip_var = tk.StringVar(value="Нет")
        ttk.OptionMenu(input_frame, self.precip_var, "Да", "Нет").grid(row=0, column=5, sticky=tk.W, padx=5, pady=2)

        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.entry_desc = tk.Text(input_frame, height=3, width=60)
        self.entry_desc.grid(row=1, column=1, columnspan=5, sticky=tk.W, padx=5, pady=2)

        ttk.Button(input_frame, text="Добавить запись", command=self.add_record).grid(row=2, column=0, columnspan=6,
                                                                                      pady=10)

        # Блок 2: Фильтрация
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация записей", padding="10")
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filter_frame, text="Дата:").grid(row=0, column=0, sticky=tk.W)
        self.filter_date = ttk.Entry(filter_frame)
        self.filter_date.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(filter_frame, text="Температура >").grid(row=0, column=2, sticky=tk.W)
        self.filter_temp = ttk.Entry(filter_frame)
        self.filter_temp.grid(row=0, column=3, sticky=tk.W, padx=5)

        ttk.Button(filter_frame, text="Применить фильтр", command=self.filter_records).grid(row=0, column=4, padx=10)
        ttk.Button(filter_frame, text="Сбросить фильтры", command=self.clear_filters).grid(row=0, column=5)

        # Блок 3: Таблица с данными (Treeview)
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('date', 'temp', 'desc', 'precip')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        self.tree.heading('date', text='Дата')
        self.tree.heading('temp', text='Температура')
        self.tree.heading('desc', text='Описание')
        self.tree.heading('precip', text='Осадки')

        # Настройка ширины колонок
        self.tree.column('date', width=120)
        self.tree.column('temp', width=100)
        self.tree.column('desc', width=300)
        self.tree.column('precip', width=80)

        # Полоса прокрутки
        yscroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=yscroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()