"""Minimal reusable UI widgets (buttons) for the sidebar panel."""
import pygame

from config import Colors


class Button:
    def __init__(self, rect, label, callback, font, active_check=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.callback = callback
        self.font = font
        self.active_check = active_check  # optional fn -> bool, highlights when True
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False

    def draw(self, surface):
        active = self.active_check() if self.active_check else False
        if active:
            color = Colors.ACCENT
        elif self.hovered:
            color = Colors.BUTTON_HOVER
        else:
            color = Colors.BUTTON
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, Colors.PANEL_BORDER, self.rect, width=1, border_radius=6)
        text_color = Colors.BACKGROUND if active else Colors.TEXT
        text = self.font.render(self.label, True, text_color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
