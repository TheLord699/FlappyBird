import pygame as pg
import random
import os
import time

from cryptography.fernet import Fernet
from pathlib import Path

pg.mixer.init()

class Bird:
	def __init__(self, game: 'Game', ui: 'Ui') -> None: # type: ignore
			self.screen_width: int = game.screen_width
			self.screen_height: int = game.screen_height
			self.ui: 'Ui' = ui # type: ignore

			self.x: int = 50
			self.y: int = 250

			self.vel_y: float = 0
			self.vel_x: float = 4  # 60: 5, 90: 4

			self.gravity: float = 0.3  # 60: 0.5, 90: 0.3
			self.jump_strength: float = -7.5  # 60: -10, 90: -7.5

			self.angle: float = 0
			self.angle_velocity: float = 0
			self.max_angle: float = 30  # 30
			self.min_angle: float = -30  # -30
			self.angle_acceleration: float = 2  # 2

			self.bird_width: int = 50
			self.bird_height: int = 50

			self.bird_image: pg.Surface | None = None

			self.flap_sound: pg.mixer.Sound = pg.mixer.Sound("assets/sounds/player/sfx_flap.wav")
			self.death_sound: pg.mixer.Sound = pg.mixer.Sound("assets/sounds/player/sfx_die.wav")
			self.hit_sound: pg.mixer.Sound = pg.mixer.Sound("assets/sounds/player/sfx_hit.wav")

			self.bird_rect: pg.Rect = pg.Rect(self.x, self.y, self.bird_width, self.bird_height)

			self.frame: float = 1
			self.frame_speed: float = 0.25
			self.direction: float = 0

			self.distance: int = 0

			self.high_score: int = 0
			self.score: int = 0

			self.error_timer: int = 250  # 60: 200, 90: 250

			self.dead: bool = False
			self.floored: bool = False
			self.death_sound_played: bool = False

			self.decryption_error: bool = False

			self.achievements: list[str] = []

			self.stationary: list[str] = ["mario", "kirby"]

			self.mode: str = "normal"

			self.skin_selected: str = "yellow"

			self.key_file: str = "assets/data/encryption_key.key"

			self.menu: str = "main"

			try:
				with open(self.key_file, "rb") as file:
					self.key: bytes = file.read()

			except FileNotFoundError:
				self.key = Fernet.generate_key()
				with open(self.key_file, "wb") as file:
					file.write(self.key)

			self.cipher_suite: Fernet = Fernet(self.key)
   
			self.file_check()

			self.load_score()

			self.frames_count: int = self.get_frames_count(self.skin_selected)

	def file_check(self) -> None:
		with open("assets/sprites/player/data_stationary.txt", "r") as file:
			folders_in_data: list[str] = file.readlines()
			self.skins_stationary: list[str] = [folder.strip() for folder in folders_in_data] + self.stationary

		self.skins: list[str] = []
		for folder in Path("assets/sprites/player").iterdir():
			if folder.is_dir():
				files_in_folder: list[str] = os.listdir(folder)
				if any(file.endswith('.png') for file in files_in_folder):
					self.skins.append(folder.name)

	def get_frames_count(self, skin_selected: str) -> int:
		directory_path: Path = Path(f"assets/sprites/player/{skin_selected}")
		folder_length: int = len([item for item in directory_path.iterdir() if item.is_file()])
  
		return folder_length

	def handle_mode(self) -> None:
		match self.mode:
			case "normal":
				self.vel_x = 4

			case "impossible":
				self.vel_x = 10

			case "crazy":
				self.vel_x = 2
				self.vel_y = 20

	def update(self, screen: pg.Surface, events: list[pg.event.Event], pipes: 'Pipes', volume: float) -> None: # type: ignore
		self.bird_rect.topleft = (self.x + 15, self.y + 10)
		#pg.draw.rect(screen, (255, 0, 0), self.bird_rect, 2)

		if self.decryption_error:
			self.error_timer -= 1
			if self.error_timer < 1:
				self.decryption_error = False

		if self.score > self.high_score:
			self.high_score = self.score
			self.save_score()

		if self.menu == "main":
			self.idle_play()

		if self.menu in {"main", "death", "play"}:
			if not self.dead:
				self.animate()
				self.check_collision(pipes)
				self.death_sound_played = False

			self.update_angle()
			self.update_position()
			#self.handle_mode()
			self.handle_events(events)
			self.render(screen)
			self.append_achievements()
			self.set_volume(volume)
			self.file_check()
   
	def render(self, screen: pg.Surface) -> None:
		try:
			if self.get_frames_count(self.skin_selected) > 1:
				self.bird_image = pg.image.load(f"assets/sprites/player/{self.skin_selected}/{self.skin_selected}{int(self.frame)}.png").convert_alpha()

			else:
				self.bird_image = pg.image.load(f"assets/sprites/player/{self.skin_selected}/{self.skin_selected}.png").convert_alpha()

			self.bird_mask = pg.mask.from_surface(self.bird_image)

			if not self.angle == 0: # Allows for an anti-aliasing effect when the image is rotating, and stops when its not(basically makes jagged edges less obvious).
				rotated_bird = pg.transform.rotozoom(self.bird_image, self.angle, 1)

			else:
				rotated_bird =	pg.transform.rotate(self.bird_image, self.angle)

			rotated_rect = rotated_bird.get_rect(center=(int(self.x + 40), int(self.y + 35)))

			screen.blit(rotated_bird, rotated_rect.topleft)

		except Exception as e:
			if self.skins:
				print("Error: frame error")
				self.skin_selected = random.choice(self.skins)
				self.frame = 1
				self.frames_count = self.get_frames_count(self.skin_selected)
				self.render(screen)
				return

	def animate(self) -> None:
		if self.frame >= self.frames_count + 0.9:
			self.direction = -self.frame_speed  # 60: -0.35, 90: -0.25

		elif self.frame <= 1:
			self.direction = self.frame_speed  # 60 :0.35, 90: 0.25

		self.frame += self.direction
		self.frame = (self.frame - 1) % self.frames_count + 1

	def restart(self) -> None:
		self.y = 250

		self.restart_timer: int = 100
		self.idle_timer: int = 25  # 60: 20, 90: 25

		self.vel_y = 0

		self.distance = 0

		self.angle = 0
		
		self.score = 0

		self.dead = False
		self.menu = "main"

	def set_volume(self, volume: float) -> None:
		self.flap_sound.set_volume(volume)
		self.death_sound.set_volume(volume)
		self.hit_sound.set_volume(volume)
  
	def handle_events(self, events: list[pg.event.Event]) -> None:
		for event in events:
			if event.type == pg.MOUSEBUTTONDOWN:
				if event.button == 1:
					if self.menu == "main" and not self.ui.volume_button_rect.collidepoint(event.pos):
						self.menu = "play"
						self.flap()

					elif self.menu == "play":
						self.flap()

			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_SPACE:
					if self.menu in {"main", "play"}:
						self.menu = "play"
						self.flap()

				elif self.menu == "main":
					if event.key == pg.K_c:
						self.menu = "creator"

					if event.key == pg.K_x:
						self.menu = "delete"

					if event.key == pg.K_LEFT:
						current_index: int = self.skins.index(self.skin_selected)
						new_index: int = (current_index - 1) % len(self.skins)
						self.skin_selected = self.skins[new_index]
						self.frames_count = self.get_frames_count(self.skin_selected)
						self.frame = 1

					elif event.key == pg.K_RIGHT:
						current_index = self.skins.index(self.skin_selected)
						new_index = (current_index + 1) % len(self.skins)
						self.skin_selected = self.skins[new_index]
						self.frames_count = self.get_frames_count(self.skin_selected)
						self.frame = 1

	def flap(self) -> None:
		self.vel_y = self.jump_strength
		self.flap_sound.play()

	def update_position(self) -> None:
		self.y += self.vel_y
		self.vel_y += self.gravity

		if not self.dead:
			self.distance += self.vel_x

		if self.dead and self.vel_y > 7 and not self.death_sound_played and not self.y >= 500:
			self.death_sound.play()
			self.death_sound_played = True

		if self.y >= 510 or self.y < 0:
			self.y = min(self.y, 510)

		if self.y < -35:
			self.y = -35
			self.vel_y = 0

	def update_angle(self) -> None:
		if self.skin_selected in self.skins_stationary:
			self.angle = 0

		else:
			if self.vel_y < 0 and self.angle < self.max_angle:
				self.angle = self.max_angle

			elif self.vel_y >= 0 and self.angle > self.min_angle:
				self.angle -= self.angle_acceleration

	def check_collision(self, pipes: 'Pipes') -> None: # type: ignore
		for pipe in pipes.pipes:
			upper_pipe_rect: pg.Rect = pg.Rect(pipe.x, 0, pipe.pipe_width, pipe.y)
			lower_pipe_rect: pg.Rect = pg.Rect(pipe.x, pipe.y + pipe.gap, pipe.pipe_width, pipe.screen_height - pipe.y - pipe.gap)

			if self.bird_rect.colliderect(upper_pipe_rect) or self.bird_rect.colliderect(lower_pipe_rect):
				self.death()

		if self.y >= 510:
			self.death()

	def save_score(self, filename: str = "assets/data/high_score.txt") -> None:
		encrypted_score: bytes = self.cipher_suite.encrypt(str(self.high_score).encode())
		with open(filename, "wb") as file:
			file.write(encrypted_score)

#this is shit, do it somewhere else!!!!
	def load_score(self, filename: str = "assets/data/high_score.txt") -> None:
		try:
			with open(filename, "rb") as file:
				encrypted_score: bytes = file.read()
				try:
					decrypted_score: str = self.cipher_suite.decrypt(encrypted_score).decode()
					self.high_score = int(decrypted_score)
					self.decryption_error = False

				except Exception:
					self.decryption_error = True
					self.save_score()

		except (FileNotFoundError, ValueError):
			self.high_score = 0
			self.save_score()

	def idle_play(self) -> None:
		if self.y >= 330:
			self.flap()

	def append_achievements(self) -> None:
		achievements = {
			10: "bronze",
			20: "silver",
			30: "gold",
			40: "platinum"
		}

		for score, achievement in sorted(achievements.items(), reverse=True):
			if self.high_score >= score and achievement not in self.achievements:
				self.achievements.append(achievement)

	def death(self) -> None:
		self.vel_y = 0
		self.dead = True
		self.menu = "death"
		self.hit_sound.play()
