import pygame
import pygame_gui
import time
from game_pack.boards import Board
from game_pack.figures import FIGURE_NAMES
from game_pack.params import *

# Поточне ігрове поле
board = None
selected_figure = None
avl_moves = []
selected_move = None
check_flag = False
msg = None
current_player = WHITE
start_time = None
elapsed_time = 0

pygame.init()
pygame.display.set_caption('Шахи')
window_size = (INITIAL_CELL_SIZE * 8 + 400, INITIAL_CELL_SIZE * 8)
surface = pygame.display.set_mode(window_size, pygame.RESIZABLE)
surface.fill(BACKGROUND_COLOR)
clock = pygame.time.Clock()
ui_manager = pygame_gui.UIManager(window_size)

panel_width = 300
scroll_panel = pygame_gui.elements.UIPanel(
    relative_rect=pygame.Rect((INITIAL_CELL_SIZE * 8 + 10, 60), (panel_width, INITIAL_CELL_SIZE * 8 - 60)),
    manager=ui_manager
)

text_container = pygame_gui.elements.UITextBox(
    html_text="",
    relative_rect=pygame.Rect((0, 0), (panel_width - 20, INITIAL_CELL_SIZE * 8 - 60)),
    manager=ui_manager,
    container=scroll_panel
)

def export_move_history(filename='move_history.txt'):
    with open(filename, 'w') as file:
        for i, move in enumerate(board.move_list, 1):
            col_letter_old = chr(move.old_col + ord('a'))
            row_number_old = str(8 - move.old_row)
            col_letter_new = chr(move.new_col + ord('a'))
            row_number_new = str(8 - move.new_row)
            from_pos = f"{col_letter_old}{row_number_old}"
            to_pos = f"{col_letter_new}{row_number_new}"
            figure_name = FIGURE_NAMES.get(f"{move.figure.side}{type(move.figure).__name__}", f"{move.figure.side}{type(move.figure).__name__}")

            move_text = f"{i}. {figure_name} from {from_pos} to {to_pos}"
            if move.is_check:
                move_text += " (Check)"
            file.write(move_text + '\n')

def start():
    global surface, board, selected_figure, avl_moves, selected_move, mode, check_flag, msg, current_player, start_time
    global panel_width, scroll_panel, text_container, window_size
    pygame.init()
    pygame.display.set_caption('Шахи')
    surface = pygame.display.set_mode(window_size, pygame.RESIZABLE)
    surface.fill(BACKGROUND_COLOR)
    clock = pygame.time.Clock()

    start_time = time.time()
    main_board = Board(WHITE)
    board = main_board
    mode = 'mode_1'

    resize_ui_elements()  # Оновлюємо розмір елементів інтерфейсу при запуску
    repaint()  # Перше промальовування фону

    while True:
        time_delta = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.VIDEORESIZE:
                window_size = event.size
                surface = pygame.display.set_mode(window_size, pygame.RESIZABLE)
                ui_manager.set_window_resolution(window_size)
                resize_ui_elements()
                repaint()  # Перемальовка фону після зміни розміру вікна

            # Обробка подій інтерфейсу
            ui_manager.process_events(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button != 1:
                    continue
                if mode == 'mode_1':
                    selected_figure = get_mouse_selected_figure(event, current_player)
                    if selected_figure is not None:
                        avl_moves = board.get_avl_moves_for_figure(selected_figure)
                        if avl_moves:
                            mode = 'mode_2'
                            continue

                if mode == 'mode_2':
                    selected_row, selected_col = get_mouse_selected_cell(event)
                    if selected_row is None or selected_col is None:
                        continue
                    selected_move = None
                    for move in avl_moves:
                        if selected_row == move.new_row and selected_col == move.new_col:
                            selected_move = move
                            break

                    if selected_move is not None:
                        if selected_move.m_type == CONVERSION:
                            selected_figure = None
                            avl_moves = []
                            board = Board(current_player)
                            mode = 'mode_3'
                            continue
                        mode = 'mode_4'
                        continue

                    new_selected_figure = get_mouse_selected_figure(event, current_player)
                    if new_selected_figure is not None:
                        selected_figure = new_selected_figure
                        avl_moves = board.get_avl_moves_for_figure(selected_figure)
                    continue

                if mode == 'mode_3':
                    selected_figure = get_mouse_selected_figure(event, current_player)
                    if selected_figure is not None:
                        selected_figure.set_pos(selected_move.new_row, selected_move.new_col)
                        selected_move.new_figure = selected_figure
                        board = main_board
                        mode = 'mode_4'
                        continue

                if mode == 'mode_6':
                    pygame.QUIT

        if mode == 'mode_4':
            board.apply_move(selected_move)
            selected_figure = None
            selected_move = None
            avl_moves = []

            check_flag = board.is_strike_figure(board.kings_dict[OPPOSITE_SIDE[current_player]])

            game_over = check_game_over(OPPOSITE_SIDE[current_player])
            if game_over == MATE:
                msg = 'ПЕРЕМОГА БІЛИХ' if current_player == WHITE else 'ПЕРЕМОГА ЧОРНИХ'
                check_flag = True
                mode = 'mode_6'
                continue
            if game_over == PAT:
                msg = 'ПАТ'
                check_flag = False
                mode = 'mode_6'
                continue

            current_player = OPPOSITE_SIDE[current_player]
            mode = 'mode_1'
            draw_move_history()
            export_move_history()

        ui_manager.update(time_delta)
        ui_manager.draw_ui(surface)
        repaint()
        clock.tick(FPS)

def check_game_over(side):
    king = board.kings_dict[side]
    check_flag = board.is_strike_figure(king)
    avl_flag = (len(board.get_all_avl_moves(side)) == 0)
    if avl_flag and check_flag:
        return MATE
    if avl_flag and not check_flag:
        return PAT
    return None

def repaint():
    # Заливка всього вікна кольором фону
    surface.fill(BACKGROUND_COLOR)

    # Блок команд малювання
    draw_cells()
    draw_select_cell()
    draw_avl_moves()
    draw_check_cell()
    draw_figures()
    draw_msg()
    draw_time()
    ui_manager.draw_ui(surface)

    pygame.display.update()

def draw_cells():
    for r in range(8):
        for c in range(8):
            color = WHITE_CELL_COLOR if (r + c) % 2 == 0 else BLACK_CELL_COLOR
            pygame.draw.rect(surface, color, (c * board.cell_size, r * board.cell_size, board.cell_size, board.cell_size))

def draw_figures():
    for row in range(8):
        for col in range(8):
            figure = board.get_figure(row, col)
            if figure:
                surface.blit(figure.image, figure.rect)

def draw_select_cell():
    if selected_figure:
        pygame.draw.rect(surface, SELECTED_CELL_COLOR,
                         (selected_figure.col * board.cell_size, selected_figure.row * board.cell_size, board.cell_size, board.cell_size))

def draw_avl_moves():
    for move in avl_moves:
        row_move = move.new_row
        col_move = move.new_col
        pygame.draw.rect(surface, AVL_MOVE_CELL_COLOR,
                         (col_move * board.cell_size + 4, row_move * board.cell_size + 4, board.cell_size - 8, board.cell_size - 8))

def draw_check_cell():
    if check_flag:
        if mode == 'mode_6':  # Игра скінчена, підсвічується клітинка короля що програв
            king = board.kings_dict[OPPOSITE_SIDE[current_player]]
        else:  # Игра не скінчена, підсвічується клітинка короля під шахом
            king = board.kings_dict[current_player]
        row, col = king.row, king.col
        pygame.draw.rect(surface, KING_ON_CHECK_COLOR,
                         (col * board.cell_size + 4, row * board.cell_size + 4, board.cell_size - 8, board.cell_size - 8))

def draw_msg():
    if not msg:
        return
    font = pygame.font.Font(None, 56)
    msg_surface = font.render(msg, 1, MSG_COLOR)
    x_pos = board.cell_size * 4 - msg_surface.get_width() // 2
    y_pos = board.cell_size * 4 - msg_surface.get_height() // 2
    padding = 10
    background_rect = pygame.Rect(
        x_pos - padding,
        y_pos - padding,
        msg_surface.get_width() + 2 * padding,
        msg_surface.get_height() + 2 * padding
    )
    pygame.draw.rect(surface, (0, 0, 0), background_rect)
    surface.blit(msg_surface, (x_pos, y_pos))

def draw_time():
    global elapsed_time
    elapsed_time = time.time() - start_time
    font = pygame.font.Font(None, 36)
    time_rect = pygame.Rect(board.cell_size * 8 + 20, 20, 160, 40)
    pygame.draw.rect(surface, BACKGROUND_COLOR, time_rect)
    time_surface = font.render(f"Час гри: {int(elapsed_time)}с", 1, (0, 0, 0))
    surface.blit(time_surface, (board.cell_size * 8 + 20, 20))

def draw_move_history():
    move_texts = []
    for i, move in enumerate(board.move_list, 1):
        col_letter_old = chr(move.old_col + ord('a'))
        row_number_old = str(8 - move.old_row)
        col_letter_new = chr(move.new_col + ord('a'))
        row_number_new = str(8 - move.new_row)
        from_pos = f"{col_letter_old}{row_number_old}"
        to_pos = f"{col_letter_new}{row_number_new}"
        figure_name = FIGURE_NAMES.get(f"{move.figure.side}{type(move.figure).__name__}", f"{move.figure.side}{type(move.figure).__name__}")

        move_text = f"{i}. {figure_name} from {from_pos} to {to_pos}"
        if move.is_check:
            move_text += " (Check)"
        move_texts.append(move_text)

    html_text = "<br>".join(move_texts)
    text_container.set_text(html_text)

def get_mouse_selected_cell(mouse_event):
    c = mouse_event.pos[0] // board.cell_size
    r = mouse_event.pos[1] // board.cell_size
    if 0 <= c < 8 and 0 <= r < 8:
        return r, c
    return None, None

def get_mouse_selected_figure(mouse_event, side=None):
    selected_row, selected_col = get_mouse_selected_cell(mouse_event)
    if selected_row is None or selected_col is None:
        return None
    figure = board.get_figure(selected_row, selected_col)
    return figure if side is None or (figure and figure.side == side) else None

def resize_ui_elements():
    global panel_width, scroll_panel, text_container, window_size
    # Рассчитайте новый размер клеток
    new_cell_size = min(window_size[1] // 8, (window_size[0] - 400) // 8)
    board.update_cell_size(new_cell_size)

    # Рассчитайте новый размер панели пропорционально размеру окна
    panel_width = max(200, (window_size[0] - board.cell_size * 8 - 20))
    scroll_panel.set_relative_position((board.cell_size * 8 + 10, 60))
    scroll_panel.set_dimensions((panel_width, board.cell_size * 8 - 60))

    # Настройка размеров текстового контейнера
    text_container.set_dimensions((panel_width - 20, board.cell_size * 8 - 60))
    text_container.set_text(text_container.html_text)  # Перерисовать текст

if __name__ == "__main__":
    start()
