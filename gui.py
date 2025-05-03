import io
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import webbrowser
import threading  # Добавлен импорт

from converter import pdf_to_excel_bytes


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF → Excel Converter")
        self.geometry("500x300")
        self.resizable(False, False)
        self.configure(bg="white")  # Явный цвет фона

        self.pdf_path = None

        # Кнопка выбора PDF
        self.choose_btn = tk.Button(
            self,
            text="Выбрать PDF…",
            width=20,
            command=self.choose_file
        )
        self.choose_btn.pack(pady=(20, 5))

        # Метка для отображения пути
        self.file_label = tk.Label(
            self,
            text="Файл не выбран",
            fg="gray",
            bg="white"  # Фон метки
        )
        self.file_label.pack(pady=5)

        # Кнопка конвертации
        self.convert_btn = tk.Button(
            self,
            text="Конвертировать в Excel",
            width=20,
            state="disabled",
            command=self.convert_file
        )
        self.convert_btn.pack(pady=(5, 15))

        # Progress bar
        self.progress = ttk.Progressbar(
            self,
            mode='indeterminate',
            length=300
        )

        # Статус-строка
        self.status = tk.Label(self, text="", fg="green", bg="white")
        self.status.pack(pady=5)

        # Футер
        self.footer = tk.Label(
            self,
            text="Created by Maxmudov Sanjar",
            fg="#6c757d",
            bg="white",  # Фон футера
            cursor="hand2"
        )
        self.footer.pack(side="bottom", pady=10)
        self.footer.bind(
            '<Button-1>',
            lambda e: webbrowser.open_new("https://www.instagram.com/__maxmudov")
        )

    def choose_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("PDF файлы", "*.pdf")],
            title="Выберите PDF для конвертации"
        )
        if not path:
            return
        self.pdf_path = path
        display = path.split("/")[-1]
        self.file_label.config(text=f"Выбран: {display}", fg="black")
        self.convert_btn.config(state="normal")
        self.status.config(text="")

    def convert_file(self):
        if not self.pdf_path:
            return

        # Получаем путь сохранения заранее
        default_name = self.pdf_path.rsplit(".", 1)[0] + ".xlsx"
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[("Excel файлы", "*.xlsx")],
            title="Сохранить как"
        )
        if not save_path:
            self.status.config(text="Сохранение отменено", fg="orange")
            return

        # Запускаем прогресс-бар
        self.progress.pack(pady=5)
        self.progress.start(10)

        # Функция для потока
        def conversion_task():
            try:
                with open(self.pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                xlsx_bytes = pdf_to_excel_bytes(pdf_bytes)

                with open(save_path, "wb") as out:
                    out.write(xlsx_bytes)

                self.after(0, lambda: self.status.config(
                    text=f"Сохранено: {save_path}",
                    fg="green"
                ))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Ошибка", str(e)))
                self.after(0, lambda: self.status.config(
                    text="Ошибка при конвертации",
                    fg="red"
                ))
            finally:
                self.after(0, self.progress.stop)
                self.after(0, self.progress.pack_forget)

        # Запуск потока
        threading.Thread(target=conversion_task, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()