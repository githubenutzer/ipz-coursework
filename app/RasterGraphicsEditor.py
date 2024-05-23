import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
from tkinter.ttk import Scale, Combobox
from PIL import Image, ImageTk, ImageGrab
import random

# Цей код реалізує растровий графічний редактор за допомогою бібліотеки Tkinter на мові програмування Python.


# Клас DrawModel відповідає за модель додатка.


class DrawModel:
    def __init__(self):
        # Ініціалізація початковий колір лінії та колір для видалення
        self.line_color = "black"
        self.erase_color = "white"
        # Координати попередньої точки
        self.prev_x = None
        self.prev_y = None
        # Список обсерверів, яким буде надсилатись сповіщення про зміни
        self.observers = set()

    # Метод для встановлення кольору
    def set_color(self, col):
        self.line_color = col
        self.notify()

    # Метод для встановлення коліру гумки
    def set_erase_color(self):
        self.line_color = self.erase_color
        self.notify()

    # Метод для очищення екрану
    def clear_screen(self):
        self.prev_x = None
        self.prev_y = None
        self.notify()

    # Метод для підписки на сповіщення
    def subscribe(self, observer):
        self.observers.add(observer)

    # Метод для відписки від сповіщень
    def unsubscribe(self, observer):
        self.observers.remove(observer)

    # Метод для сповіщення обсерверів про зміни
    def notify(self):
        for observer in self.observers:
            observer.update()


# Клас DrawView відповідає за представлення додатка та його інтерфейс.


class DrawView:
    def __init__(self, root, presenter):
        # Ініціалізація головного вікна, презентера та поточного інструменту
        self.root = root
        self.presenter = presenter
        self.current_tool = "pencil"
        # Налаштування основних властивостей вікна
        self.root.title("Растровий графічний редактор")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)
        self.root.config(bg="#38454F")
        # Налаштування інтерфейсу
        self.setup_ui()

    # Метод для налаштування інтерфейсу
    def setup_ui(self):
        self.create_color_palette()
        self.create_menu()
        self.create_tool_buttons()
        self.create_width_selector()
        self.create_draw_area()
        self.set_cursor()

    # Метод для створення меню
    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Відкрити", command=self.presenter.open_image)
        file_menu.add_command(label="Зберегти", command=self.presenter.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Очистити", command=self.presenter.clear_screen)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self.presenter.exit_application)
        menu_bar.add_cascade(label="Файл", menu=file_menu)

    # Метод для створення кнопок вибору інстументів
    def create_tool_buttons(self):
        buttons = [
            ("Олівець", lambda: self.set_tool("pencil"), 10, 10),
            ("Гумка", lambda: self.set_tool("eraser"), 10, 55),
            ("Заливка", lambda: self.set_tool("fill"), 170, 10),
            ("Розпилювач", lambda: self.set_tool("sprayer"), 170, 55),
            ("Пряма", lambda: self.set_tool("line"), 330, 10),
            ("Пунктирна пряма", lambda: self.set_tool("dashed_line"), 330, 55),
            ("Прямокутник", lambda: self.set_tool("rectangle"), 490, 10),
            ("Трикутник", lambda: self.set_tool("triangle"), 490, 55),
            ("Овал", lambda: self.set_tool("oval"), 650, 10),
            ("Текст", lambda: self.set_tool("text"), 650, 55),
        ]
        for text, command, x, y in buttons:
            btn = tk.Button(
                self.root,
                text=text,
                font=("Corbel", 12),
                bd=4,
                bg="#38454F",
                fg="white",
                width=15,
                command=command,
                relief=tk.RIDGE,
            )
            btn.place(x=x, y=y)

    # Метод для встановлення курсору, в залежності від інструмента
    def set_cursor(self):
        if self.current_tool == "pencil":
            self.canvas.config(cursor="pencil")
        elif self.current_tool == "eraser":
            self.canvas.config(cursor="target")
        elif self.current_tool == "sprayer":
            self.canvas.config(cursor="spraycan")
        elif self.current_tool == "fill":
            self.canvas.config(cursor="spraycan")
        elif self.current_tool == "text":
            self.canvas.config(cursor="top_tee")
        else:
            self.canvas.config(cursor="tcross")

    # Метод для встановлення інструмента
    def set_tool(self, tool):
        self.current_tool = tool
        self.set_cursor()
        if self.current_tool == "fill":
            self.canvas.bind("<Button-1>", self.fill_canvas)
        elif self.current_tool == "text":
            self.canvas.bind("<Button-1>", self.place_text)
        else:
            self.canvas.bind("<Button-1>", self.start_drawing)

    # Метод для створення повзунка розміру
    def create_width_selector(self):
        self.width_frame = tk.LabelFrame(
            self.root,
            text="Розмір",
            font=("Corbel", 12),
            bd=5,
            bg="#38454F",
            fg="white",
            relief=tk.RIDGE,
        )
        self.width_frame.place(x=817, y=5, height=87, width=70)
        self.line_width = Scale(
            self.width_frame, orient=tk.VERTICAL, from_=36, to=1, length=58
        )
        self.line_width.set(1)
        self.line_width.grid(row=0, column=1, padx=15)

    # Метод для створення палітри кольорів
    def create_color_palette(self):
        self.color_frame = tk.LabelFrame(
            self.root,
            text="Кольори",
            font=("Corbel", 12),
            bd=5,
            bg="#38454F",
            labelanchor="n",
            fg="white",
            relief=tk.RIDGE,
        )
        self.color_frame.place(x=905, y=5, width=363, height=87)
        colors = [
            "black", "white", "grey", "lightgrey", "brown", "darkgoldenrod",
            "red", "pink", "orange", "yellow", "lightyellow", "beige", "green",
            "lightgreen", "lightblue", "skyblue", "darkblue", "blue", "purple",
        ]
        for i, color in enumerate(colors):
            row = i % 2
            column = i // 2

            tk.Button(
                self.color_frame,
                bd=2,
                bg=color,
                width=3,
                command=lambda col=color: self.presenter.set_color(col),
                relief=tk.RIDGE,
            ).grid(row=row, column=column, padx=2, pady=2)

        tk.Button(
            self.color_frame,
            text="Інш.",
            font=("Corbel", 10),
            bd=2,
            bg="#38454F",
            fg="white",
            width=3,
            command=self.pick_custom_color,
            relief=tk.RIDGE,
        ).grid(row=1, column=9, padx=2, pady=2)

    # Метод для вибору власного кольору
    def pick_custom_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.presenter.set_color(color)

    # Метод для створення полотна
    def create_draw_area(self):
        self.canvas = tk.Canvas(
            self.root, bg="white", bd=5, relief=tk.GROOVE, height=600, width=1250
        )
        self.canvas.place(x=7, y=100, anchor="nw")
        self.canvas.bind("<Button-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_drawing)

    # Метод для координат початку малювання
    def start_drawing(self, event):
        self.start_x = event.x
        self.start_y = event.y

    # Метод для малювання та опису частини інструментів
    def draw(self, event):
        if self.current_tool == "pencil":
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, capstyle=tk.ROUND, smooth=tk.TRUE,
                                    fill=self.presenter.model.line_color,
                                    width=self.line_width.get())
            self.start_x = event.x
            self.start_y = event.y
        elif self.current_tool == "eraser":
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, capstyle=tk.ROUND, smooth=tk.TRUE,
                                    fill=self.presenter.model.erase_color,
                                    width=self.line_width.get())
            self.start_x = event.x
            self.start_y = event.y
        elif self.current_tool == "fill":
            self.fill_canvas(event)
        elif self.current_tool == "sprayer":
            for _ in range(30):
                x = event.x + random.randint(-15, 15)
                y = event.y + random.randint(-15, 15)
                self.canvas.create_oval(x, y, x + 1, y + 1, fill=self.presenter.model.line_color,
                                        outline=self.presenter.model.line_color)
        elif self.current_tool == "line":
            self.canvas.delete("temp")
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                    fill=self.presenter.model.line_color,
                                    width=self.line_width.get(), tags="temp")
        elif self.current_tool == "dashed_line":
            self.canvas.delete("temp")
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                    fill=self.presenter.model.line_color,
                                    width=self.line_width.get(), dash=(5, 5), tags="temp")
        elif self.current_tool == "rectangle":
            self.canvas.delete("temp")
            self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                         outline=self.presenter.model.line_color,
                                         width=self.line_width.get(), tags="temp")
        elif self.current_tool == "triangle":
            self.canvas.delete("temp")
            x1 = (self.start_x + event.x) / 2
            y1 = self.start_y
            x2 = event.x
            y2 = event.y
            x3 = self.start_x
            y3 = event.y
            self.canvas.create_polygon(x1, y1, x2, y2, x3, y3, outline=self.presenter.model.line_color,
                                       width=self.line_width.get(), fill="", tags="temp")
        elif self.current_tool == "oval":
            self.canvas.delete("temp")
            self.canvas.create_oval(self.start_x, self.start_y, event.x, event.y,
                                    outline=self.presenter.model.line_color,
                                    width=self.line_width.get(), tags="temp")

    # Метод для опису заливки
    def fill_canvas(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        if not item:
            self.canvas.config(bg=self.presenter.model.line_color)
        else:
            item = item[0]
            self.canvas.itemconfig(item, fill=self.presenter.model.line_color)

    # Метод для опису тексту
    def place_text(self, event):
        text_dialog = tk.Toplevel(self.root)
        text_dialog.title("Введення тексту")

        text_label = tk.Label(text_dialog, text="Текст:")
        text_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        text_entry = tk.Entry(text_dialog, width=23)
        text_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        font_label = tk.Label(text_dialog, text="Шрифт:")
        font_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        font_combobox = Combobox(text_dialog, state="readonly", width=20)
        font_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        font_combobox["values"] = ("Arial", "Calibri", "Courier New", "Times New Roman")
        font_combobox.current(1)

        size_label = tk.Label(text_dialog, text="Розмір:")
        size_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        size_entry = tk.Entry(text_dialog, width=2)
        size_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        size_entry.insert(0, "11")

        # Метод для застосування тексту
        def apply_text():
            entered_text = text_entry.get()
            font = (font_combobox.get(), int(size_entry.get()))
            self.canvas.create_text(event.x, event.y, text=entered_text,
                                    fill=self.presenter.model.line_color, font=font)
            text_dialog.destroy()

        apply_button = tk.Button(text_dialog, text="Застосувати", command=apply_text)
        apply_button.grid(row=3, columnspan=2, pady=10)

    # Метод для встановлення кінцевих координат малювання фігур та ліній
    def end_drawing(self, event):
        if self.current_tool == "line":
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                    fill=self.presenter.model.line_color,
                                    width=self.line_width.get())
        elif self.current_tool == "dashed_line":
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                    fill=self.presenter.model.line_color,
                                    width=self.line_width.get(), dash=(5, 5))
        elif self.current_tool == "rectangle":
            self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                         outline=self.presenter.model.line_color,
                                         width=self.line_width.get())
        elif self.current_tool == "triangle":
            x1 = (self.start_x + event.x) / 2
            y1 = self.start_y
            x2 = event.x
            y2 = event.y
            x3 = self.start_x
            y3 = event.y
            self.canvas.create_polygon(x1, y1, x2, y2, x3, y3, outline=self.presenter.model.line_color,
                                       width=self.line_width.get(), fill="")
        elif self.current_tool == "oval":
            self.canvas.create_oval(self.start_x, self.start_y, event.x, event.y,
                                    outline=self.presenter.model.line_color,
                                    width=self.line_width.get())

    # Метод для відкривання зображення
    def open_image(self, image):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        image_width = image.width()
        image_height = image.height()

        x = (canvas_width - image_width) // 2
        y = (canvas_height - image_height) // 2

        self.clear_screen()

        self.canvas.create_image(x, y, anchor="nw", image=image)
        self.canvas.image = image

    # Метод для збереження зображення
    def save_image(self, file_path):
        self.root.update_idletasks()

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        x0 = self.canvas.winfo_rootx() + 7
        y0 = self.canvas.winfo_rooty() + 7

        x1 = x0 + canvas_width - 14
        y1 = y0 + canvas_height - 14

        image = ImageGrab.grab(bbox=(x0, y0, x1, y1))

        file_extension = file_path.split(".")[-1].lower()
        if file_extension in ["png", "jpg", "jpeg", "tiff", "gif"]:
            image.save(file_path)
        else:
            messagebox.showerror("Помилка", "Непідтримуваний формат файлу.")

    # Метод для очищення області малювання
    def clear_screen(self):
        self.canvas.delete("all")


# Клас DrawPresenter відповідає за взаємодію між моделлю та представленням.


class DrawPresenter:
    def __init__(self, root, model):
        # Ініціалізація презентера
        self.root = root
        self.model = model
        self.view = DrawView(root, self)
        self.model.subscribe(self)

    # Метод для встановлення кольору малювання
    def set_color(self, col):
        self.model.set_color(col)

    # Метод для відкриванняя зображення
    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("TIFF files", "*.tiff"),
                ("GIF files", "*.gif"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            try:
                image = Image.open(file_path)
                photo = ImageTk.PhotoImage(image)
                self.view.open_image(photo)
            except Exception as e:
                messagebox.showerror("Сталась помилка", f"Не вдалось відкрити зображення: {e}")

    # Метод для Збереження зображення
    def save_image(self):
        file_path = filedialog.asksaveasfilename(
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("TIFF files", "*.tiff"),
                ("GIF files", "*.gif")]
        )
        if file_path:
            try:
                self.root.update_idletasks()
                self.view.save_image(file_path)
                messagebox.showinfo("Збереження зображення", "Зображення успішно збережено.")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалось зберегти зображення: {e}")

    # Метод для очищення полотна
    def clear_screen(self):
        self.view.clear_screen()

    # Метод для опису виходу з програми
    def quit(self):
        self.root.destroy()

    # Метод для виходу з програми
    def exit_application(self):
        user_choice = messagebox.askyesnocancel("Зберегти зображення", "Бажаєте зберегти зображення перед виходом?")
        if user_choice is None:
            return
        elif user_choice:
            self.save_image()
        self.quit()

    # Метод для оновлення відображення
    def update(self):
        self.view.canvas.update()


if __name__ == "__main__":
    root = tk.Tk()
    model = DrawModel()
    presenter = DrawPresenter(root, model)
    root.mainloop()
