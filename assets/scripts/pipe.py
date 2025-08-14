import pygame as pg
import random

pg.mixer.init()

class Pipes:
	def __init__(self, game, bird_instance) -> None:
		self.screen_width: int = game.screen_width
		self.screen_height: int = game.screen_height
		self.bird_instance = bird_instance

		self.pipes: list[Pipe] = []
		self.pipe_width: int = 104
		self.gap: int = 200
		self.speed: int = 5

		self.max_timer: int = 200
		self.min_timer: int = 120

		self.timer: float = self.max_timer
		self.remove_all_pipes: bool = True

		self.decrement_factor: float = 0.3
		self.decrement_value: float = 0.1

	def update(self, screen: pg.Surface, volume: int) -> None:
		if self.bird_instance.menu in {"main", "play", "death"}:
			self.timed_spawn()
			self.remove_offscreen_pipes()

			if self.bird_instance.menu == "main":
				self.reset_timer()

			for pipe in self.pipes:
				if self.bird_instance.menu == "play":
					pipe.move()
					pipe.increase_score()
				pipe.update(screen, volume)

		else:
			self.remove_pipes()

	def remove_pipes(self) -> None:
		self.pipes = []

	def spawn_pipe(self) -> None:
		min_y: int = 50
		max_y: int = self.screen_height - 300
  
		y: int = random.randint(min_y, max_y)
  
		pipe: Pipe = Pipe(self.screen_width, self.screen_height, y, self.pipe_width, self.gap, self.bird_instance.vel_x, self.bird_instance)
		self.pipes.append(pipe)

	def remove_offscreen_pipes(self) -> None:
		self.pipes = [pipe for pipe in self.pipes if pipe.x > -self.pipe_width]

	def reset_timer(self) -> None:
		self.max_timer = 200
		self.timer = self.max_timer
		self.remove_all_pipes = True

	def timed_spawn(self) -> None:
		if self.bird_instance.menu == "play":
			self.remove_all_pipes = True
			if self.timer <= 0:
				self.spawn_pipe()
				self.timer = self.max_timer
				self.max_timer = max(self.min_timer, self.max_timer - 2.5)

			else:
				self.timer -= self.decrement_value + self.bird_instance.vel_x * self.decrement_factor

		elif self.bird_instance.menu == "main":
			if self.remove_all_pipes:
				self.remove_pipes()
				self.remove_all_pipes = False

class Pipe:
	def __init__(self, screen_width: int, screen_height: int, y: int, pipe_width: int, gap: int, speed: int, bird_instance) -> None:
		self.x: int = screen_width
		self.y: int = y
		self.pipe_width: int = pipe_width
		self.gap: int = gap
		self.speed: int = speed
		self.screen_height: int = screen_height

		self.bird_instance = bird_instance
		self.pipe_image: pg.Surface = self.load_pipe_image()
		self.point_sound: pg.mixer.Sound = pg.mixer.Sound("assets/sounds/player/sfx_point.wav")
		self.score_increment: bool = True

		self.update_pipe_rects()

	def load_pipe_image(self) -> pg.Surface:
		if self.bird_instance.skin_selected == "plane":
			return pg.image.load("assets/sprites/obstacle/building.png").convert_alpha()

		else:
			return pg.image.load("assets/sprites/obstacle/pipe.png").convert_alpha()

	def update_pipe_rects(self) -> None:
		self.upper_pipe_rect: pg.Rect = pg.Rect(self.x, 0, self.pipe_width, self.y)
		self.lower_pipe_rect: pg.Rect = pg.Rect(self.x, self.y + self.gap, self.pipe_width, self.screen_height - self.y - self.gap)

		self.upper_pipe_image: pg.Surface = self.pipe_image.subsurface((0, 0, self.pipe_width, self.y))
		self.lower_pipe_image: pg.Surface = self.pipe_image.subsurface((0, 0, self.pipe_width, self.screen_height - self.y - self.gap))

	def render(self, screen: pg.Surface) -> None:
		flipped_upper_pipe_image: pg.Surface = pg.transform.flip(self.upper_pipe_image, False, True)
		screen.blit(flipped_upper_pipe_image, (self.x, 0))
		screen.blit(self.lower_pipe_image, (self.x, self.y + self.gap))

		# pipe hitboxes
		# pg.draw.rect(screen, (255, 0, 0), self.upper_pipe_rect, 2)
		# pg.draw.rect(screen, (255, 0, 0), self.lower_pipe_rect, 2)

	def update(self, screen: pg.Surface, volume: int) -> None:
		self.render(screen)
		self.volume(volume)
		self.increase_score()

	def move(self) -> None:
		self.x -= self.speed
		self.update_pipe_rects()

	def volume(self, volume: int) -> None:
		self.point_sound.set_volume(volume)

	def increase_score(self) -> None:
		if self.x <= self.bird_instance.x and self.score_increment:
			self.bird_instance.score += 1
			self.point_sound.play()
			self.score_increment = False
