import pygame as pg

from bird import Bird

class Ui:
	def __init__(self, game, flappy_bird: Bird) -> None:
		self.screen_width: int = game.screen_width
		self.screen_height: int = game.screen_height
  
		self.flappy_bird: Bird = flappy_bird
  
		self.width: int = 0
		self.height: int = 0
  
		self.start_image: pg.Surface | None = None
		self.frame: float = 1.0
		
		self.restart_image: pg.Surface = pg.image.load("assets/sprites/ui/restart_button.png").convert_alpha()
		self.volume_on_image: pg.Surface = pg.image.load("assets/sprites/ui/volume_on.png").convert_alpha()
		self.volume_off_image: pg.Surface = pg.image.load("assets/sprites/ui/volume_off.png").convert_alpha()
  
		self.badge_images: dict[int, pg.Surface] = {
            40: pg.image.load("assets/sprites/ui/platinum.png").convert_alpha(),
            30: pg.image.load("assets/sprites/ui/gold.png").convert_alpha(),
            20: pg.image.load("assets/sprites/ui/silver.png").convert_alpha(),
            10: pg.image.load("assets/sprites/ui/bronze.png").convert_alpha(),
        }
		
		self.volume_button_rect: pg.Rect = self.volume_on_image.get_rect(topleft=(self.screen_width - 70, 20))
		self.restart_button_rect: pg.Rect = self.restart_image.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
		
		self.restart_mask: pg.Mask = pg.mask.from_surface(self.restart_image)
		self.volume_on: bool = True
	
	def render_volume_button(self, screen: pg.Surface) -> None:
		if self.flappy_bird.menu in {"death", "main"}:
			if self.volume_on:
				screen.blit(self.volume_on_image, self.volume_button_rect.topleft)

			else:
				screen.blit(self.volume_off_image, self.volume_button_rect.topleft)
	
	def render_restart_button(self, screen: pg.Surface) -> None:
		if self.flappy_bird.menu == "death":
			screen.blit(self.restart_image, self.restart_button_rect.topleft)

	def handle_event(self, event: pg.event.Event) -> None:
		if event.type == pg.MOUSEBUTTONDOWN:
			if event.button == 1:
				if self.volume_button_rect.collidepoint(event.pos) and (self.flappy_bird.menu in {"death", "main"}):
					self.volume_on = not self.volume_on
					pg.mixer.music.set_volume(1.0 if self.volume_on else 0.0)
				
				elif self.flappy_bird.menu == "death":
					x, y = event.pos
					local_x = x - self.restart_button_rect.left
					local_y = y - self.restart_button_rect.top
					if 0 <= local_x < self.restart_mask.get_size()[0] and 0 <= local_y < self.restart_mask.get_size()[1]:
						if self.restart_mask.get_at((local_x, local_y)):
							self.flappy_bird.restart()

	def start_ui(self, screen: pg.Surface) -> None:
		if self.flappy_bird.menu == "main":
			self.frame += 0.05
			if self.frame > 2.99:
				self.frame = 1
				
			self.start_image = pg.image.load(f"assets/sprites/ui/start{int(self.frame)}.png").convert_alpha()
			screen.blit(self.start_image, (self.screen_width / 5, self.screen_height / 5))
	
	def render_text_with_outline(self, screen: pg.Surface, font: pg.font.Font, text: str, color: tuple[int, int, int], outline_color: tuple[int, int, int], position: tuple[int, int]) -> None:
		outline_surface: pg.Surface = font.render(text, True, outline_color)
		outline_rect: pg.Rect = outline_surface.get_rect(center=(position[0], position[1] + 3))
		screen.blit(outline_surface, outline_rect)
		
		text_surface: pg.Surface = font.render(text, True, color)
		text_rect: pg.Rect = text_surface.get_rect(center=position)
		screen.blit(text_surface, text_rect)

	def render_score(self, screen: pg.Surface, font: pg.font.Font) -> None:
		if self.flappy_bird.menu in {"play", "death"}:
			if not self.flappy_bird.menu == "death":
				self.render_text_with_outline(screen, font, str(self.flappy_bird.score), (255, 255, 255), (0, 0, 0), (self.screen_width // 2, 50))
    
			else:
				position: tuple[int, int] = (self.screen_width // 1.4 - 10, 210) if self.flappy_bird.score >= 10 else (self.screen_width // 1.4, 210)
				self.render_text_with_outline(screen, font, str(self.flappy_bird.score), (255, 255, 255), (0, 0, 0), position)
	
	def render_highscore(self, screen: pg.Surface, font: pg.font.Font) -> None:
		if self.flappy_bird.menu == "death":
			position: tuple[int, int] = (self.screen_width // 1.4 - 10, 293) if self.flappy_bird.high_score >= 10 else (self.screen_width // 1.4, 293)
			self.render_text_with_outline(screen, font, str(self.flappy_bird.high_score), (255, 255, 255), (0, 0, 0), position)
	
	def render_decryption_error(self, screen: pg.Surface, font: pg.font.Font) -> None:
		if self.flappy_bird.decryption_error and not self.flappy_bird.menu == "death":
			self.render_text_with_outline(screen, font, "Error: Failed to decrypt score", (255, 255, 255), (0, 0, 0), (self.screen_width // 2, 90))
	
	def render_fps(self, screen: pg.Surface, font: pg.font.Font, clock: pg.time.Clock) -> None:
		fps_text: str = f"FPS: {int(clock.get_fps())}"
		self.render_text_with_outline(screen, font, fps_text, (255, 255, 255), (0, 0, 0), (70, 20))

	def render_score_board(self, screen: pg.Surface) -> None:
		if self.flappy_bird.menu == "death":
			score_board_image: pg.Surface = pg.image.load("assets/sprites/ui/score_board.png").convert_alpha()
			game_over_image: pg.Surface = pg.image.load("assets/sprites/ui/gameover.png").convert_alpha()
			
			screen.blit(score_board_image, (self.screen_width / 5, self.screen_height / 5))
			screen.blit(game_over_image, (self.screen_width / 3.8, self.screen_height / 15))
	
	def render_badge(self, screen: pg.Surface) -> None:
		if self.flappy_bird.menu == "death":
			badge_image: pg.Surface = None

			for threshold, image in sorted(self.badge_images.items(), reverse=True):
				if self.flappy_bird.score >= threshold:
					badge_image = image
					break

			if badge_image:
				screen.blit(badge_image, (self.screen_width / 3.6, self.screen_height / 2.85))

	def update(self, screen: pg.Surface, font: pg.font.Font, clock: pg.time.Clock, events: list[pg.event.Event]) -> None:
		self.start_ui(screen)
		self.render_decryption_error(screen, font)
		self.render_score_board(screen)
		self.render_badge(screen)
		self.render_score(screen, font)
		self.render_highscore(screen, font)
		self.render_volume_button(screen)
		self.render_restart_button(screen)
		#self.render_fps(screen, font, clock)
		for event in events:
			self.handle_event(event)
