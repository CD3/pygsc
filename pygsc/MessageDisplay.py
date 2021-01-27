import os
import select
import threading
import logging


try:
  os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
  import pygame
  have_pygame = True
except:
  have_pygame = False

logger = logging.getLogger(__name__)

class PygameMessageDisplay:
  def __init__(self,width=800,height=20,font_name="courier",font_size=20):
    self.text_font_name = font_name
    self.text_font_size = font_size
    self.text_color = (200,200,200)
    self.win_width = width
    self.win_height = height
    self.win_color = (0,0,0)



    self.running = False
    self.exit = False
    self.piper,self.pipew = os.pipe()
    self.screen = None

    self.display_thread = threading.Thread(target = self.run)



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



  def run(self):
    self.running = True
    self.text_font = pygame.font.SysFont(self.text_font_name,self.text_font_size)
    # self.screen = pygame.display.set_mode((self.win_width,self.win_height),pygame.NOFRAME)
    self.screen = pygame.display.set_mode((self.win_width,self.win_height))
    self.screen.fill(self.win_color)
    pygame.display.flip()
    self.set_message("")

    while not self.exit:
      ifds,ofds,efds = select.select([self.piper],[],[],1)
      if len(ifds) > 0:
        self.screen.fill(self.win_color)

        text = os.read(ifds[0],2048).decode()
        rendered_text = self.text_font.render(text,True,self.text_color)
        pos = ( (self.screen.get_width()- rendered_text.get_width())/2, rendered_text.get_height())

        self.screen.blit(rendered_text, pos )
        pygame.display.flip()

  def set_message(self,text):
    os.write(self.pipew,text.encode())

  def is_running(self):
    return self.running

class DummyMessageDisplay:
  def __init__(self,width=800,height=200,font_name="courier",font_size=20):
    pass

  def start(self):
    pass

  def shutdown(self):
    pass

  def set_message(self,text):
    pass

  def is_running(self):
    return True

if have_pygame:
  MessageDisplay = PygameMessageDisplay
else:
  MessageDisplay = None
