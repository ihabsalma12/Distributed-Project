import pygame

pygame.init()


class ChatBubble:
    def __init__(self, screen, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.screen = screen

    def draw(self):
        pygame.draw.rect(self.screen, (255,255,255), self.rect, border_radius=5)
        font = pygame.font.Font(None, 22)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        pass


class Button:
    def __init__(self, screen, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.screen = screen

    def draw(self):
        pygame.draw.rect(self.screen, (200, 200, 200), self.rect)
        font = pygame.font.Font(None, 32)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.callback()

class TextBox:
    def __init__(self, screen, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.screen = screen

    def draw(self):
        pygame.draw.rect(self.screen, (255, 255, 255), self.rect, 2)
        font = pygame.font.Font(None, 32)
        text_surface = font.render(self.text, True, (0, 0, 0))
        self.screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
                print('self.text:', self.text)