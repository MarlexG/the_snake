"""Игра «Змейка» на pg.

Реализует классическую игру «Змейка»: змейка движется по игровому полю,
съедает яблоки и растёт в длину. При столкновении с собой игра сбрасывается.
Змейка может проходить сквозь стены и появляться с противоположной стороны.
"""

from random import randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Таблица поворотов: (клавиша, текущее направление) -> новое направление
TURNS = {
    (pg.K_UP, RIGHT): UP,
    (pg.K_UP, LEFT): UP,
    (pg.K_DOWN, RIGHT): DOWN,
    (pg.K_DOWN, LEFT): DOWN,
    (pg.K_LEFT, UP): LEFT,
    (pg.K_LEFT, DOWN): LEFT,
    (pg.K_RIGHT, UP): RIGHT,
    (pg.K_RIGHT, DOWN): RIGHT,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """Инициализирует позицию и цвет объекта."""
        position = position or (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = position
        self.body_color = body_color

    def _draw_cell(self, position=None, color=None):
        """Отрисовывает одну ячейку на игровом поле."""
        position = position or self.position
        color = color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Отрисовывает объект. Переопределяется в наследниках."""
        raise NotImplementedError(
            'Метод draw должен быть переопределён в дочернем классе'
        )


class Apple(GameObject):
    """Яблоко — цель змейки."""

    def __init__(self, occupied_cells=None):
        """Создаёт яблоко в случайной свободной позиции."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(occupied_cells)

    def randomize_position(self, occupied_cells=None):
        """Устанавливает случайную позицию, не занятую другими объектами."""
        if occupied_cells is None:
            occupied_cells = set()

        while True:
            new_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if new_position not in occupied_cells:
                self.position = new_position
                return

    def draw(self):
        """Отрисовывает яблоко как квадрат с рамкой."""
        self._draw_cell()


class Snake(GameObject):
    """Змейка, управляемая игроком."""

    def __init__(self):
        """Создаёт змейку из одного сегмента в центре поля."""
        super().__init__(body_color=SNAKE_COLOR)
        self.reset()

    def reset(self):
        """Возвращает змейку в начальное состояние."""
        start = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [start]
        self.length = 1
        directions = [UP, DOWN, LEFT, RIGHT]
        self.direction = directions[randint(0, 3)]
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def _opposite(self, direction):
        """Возвращает направление, противоположное заданному."""
        return (-direction[0], -direction[1])

    def update_direction(self, next_direction):
        """Применяет новое направление, если оно допустимо."""
        if next_direction and next_direction != self._opposite(self.direction):
            self.direction = next_direction

    def move(self):
        """Перемещает змейку на одну клетку в текущем направлении."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self):
        """Отрисовывает все сегменты змейки."""
        for position in self.positions:
            self._draw_cell(position)


def handle_keys(snake):
    """Возвращает направление, выбранное игроком, или None."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            return TURNS.get((event.key, snake.direction), None)
    return None


def main():
    """Запускает основной игровой цикл."""
    pg.init()
    snake = Snake()
    apple = Apple(occupied_cells=set(snake.positions))

    while True:
        clock.tick(SPEED)

        screen.fill(BOARD_BACKGROUND_COLOR)   # ← стираем всё перед отрисовкой

        next_direction = handle_keys(snake)
        snake.update_direction(next_direction)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(occupied_cells=set(snake.positions))

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()

        pg.display.update()


if __name__ == '__main__':
    main()
