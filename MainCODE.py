from pygame import *
from random import randint

# --- Setup ---
back = (200, 255, 255)
win_width = 1000
win_height = 700
window = display.set_mode((win_width, win_height))
display.set_caption("Table Tennis V.5")
clock = time.Clock()
FPS = 60

# --- Fonts ---
font.init()
score_font = font.Font(None, 50)
menu_font = font.Font(None, 60)
end_font = font.Font(None, 70)

# --- Classes ---
class GameSprite(sprite.Sprite):
    def __init__(self, img, x, y, speed, width, height):
        super().__init__()
        self.original_image = transform.scale(image.load(img), (width, height))
        self.image = self.original_image.copy()
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

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

# --- Sprites ---
racket1 = Player('Racket.png', 30, 300, 6, 50, 150)
racket2 = Player('Racket.png', win_width - 80, 300, 6, 50, 150)
ball = GameSprite('Tennis4K.png', 400, 300, 4, 50, 50)

# --- Game Variables ---
score1 = 0
score2 = 0
speed_x = 5
speed_y = 5
spin = 0.0
angle = 0
trail = []
trail_length = 15
trail_color = (255, 165, 0)  # 🟠 Default Orange

charge1 = 0
charge2 = 0
curve_charge1 = 0
max_charge = 100

power_cooldown1 = 0
power_cooldown2 = 0
curve_cooldown1 = 0
cooldown_max = 120  # 2 seconds cooldown

ai_enabled = None
game_running = False
paused = False
finish = False
in_menu = True

# --- Main Loop ---
while True:
    for e in event.get():
        if e.type == QUIT:
            quit()
        if in_menu:
            if e.type == KEYDOWN:
                if e.key == K_1:
                    ai_enabled = True
                    in_menu = False
                    game_running = True
                elif e.key == K_2:
                    ai_enabled = False
                    in_menu = False
                    game_running = True
        elif e.type == KEYDOWN and game_running:
            if e.key == K_ESCAPE:
                paused = not paused
            elif paused:
                if e.key == K_r:
                    finish = False
                    paused = False
                    ball.rect.center = (win_width // 2, win_height // 2)
                    speed_x = 5 if score1 <= score2 else -5
                    speed_y = 5
                    spin = 0
                    charge1 = 0
                    charge2 = 0
                    curve_charge1 = 0
                    power_cooldown1 = 0
                    power_cooldown2 = 0
                    curve_cooldown1 = 0
                    trail.clear()
                    trail_color = (255, 165, 0)
                elif e.key == K_q:
                    paused = False
                    in_menu = True
                    game_running = False
                    finish = False
                    score1 = 0
                    score2 = 0
                    ball.rect.center = (win_width // 2, win_height // 2)
                    trail.clear()
                    trail_color = (255, 165, 0)

    if in_menu:
        window.fill((50, 50, 80))
        window.blit(menu_font.render("Choose Game Mode", True, (255, 255, 255)), (win_width//2 - 200, 200))
        window.blit(score_font.render("1 - Play vs AI", True, (200, 200, 200)), (win_width//2 - 150, 300))
        window.blit(score_font.render("2 - 2 Player Mode", True, (200, 200, 200)), (win_width//2 - 150, 360))
        display.update()
        clock.tick(FPS)
        continue

    if paused:
        window.blit(end_font.render("Paused", True, (0, 0, 0)), (win_width//2 - 100, win_height//2 - 80))
        window.blit(score_font.render("Press ESC to Resume", True, (0, 0, 0)), (win_width//2 - 150, win_height//2 - 20))
        window.blit(score_font.render("Press R to Restart", True, (0, 0, 0)), (win_width//2 - 150, win_height//2 + 30))
        window.blit(score_font.render("Press Q to Quit to Menu", True, (0, 0, 0)), (win_width//2 - 150, win_height//2 + 80))
        display.update()
        clock.tick(FPS)
        continue

    if game_running and not finish:
        window.fill(back)

        keys = key.get_pressed()
        charging1 = keys[K_e] and power_cooldown1 == 0
        charging2 = keys[K_RSHIFT] and power_cooldown2 == 0 if not ai_enabled else False
        charging_curve1 = keys[K_d] and curve_cooldown1 == 0

        if charging1 and charge1 < max_charge:
            charge1 += 1
        if charging2 and charge2 < max_charge:
            charge2 += 1
        if charging_curve1 and curve_charge1 < max_charge:
            curve_charge1 += 1

        racket1.update_l()
        if ai_enabled:
            if ball.rect.centery < racket2.rect.centery and racket2.rect.top > 0:
                racket2.rect.y -= racket2.speed
            elif ball.rect.centery > racket2.rect.centery and racket2.rect.bottom < win_height:
                racket2.rect.y += racket2.speed
        else:
            racket2.update_r()

        ball.rect.x += speed_x + int(spin * 0.2)
        ball.rect.y += speed_y + int(spin * 0.8)
        trail.append((ball.rect.centerx, ball.rect.centery))
        if len(trail) > trail_length:
            trail.pop(0)

        angle += spin * 1.5
        ball.image = transform.rotate(ball.original_image, angle)
        ball.rect = ball.image.get_rect(center=ball.rect.center)

        if ball.rect.top < 0:
            ball.rect.top = 0
            speed_y *= -1
            spin *= -1
        if ball.rect.bottom > win_height:
            ball.rect.bottom = win_height
            speed_y *= -1
            spin *= -1

        if sprite.collide_rect(racket1, ball):
            speed_x = abs(speed_x)
            ball.rect.left = racket1.rect.right
            offset = (ball.rect.centery - racket1.rect.centery) // 10
            spin = offset * 3.5
            speed_y += offset // 2

            if charge1 >= max_charge and power_cooldown1 == 0:
                speed_x += 4
                speed_y += offset
                spin *= 2.5
                charge1 = 0
                power_cooldown1 = cooldown_max
                trail_color = (255, 0, 0)  # 🔴 Power Shot
            elif curve_charge1 >= max_charge and curve_cooldown1 == 0:
                spin = 12.0 if offset >= 0 else -12.0
                speed_x += 3
                speed_y += 2 if spin > 0 else -2
                curve_charge1 = 0
                curve_cooldown1 = cooldown_max
                trail_color = (0, 0, 255)  # 🔵 Curve Shot
            else:
                trail_color = (255, 165, 0)  # 🟠 Normal

        if sprite.collide_rect(racket2, ball):
            speed_x = -abs(speed_x)
            ball.rect.right = racket2.rect.left
            offset = (ball.rect.centery - racket2.rect.centery) // 10
            spin = offset * 3.5
            speed_y += offset // 2
            if charge2 >= max_charge and power_cooldown2 == 0:
                speed_x -= 4
                speed_y += offset
                spin *= 2.5
                charge2 = 0
                power_cooldown2 = cooldown_max
                trail_color = (255, 0, 0)  # 🔴 Power Shot
            else:
                trail_color = (255, 165, 0)  # 🟠 Normal

        if ball.rect.left <= 0:
            score2 += 1
            finish = True
            window.blit(end_font.render("Player 2 Scores!", True, (180, 0, 0)), (win_width // 2 - 200, win_height // 2))
        if ball.rect.right >= win_width:
            score1 += 1
            finish = True
            window.blit(end_font.render("Player 1 Scores!", True, (180, 0, 0)), (win_width // 2 - 200, win_height // 2))

        spin *= 0.985
        speed_x = max(min(speed_x, 12), -12)
        speed_y = max(min(speed_y, 12), -12)

        for i, pos in enumerate(trail):
            alpha = int(255 * (i + 1) / trail_length)
            trail_surf = Surface((ball.rect.width, ball.rect.height), SRCALPHA)
            draw.circle(trail_surf, (*trail_color, alpha), (ball.rect.width // 2, ball.rect.height // 2), ball.rect.width // 2)
            window.blit(trail_surf, (pos[0] - ball.rect.width // 2, pos[1] - ball.rect.height // 2))

        racket1.reset()
        racket2.reset()
        ball.reset()

        window.blit(score_font.render(f"{score1} : {score2}", True, (0, 0, 0)), (win_width // 2 - 40, 20))

        # UI Bars
        draw.rect(window, (0, 0, 0), (30, 30, 100, 10), 2)
        draw.rect(window, (0, 200, 0), (30, 30, charge1, 10))
        draw.rect(window, (0, 0, 0), (30, 50, 100, 10), 2)
        draw.rect(window, (0, 0, 200), (30, 50, curve_charge1, 10))
        draw.rect(window, (0, 0, 0), (30, 70, 100, 10), 2)
        draw.rect(window, (100, 100, 100), (30, 70, 100 - power_cooldown1 * 100 // cooldown_max, 10))

        draw.rect(window, (0, 0, 0), (win_width - 130, 30, 100, 10), 2)
        draw.rect(window, (0, 200, 0), (win_width - 130, 30, charge2, 10))
        draw.rect(window, (0, 0, 0), (win_width - 130, 50, 100, 10), 2)
        draw.rect(window, (100, 100, 100), (win_width - 130, 50, 100 - power_cooldown2 * 100 // cooldown_max, 10))

        if charge1 >= max_charge and power_cooldown1 == 0:
            window.blit(score_font.render("Power Ready", True, (0, 200, 0)), (140, 10))
        if curve_charge1 >= max_charge and curve_cooldown1 == 0:
            window.blit(score_font.render("Curve Ready", True, (0, 0, 200)), (140, 40))

        # Cooldown ticking
        if power_cooldown1 > 0:
            power_cooldown1 -= 1
        if power_cooldown2 > 0:
            power_cooldown2 -= 1
        if curve_cooldown1 > 0:
            curve_cooldown1 -= 1

    elif finish and key.get_pressed()[K_SPACE]:
        finish = False
        ball.rect.center = (win_width // 2, win_height // 2)
        speed_x = 5 if score1 <= score2 else -5
        speed_y = 5
        spin = 0
        charge1 = 0
        charge2 = 0
        curve_charge1 = 0
        trail.clear()
        power_cooldown1 = 0
        power_cooldown2 = 0
        curve_cooldown1 = 0
        trail_color = (255, 165, 0)

    display.update()
    clock.tick(FPS)
