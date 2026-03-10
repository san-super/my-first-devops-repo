"""Snake game 'Изгиб Питона' on Pygame with OOP."""

import random
from typing import List, Tuple, Optional

import pygame

# Константы игры
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
CELL_SIZE = 20

GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


class GameObject:
    """Базовый класс для игровых объектов на поле."""

    def __init__(self, position: Tuple[int, int], body_color: Tuple[int, int, int]) -> None:
        """
        Инициализировать объект.

        :param position: Начальная позиция в пикселях (x, y).
        :param body_color: Цвет объекта в формате RGB.
        """
        self.position: Tuple[int, int] = position
        self.body_color: Tuple[int, int, int] = body_color

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовать объект на заданной поверхности.

        Метод должен быть переопределён в дочерних классах.
        """
        raise NotImplementedError("Subclasses must implement draw() method.")


class Apple(GameObject):
    """Класс, описывающий яблоко на игровом поле."""

    def __init__(self) -> None:
        """Создать яблоко с красным цветом и случайной позицией."""
        super().__init__((0, 0), RED)
        self.randomize_position()

    def randomize_position(self) -> None:
        """Установить случайное положение яблока в пределах игрового поля."""
        cell_x = random.randint(0, GRID_WIDTH - 1)
        cell_y = random.randint(0, GRID_HEIGHT - 1)
        self.position = (cell_x * CELL_SIZE, cell_y * CELL_SIZE)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать яблоко на переданной поверхности."""
        rect = pygame.Rect(self.position[0], self.position[1], CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, self.body_color, rect)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    def __init__(self) -> None:
        """Создать змейку с длиной 1, в центре поля, движущуюся вправо."""
        center_x = (GRID_WIDTH // 2) * CELL_SIZE
        center_y = (GRID_HEIGHT // 2) * CELL_SIZE
        super().__init__((center_x, center_y), GREEN)

        self.length: int = 1
        self.positions: List[Tuple[int, int]] = [self.position]
        # начальное направление — вправо
        self.direction: Tuple[int, int] = (1, 0)
        self.next_direction: Optional[Tuple[int, int]] = None

    def get_head_position(self) -> Tuple[int, int]:
        """Вернуть текущую позицию головы змейки."""
        return self.positions[0]

    def update_direction(self) -> None:
        """Обновить направление движения, если задано новое и оно не противоположно текущему."""
        if self.next_direction is None:
            return

        cur_dx, cur_dy = self.direction
        new_dx, new_dy = self.next_direction

        # запрет разворота назад
        if (cur_dx == -new_dx and cur_dx != 0) or (cur_dy == -new_dy and cur_dy != 0):
            self.next_direction = None
            return

        self.direction = self.next_direction
        self.next_direction = None

    def move(self) -> None:
        """
        Передвинуть змейку на одну ячейку.

        Добавляет новую голову в начало списка positions.
        Если длина не увеличилась, удаляет последний элемент.
        Реализует "проход через стену": выход за границу с одной стороны
        переносит голову на противоположную.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_x = head_x + dx * CELL_SIZE
        new_y = head_y + dy * CELL_SIZE

        # проход через стены
        if new_x < 0:
            new_x = WINDOW_WIDTH - CELL_SIZE
        elif new_x >= WINDOW_WIDTH:
            new_x = 0

        if new_y < 0:
            new_y = WINDOW_HEIGHT - CELL_SIZE
        elif new_y >= WINDOW_HEIGHT:
            new_y = 0

        new_head = (new_x, new_y)

        self.positions.insert(0, new_head)
        self.position = new_head  # для соответствия базовому классу

        # если длина не увеличилась, удалить хвост
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовать змейку на игровом поле.

        Для каждого сегмента рисуется квадрат нужного цвета.
        След затирается в основном цикле перерисовкой фона.
        """
        for pos in self.positions:
            rect = pygame.Rect(pos[0], pos[1], CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, self.body_color, rect)

    def reset(self) -> None:
        """Сбросить змейку в начальное состояние после столкновения с собой."""
        center_x = (GRID_WIDTH // 2) * CELL_SIZE
        center_y = (GRID_HEIGHT // 2) * CELL_SIZE
        self.position = (center_x, center_y)
        self.length = 1
        self.positions = [self.position]
        self.direction = (1, 0)
        self.next_direction = None


def handle_keys(snake: Snake) -> None:
    """
    Обработать нажатия клавиш и обновить желаемое направление движения змейки.

    Используются стрелки клавиатуры.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.next_direction = (0, -1)
            elif event.key == pygame.K_DOWN:
                snake.next_direction = (0, 1)
            elif event.key == pygame.K_LEFT:
                snake.next_direction = (-1, 0)
            elif event.key == pygame.K_RIGHT:
                snake.next_direction = (1, 0)


def main() -> None:
    """Основная функция игры: инициализация, главный цикл и отрисовка."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Изгиб Питона")

    clock = pygame.time.Clock()

    snake = Snake()
    apple = Apple()

    running = True
    while running:
        # ограничение FPS
        clock.tick(20)

        # обработка ввода
        handle_keys(snake)
        snake.update_direction()

        # движение змейки
        snake.move()

        # проверка, съела ли змейка яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()

        # проверка столкновения с собой
        head = snake.get_head_position()
        if head in snake.positions[1:]:
            snake.reset()
            apple.randomize_position()

        # отрисовка
        screen.fill(BLACK)
        snake.draw(screen)
        apple.draw(screen)

        pygame.display.update()


if __name__ == "__main__":
    main()
