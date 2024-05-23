import unittest
from unittest.mock import MagicMock
from app.RasterGraphicsEditor import DrawModel, DrawPresenter


# Набір тестів для класу DrawModel


class TestDrawModel(unittest.TestCase):
    # Метод setUp() викликається перед кожним тестом і створює екземпляр класу DrawModel
    def setUp(self):
        self.model = DrawModel()

    # Перевірка методу для встановлення кольору
    def test_set_color(self):
        self.model.set_color("red")
        self.assertEqual(self.model.line_color, "red")

    # Перевірка методу для встановлення коліру гумки
    def test_set_erase_color(self):
        self.model.set_erase_color()
        self.assertEqual(self.model.line_color, self.model.erase_color)

    # Перевірка для очищення екрану
    def test_clear_screen(self):
        self.model.prev_x = 100
        self.model.prev_y = 100
        self.model.clear_screen()
        self.assertIsNone(self.model.prev_x)
        self.assertIsNone(self.model.prev_y)

    # Перевірка методу підписки на сповіщення
    def test_subscribe(self):
        observer = MagicMock()
        self.model.subscribe(observer)
        self.assertIn(observer, self.model.observers)

    # Перевірка методу відписки на сповіщення
    def test_unsubscribe(self):
        observer = MagicMock()
        self.model.subscribe(observer)
        self.model.unsubscribe(observer)
        self.assertNotIn(observer, self.model.observers)

    # Перевірка методу для сповіщення обсерверів про зміни
    def test_notify(self):
        observer = MagicMock()
        self.model.subscribe(observer)
        self.model.notify()
        observer.update.assert_called_once()


# Набір тестів для класу DrawView


class TestDrawView(unittest.TestCase):
    def setUp(self):
        # Створення макетів об'єктів для тестування
        self.root = MagicMock()
        self.model = MagicMock()
        self.presenter = DrawPresenter(self.root, self.model)
        self.view = self.presenter.view

    # Перевірка методу для створення меню
    def test_create_menu(self):
        if self.view.root.winfo_exists():
            menu = self.view.root.nametowidget(self.view.root['menu'])
            self.assertIsNotNone(menu)

    # Перевірка методу для створення кнопок вибору інстументів
    def test_create_tool_buttons(self):
        self.view.create_tool_buttons = MagicMock()
        self.view.setup_ui()
        self.view.create_tool_buttons.assert_called_once()

    # Перевірка методу для створення повзунка розміру
    def test_create_width_selector(self):
        self.assertIsNotNone(self.view.width_frame)

    # Перевірка методу для створення палітри кольорів
    def test_create_color_palette(self):
        self.assertIsNotNone(self.view.color_frame)

    # Перевірка методу для створення полотна
    def test_create_draw_area(self):
        self.assertIsNotNone(self.view.canvas)

    # Перевірка методу для координат початку малювання
    def test_start_drawing(self):
        event = type('', (), {})()
        event.x = 10
        event.y = 20
        self.view.start_drawing(event)
        self.assertIsNotNone(self.view.start_x)
        self.assertIsNotNone(self.view.start_y)


# Набір тестів для класу DrawPresenter


class TestDrawPresenter(unittest.TestCase):
    def setUp(self):
        # Створення макетів об'єктів для тестування
        self.root = MagicMock()
        self.model = MagicMock()
        self.view = MagicMock()
        self.presenter = DrawPresenter(self.root, self.model)
        self.presenter.view = self.view

    # Перевірка методу для встановлення кольору малювання
    def test_set_color(self):
        self.presenter.set_color("blue")
        self.model.set_color.assert_called_once_with("blue")

    # Перевірка методу для очищення полотна
    def test_clear_screen(self):
        self.presenter.clear_screen()
        self.view.clear_screen.assert_called_once()

    # Перевірка методу опису виходу з програми
    def test_quit(self):
        self.presenter.quit()
        self.root.destroy.assert_called_once()

    # Перевірка методу для оновлення
    def test_update(self):
        self.presenter.update()
        self.view.canvas.update.assert_called_once()


if __name__ == "__main__":
    unittest.main()
