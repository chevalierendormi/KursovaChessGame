import os
import sys
import pygame
from game_pack.params import *

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class Figure(pygame.sprite.Sprite):
    def __init__(self, filename, r, c, side, board):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(resource_path(filename)).convert_alpha()
        self.row = r
        self.col = c
        self.side = side
        self.board = board
        self.is_drop = False
        self.update_image()

    def set_pos(self, r, c):
        self.row = r
        self.col = c
        self.update_rect()

    def update_image(self):
        self.image = pygame.transform.scale(self.image, (self.board.cell_size, self.board.cell_size))
        self.rect = self.image.get_rect(topleft=(self.col * self.board.cell_size, self.row * self.board.cell_size))

    def update_rect(self):
        self.rect = self.image.get_rect(topleft=(self.col * self.board.cell_size, self.row * self.board.cell_size))

    @staticmethod
    def is_valid_pos(r, c):
        return 0 <= r <= 7 and 0 <= c <= 7

class King(Figure):
    def __init__(self, r, c, side, board):
        Figure.__init__(self, 'images/' + side + 'King.png', r, c, side, board)

    def get_actions(self):
        result = []
        offsets = [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, 1), (1, 1), (1, -1), (-1, -1)]
        for delta_row, delta_col in offsets:
            r1 = self.row + delta_row
            c1 = self.col + delta_col
            if not self.is_valid_pos(r1, c1):
                continue
            result.append((r1, c1))
        return result

class Queen(Figure):
    def __init__(self, r, c, side, board):
        Figure.__init__(self, 'images/' + side + 'Queen.png', r, c, side, board)

    def get_actions(self):
        result = []
        offsets = [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, 1), (1, 1), (1, -1), (-1, -1)]
        for delta_row, delta_col in offsets:
            mul = 0
            while True:
                mul += 1
                r1 = self.row + mul * delta_row
                c1 = self.col + mul * delta_col
                if not self.is_valid_pos(r1, c1):
                    break
                result.append((r1, c1))
                figure = self.board.get_figure(r1, c1)
                if figure is not None:
                    break
        return result

class Rook(Figure):
    def __init__(self, r, c, side, board):
        Figure.__init__(self, 'images/' + side + 'Rook.png', r, c, side, board)

    def get_actions(self):
        result = []
        offsets = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        for delta_row, delta_col in offsets:
            mul = 0
            while True:
                mul += 1
                r1 = self.row + mul * delta_row
                c1 = self.col + mul * delta_col
                if not self.is_valid_pos(r1, c1):
                    break
                result.append((r1, c1))
                figure = self.board.get_figure(r1, c1)
                if figure is not None:
                    break
        return result

class Bishop(Figure):
    def __init__(self, r, c, side, board):
        Figure.__init__(self, 'images/' + side + 'Bishop.png', r, c, side, board)

    def get_actions(self):
        result = []
        offsets = [(-1, 1), (1, 1), (1, -1), (-1, -1)]
        for delta_row, delta_col in offsets:
            mul = 0
            while True:
                mul += 1
                r1 = self.row + mul * delta_row
                c1 = self.col + mul * delta_col
                if not self.is_valid_pos(r1, c1):
                    break
                result.append((r1, c1))
                figure = self.board.get_figure(r1, c1)
                if figure is not None:
                    break
        return result

class Knight(Figure):
    def __init__(self, r, c, side, board):
        Figure.__init__(self, 'images/' + side + 'Knight.png', r, c, side, board)

    def get_actions(self):
        result = []
        offsets = [(-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1)]
        for delta_row, delta_col in offsets:
            r1 = self.row + delta_row
            c1 = self.col + delta_col
            if not self.is_valid_pos(r1, c1):
                continue
            result.append((r1, c1))
        return result

class Pawn(Figure):
    def __init__(self, r, c, side, board):
        Figure.__init__(self, 'images/' + side + 'Pawn.png', r, c, side, board)
        self.direction = 1 if self.row == 1 else -1

    def get_actions(self, *args):
        result = []
        if PAWN_MOVES in args or not args:
            r1 = self.row + self.direction
            c = self.col
            if self.is_valid_pos(r1, c) and self.board.get_figure(r1, c) is None:
                result.append((r1, c))
            if self.row == 1 or self.row == 6:
                r2 = self.row + 2 * self.direction
                if self.is_valid_pos(r2, c) and self.board.get_figure(r1, c) is None and self.board.get_figure(r2, c) is None:
                    result.append((r2, c))
        if PAWN_TAKES in args or not args:
            offsets = (-1, 1)
            r1 = self.row + self.direction
            for offset in offsets:
                c1 = self.col + offset
                if self.is_valid_pos(r1, c1):
                    result.append((r1, c1))
        return result

FIGURE_NAMES = {
    'w_King': 'White King',
    'w_Queen': 'White Queen',
    'w_Rook': 'White Rook',
    'w_Bishop': 'White Bishop',
    'w_Knight': 'White Knight',
    'w_Pawn': 'White Pawn',
    'b_King': 'Black King',
    'b_Queen': 'Black Queen',
    'b_Rook': 'Black Rook',
    'b_Bishop': 'Black Bishop',
    'b_Knight': 'Black Knight',
    'b_Pawn': 'Black Pawn'
}
