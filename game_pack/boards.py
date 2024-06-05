from game_pack.figures import *

class Move:
    def __init__(self, move_type, figure, new_row, new_col):
        self.m_type = move_type
        self.figure = figure
        self.new_row = new_row
        self.new_col = new_col
        self.old_row = figure.row
        self.old_col = figure.col
        self.is_check = False

class Board:
    def __init__(self, pl1_side):
        self.pl1_side = pl1_side
        self.pl2_side = OPPOSITE_SIDE[pl1_side]
        self.pl1_figures = []
        self.pl2_figures = []
        self.figures_dict = {self.pl1_side: self.pl1_figures, self.pl2_side: self.pl2_figures}
        self.kings_dict = {}
        self.cell_size = INITIAL_CELL_SIZE

        if self.pl2_side == WHITE:
            self.pl2_king = King(0, 3, self.pl2_side, self)
            self.kings_dict[WHITE] = self.pl2_king
            self.pl2_figures.append(self.pl2_king)
            self.pl2_figures.append(Queen(0, 4, self.pl2_side, self))

        if self.pl2_side == BLACK:
            self.pl2_king = King(0, 4, self.pl2_side, self)
            self.kings_dict[BLACK] = self.pl2_king
            self.pl2_figures.append(self.pl2_king)
            self.pl2_figures.append(Queen(0, 3, self.pl2_side, self))

        self.pl2_figures.extend([
            Rook(0, 0, self.pl2_side, self),
            Rook(0, 7, self.pl2_side, self),
            Knight(0, 1, self.pl2_side, self),
            Knight(0, 6, self.pl2_side, self),
            Bishop(0, 2, self.pl2_side, self),
            Bishop(0, 5, self.pl2_side, self)
        ])

        for i in range(0, 8):
            self.pl2_figures.append(Pawn(1, i, self.pl2_side, self))

        if self.pl1_side == BLACK:
            self.pl1_king = King(7, 3, self.pl1_side, self)
            self.kings_dict[BLACK] = self.pl1_king
            self.pl1_figures.append(self.pl1_king)
            self.pl1_figures.append(Queen(7, 4, self.pl1_side, self))

        if self.pl1_side == WHITE:
            self.pl1_king = King(7, 4, self.pl1_side, self)
            self.kings_dict[WHITE] = self.pl1_king
            self.pl1_figures.append(self.pl1_king)
            self.pl1_figures.append(Queen(7, 3, self.pl1_side, self))

        self.pl1_figures.extend([
            Rook(7, 0, self.pl1_side, self),
            Rook(7, 7, self.pl1_side, self),
            Knight(7, 1, self.pl1_side, self),
            Knight(7, 6, self.pl1_side, self),
            Bishop(7, 2, self.pl1_side, self),
            Bishop(7, 5, self.pl1_side, self)
        ])

        for i in range(0, 8):
            self.pl1_figures.append(Pawn(6, i, self.pl1_side, self))

        self.cells = [[None for _ in range(8)] for _ in range(8)]
        for figure in self.pl2_figures + self.pl1_figures:
            self.cells[figure.row][figure.col] = figure

        self.move_list = []

    def update_cell_size(self, new_size):
        self.cell_size = new_size
        for figure in self.pl2_figures + self.pl1_figures:
            figure.update_image()

    def get_moves_count(self):
        return len(self.move_list)

    def get_all_avl_moves(self, side):
        work_list = self.figures_dict[side]
        result = []
        for figure in work_list:
            if figure.is_drop:
                continue
            result.extend(self.get_avl_moves_for_figure(figure))
        return result

    def get_avl_moves_for_figure(self, figure):
        moves = []
        figure_type = type(figure)

        if figure_type == Pawn:
            actions = figure.get_actions(PAWN_MOVES)
            for new_row, new_col in actions:
                if new_row == 0 or new_row == 7:
                    moves.append(self.create_conversion_move(figure, new_row, new_col))
                else:
                    moves.append(self.create_normal_move(figure, new_row, new_col))
            actions = figure.get_actions(PAWN_TAKES)
            for new_row, new_col in actions:
                drop_figure = self.get_figure(new_row, new_col)
                if drop_figure is None or drop_figure.side == figure.side:
                    continue
                if new_row == 0 or new_row == 7:
                    moves.append(self.create_conversion_move(figure, new_row, new_col))
                else:
                    moves.append(self.create_take_move(figure, new_row, new_col))
            if self.get_moves_count() > 0:
                last_move = self.move_list[-1]
                if type(last_move.figure) == Pawn and last_move.figure.side != figure.side:
                    r0 = min(last_move.new_row, last_move.old_row)
                    r2 = max(last_move.new_row, last_move.old_row)
                    if (r2 - r0) == 2:
                        c = last_move.new_col
                        for r1, c1 in actions:
                            if r0 < r1 < r2 and c1 == c:
                                moves.append(self.create_passed_take_move(figure, r1, c1, last_move.figure))

        if figure_type == King:
            if not self.was_move(figure):
                if not self.is_strike_cell(figure.row, figure.col, OPPOSITE_SIDE[figure.side]):
                    l_rook = self.get_figure(figure.row, 0)
                    if type(l_rook) == Rook and not self.was_move(l_rook):
                        cell_list = [(figure.row, 1), (figure.row, 2)]
                        if figure.col == 4:
                            cell_list.append((figure.row, 3))
                        allowed_cells_flag = all(
                            self.get_figure(row, col) is None and not self.is_strike_cell(row, col, OPPOSITE_SIDE[figure.side])
                            for row, col in cell_list
                        )
                        if allowed_cells_flag:
                            moves.append(self.create_castling_move(figure, figure.row, figure.col - 2, l_rook, figure.row, figure.col - 1))
                    r_rook = self.get_figure(figure.row, 7)
                    if type(r_rook) == Rook and not self.was_move(r_rook):
                        cell_list = [(figure.row, 6), (figure.row, 5)]
                        if figure.col == 3:
                            cell_list.append((figure.row, 4))
                        allowed_cells_flag = all(
                            self.get_figure(row, col) is None and not self.is_strike_cell(row, col, OPPOSITE_SIDE[figure.side])
                            for row, col in cell_list
                        )
                        if allowed_cells_flag:
                            moves.append(self.create_castling_move(figure, figure.row, figure.col + 2, r_rook, figure.row, figure.col + 1))

        if figure_type != Pawn:
            actions = figure.get_actions()
            for new_row, new_col in actions:
                drop_figure = self.get_figure(new_row, new_col)
                if drop_figure is None:
                    moves.append(self.create_normal_move(figure, new_row, new_col))
                elif drop_figure.side != figure.side:
                    moves.append(self.create_take_move(figure, new_row, new_col))

        avl_moves = []
        king = self.kings_dict[figure.side]
        for move in moves:
            if move.m_type == CONVERSION:
                move.new_figure = Queen(move.new_row, move.new_col, figure.side, self)
            self.apply_move(move)
            if not self.is_strike_figure(king):
                avl_moves.append(move)
            self.cancel_move()
            if move.m_type == CONVERSION:
                move.new_figure = None

        return avl_moves

    @staticmethod
    def create_normal_move(figure, new_row, new_col):
        return Move(NORMAL_MOVE, figure, new_row, new_col)

    def create_take_move(self, figure, new_row, new_col):
        move = Move(TAKE_MOVE, figure, new_row, new_col)
        move.drop_figure = self.get_figure(new_row, new_col)
        return move

    def create_conversion_move(self, figure, new_row, new_col):
        move = Move(CONVERSION, figure, new_row, new_col)
        move.drop_figure = self.get_figure(new_row, new_col)
        move.new_figure = None
        return move

    @staticmethod
    def create_passed_take_move(figure, new_row, new_col, drop_figure):
        move = Move(PASSED_TAKE, figure, new_row, new_col)
        move.drop_figure = drop_figure
        return move

    @staticmethod
    def create_castling_move(figure, new_row_figure, new_col_figure, rook, new_row_rook, new_col_rook):
        move = Move(CASTLING, figure, new_row_figure, new_col_figure)
        move.rook = rook
        move.old_row_rook = rook.row
        move.old_col_rook = rook.col
        move.new_row_rook = new_row_rook
        move.new_col_rook = new_col_rook
        return move

    def apply_move(self, move):
        self.move_list.append(move)
        if move.m_type == NORMAL_MOVE:
            move.figure.set_pos(move.new_row, move.new_col)
            self.cells[move.old_row][move.old_col] = None
            self.cells[move.new_row][move.new_col] = move.figure
        elif move.m_type == TAKE_MOVE or move.m_type == PASSED_TAKE:
            move.figure.set_pos(move.new_row, move.new_col)
            move.drop_figure.is_drop = True
            self.cells[move.drop_figure.row][move.drop_figure.col] = None
            self.cells[move.old_row][move.old_col] = None
            self.cells[move.new_row][move.new_col] = move.figure
        elif move.m_type == CONVERSION:
            move.figure.set_pos(move.new_row, move.new_col)
            move.figure.is_drop = True
            if move.drop_figure is not None:
                move.drop_figure.is_drop = True
            self.figures_dict[move.new_figure.side].append(move.new_figure)
            self.cells[move.old_row][move.old_col] = None
            self.cells[move.new_figure.row][move.new_col] = move.new_figure
        elif move.m_type == CASTLING:
            move.figure.set_pos(move.new_row, move.new_col)
            move.rook.set_pos(move.new_row_rook, move.new_col_rook)
            self.cells[move.old_row][move.old_col] = None
            self.cells[move.new_row][move.new_col] = move.figure
            self.cells[move.old_row_rook][move.old_col_rook] = None
            self.cells[move.new_row_rook][move.new_col_rook] = move.rook
        move.is_check = self.is_strike_figure(self.kings_dict[OPPOSITE_SIDE[move.figure.side]])

    def cancel_move(self):
        if not self.move_list:
            return
        last_move = self.move_list.pop(-1)
        if last_move.m_type == NORMAL_MOVE:
            last_move.figure.set_pos(last_move.old_row, last_move.old_col)
            self.cells[last_move.new_row][last_move.new_col] = None
            self.cells[last_move.old_row][last_move.old_col] = last_move.figure
            return
        if last_move.m_type == TAKE_MOVE or last_move.m_type == PASSED_TAKE:
            last_move.figure.set_pos(last_move.old_row, last_move.old_col)
            last_move.drop_figure.is_drop = False
            self.cells[last_move.new_row][last_move.new_col] = None
            self.cells[last_move.old_row][last_move.old_col] = last_move.figure
            self.cells[last_move.drop_figure.row][last_move.drop_figure.col] = last_move.drop_figure
            return
        if last_move.m_type == CONVERSION:
            last_move.figure.set_pos(last_move.old_row, last_move.old_col)
            last_move.figure.is_drop = False
            if last_move.drop_figure is not None:
                last_move.drop_figure.is_drop = False
            work_list = self.figures_dict[last_move.new_figure.side]
            work_list.remove(last_move.new_figure)
            self.cells[last_move.new_row][last_move.new_col] = None
            self.cells[last_move.old_row][last_move.old_col] = last_move.figure
            if last_move.drop_figure is not None:
                self.cells[last_move.drop_figure.row][last_move.drop_figure.col] = last_move.drop_figure
            return
        if last_move.m_type == CASTLING:
            last_move.figure.set_pos(last_move.old_row, last_move.old_col)
            last_move.rook.set_pos(last_move.old_row_rook, last_move.old_col_rook)
            self.cells[last_move.new_row][last_move.new_col] = None
            self.cells[last_move.old_row][last_move.old_col] = last_move.figure
            self.cells[last_move.new_row_rook][last_move.new_col_rook] = None
            self.cells[last_move.old_row_rook][last_move.old_col_rook] = last_move.rook
            return

    def is_strike_cell(self, row, col, side):
        work_list = self.figures_dict[side]
        for figure in work_list:
            if figure.is_drop:
                continue
            figure_type = type(figure)
            if figure_type == Pawn:
                actions = figure.get_actions(PAWN_TAKES)
            else:
                actions = figure.get_actions()
            for r, c in actions:
                if r == row and c == col:
                    return True
        return False

    def is_strike_figure(self, figure):
        return self.is_strike_cell(figure.row, figure.col, OPPOSITE_SIDE[figure.side])

    def was_move(self, figure):
        return any(move.figure == figure for move in self.move_list)

    def get_figure(self, r, c):
        return self.cells[r][c]

class SelectorBoard:
    def __init__(self, side, main_board):
        self.queen = Queen(3, 3, side, main_board)
        self.rook = Rook(3, 4, side, main_board)
        self.bishop = Bishop(4, 3, side, main_board)
        self.knight = Knight(4, 4, side, main_board)

    def get_figure(self, r, c):
        if r == 3 and c == 3:
            return self.queen
        if r == 3 and c == 4:
            return self.rook
        if r == 4 and c == 3:
            return self.bishop
        if r == 4 and c == 4:
            return self.knight
        return None
