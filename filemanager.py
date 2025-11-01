import pygame
from pathlib import Path
from typing import Optional

pygame.init()


class PygameFileManager:
    _instance = None

    @staticmethod
    def get_instance():
        if PygameFileManager._instance is None:
            PygameFileManager._instance = PygameFileManager()
        return PygameFileManager._instance

    def __init__(self):
        if PygameFileManager._instance is not None:
            raise Exception("Singleton already exists")

        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Select a file")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 25)
        self.small_font = pygame.font.SysFont("consolas", 18)

        self.running = True
        self.selected_file: Optional[Path] = None
        self.current_path = Path.cwd()
        self.items: list[Path] = []
        self.ITEM_HEIGHT = 30

    def list_dir(self):
        self.items = []
        if self.current_path.parent != self.current_path:
            self.items.append(self.current_path.parent)

        self.items += sorted(
            [
                p
                for p in self.current_path.iterdir()
                if not p.name.startswith(".")
                and (p.is_dir() or p.suffix.lower() == ".json")
            ]
        )

    def draw(self):
        self.screen.fill((30, 30, 30))

        path_text = self.small_font.render(
            str(self.current_path), True, (200, 200, 200)
        )
        self.screen.blit(path_text, (10, 10))

        start_y = 40
        mx, my = pygame.mouse.get_pos()
        for i, item in enumerate(self.items):
            y = start_y + i * self.ITEM_HEIGHT
            if y < 40 or y > self.HEIGHT - self.ITEM_HEIGHT:
                continue

            rect = pygame.Rect(10, y, self.WIDTH - 20, self.ITEM_HEIGHT)
            if rect.collidepoint(mx, my):
                pygame.draw.rect(self.screen, (50, 50, 80), rect)

            if i == 0 and self.current_path.parent != self.current_path:
                text_str = "[← BACK]"
                color = (255, 180, 180)
            else:
                color = (180, 180, 255) if item.is_dir() else (200, 200, 200)
                prefix = "[DIR] " if item.is_dir() else "[FILE] "
                text_str = prefix + item.name

            text = self.font.render(text_str, True, color)
            self.screen.blit(text, (15, y))

        pygame.display.flip()

    def run(self) -> Optional[Path]:
        self.list_dir()
        while self.running:
            self.clock.tick(60)
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    _, my = event.pos
                    index = (my - 40) // self.ITEM_HEIGHT
                    if 0 <= index < len(self.items):
                        clicked = self.items[index]

                        if index == 0 and self.current_path.parent != self.current_path:
                            self.current_path = clicked
                            self.list_dir()
                        elif clicked.is_dir():
                            self.current_path = clicked
                            self.list_dir()
                        else:
                            self.selected_file = clicked
                            self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

        pygame.display.quit()
        return self.selected_file


if __name__ == "__main__":
    file_manager = PygameFileManager.get_instance()
    file_path = file_manager.run()
    if file_path:
        print("Selected file:", file_path)
    else:
        print("No file selected")
