import pygame

class FontManager:
    _cache = {}

    @staticmethod
    def get(size: int, bold=True, name="futura"):
        key = (name, size, bold)
        if key not in FontManager._cache:
            FontManager._cache[key] = pygame.font.SysFont(name, size, bold)
        return FontManager._cache[key]