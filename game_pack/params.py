# Частота кадрів
FPS = 60

# Колір фону
BACKGROUND_COLOR = (200, 200, 255)

# Константи сторін
WHITE = 'w_'
BLACK = 'b_'

# Словарь для швидко визначення протилежної сторони
OPPOSITE_SIDE = {WHITE: BLACK, BLACK: WHITE}

# Ширина/висота клітини дошки в пікселях
INITIAL_CELL_SIZE = 100

# Колори для білих і чорних клітин
WHITE_CELL_COLOR = (230, 230, 230)
BLACK_CELL_COLOR = (150, 150, 150)

# Колір тексту для повідомлень
MSG_COLOR = (255, 10, 10)

# Колір виділеної ячейки
SELECTED_CELL_COLOR = (80, 80, 200)

# Колір клітинки короля, якщо він під шахом
KING_ON_CHECK_COLOR = (255, 0, 0)

# Колір клітинки, доступної для ходу
AVL_MOVE_CELL_COLOR = (120, 255, 120)

# Імена дій, доступних для пішака
PAWN_MOVES = 'pawn_moves'
PAWN_TAKES = 'pawn_takes'

# Типи ходів
NORMAL_MOVE = 'normal_move'  # Звичайний хід
TAKE_MOVE = 'take_move'      # Хід-взяття
CASTLING = 'castling'        # Рокировка
CONVERSION = 'conversion'    # Перетворення пішака в іншу фігуру
PASSED_TAKE = 'passed_take'  # Взяття на проході

# Варіанти завершення гри
MATE = 'ate'  # Гра завершилася матом
PAT = 'pat'  # Гра завершилася патом