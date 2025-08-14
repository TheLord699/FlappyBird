import pygame as pg

from bird import Bird

class Background:
	def __init__(self, game, bird_instance: Bird) -> None:
		self.screen_width: int = game.screen_width
		self.screen_height: int = game.screen_height

		self.bird_instance: Bird = bird_instance

		self.ground_image: pg.Surface = pg.image.load(f"assets/sprites/obstacle/ground_{self.bird_instance.mode}.png").convert()
		self.ground_width: int = self.ground_image.get_width()

		self.ground_x1: int = 0
		self.ground_x2: int = self.ground_x1 + self.ground_width
		self.ground_y: int = self.screen_height - 28

	def ground_move(self) -> None:
		if not self.bird_instance.dead:
			self.ground_x1 -= self.bird_instance.vel_x
			self.ground_x2 -= self.bird_instance.vel_x

			if self.ground_x1 <= -self.ground_width:
				self.ground_x1 = self.ground_x2 + self.ground_width

			if self.ground_x2 <= -self.ground_width:
				self.ground_x2 = self.ground_x1 + self.ground_width

	def update(self, screen: pg.Surface) -> None:
		if self.bird_instance.menu in {"main", "play", "death"}:
			self.ground_move()
		self.render(screen)

	def render(self, screen: pg.Surface) -> None:
		self.ground_image = pg.image.load(f"assets/sprites/obstacle/ground_{self.bird_instance.mode}.png").convert()
		screen.blit(self.ground_image, (self.ground_x1, self.ground_y))
		screen.blit(self.ground_image, (self.ground_x2, self.ground_y))
