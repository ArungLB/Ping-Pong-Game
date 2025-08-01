from pygame import *

# --- Classes ---
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed, width, height):
        super().__init__()
        self.original_image = transform.scale(image.load(player_image), (width, height))
        self.image = self.original_image.copy()
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update_r(self):
        keys = key.get_pressed()
        if keys[K_UP] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.y < win_height - self.rect.height - 5:
            self.rect.y += self.speed

    def update_l(self):
        keys = key.get_pressed()
        if keys[K_w] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[K_s] and self.rect.y < win_height - self.rect.height - 5:
            self.rect.y += self.speed

# --- Game Setup ---
back = (200, 255, 255)
win_width = 1000
win_height = 700
window = display.set_mode((win_width, win_height))
display.set_caption("Spinning Ball Pong")
window.fill(back)

game = True
finish = False
clock = time.Clock()
FPS = 60

# AI toggle
ai_enabled = True  # set to False for 2-player mode

# Sprites
racket1 = Player('Racket.png', 30, 300, 6, 50, 150)
racket2 = Player('Racket.png', win_width - 80, 300, 6, 50, 150)
ball = GameSprite('Tennis_Ball.png', 400, 300, 4, 50, 50)

# Fonts
font.init()
score_font = font.Font(None, 50)
end_font = font.Font(None, 70)

# Score
score1 = 0
score2 = 0

# Ball physics
speed_x = 5
speed_y = 5
spin = 0
angle = 0

# Power charge system
charge1 = 0
charge2 = 0
max_charge = 100

# --- Main Loop ---
while game:
    for e in event.get():
        if e.type == QUIT:
            game = False

    if not finish:
        window.fill(back)

        # --- INPUT & CHARGING ---
        keys = key.get_pressed()
        charging1 = keys[K_e]
        charging2 = keys[K_RSHIFT] if not ai_enabled else False  # AI doesn't press keys

        if charging1 and charge1 < max_charge:
            charge1 += 1
        elif not charging1 and charge1 < max_charge:
            charge1 = max(0, charge1 - 1)

        if charging2 and charge2 < max_charge:
            charge2 += 1
        elif not charging2 and charge2 < max_charge:
            charge2 = max(0, charge2 - 1)

        # --- MOVEMENT ---
        racket1.update_l()

        if ai_enabled:
            # AI logic: follow the ball
            if ball.rect.centery < racket2.rect.centery and racket2.rect.top > 0:
                racket2.rect.y -= racket2.speed
            elif ball.rect.centery > racket2.rect.centery and racket2.rect.bottom < win_height:
                racket2.rect.y += racket2.speed
        else:
            racket2.update_r()

        # --- Ball logic ---
        if ball.rect.top < 0:
            ball.rect.top = 0
            speed_y *= -1
            spin *= -1
        if ball.rect.bottom > win_height:
            ball.rect.bottom = win_height
            speed_y *= -1
            spin *= -1

        # Move ball
        ball.rect.x += speed_x
        ball.rect.y += speed_y + int(spin)

        # Spin animation
        angle += spin
        ball.image = transform.rotate(ball.original_image, angle)
        ball.rect = ball.image.get_rect(center=ball.rect.center)

        # Paddle collisions
        if sprite.collide_rect(racket1, ball):
            speed_x = abs(speed_x)
            ball.rect.left = racket1.rect.right
            offset = (ball.rect.centery - racket1.rect.centery) // 10
            spin = offset * 2
            speed_y += offset // 2
            if charge1 >= max_charge:
                speed_x += 4
                speed_y += offset
                spin *= 2
                charge1 = 0

        if sprite.collide_rect(racket2, ball):
            speed_x = -abs(speed_x)
            ball.rect.right = racket2.rect.left
            offset = (ball.rect.centery - racket2.rect.centery) // 10
            spin = offset * 2
            speed_y += offset // 2
            if charge2 >= max_charge:
                speed_x -= 4
                speed_y += offset
                spin *= 2
                charge2 = 0

        # Scoring
        if ball.rect.left <= 0:
            score2 += 1
            finish = True
            winner_text = end_font.render("Player 2 Scores!", True, (180, 0, 0))
            window.blit(winner_text, (win_width // 2 - 200, win_height // 2))

        if ball.rect.right >= win_width:
            score1 += 1
            finish = True
            winner_text = end_font.render("Player 1 Scores!", True, (180, 0, 0))
            window.blit(winner_text, (win_width // 2 - 200, win_height // 2))

        # Spin decay
        spin *= 0.97

        # Limit ball speed
        speed_x = max(min(speed_x, 12), -12)
        speed_y = max(min(speed_y, 12), -12)

        # --- DRAW ---
        racket1.reset()
        racket2.reset()
        ball.reset()

        # Score display
        score_display = score_font.render(f"{score1} : {score2}", True, (0, 0, 0))
        window.blit(score_display, (win_width // 2 - 40, 20))

        # Charge bars
        draw.rect(window, (0, 0, 0), (30, 30, 100, 10), 2)
        draw.rect(window, (0, 200, 0), (30, 30, charge1, 10))

        draw.rect(window, (0, 0, 0), (win_width - 130, 30, 100, 10), 2)
        draw.rect(window, (0, 200, 0), (win_width - 130, 30, charge2, 10))

    else:
        if key.get_pressed()[K_SPACE]:
            finish = False
            ball.rect.center = (win_width // 2, win_height // 2)
            speed_x = 5 if score1 <= score2 else -5
            speed_y = 5
            spin = 0
            charge1 = 0
            charge2 = 0

    display.update()
    clock.tick(FPS)
