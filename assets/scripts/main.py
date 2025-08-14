#Gulp
import random
import pygame as pg
import logging

from background import Background
from bird import Bird
from pipe import Pipes
from ui import Ui
from creation import CharacterCreator

logging.basicConfig(level=logging.INFO, format='%(message)s')

class FlappyBirdGame:
	def __init__(self) -> None:
		pg.init()
  
		self.fps: int = 90 # default: 90
		self.version: str = "1.1.5"
  
		self.screen_width: int = 800 
		self.screen_height: int = 600
  
		icon: pg.Surface = pg.image.load("assets/sprites/player/yellow/yellow1.png")

		self.screen: pg.Surface = pg.display.set_mode((self.screen_width, self.screen_height), pg.DOUBLEBUF | pg.SCALED)

		pg.display.set_caption("FlappyBird " + self.version)
		pg.display.set_icon(icon)

		self.clock: pg.time.Clock = pg.time.Clock()
		self.font: pg.font.Font = pg.font.Font("assets/sprites/font/flappy_bird.ttf", 36) # size: 36
  
		self.time_of_day: tuple[str, str, str] = ("day", "night", "impossible")

		self.init_game_objects()
		self.init_background()
		self.run_game()

	def init_game_objects(self) -> None:
		self.ui: Ui = Ui(self, flappy_bird=None)
		self.flappy_bird: Bird = Bird(self, self.ui)
		self.ui.flappy_bird = self.flappy_bird
		self.pipes: Pipes = Pipes(self, self.flappy_bird)
		self.background: Background = Background(self, self.flappy_bird)
		self.creator: CharacterCreator = CharacterCreator(self.flappy_bird)

	def init_background(self) -> None:
		self.current_time: str = random.choice(self.time_of_day[:2])
		self.background_image: pg.Surface = pg.image.load(f"assets/sprites/background/{self.current_time}.png").convert()

		self.background_x: float = self.screen_width / 1000
		self.background_y: float = self.screen_height / -10

		self.background_selected: bool = False

	# Not lazy, background is stationary in flappy bird
	def update_background(self) -> None:
		if self.flappy_bird.menu == "death":
			self.background_selected = False

		else:
			if not self.background_selected:
				if self.flappy_bird.mode == "normal":
					self.current_time = random.choice(self.time_of_day[:2])

				elif self.flappy_bird.mode == "impossible":
					self.current_time = self.flappy_bird.mode

				self.background_image = pg.image.load(f"assets/sprites/background/{self.current_time}.png").convert()
				self.background_selected = True

		self.screen.blit(self.background_image, (self.background_x, self.background_y))

	def update(self) -> None:
		self.update_background()
		self.pipes.update(self.screen, self.volume)
		self.background.update(self.screen)
		self.flappy_bird.update(self.screen, self.events, self.pipes, self.volume)
		self.ui.update(self.screen, self.font, self.clock, self.events)
		self.creator.update()

	def handle_events(self) -> None:
		self.events: list[pg.event.Event] = pg.event.get()
		for event in self.events:
			if event.type == pg.QUIT:
				self.running = False
	
			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					self.running = False
	 
				if event.key == pg.K_o:
					self.flappy_bird.menu = "death"
    
				if event.key == pg.K_p:
					self.flappy_bird.restart()

	def run_game(self) -> None:
		self.running: bool = True
		while self.running:
			self.handle_events()
			self.volume: int = 1 if self.ui.volume_on else 0
			self.update()

			pg.display.flip()
			self.clock.tick(self.fps)

		print("Thanks for playing!")
		pg.quit()

if __name__ == "__main__":
	FlappyBirdGame()