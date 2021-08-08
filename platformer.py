from typing import final
import pygame
from pygame.locals import *
import pickle
from os import path

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')




#define font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)



#define game variables
tile_size = 50
game_over = 0
main_menu = True
level = 1
max_levels = 8
score = 0



 
#define colors
white = (255, 255, 255)
blue = (0, 0, 255)


#load images
bg_img = pygame.image.load('bg.png')
restart_img = pygame.image.load('restart.png')
start_img = pygame.image.load('start.png')
exit_img = pygame.image.load('exit.png')




def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


#function to reset level
def reset_level(level):
	player.reset(100, screen_height - 130)
	blob_group.empty()
	lava_group.empty()
	exit_group.empty()
	water_group.empty()
	bug_group.empty()
	platformy_group.empty()
	platformx_group.empty()
	ch1_group.empty()
	ch3_group.empty()
	ch4_group.empty()
	ch5_group.empty()
	ch6_group.empty()
	ch12_group.empty()
	finale_group.empty()

	#load in level data and create world
	if path.exists(f'level{level}_data'):
		pickle_in = open(f'level{level}_data', 'rb')
		world_data = pickle.load(pickle_in)
	world = World(world_data)

	return world



class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		#draw button
		screen.blit(self.image, self.rect)

		return action


class Player():
	def __init__(self, x, y):
		self.reset(x, y)



	def update(self, game_over):
		dx = 0
		dy = 0
		walk_cooldown = 5
		col_thresh = 20

		if game_over == 0:
			#get keypresses
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
				self.vel_y = -18
				self.jumped = True
			if key[pygame.K_SPACE] == False:
				self.jumped = False
			if key[pygame.K_LEFT]:
				dx -= 5
				self.counter += 1
				self.direction = -1
			if key[pygame.K_RIGHT]:
				dx += 5
				self.counter += 1
				self.direction = 1
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#handle animation
			if self.counter > walk_cooldown:
				self.counter = 0	
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
					
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#add gravity
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			#check for collision
			self.in_air = True
			for tile in world.tile_list:
				#check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#check if above the ground i.e. falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False


			#check for collision with enemies
			if pygame.sprite.spritecollide(self, blob_group, False):
				game_over = -1
			
			#check collision with bug
			if pygame.sprite.spritecollide(self, bug_group, False):
				game_over = -1





			#check for collision with lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1


			#check for collision with water
			if pygame.sprite.spritecollide(self, water_group, False):
				game_over = -1

			#check for collision with exit
			if pygame.sprite.spritecollide(self, exit_group, False):
				game_over = 1








			#check for collision with platforms
			for platform in platformx_group:
				#collision in the x direction
				if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#collision in the y direction
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below platform
					if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
						self.vel_y = 0
						dy = platform.rect.bottom - self.rect.top
					#check if above platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						dy = 0
					#move sideways with the platform
					if platform.move_x != 0:
						self.rect.x += platform.move_direction





			#check for collision with platforms
			for platform in platformy_group:
				#collision in the x direction
				if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#collision in the y direction
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below platform
					if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
						self.vel_y = 0
						dy = platform.rect.bottom - self.rect.top
					#check if above platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						dy = 0
					#move sideways with the platform
					if platform.move_x != 0:
						self.rect.x += platform.move_direction


			#update player coordinates
			self.rect.x += dx
			self.rect.y += dy


		elif game_over == -1:
			self.image = self.dead_image
			if self.rect.y > 200:
				self.rect.y -= 5




		elif game_over == -1:
			self.image = self.dead_image
			draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2)
			if self.rect.y > 200:
				self.rect.y -= 5


		#draw player onto screen
		screen.blit(self.image, self.rect)

		


		return game_over


	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load('main3.png')
			img_right = pygame.transform.scale(img_right, (40, 80))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load('ghost_normal.png')
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True



class World():
	def __init__(self, data):
		self.tile_list = []

		#load images
		dirt_img = pygame.image.load('grassCenter_rounded.png')
		grass_img = pygame.image.load('grass.png')
		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 3:
					blob = Blob(col_count * tile_size, row_count * tile_size + 15)
					blob_group.add(blob)
				if tile == 4:
					platform = Platformx(col_count * tile_size, row_count * tile_size, 1, 0)
					platformx_group.add(platform)
				if tile == 5:
					platform = Platformy(col_count * tile_size, row_count * tile_size, 0, 1)
					platformy_group.add(platform)
				if tile == 6:
					lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					lava_group.add(lava)
				if tile == 7:
					drink = Drink(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					drink_group.add(drink)
				if tile == 8:
					exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
					exit_group.add(exit)
				if tile == 9:
					water = Water(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					water_group.add(water)
				if tile == 10:
					bug = Bug(col_count * tile_size, row_count * tile_size + 15)
					bug_group.add(bug)	
				if tile == 11:
						ch1 = Ch1(col_count * tile_size, row_count * tile_size + (tile_size // 2))
						ch1_group.add(ch1)
				if tile == 12:
						ch3 = Ch3(col_count * tile_size, row_count * tile_size + (tile_size // 2))
						ch3_group.add(ch3)
				if tile == 13:
						ch4 = Ch4(col_count * tile_size, row_count * tile_size + (tile_size // 2))
						ch4_group.add(ch4)
				if tile == 14:
						ch5 = Ch5(col_count * tile_size, row_count * tile_size + (tile_size // 2))
						ch5_group.add(ch5)
				if tile == 15:
						ch6 = Ch6(col_count * tile_size, row_count * tile_size + (tile_size // 2))
						ch6_group.add(ch6)
				if tile == 16:
					berry = Berry(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					berry_group.add(berry)
				if tile == 17:
					ch12 = Ch12(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					ch12_group.add(ch12)
				if tile == 18:
					egg = Egg(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					egg_group.add(egg)
				if tile == 19:
					finale = Finale(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					finale_group.add(finale)
				col_count += 1
			row_count += 1


	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])
			pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


music = pygame.mixer.music.load('song.mp3')
pygame.mixer.music.play(-1)












class Bug(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('fly.png')
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0



	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1













class Blob(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('turtle fixed.png')
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0


	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1



class Platformx(pygame.sprite.Sprite):
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('platform_x.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0
		self.move_direction = 1
		self.move_x = move_x
		self.move_y = move_y


	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1



class Platformy(pygame.sprite.Sprite):
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('platform_y.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0
		self.move_direction = 1
		self.move_x = move_x
		self.move_y = move_y



	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1

class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('dirtCaveSpikeBottom.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y



	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1


class Ch1(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		ch1_img = pygame.image.load('ch1.png')
		self.image = pygame.transform.scale(ch1_img, (500,500))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		screen.blit(ch1_img, (-1000,-1000))





class Ch3(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		ch3_img = pygame.image.load('ch3.png')
		self.image = pygame.transform.scale(ch3_img, (500,500))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		screen.blit(ch3_img, (-1000,-1000))







class Ch4(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		ch4_img = pygame.image.load('ch4.png')
		self.image = pygame.transform.scale(ch4_img, (500,500))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		screen.blit(ch4_img, (-1000,-1000))







class Ch5(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		ch5_img = pygame.image.load('ch5.png')
		self.image = pygame.transform.scale(ch5_img, (500,500))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		screen.blit(ch5_img, (-1000,-1000))





class Ch6(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		ch6_img = pygame.image.load('ch6.png')
		self.image = pygame.transform.scale(ch6_img, (500,500))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		screen.blit(ch6_img, (-1000,-1000))





class Ch12(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		ch12_img = pygame.image.load('ch12.png')
		self.image = pygame.transform.scale(ch12_img, (500,500))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		screen.blit(ch12_img, (-1000,-1000))





class Finale(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		finale_img = pygame.image.load('finale.png')
		self.image = pygame.transform.scale(finale_img, (500,500))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

		screen.blit(finale_img, (-1000,-1000))





class Drink(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('drink.png')
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)




class Berry(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('Berry.png')
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)





class Egg(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('egg.png')
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)





class Water(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('waves6.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


class Exit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('gate.png')
		self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y



player = Player(100, screen_height - 130)

blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
bug_group = pygame.sprite.Group()
drink_group = pygame.sprite.Group()
platformx_group = pygame.sprite.Group()
platformy_group = pygame.sprite.Group()
ch1_group = pygame.sprite.Group()
ch3_group = pygame.sprite.Group()
ch4_group = pygame.sprite.Group()
ch5_group = pygame.sprite.Group()
ch6_group = pygame.sprite.Group()
berry_group = pygame.sprite.Group()
egg_group = pygame.sprite.Group()
ch12_group = pygame.sprite.Group()
finale_group = pygame.sprite.Group()





#create dummy coin for showing the score
score_drink = Drink(tile_size // 2, tile_size // 2)
drink_group.add(score_drink)

score_berry = Berry(tile_size // 2, tile_size // 2)
berry_group.add(score_berry)

score_egg = Egg(tile_size // 2, tile_size // 2)
egg_group.add(score_egg)


#load in level data and create world
if path.exists(f'level{level}_data'):
	pickle_in = open(f'level{level}_data', 'rb')
	world_data = pickle.load(pickle_in)
world = World(world_data)


#create buttons
restart_button = Button(screen_width // 2 - 200, screen_height // 2 + 150, restart_img)
start_button = Button(screen_width // 2 - 500, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 50, screen_height // 2, exit_img)
run = True
while run:

	clock.tick(fps)

	screen.blit(bg_img, (0, 0))


	if main_menu == True:
		if exit_button.draw():
			run = False
		if start_button.draw():
			main_menu = False
	else:
		world.draw()

		if game_over == 0:
			blob_group.update()
			platformx_group.update()
			platformy_group.update()
			berry_group.update()
			drink_group.update()
			egg_group.update()
			#update score
			#check if a coin has been collected
			if pygame.sprite.spritecollide(player, drink_group, True):
				score += 1
			draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

			if pygame.sprite.spritecollide(player, berry_group, True):
				score += 1



			if pygame.sprite.spritecollide(player, egg_group, True):
				score += 1

		if game_over == 0:
			bug_group.update()
		
		blob_group.draw(screen)
		bug_group.draw(screen)
		lava_group.draw(screen)
		exit_group.draw(screen)
		water_group.draw(screen)
		drink_group.draw(screen)
		platformx_group.draw(screen)
		platformy_group.draw(screen)
		ch1_group.draw(screen)
		ch3_group.draw(screen)
		ch4_group.draw(screen)
		ch5_group.draw(screen)
		ch6_group.draw(screen)
		berry_group.draw(screen)
		egg_group.draw(screen)
		ch12_group.draw(screen)
		finale_group.draw(screen)
		game_over = player.update(game_over)

		#if player has died
		if game_over == -1:
			if restart_button.draw():
				world_data = []
				world = reset_level(level)
				game_over = 0


		#if player has completed the level
		if game_over == 1:
			#reset game and go to next level
			level += 1
			if level <= max_levels:
				#reset level
				world_data = []
				world = reset_level(level)
				game_over = 0
				score = 0
			else:
				if restart_button.draw():
					level = 1
					#reset level
					world_data = []
					world = reset_level(level)
					game_over = 0
					score = 0



	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()
