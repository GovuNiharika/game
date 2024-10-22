import pgzrun
import random
import time

TITLE = "Zombie vs Tank"
WIDTH = 800
HEIGHT = 640

UP = 180
DOWN = 0
LEFT = 270
RIGHT = 90
BULLET_SPEED = 30

blue_tank = Actor("tank_blue")
blue_tank.x = WIDTH / 2
blue_tank.y = HEIGHT / 2

bullet = Actor("bulletblue")
bullet_fired = False

zombie_list = []
ZOMBIE_SPEED = 0.1

score = 0
level = 1
target_scores = {1: 25, 2: 35, 3: 45}
game_over = False
game_won = False
show_level_transition = False
transition_timer = 0
show_target_score = True
target_score_timer = 0

restart_button = Actor("restart_button.png")  # Add a restart button image
restart_button.x = WIDTH // 2
restart_button.y = HEIGHT // 2 + 50  # Position it below the game over text

# Define the zombie transition image for display at the center-top
zombie_transition_image = Actor("zombie_stand.png")
zombie_transition_image.x = WIDTH // 2
zombie_transition_image.y = 100 

# Questions and answers for Level 1 and Level 2
questions = ("How is a code block indicated in Python?",
             "What is the output of print(2 * 3)?",
             "What is the output of len(hello)?")

options = (("A.Brackets", "B.Indentation", "C. Keys", "D. None of the Above"),
           ("A. 5", "B. 6", "C. 8", "D. 9"),
           ("A. 5", "B. 4", "C. 6", "D. 7"))

answers = ("B", "B", "A")
guesses = []
current_question = 0
show_question_screen = False
question_options = []

feedback_message = ""
feedback_message_color = "white"
feedback_message_display_time = 0
feedback_message_duration = 2  # Duration to display the message

quiz_completed_timer = 0
quiz_completed_duration = 2 

# New questions for Level 3
level_3_questions = (
    "What is the keyword used to define a function in Python?",
    "What is the correct file extension for Python files?",
    "What does the 'self' keyword represent in a class?"
)

level_3_options = (
    ("A. func", "B. define", "C. def", "D. function"),
    ("A. .py", "B. .pyt", "C. .pt", "D. .python"),
    ("A. Instance", "B. Method", "C. Class", "D. None of the Above")
)

level_3_answers = ("C", "A", "A")

def draw():
    global show_level_transition, transition_timer, show_target_score, target_score_timer
    global show_question_screen, question_options, feedback_message, feedback_message_color, feedback_message_display_time
    global quiz_completed_timer

    if feedback_message:
        screen.fill("black")
        screen.draw.text(feedback_message, 
                         center=(WIDTH // 2, HEIGHT // 2), 
                         fontsize=50, 
                         color=feedback_message_color, 
                         bold=False)
        if time.time() - feedback_message_display_time > feedback_message_duration:
            feedback_message = ""  # Clear message after duration

    elif show_question_screen:
        screen.fill("black")
        screen.draw.text(questions[current_question], (50, 50), fontsize=30, color="white")
        y = 100
        for i, option in enumerate(question_options):
            screen.draw.text(f"{i + 1}. {option}", (50, y), fontsize=25, color="white")
            y += 40
    elif show_target_score:
        screen.fill("black")
        screen.draw.text(f"Target Score: {target_scores[level]}",
                         center=(WIDTH // 2, HEIGHT // 2), fontsize=50, color="orange")
        if time.time() - target_score_timer > 2:
            show_target_score = False
    elif show_level_transition:
        screen.fill("black")
        zombie_transition_image.draw()
        screen.draw.text(f"Level {level - 1} Complete! Score: {target_scores[level - 1]}",
                         center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=50)
        screen.draw.text(f"Next Level: {level}",
                         center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=50)
        if time.time() - transition_timer > 2:
            show_level_transition = False
            start_next_level()
            start_quiz()  # Call to start the quiz after level transition
    elif quiz_completed_timer > 0:
        screen.fill("black")
        zombie_transition_image.draw()
        screen.draw.text("It's Done. Starting Next Level", 
                         center=(WIDTH // 2, HEIGHT // 2), 
                         fontsize=50, 
                         color="yellow", 
                         bold=False)
        if time.time() - quiz_completed_timer > quiz_completed_duration:
            quiz_completed_timer = 0  # Reset the timer
            start_next_level()
    
    elif game_won:
        screen.blit("zombie_stand.png", (0, 0))
        screen.draw.text(f"YOU WON!", center=(WIDTH // 2, HEIGHT // 3 - 25), fontsize=50, color="dark blue")
        screen.draw.text(f"Final Score: {score}", center=(WIDTH // 2, HEIGHT // 3 + 25), fontsize=50, color="dark blue")
    elif game_over:
        screen.blit("zombie_stand.png", (0, 0))
        screen.draw.text(f"YOU LOST", center=(WIDTH // 2, HEIGHT // 3 - 25), fontsize=50, color="dark blue")
        screen.draw.text(f"Final Score: {score}", center=(WIDTH // 2, HEIGHT // 3 + 25), fontsize=50, color="dark blue")
        restart_button.draw() 
    else:
        screen.blit("tank.png", (0, 0))
        blue_tank.draw()
        bullet.draw()
        for zomb in zombie_list:
            zomb.draw()
        draw_scoreboard()

def start_quiz():
    global show_question_screen, current_question, question_options
    show_question_screen = True
    question_options = options[current_question]

def on_mouse_down(pos):
    global show_question_screen, current_question, feedback_message, feedback_message_color, feedback_message_display_time
    
    if game_over:  # Check if the game is over to handle the restart option
        if restart_button.collidepoint(pos):  # Check if the restart button is clicked
            restart_level()  # Call the restart function
        return 
    
    if show_question_screen:
        y = 100
        for i, option in enumerate(question_options):
            if 100 < pos[1] < 140 + i * 40:
                if option.startswith(answers[current_question]):
                    feedback_message = "Correct!"
                    feedback_message_color = "light green"
                    feedback_message_display_time = time.time()
                    current_question += 1
                    if current_question < len(questions):
                        start_quiz()
                    else:
                        feedback_message = "Quiz Completed. Starting the Next Level"
                        feedback_message_color = "yellow"
                        feedback_message_display_time = time.time()
                        # Call a function to handle level transition after quiz completion
                        start_quiz_completed_display()
                        end_quiz_and_start_next_level()
                else:
                    feedback_message = "Incorrect. Try Again."
                    feedback_message_color = "red"
                    feedback_message_display_time = time.time()
                break

def start_quiz_completed_display():
    global quiz_completed_timer
    quiz_completed_timer = time.time()  # Set timer to display "Quiz Completed"

def end_quiz_and_start_next_level():
    global show_question_screen, current_question, feedback_message, feedback_message_color, feedback_message_display_time
    # Clear quiz screen and reset for next level
    show_question_screen = False
    current_question = 0
    feedback_message = ""
    feedback_message_color = "white"
    feedback_message_display_time = 0
    start_next_level()  # Start the next level after quiz completion

def draw_scoreboard():
    box_width = 140
    box_height = 60
    box_x = WIDTH - box_width - 10
    box_y = 10

    screen.draw.filled_rect(Rect((box_x, box_y), (box_width, box_height)), "lightgrey")

    # Target score
    screen.draw.text(f"Target: {target_scores[level]}", 
                     (box_x + 10, box_y + 5), 
                     fontsize=20, color="red")

    # Score
    screen.draw.text(f"Score: {score}", 
                     (box_x + 10, box_y + 25), 
                     fontsize=20, color="black")

    # Level number
    screen.draw.text(f"Level: {level}", 
                     (box_x + 10, box_y + 45), 
                     fontsize=20, color="black", bold=True)

def update():
    global bullet_fired
    if keyboard.left:
        blue_tank.x -= 5
        blue_tank.angle = LEFT
    if keyboard.right:
        blue_tank.x += 5
        blue_tank.angle = RIGHT
    if keyboard.up:
        blue_tank.y -= 5
        blue_tank.angle = UP
    if keyboard.down:
        blue_tank.y += 5
        blue_tank.angle = DOWN
    if keyboard.space:
        if not bullet_fired:
            bullet_fired = True
            sounds.laserretro_004.play()
            if blue_tank.angle == LEFT:
                bullet.x = blue_tank.x - 30
                bullet.y = blue_tank.y
            elif blue_tank.angle == RIGHT:
                bullet.x = blue_tank.x + 30
                bullet.y = blue_tank.y
            elif blue_tank.angle == DOWN:
                bullet.x = blue_tank.x
                bullet.y = blue_tank.y + 30
            elif blue_tank.angle == UP:
                bullet.x = blue_tank.x
                bullet.y = blue_tank.y - 30

    if not game_won and not game_over and not show_target_score and not show_level_transition:
        shoot_bullet()
        create_zombies()
        move_zombie()

def shoot_bullet():
    global bullet_fired
    if bullet_fired:
        if blue_tank.angle == LEFT:
            bullet.x -= BULLET_SPEED
        elif blue_tank.angle == RIGHT:
            bullet.x += BULLET_SPEED
        elif blue_tank.angle == DOWN:
            bullet.y += BULLET_SPEED
        elif blue_tank.angle == UP:
            bullet.y -= BULLET_SPEED

        if bullet.x >= WIDTH or bullet.x <= 0 or bullet.y >= HEIGHT or bullet.y <= 0:
            bullet_fired = False

def create_zombies():
    if len(zombie_list) < 10:
        loc_rand = random.randint(0, 3)
        if loc_rand == 0:
            y = random.randint(40, HEIGHT - 40)
            z = Actor("zombie_stand.png")
            z.x = 1
            z.y = y
            zombie_list.append(z)
        elif loc_rand == 1:
            y = random.randint(40, HEIGHT - 40)
            z = Actor("zombie_stand.png")
            z.x = WIDTH - 1
            z.y = y
            zombie_list.append(z)
        elif loc_rand == 2:
            x = random.randint(40, WIDTH - 40)
            z = Actor("zombie_stand.png")
            z.y = 1
            z.x = x
            zombie_list.append(z)
        elif loc_rand == 3:
            x = random.randint(40, WIDTH - 40)
            z = Actor("zombie_stand.png")
            z.y = HEIGHT - 1
            z.x = x
            zombie_list.append(z)

def move_zombie():
    global score, game_over, level, game_won, show_level_transition, transition_timer
    for zomb in zombie_list:
        if zomb.x < blue_tank.x:
            zomb.x += ZOMBIE_SPEED
        elif zomb.x > blue_tank.x:
            zomb.x -= ZOMBIE_SPEED
        if zomb.y < blue_tank.y:
            zomb.y += ZOMBIE_SPEED
        elif zomb.y > blue_tank.y:
            zomb.y -= ZOMBIE_SPEED

        if zomb.colliderect(bullet):
            zombie_list.remove(zomb)
            score += 1
            if score >= target_scores[level]:
                if level < 3:
                    show_level_transition = True
                    transition_timer = time.time()
                    level += 1  # Increment level after showing transition
                else:
                    game_won = True
        if zomb.colliderect(blue_tank):
            game_over = True


def restart_level():
    global score, level, game_over, blue_tank, bullet_fired, zombie_list
    # Reset necessary variables
    score = 0
    level = 1
    game_over = False
    blue_tank.x = WIDTH / 2
    blue_tank.y = HEIGHT / 2
    bullet_fired = False
    zombie_list = []  # Clear the zombie list


def start_next_level():
    global score, zombie_list, blue_tank, bullet_fired, questions, options, answers
    score = 0
    zombie_list.clear()
    blue_tank.x = WIDTH / 2
    blue_tank.y = HEIGHT / 2
    bullet_fired = False
    show_target_score = True
    target_score_timer = time.time()

    # Prepare for the quiz at the beginning of Level 3
    if level == 3:
        questions = level_3_questions
        options = level_3_options
        answers = level_3_answers

pgzrun.go()