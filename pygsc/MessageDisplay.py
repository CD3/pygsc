import os
import select
import threading
import logging


try:
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
    import pygame

    have_pygame = True
except:
    have_pygame = False

logger = logging.getLogger(__name__)


class PygameMessageDisplay:
    """
    A class for displaying messages to the screen using PyGame.
    """

    def __init__(self, width=800, height=20, font_name="courier", font_size=20):
        self.text_font_name = font_name
        self.text_font_size = font_size
        self.text_color = (200, 200, 200)
        self.win_width = width
        self.win_height = height
        self.win_color = (0, 0, 0)
        self.text = ""

        # the text will be rendered in its own thread and we need a way
        # to communicate with it. so we will use a pipe with a "read"
        # side and a "write" side. when we want to update the message,
        # we just write to the write side. the render thread will monitor
        # the read side and update when it recieves data.
        self.running = False
        self.exit = False
        self.piper, self.pipew = os.pipe()
        self.screen = None

        self.display_thread = threading.Thread(target=self.run)

    def shutdown(self):
        self.exit = True
        self.display_thread.join()
        pygame.quit()

    def start(self):
        logger.info("Initializing pygame")
        pygame.font.init()
        pygame.display.init()
        logger.info("Starting display thread")
        self.display_thread.start()

    def __display_text(self):
        text = self.text
        self.screen.fill(self.win_color)
        line_num = 1
        for line in text.split("\n"):
            rendered_line = self.text_font.render(line, True, self.text_color)
            pos = (
                (self.screen.get_width() - rendered_line.get_width()) / 2,
                line_num*rendered_line.get_height(),
            )
            line_num += 1
            self.screen.blit(rendered_line, pos)
        pygame.display.flip()

    def run(self):
        self.running = True
        self.text_font = pygame.font.SysFont(self.text_font_name, self.text_font_size)
        self.screen = pygame.display.set_mode(
            (self.win_width, self.win_height), pygame.SHOWN | pygame.RESIZABLE
        )
        self.__display_text()

        while not self.exit:
            for e in pygame.event.get():
                if e.type == pygame.WINDOWRESIZED:
                    self.win_width = e.x
                    self.win_height = e.y
                    self.screen = pygame.display.set_mode(
                        (self.win_width, self.win_height),
                        pygame.SHOWN | pygame.RESIZABLE,
                    )
                    self.__display_text()

            ifds, ofds, efds = select.select([self.piper], [], [], 0.1)
            if len(ifds) > 0:
                self.text = os.read(ifds[0], 2048).decode()
                self.__display_text()

    def set_message(self, text):
        os.write(self.pipew, text.encode())

    def is_running(self):
        return self.running


class DummyMessageDisplay:
    """
    A message display class that can be used by a caller but does nothing.
    That way, the caller does not need to know if the backend we need to display
    a message is available/working correctly.
    """

    def __init__(self, width=800, height=200, font_name="courier", font_size=20):
        pass

    def start(self):
        pass

    def shutdown(self):
        pass

    def set_message(self, text):
        pass

    def is_running(self):
        return True


if have_pygame:
    MessageDisplay = PygameMessageDisplay
else:
    MessageDisplay = None
