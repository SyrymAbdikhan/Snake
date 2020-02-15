import pygame
import os
import sqlite3
import random
import copy
import operator

pygame.init()
size = width, height = 500, 530
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Snake")


class Board:
    def __init__(self):
        self.rows = rows
        self.board = copy.deepcopy(boards[board_type])
        self.left = 0
        self.top = 30
        self.cell_size = 20
        self.snake = pygame.image.load(os.path.join('data', 'sprites', 'snake.png'))
        self.stone = pygame.image.load(os.path.join('data', 'sprites', 'stone.png'))
        self.snack = pygame.image.load(os.path.join('data', 'sprites', 'snack.png'))

    def render(self):  # drawing a board
        pygame.draw.line(screen, (0, 0, 0), (0, self.top), (width, self.top), 3)
        for row in range(self.rows):
            for col in range(self.rows):
                x = col * self.cell_size + self.left
                y = row * self.cell_size + self.top
                if self.board[row][col] == 1:
                    screen.blit(self.snake, (x, y))
                elif self.board[row][col] == 2:
                    screen.blit(self.snack, (x, y))
                elif self.board[row][col] == 3:
                    screen.blit(self.stone, (x, y))


class Snake(Board):

    def __init__(self, x, y):
        super().__init__()
        self.body = [(x, y)]
        self.board[y][x] = 1
        self.xdir = 1
        self.ydir = 0
        pygame.mixer.music.load(os.path.join('data', 'sounds', 'apple_bite.mp3'))

    def reset(self, x, y):
        self.body = [(x, y)]
        self.board[y][x] = 1
        self.xdir = 1
        self.ydir = 0

    def make_move(self, x, y):
        global game_loop_run
        if self.board[y + self.ydir][x + self.xdir] not in [3, 1]:
            self.board[y + self.ydir][x + self.xdir] = 1
            self.body.append((x + self.xdir, y + self.ydir))
        else:
            game_loop_run = False
            reset()

    def move(self):
        global snack, score
        x, y = self.body[-1]
        if self.xdir == 1:
            if x + 1 <= self.rows - 1:
                self.make_move(x, y)
            else:
                self.board[y][0] = 1
                self.body.append((0, y))
        elif self.xdir == -1:
            if x - 1 >= 0:
                self.make_move(x, y)
            else:
                self.board[y][rows - 1] = 1
                self.body.append((rows - 1, y))
        elif self.ydir == -1:
            if y - 1 >= 0:
                self.make_move(x, y)
            else:
                self.board[rows - 1][x] = 1
                self.body.append((x, rows - 1))
        elif self.ydir == 1:
            if y + 1 <= self.rows - 1:
                self.make_move(x, y)
            else:
                self.board[0][x] = 1
                self.body.append((x, 0))

        if self.body[-1] != snack:
            tail_x, tail_y = self.body[0]
            if len(self.body) > 1:
                self.board[tail_y][tail_x] = 0
                self.body.remove((tail_x, tail_y))
        else:
            score += 1
            pygame.mixer.music.play()
            if score % 10 != 0:
                snack = summon_snack()

        self.render()
        pygame.draw.circle(screen, (0, 0, 0),
                           (self.body[-1][0] * self.cell_size + self.left + 6, self.body[-1][1] * self.cell_size + self.top + 7), 3)
        pygame.draw.circle(screen, (0, 0, 0),
                           (self.body[-1][0] * self.cell_size + self.left + 14, self.body[-1][1] * self.cell_size + self.top + 7), 3)


class DataBase:
    def __init__(self):
        self.conn = sqlite3.connect(os.path.join('data', 'savings', 'scores.db'))
        self.c = self.conn.cursor()
        self.data = self.load_data()

    def load_data(self):
        self.c.execute("SELECT * FROM scores")
        unsorted_data = self.c.fetchall()
        data = sorted(unsorted_data, key=lambda student: student[1])
        return data

    def add_member(self, name, score):
        for el in self.data:
            if name == el[0]:
                if score > el[1]:
                    self.c.execute("DELETE FROM scores WHERE name=?", (name,))
                    self.c.execute("INSERT INTO scores VALUES (?, ?)", (name, score))
                    self.conn.commit()
                    self.data = self.load_data()
                return
        self.c.execute("INSERT INTO scores VALUES (?, ?)", (name, score))
        self.conn.commit()
        self.data = self.load_data()


def reset():
    global snake, boards, board_type, snack, fps, delay
    fps = 10
    delay = 50
    board_type = 1
    snake.board = copy.deepcopy(boards[board_type])
    snake.reset(1, rows // 2)
    snack = summon_snack()


def summon_snack():
    global snake
    snack_pos = fx, fy = (random.randint(0, rows - 1), random.randint(0, rows - 1))
    while snake.board[fy][fx] in [1, 3]:
        snack_pos = fx, fy = (random.randint(0, rows - 1), random.randint(0, rows - 1))
    snake.board[fy][fx] = 2
    return snack_pos


def load_boards():
    boards = {}
    count = 1
    with open(os.path.join('data', 'savings', 'boards.txt'), 'r') as f:
        d_boards = f.read().split('===')
    for board in d_boards:
        board = board.split('\n')
        new_board = []
        for row in board:
            row = list(map(int, list(row)))
            if row:
                new_board.append(row)
        boards[count] = new_board
        count += 1
    return boards


def draw_text_by_rect(text, font, color, rect):
    text = font.render(text, 1, color)
    x = rect[2] // 2 - text.get_width() // 2 + rect[0]
    y = rect[3] // 2 - text.get_height() // 2 + rect[1]
    screen.blit(text, (x, y))


def draw_text(text, font, color, pos):
    text = font.render(text, 1, color)
    screen.blit(text, pos)


def submit():

    global score
    input_box = pygame.Rect(width // 4, height // 2, width // 2, 50)
    submit_btn = pygame.Rect(width // 4, height - 200, width // 2, 50)
    menu_btn = pygame.Rect(width // 4, height - 80, width // 2, 50)

    text_input = ''
    active = False
    run = True

    while run:

        screen.fill(bgcolor)
        pygame.draw.rect(screen, btn_color, input_box)
        if not active:
            pygame.draw.rect(screen, border_color, input_box, 2)
        else:
            pygame.draw.rect(screen, (150, 150, 150), input_box, 2)
        pygame.draw.rect(screen, btn_color, submit_btn)
        pygame.draw.rect(screen, border_color, submit_btn, 2)
        pygame.draw.rect(screen, btn_color, menu_btn)
        pygame.draw.rect(screen, border_color, menu_btn, 2)

        draw_text(text_input, font, text_color, (width // 4 + 5, height // 2 + 15))
        draw_text_by_rect('Submit', font, text_color, submit_btn)
        draw_text_by_rect('Menu', font, text_color, menu_btn)

        pygame.time.delay(delay)
        clock.tick(fps)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if submit_btn.collidepoint(event.pos):
                    if text_input:
                        database.add_member(text_input, score)
                        text_input = ''
                        run = False
                        score = 0
                    active = False
                if menu_btn.collidepoint(event.pos):
                    run = False
                    score = 0
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if text_input:
                            database.add_member(text_input, score)
                            text_input = ''
                            run = False
                            score = 0
                        active = False
                    elif event.key == pygame.K_BACKSPACE:
                        text_input = text_input[:-1]
                    else:
                        if len(text_input) < 16:
                            text_input += event.unicode


def end_window(win=False):

    global score
    submit_btn = pygame.Rect(width // 4, height - 200, width // 2, 50)
    restart_btn = pygame.Rect(width // 4, height - 140, width // 2, 50)
    menu_btn = pygame.Rect(width // 4, height - 80, width // 2, 50)
    run = True

    while run:

        screen.fill(bgcolor)
        pygame.draw.rect(screen, btn_color, submit_btn)
        pygame.draw.rect(screen, border_color, submit_btn, 2)
        pygame.draw.rect(screen, btn_color, restart_btn)
        pygame.draw.rect(screen, border_color, restart_btn, 2)
        pygame.draw.rect(screen, btn_color, menu_btn)
        pygame.draw.rect(screen, border_color, menu_btn, 2)

        draw_text_by_rect('Submit score', font, text_color, submit_btn)
        draw_text_by_rect('Restart', font, text_color, restart_btn)
        draw_text_by_rect('Menu', font, text_color, menu_btn)

        if win:
            draw_text_by_rect('YOU', tfont, text_color, (0, 0, width, height // 2 - 65))
            draw_text_by_rect('WON', tfont, text_color, (0, 0, width, height // 2 + 65))
        else:
            draw_text_by_rect('GAME', tfont, text_color, (0, 0, width, height // 2 - 65))
            draw_text_by_rect('OVER', tfont, text_color, (0, 0, width, height // 2 + 65))

        draw_text_by_rect(f'total score: {score}', font, text_color, (0, height // 4, width, height // 2))

        pygame.time.delay(delay)
        clock.tick(fps)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if submit_btn.collidepoint(event.pos):
                    run = False
                    submit()
                if restart_btn.collidepoint(event.pos):
                    run = False
                    score = 0
                    game()
                if menu_btn.collidepoint(event.pos):
                    run = False
                    score = 0


def wait():

    global score
    menu_btn = pygame.Rect(width - width // 4, 0, width // 4, 30)
    count = fps * 3 - 1
    run = True

    while run:

        screen.fill(bgcolor)
        snake.render()
        pygame.draw.rect(screen, btn_color, menu_btn)
        pygame.draw.rect(screen, border_color, menu_btn, 2)
        pygame.draw.line(screen, border_color, (0, 30), (width, 30), 2)

        draw_text_by_rect('menu', font, text_color, menu_btn)
        draw_text(f'score: {score}', font, text_color, (5, 5))

        draw_text_by_rect(str(count // fps + 1), tfont, text_color, (0, 0, width, height))
        count -= 1

        if count <= 0:
            run = False

        pygame.time.delay(delay)
        clock.tick(fps)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()


def game():

    global delay, fps, boards, board_type, snack, snake, game_loop_run, score
    menu_btn = pygame.Rect(width - width // 4, 0, width // 4, 30)

    last_score = 0
    game_loop_run = True
    clicked = False

    wait()
    while game_loop_run:

        screen.fill(bgcolor)
        pygame.draw.rect(screen, btn_color, menu_btn)
        pygame.draw.rect(screen, border_color, menu_btn, 2)
        pygame.draw.line(screen, border_color, (0, 30), (width, 30), 2)

        draw_text_by_rect('menu', font, text_color, menu_btn)
        draw_text(f'score: {score}', font, text_color, (5, 5))

        snake.move()

        pygame.time.delay(delay)
        clock.tick(fps)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_btn.collidepoint(event.pos):
                    game_loop_run = False
                    clicked = True
                    reset()
                    last_score = 0

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and snake.ydir != 1:
            snake.xdir = 0
            snake.ydir = -1
        elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and snake.ydir != -1:
            snake.xdir = 0
            snake.ydir = 1
        elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and snake.xdir != -1:
            snake.xdir = 1
            snake.ydir = 0
        elif (keys[pygame.K_a] or keys[pygame.K_LEFT]) and snake.xdir != 1:
            snake.xdir = -1
            snake.ydir = 0

        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            fps = 20
            delay = 0
        else:
            fps = 10
            delay = 50

        if score % 10 == 0 and score != last_score:
            if board_type == len(boards):
                reset()
                game_loop_run = False
                end_window(True)
            else:
                fps = 10
                delay = 50
                board_type += 1
                last_score = score
                snake.board = copy.deepcopy(boards[board_type])
                snake.reset(1, rows // 2)
                snack = summon_snack()
                wait()

        if not game_loop_run and not clicked:
            end_window()


def options():

    back_btn = pygame.Rect(width - width // 4 - 10, height - 40, width // 4, 30)

    wkey = pygame.image.load(os.path.join('data', 'sprites', 'keys', 'wkey.png'))
    upkey = pygame.image.load(os.path.join('data', 'sprites', 'keys', 'upkey.png'))
    skey = pygame.image.load(os.path.join('data', 'sprites', 'keys', 'skey.png'))
    downkey = pygame.image.load(os.path.join('data', 'sprites', 'keys', 'downkey.png'))
    akey = pygame.image.load(os.path.join('data', 'sprites', 'keys', 'akey.png'))
    leftkey = pygame.image.load(os.path.join('data', 'sprites', 'keys', 'leftkey.png'))
    dkey = pygame.image.load(os.path.join('data', 'sprites', 'keys', 'dkey.png'))
    rightkey = pygame.image.load(os.path.join('data', 'sprites', 'keys', 'rightkey.png'))
    shiftkey = pygame.image.load(os.path.join('data', 'sprites', 'keys', 'shiftkey.png'))
    shiftkey = pygame.transform.scale(shiftkey, (155, 64))

    run = True

    while run:

        screen.fill(bgcolor)
        pygame.draw.rect(screen, btn_color, back_btn)
        pygame.draw.rect(screen, border_color, back_btn, 2)

        screen.blit(wkey, (50, 55))
        screen.blit(upkey, (140, 55))
        screen.blit(skey, (50, 130))
        screen.blit(downkey, (140, 130))
        screen.blit(akey, (50, 205))
        screen.blit(leftkey, (140, 205))
        screen.blit(dkey, (50, 280))
        screen.blit(rightkey, (140, 280))
        screen.blit(shiftkey, (50, 355))

        draw_text_by_rect('back', font, text_color, back_btn)
        draw_text_by_rect('truns snake up', font, text_color, (width // 2, 55, width // 2, 64))
        draw_text_by_rect('truns snake down', font, text_color, (width // 2, 130, width // 2, 64))
        draw_text_by_rect('truns snake left', font, text_color, (width // 2, 205, width // 2, 64))
        draw_text_by_rect('truns snake right', font, text_color, (width // 2, 280, width // 2, 64))
        draw_text_by_rect('speed ups snake', font, text_color, (width // 2, 355, width // 2, 64))

        pygame.time.delay(delay)
        clock.tick(fps)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    run = False


def show_scores():

    back_btn = pygame.Rect(width - width // 4 - 10, height - 40, width // 4, 30)
    data = database.data
    run = True

    while run:

        screen.fill(bgcolor)
        pygame.draw.rect(screen, btn_color, back_btn)
        pygame.draw.rect(screen, border_color, back_btn, 2)
        pygame.draw.line(screen, border_color, (0, 30), (width, 30), 2)
        pygame.draw.line(screen, border_color, (width // 2, 30), (width // 2, height - 50), 2)
        for i in range(15):
            pygame.draw.line(screen, border_color, (0, 60 + 30 * i), (width, 60 + 30 * i), 2)

        draw_text_by_rect('back', font, text_color, back_btn)
        draw_text_by_rect('names', font, text_color, (0, 0, width // 2, 30))
        draw_text_by_rect('scores', font, text_color, (width // 2, 0, width // 2 - 1, 30))
        for i, el in enumerate(data[::-1]):
            if i == 15: 
                break
            draw_text_by_rect(el[0], font, text_color, (0, 30 + 20 * i, width // 2, 30 + 20 * i))
            draw_text_by_rect(str(el[1]), font, text_color, (width // 2, 30 + 20 * i, width // 2, 30 + 20 * i))

        pygame.time.delay(delay)
        clock.tick(fps)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                   run = False


def menu():

    start_btn = pygame.Rect(width // 4, height - 260, width // 2, 50)
    options_btn = pygame.Rect(width // 4, height - 200, width // 2, 50)
    scores_btn = pygame.Rect(width // 4, height - 140, width // 2, 50)
    exit_btn = pygame.Rect(width // 4, height - 80, width // 2, 50)

    while True:

        screen.fill(bgcolor)
        pygame.draw.rect(screen, btn_color, start_btn)
        pygame.draw.rect(screen, border_color, start_btn, 2)
        pygame.draw.rect(screen, btn_color, options_btn)
        pygame.draw.rect(screen, border_color, options_btn, 2)
        pygame.draw.rect(screen, btn_color, scores_btn)
        pygame.draw.rect(screen, border_color, scores_btn, 2)
        pygame.draw.rect(screen, btn_color, exit_btn)
        pygame.draw.rect(screen, border_color, exit_btn, 2)

        draw_text_by_rect('Start', font, text_color, start_btn)
        draw_text_by_rect('Options', font, text_color, options_btn)
        draw_text_by_rect('Scores', font, text_color, scores_btn)
        draw_text_by_rect('Exit', font, text_color, exit_btn)
        draw_text_by_rect('SNAKE', tfont, text_color, (0, 0, width, height // 2))

        pygame.time.delay(delay)
        clock.tick(fps)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos):
                    game()
                if options_btn.collidepoint(event.pos):
                    options()
                if scores_btn.collidepoint(event.pos):
                    show_scores()
                if exit_btn.collidepoint(event.pos):
                    pygame.quit()
                    exit()


if __name__ == '__main__':
    boards = load_boards()
    board_type = 1
    game_loop_run = True

    rows = 25
    snake = Snake(1, rows // 2)
    snack = summon_snack()
    score = 0

    bgcolor = (155, 186, 90)  # (0, 18, 35)
    text_color = (43, 51, 26)  # (220, 220, 220)
    btn_color = (155, 186, 90)  # (0, 9, 17)
    border_color = (39, 47, 23) # (0, 4, 8)
    font = pygame.font.Font(None, 35)
    tfont = pygame.font.Font(None, 120)
    database = DataBase()

    fps = 10
    delay = 50
    clock = pygame.time.Clock()

    menu()
