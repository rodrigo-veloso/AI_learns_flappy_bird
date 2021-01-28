import pygame, sys
import neat
import time
import os
import random
import numpy as np
#import input_box as ib
from pygame.locals import *
import shelve
import fileinput
import pickle
#import tensorflow as tf
#from tensorflow.python.framework.ops import disable_eager_execution
pygame.init()
pygame.font.init()

STAT_FONT = pygame.font.SysFont('Sans', 30)

def resource_path(relative_path):
	try:
	# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)

sub_path = resource_path("sub")
sys.path.insert(0, sub_path)
#from sub import input_box as ib 



#set screen dimensional
WIN_WIDTH = int(288)
WIN_HEIGHT = int(512)

GEN = 0
MAX_SCORE = 20

#load images
#scale2x double the size of original image

image_url_bird1 = resource_path("data/assets/sprites/bluebird-upflap.png")
image_url_bird2 = resource_path("data/assets/sprites/bluebird-midflap.png")
image_url_bird3 = resource_path("data/assets/sprites/bluebird-downflap.png")

BIRD_IMGS = [pygame.image.load(image_url_bird1), 
pygame.image.load(image_url_bird2),
pygame.image.load(image_url_bird3)]

BIRD_IMGS_ALPHA = [pygame.image.load(image_url_bird1), 
pygame.image.load(image_url_bird2),
pygame.image.load(image_url_bird3)]


for x, image in enumerate(BIRD_IMGS_ALPHA):
	BIRD_IMGS_ALPHA[x].set_alpha(128)


image_url_pipe = resource_path("data/assets/sprites/pipe-red.png")
image_url_base = resource_path("imagens/base.png")
image_url_bg = resource_path("data/assets/sprites/background-night.png")
PIPE_IMG = pygame.image.load(image_url_pipe)
BASE_IMG = pygame.image.load(image_url_base)
BACKGROUND_IMG = pygame.image.load(image_url_bg)



class InputBox:
	COLOR_INACTIVE = pygame.Color(144,238,144)
	COLOR_ACTIVE = pygame.Color(34,139,34)

	def __init__(self, x, y, w, h, text=''):
		self.rect = pygame.Rect(x, y, w, h)
		self.color = self.COLOR_INACTIVE
		self.text = text
		self.txt_surface = pygame.font.SysFont('Sans', 30).render(text, True, self.color)
		self.active = False

	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			# If the user clicked on the input_box rect.
			if self.rect.collidepoint(event.pos):
			# Toggle the active variable.
				self.active = not self.active
			else:
				self.active = False
			# Change the current color of the input box.
			self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
		if event.type == pygame.KEYDOWN:
			if self.active:
				if event.key == pygame.K_RETURN:
					print(self.text)
					self.text = ''
				elif event.key == pygame.K_BACKSPACE:
					self.text = self.text[:-1]
				else:
					self.text += event.unicode
				# Re-render the text.
				self.txt_surface = pygame.font.SysFont('Sans', 30).render(self.text, True, self.color)

	def update(self):
		# Resize the box if the text is too long.
		width = max(200, self.txt_surface.get_width()+10)
		self.rect.w = width

	def draw(self, screen):
		# Blit the text.
		screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y))
		# Blit the rect.
		pygame.draw.rect(screen, self.color, self.rect, 2)



class Bird:
	IMGS = BIRD_IMGS
	IMGS_ALPHA = BIRD_IMGS_ALPHA
	MAX_ROTATION = 25 #the max rotation angle of the bird
	ROT_VEL = 20 #bird rotation velocity
	ANIMATION_TIME = 5 #how long to show each bird animation

	def __init__(self,x,y,alpha=False):
		self.x = x #cordenada x do bird, inicial 0
		self.y = y #cordenada y do bird, inicial 0
		self.alpha = alpha
		self.tilt = 0 #ângulo do bird, jump or falling down
		self.tick_count = 0 #física do bird
		self.vel = 0 #velocidade do bird
		self.height = self.y #altura do bird
		self.img_count = 0 #para saber qual imagem esta sendo mostrada do bird para poder animar corretamente
		self.img = self.IMGS[0] #bird1.png imagem padrão
		self.d = 0
		self.max_vel = 10
		self.flapped = False
		self.acc = 1

	def jump(self):
		self.vel = -9
		self.tick_count = 0 #when we last jump
		self.height = self.y
		self.flapped = True

	def move(self):
		self.tick_count += 1 #how much we moved before another jump
		#d nos diz quanto o bird se move para cima ou para baixc
		# tick_count é como se fosse o tempo
		self.d = self.vel*self.tick_count + 2.0*self.tick_count**2 #how many pixels we are going up or down of on frame
		#isto resulta em um arco na trajetoria do bird
		#é bom usar uma velocidade limite do bird
		if self.d >=10:
			self.d = 10
		if self.d < 0:
			self.d -= 1
		#self.y = self.y + self.d
		if self.vel < self.max_vel and not self.flapped:
			self.vel += self.acc
		if self.flapped:
			self.flapped = False
		self.y += self.vel
		#print('y = ' + str(self.y))
		#print('d = '+str(d))
		#agora temos que rotacionar o bird

		if self.d < 0  or self.y < self.height + 50: #bird esta subindo
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		else: #bird está descendo e passou da posição inicial do jump
			if self.tilt > -90:
				self.tilt -= self.ROT_VEL

	def draw(self,win):
		if self.alpha:
			self.img_count += 1
			#fazer as asas baterem baseado em um frame de 30 seg
			if self.img_count < self. ANIMATION_TIME: #5
				self.img = self.IMGS_ALPHA[0]
			elif self.img_count < self.ANIMATION_TIME*2: #10
				self.img = self.IMGS_ALPHA[1]
			elif self.img_count < self.ANIMATION_TIME*3: #15
				self.img = self.IMGS_ALPHA[2]
			elif self.img_count < self.ANIMATION_TIME*4: #20
				self.img = self.IMGS_ALPHA[1]
			elif self.img_count < self.ANIMATION_TIME*4 +1:
				self.img = self.IMGS_ALPHA[0]
				self.img_count = 0
			#ultima check, se o bird estiver caindo em um angulo de 90 graus, ele nao bate as asas
			if self.tilt <= -80:
				self.img = self.IMGS_ALPHA[1]
				self.img_count = self.ANIMATION_TIME
			#rotação da imagem
			#função do stackoverflow de como rotacionar a imagem em torno do seu centro
			rotated_image = pygame.transform.rotate(self.img,self.tilt) #em geral faz rotação em torno do canto superior esquerdo mas queremos no centro
			new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft =(self.x, self.y)).center) #rotação em torno do centro
			win.blit(rotated_image, new_rect.topleft) #função que rotaciona a imagem no pygame

		else:
			self.img_count += 1
			#fazer as asas baterem baseado em um frame de 30 seg
			if self.img_count < self. ANIMATION_TIME: #5
				self.img = self.IMGS[0]
			elif self.img_count < self.ANIMATION_TIME*2: #10
				self.img = self.IMGS[1]
			elif self.img_count < self.ANIMATION_TIME*3: #15
				self.img = self.IMGS[2]
			elif self.img_count < self.ANIMATION_TIME*4: #20
				self.img = self.IMGS[1]
			elif self.img_count < self.ANIMATION_TIME*4 +1:
				self.img = self.IMGS[0]
				self.img_count = 0
			#ultima check, se o bird estiver caindo em um angulo de 90 graus, ele nao bate as asas
			if self.tilt <= -80:
				self.img = self.IMGS[1]
				self.img_count = self.ANIMATION_TIME
			#rotação da imagem
			#função do stackoverflow de como rotacionar a imagem em torno do seu centro
			rotated_image = pygame.transform.rotate(self.img,self.tilt) #em geral faz rotação em torno do canto superior esquerdo mas queremos no centro
			new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft =(self.x, self.y)).center) #rotação em torno do centro
			win.blit(rotated_image, new_rect.topleft) #função que rotaciona a imagem no pygame

	def get_mask(self):
		return pygame.mask.from_surface(self.img)

class Pipe:
	GAP = 100
	TIMESTEP = 5
	VELMAX = 4

	def __init__ (self, x, reference):
		self.x = x
		self.height = 250

		self.top = 0
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
		self.PIPE_BOTTOM = PIPE_IMG 
		self.vel = 4
		self.uptime = self.TIMESTEP
		self.reference = reference

		self.passed = False #for collison and AI
		self.set_height() #define where the top pipe is the botton as well, and also how is the size of them

	def set_height(self):
		possible = False
		while not possible:
			self.height = random.randrange(int(WIN_HEIGHT*(0.85)*0.1),int(WIN_HEIGHT* 0.8 - Pipe.GAP))
			self.top = self.height - self.PIPE_TOP.get_height()
			self.bottom = self.height + self.GAP
			#print('height gap: ' + str(self.height))
			if not self.reference - 75 > (self.height + self.bottom)/2.0 and not self.reference + 140 < (self.height + self.bottom)/2.0:
				 possible = True
		#self.height += int(WIN_HEIGHT*(0.85)*0.1)

	def move(self, begin):
		if (time.time() - begin) > self.uptime:
			self.vel += 1
			self.uptime += self.TIMESTEP
		if self.vel > self.VELMAX:
			self.x -= self.VELMAX
			return self.vel
		else:
			self.x -= self.vel
			return self.vel
		


	def draw(self, win):
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

	def collide(self,bird):
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		top_offset = (self.x - bird.x, self.top - round(bird.y)) #ve se dois pixels fazer overlap
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		#verificar se as mask colidem
		bottom_point = bird_mask.overlap(bottom_mask, bottom_offset) #se não colide retorna none type
		top_point = bird_mask.overlap(top_mask, top_offset) 
		#verificar se top ou bottom top sao none type, ou seja se colidem ou nao
		#if top_point:
			#print('top')
		#if #bottom_point:
			#print('bottom')
		self.top_point =top_point
		self.bottom_point = bottom_point
		if top_point or bottom_point:
			return True

		return False

class Base:
	VELMAX = 4
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG
	TIMESTEP = 5

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH
		self.vel = 4
		self.uptime = self.TIMESTEP

	def move(self, begin):
		if (time.time() - begin) > self.uptime:
			self.vel += 1
			self.uptime += self.TIMESTEP

		if self.vel > self.VELMAX:
			self.x1 -= self.VELMAX
			self.x2 -= self.VELMAX
		else:
			self.x1 -= self.vel
			self.x2 -= self.vel
		#move duas imagens iguais para o lado para dar a ideia de movimento da base
		#a ideia é quando uma imagem termina de passar pela janela ela volta do inicio

		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH <0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		win.blit(self.IMG, (self.x1,self.y))
		win.blit(self.IMG, (self.x2,self.y))


def draw_window_ai(win, birds, pipes, base, score, vel, gen, text, button_test1):
	win.blit(BACKGROUND_IMG, (0,0)) #função que escreve na tela
	for pipe in pipes:
		pipe.draw(win)
	base.draw(win)
	text1 = STAT_FONT.render("Score: " +str(score), 1, (255,255,255))
	win.blit(text1, (WIN_WIDTH - 10 - text1.get_width(),10))
	#text = STAT_FONT.render("Velocidade: " +str(vel), 1, (0,0,0))
	#win.blit(text, (WIN_WIDTH - 10 - text.get_width(),730))
	text1 = STAT_FONT.render("Gen: " +str(gen), 1, (255,255,255))
	win.blit(text1, (10, 10))
	for bird in birds:
		bird.draw(win)
	pygame.draw.rect(win, (144,238,144),button_test1)
	win.blit(text, ((25)+10, 650))
	pygame.display.update()#dar refresh na screen

def draw_window_solo(win, birds, pipes, base, score, high_score):
	win.blit(BACKGROUND_IMG, (0,0)) #função que escreve na tela
	#print(pipes[-1].vel)
	for pipe in pipes:
		pipe.draw(win)
	base.draw(win)
	text = STAT_FONT.render("Score: " +str(score), 1, (255,255,255))
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(),10))
	#text = STAT_FONT.render("Recorde: " +str(high_score), 1, (255,255,255))
	#win.blit(text, (10, 10))
	for bird in birds:
		bird.draw(win)
	pygame.display.update()#dar refresh na screen

def simula_ia(genomes, config): #fitness function
	#trocar de um bird para multiples birdows
	global GEN
	if isinstance(GEN, int):
		GEN += 1
	else:
		pass
	global MAX_SCORE
	nets = []
	ge = []
	birds = []
	#basicamente um loop que vai criar todos os birds de uma poplação e também associar a cada um deles seu net
	for _, g in genomes: #tem que ser assim pois genome é um tuple
		 net = neat.nn.FeedForwardNetwork.create(g, config)
		 nets.append(net)
		 birds.append(Bird(230,350))
		 g.fitness = 0
		 ge.append(g)

	base = Base(730)
	pipes = [Pipe(600)]
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) #criar janela do pygame
	clock = pygame.time.Clock()
	run = True
	score = 0
	begin = time.time()
	t = 30
	while run:
		click = False
		clock.tick(t)

		for event in pygame.event.get():
			# if event.type == pygame.MOUSEBUTTONUP:
			# 	bird.jump()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()

		#precisamos agora move o bird de acordo com o seu net
		#definir qual o pipe estamos a ver
		pipe_ind = 0
		if len(birds) > 0:
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
				pipe_ind = 1 #basicamente, diz qual o pipe a net vai usar como ref, se o bird passou de um pipe olha o proxino
		else: #todos os birds morreram
			run = False
			break #entao encerra
		for x, bird in enumerate(birds):
			#add fitness a cada frame
			ge[x].fitness += 0.1 #ganha 1 por segundo vivo
			bird.move()
			#retorna o valor da net
			# passar todos os inputs, (y do bird, distancia entre o y do bird e o y do pipe de cima, e o distância do bird ao pipe de baixo)
			output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
			#output = nets[x].activate((bird.y, pipes[pipe_ind].height, pipes[pipe_ind].bottom))
			if output[0] > 0.5: #output é uma lista
				bird.jump()
		add_pipe = False
		rem = []
		for pipe in pipes:
			for x, bird in enumerate(birds):
				if pipe.collide(bird):
					ge[x].fitness -= 1 #punição caso acerte um pipe
					birds.pop(x) #remove o passáro que bater
					nets.pop(x)
					ge.pop(x)
				if not pipe.passed and pipe.x < bird.x: #cheka se o bird passou o pipe e gera novo pipe
					pipe.passed = True
					add_pipe = True

			if pipe.x + pipe.PIPE_TOP.get_width() < 0: #pipe of the screen so need to remove
				rem.append(pipe)
			

			vel = pipe.move(begin)

		if add_pipe:
			score += 1

			for g in ge:
				g.fitness += 15 #add 15 to fitness if o bird conseguiu passar pelo pipe
			pipes.append(Pipe(600)) #quanto menor o valor mas rapido aparece

		for r in rem:
			pipes.remove(r)
		#check se o bird caiu no chao, ou passou do teto
		for x, bird in enumerate(birds):
			if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)

		if score >= 10 and score < 20 :
			t=60 #90
		if score >= 20 and score < 30:
			t=90 #150
		if score >= 30 and score < 40:
			t=120 #210
		if score >= 40 and score < 50:
			t=150 #270
		if score >= 50 and score < 100:
			t=200
		if score >= 100:
			t=300
		base.move(begin)

		mx, my = pygame.mouse.get_pos() 
		text = STAT_FONT.render("< Voltar", 1, (255,255,255))
		button_test1 = pygame.Rect(25,  650, text.get_width()+20, 50)

		draw_window_ai(win, birds, pipes, base, score, vel, GEN, text, button_test1)
		
		

		if button_test1.collidepoint((mx,my)):
			if click:
				ia_menu(win)

def player_vs_ai(genomes): #player vs ai
	#trocar de um bird para multiples birdows
	try:
		score_path = resource_path('data/score.txt')
		d = shelve.open(score_path)     
		high_score = d['score']         
		d.close()
	except:
		high_score = 0
	#local_dir = os.path.dirname(__file__)
	#config_path = os.path.join(local_dir, "data/config-feedforward.txt")
	config_path = resource_path('data/config-feedforward.txt')
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
					neat.DefaultSpeciesSet, neat.DefaultStagnation,
					config_path) 
	global GEN
	if isinstance(GEN, int):
		GEN += 1
	else:
		pass
	nets = []
	ge = []
	birds = []
	score = 0
	recorde = False
	#basicamente um loop que vai criar todos os birds de uma poplação e também associar a cada um deles seu net
	for _, g in genomes: #tem que ser assim pois genome é um tuple
		 net = neat.nn.FeedForwardNetwork.create(g, config)
		 nets.append(net)
		 birds.append(Bird(230,350,True))#ai bird
		 g.fitness = 0
		 ge.append(g)
	base = Base(730)
	pipes = [Pipe(600)]
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) #criar janela do pygame
	clock = pygame.time.Clock()
	run = True
	score = 0
	birds.append(Bird(230,350)) #my bird
	begin = time.time()
	t = 30
	while run:
		clock.tick(t)
		for event in pygame.event.get():
			# if event.type == pygame.MOUSEBUTTONUP:
			# 	bird.jump()
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()
			#player play
			if event.type == KEYDOWN:
				if event.key == K_SPACE:
			 		birds[1].jump()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					birds[1].jump()

		#precisamos agora move o bird de acordo com o seu net
		#definir qual o pipe estamos a ver
		pipe_ind = 0
		if len(birds) > 0:
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
				pipe_ind = 1 #basicamente, diz qual o pipe a net vai usar como ref, se o bird passou de um pipe olha o proxino
		else: #todos os birds morreram
			run = False
			break #entao encerra
		for x, bird in enumerate(birds):
			#add fitness a cada frame
			#ge[x].fitness += 0.1 #ganha 1 por segundo vivo
			bird.move()
			#retorna o valor da net
			# passar todos os inputs, (y do bird, distancia entre o y do bird e o y do pipe de cima, e o distância do bird ao pipe de baixo)
		#ai play...
		output = nets[0].activate((birds[0].y, abs(birds[0].y - pipes[pipe_ind].height), abs(birds[0].y - pipes[pipe_ind].bottom)))
			#output = nets[x].activate((bird.y, pipes[pipe_ind].height, pipes[pipe_ind].bottom))
		if output[0] > 0.5: #output é uma lista
			birds[0].jump()


		add_pipe = False
		rem = []
		for pipe in pipes:
			if pipe.collide(birds[0]):
				#ai perdeu
				victory = True
				player_ai_menu(win, birds, pipes, base, score, high_score, recorde, victory, genomes)
			elif pipe.collide(birds[1]):
				#player perdeu
				victory = False
				player_ai_menu(win, birds, pipes, base, score, high_score, recorde, victory, genomes)
			if not pipe.passed and pipe.x < birds[1].x: #cheka se o bird passou o pipe e gera novo pipe
				pipe.passed = True
				add_pipe = True

			if pipe.x + pipe.PIPE_TOP.get_width() < 0: #pipe of the screen so need to remove
				rem.append(pipe)
			

			vel = pipe.move(begin)

		if add_pipe:
			score += 1
			if score > high_score:
				high_score = score
				recorde = True
			for g in ge:
				g.fitness += 15 #add 15 to fitness if o bird conseguiu passar pelo pipe
			pipes.append(Pipe(600)) #quanto menor o valor mas rapido aparece

		for r in rem:
			pipes.remove(r)
		#check se o bird caiu no chao, ou passou do teto
		if birds[0].y + birds[0].img.get_height() >= 730 or birds[0].y < 0:
			#ai perdeu
			victory = True
			player_ai_menu(win, birds, pipes, base, score, high_score, recorde, victory, genomes)
		elif birds[1].y + birds[1].img.get_height() >= 730 or birds[1].y < 0:
			#player perdeu
			victory = False
			player_ai_menu(win, birds, pipes, base, score, high_score, recorde, victory, genomes)

		base.move(begin)
		draw_window_solo(win, birds, pipes, base, score, high_score)

def jogo_solo(): #fitness function
	#trocar de um bird para multiples birdows
	#basicamente um loop que vai criar todos os birds de uma poplação e também associar a cada um deles seu net
	birds = []
	y = random.randrange(int(WIN_HEIGHT*(0.85)*0.1),int(WIN_HEIGHT* 0.8))
	birds.append(Bird(int(WIN_WIDTH * 0.5),y))
	base = Base(WIN_HEIGHT* 0.85)
	pipes = [Pipe(WIN_WIDTH+10,birds[0].y)]
	recorde = False
	try:
		high_score = 0
	except:
		high_score = 0

	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) #criar janela do pygame
	clock = pygame.time.Clock()
	run = True
	score = 0
	begin = time.time()
	while run:
		clock.tick(30)
		birds[0].move()
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key == K_SPACE:
			 		birds[0].jump()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					birds[0].jump()
			if event.type == pygame.QUIT:
				run = False
				pygame.quit()
				quit()

		#precisamos agora move o bird de acordo com o seu net
		#definir qual o pipe estamos a ver
				
		add_pipe = False
		rem = []
		for pipe in pipes:
			if pipe.collide(birds[0]):
				lost_menu(win, birds, pipes, base, score, high_score, recorde)
			if not pipe.passed and pipe.x < birds[0].x: #cheka se o bird passou o pipe e gera novo pipe
					pipe.passed = True
					add_pipe = True

			if pipe.x + pipe.PIPE_TOP.get_width() < 0: #pipe of the screen so need to remove
				rem.append(pipe)
			

			vel = pipe.move(begin)

		if add_pipe:
			score += 1
			if score > high_score:
				high_score = score
				recorde = True
			pipes.append(Pipe(WIN_WIDTH+10,pipes[0].height)) #quanto menor o valor mas rapido aparece

		for r in rem:
			pipes.remove(r)
		#(bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom))
		#print('bird.y = '+str(birds[0].y))
		#print('d1 = '+str(abs(birds[0].y - pipes[-1].height)))
		#print('d2 = '+str(abs(birds[0].x - pipes[-1].x)))
		#check se o bird caiu no chao, ou passou do teto
		if birds[0].y + birds[0].img.get_height() >= WIN_HEIGHT* 0.85 or birds[0].y < 0:
			lost_menu(win, birds, pipes, base, score, high_score, recorde)

		base.move(begin)
		draw_window_solo(win, birds, pipes, base, score, high_score)

def check_above(y,bottom,height):

	delta = 40

	if y > (bottom) - delta :
		above_bottom = 1
	else:
		above_bottom = 0
	if y > height + delta:
		above_top = 1
	else:
		above_top = 0

	if y >= (bottom + height)/2:
		above_center = 1
	else:
		above_center = 0

	return above_bottom, above_top, above_center

def q_learning(): #fitness function
	#Q = np.zeros((400,WIN_WIDTH+1,16,2,2,2))
	#experiences = np.zeros((400,WIN_WIDTH+1,16,2,2,2))
	#Q = np.zeros((400,20,2,2,2))
	#experiences = np.zeros((400,20,2,2,2))
	#Q = np.zeros((400,400,513,2))
	#experiences = np.zeros((400,400,513,2))
	N = 5
	Q = np.zeros((int(500/N),104,int(500/N),20,2,2,2))
	experiences = np.zeros((int(500/N),104,int(500/N),20,2,2,2))
	#Q = np.zeros((int(500/N),int(500/N),int(500/N),2))
	#experiences = np.zeros((int(500/N),int(500/N),int(500/N),2))
	#Q = np.zeros((int(500/N),20,2))
	#experiences = np.zeros((int(500/N),20,2))
	#Q = np.zeros((int(800/4+1),int(680/4+1),19,2))
	#experiences = np.zeros((int(800/4+1),int(680/4+1),19,2))
	#Q = np.load('Q_caso_3.npy')
	#print(Q)
	max_iter=200000
	mu = 0.7
	lambda_ = .9
	epsilon = 1
	data_reward = []
	data_score = []
	data_game = []
	games = 0
	weight_updates = 0
	total_reward = 0
	total_score = 0
	max_reward = 20
	max_score = 0
	train_mode = False
	frames = 1
	if train_mode:
		epsilon = 0.5
	count = 0
	max_score = 0
	print('estado: '+str(13))
	for i in range(max_iter):
		#if np.mod(i,500)==0 and epsilon < 0.98:
		#	epsilon += 0.01
		if i > 1000 and epsilon < 1:
			if i%500 == 0:
				epsilon += 0.01
		collide = False
		collide_out = False
		birds = []
		y = random.randrange(int(WIN_HEIGHT*(0.85)*0.06),int(WIN_HEIGHT* 0.83))
		birds.append(Bird(int(WIN_WIDTH * 0.5),y))
		base = Base(WIN_HEIGHT* 0.85)
		pipes = [Pipe(WIN_WIDTH+10,birds[0].y)]
		pipes_see = pipes.copy()
		recorde = False
		#if abs(birds[0].y - (pipes_see[-1].bottom + pipes_see[-1].height)/2)>75:
		#	print('vai dar ruim')
		win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) #criar janela do pygame
		clock = pygame.time.Clock()
		run = True
		score = 0
		begin = time.time()
		j = 0
		mean_score = 0
		while run:
			passed = False
			if train_mode:
				clock.tick(60000)
			else:
				clock.tick(30)

			above_bottom, above_top, above_center = check_above(birds[0].y,pipes_see[-1].bottom,pipes_see[-1].height)
			#s = (int(abs(birds[0].y -pipes_see[-1].bottom)),int((birds[0].vel+9)),above_bottom,above_top)
			#s = (int(abs(birds[0].y -(pipes_see[-1].bottom + pipes_see[-1].height)/2)),int((birds[0].d+20)/2),above_bottom,above_top)
			#s = (int(abs(birds[0].y - (pipes_see[-1].bottom))),int(abs(birds[0].y - (pipes_see[-1].height))),int(birds[0].y))
			#s = (int(abs(birds[0].y -pipes_see[-1].bottom)),int(abs(birds[0].x-(pipes_see[-1].x+52))),int(abs(birds[0].y -pipes_see[-1].height)),int(birds[0].vel+9))
			#s = (int(abs(birds[0].y -pipes_see[-1].bottom)),int(abs(birds[0].x-(pipes_see[-1].x+52))),int(abs(birds[0].y -pipes_see[-1].height)),int(birds[0].vel+9))
			#s = (int(birds[0].y/N),int(pipes_see[-1].bottom/N),int(pipes_see[-1].height/N))
			#print(s)
			#s = (int(abs(birds[0].y -(pipes_see[-1].bottom + pipes_see[-1].height)/2)),int(pipes_see[-1].x-100),int((birds[0].d+20)/2),above_bottom,above_top)
			#s = (int((birds[0].d+20)/2),above_bottom,above_top)
			#s = (int((abs(birds[0].y -(pipes_see[-1].bottom + pipes_see[-1].height)/2))/4),int(pipes_see[-1].x/4),int((birds[0].d+20)/2))
			#print(s)
			s = (int(abs(birds[0].y -pipes_see[-1].bottom)/N),int(abs(birds[0].x-(pipes_see[-1].x+52))/2),int(abs(birds[0].y -pipes_see[-1].height)/N),int(birds[0].vel+9),above_bottom, above_top)
			a = 0
			if np.mod(j,frames) == 0:
				actions = Q[s]
				#print(actions)
				a = select_actions(actions, epsilon)
			if a == 1:
				birds[0].jump()
			for event in pygame.event.get():
				#print('bird.y = '+str(birds[0].y))
				#print('d1 = '+str(abs(birds[0].y - pipes[-1].height)))
				#print('d2 = '+str(abs(birds[0].x - pipes[-1].x)))
				if event.type == pygame.QUIT or count > 5:
					if train_mode:
						np.save('Q_best',Q)
					run = False
					pygame.quit()
					quit()
			birds[0].move()
			#s_ = [int(birds[0].y),int(pipes[-1].height),int(pipes[-1].bottom)]
			#print(s)
			#precisamos agora move o bird de acordo com o seu net
			#definir qual o pipe estamos a ver
			#print(s)
			add_pipe = False
			rem = []
			rem_see = []
			for k,pipe in enumerate(pipes):
				if pipe.collide(birds[0]):
					collide = True
				if pipes_see[k].collide(birds[0]):
					pass
					#if s_[2]==0 and s_[3]==1 or s_[2]==1 and s_[3]==0:
						#print(s_)
				#		print(birds[0].y > (pipe.bottom) - 65)
				#		print(birds[0].y > (pipes_see[-1].bottom) - 65)
				#		print(pipe.bottom)
				#		print(pipe.height)
				#		print(pipe.height-pipe.bottom)
				#		if pipe.top_point:
				#			print('top')
				#		if pipe.bottom_point:
				#			print('bottom')
				#		print('bateu')
				if not pipe.passed and pipe.x < birds[0].x - 52 : #cheka se o bird passou o pipe e gera novo pipe
						pipe.passed = True
						#add_pipe = True
						passed = True
					#passed = True

				if pipe.x + pipe.PIPE_TOP.get_width() < 0: #pipe of the screen so need to remove
					rem.append(pipe)
				if k < len(pipes_see) and pipes_see[k].x + pipes_see[k].PIPE_TOP.get_width() < 0: #pipe of the screen so need to remove
					rem_see.append(pipes_see[k])
				
				vel = pipe.move(begin)
				if k < len(pipes_see):
					vel = pipes_see[k].move(begin)

			above_bottom, above_top, _ = check_above(birds[0].y,pipes_see[-1].bottom,pipes_see[-1].height)
			#s_ = (int(abs(birds[0].y -pipes_see[-1].bottom)),int((birds[0].vel+9)),above_bottom,above_top)
			#s_ = (int(abs(birds[0].y -(pipes_see[-1].bottom + pipes_see[-1].height)/2)),int((birds[0].d+20)/2),above_bottom,above_top)
			#s_ = (int(abs(birds[0].y -pipes_see[-1].bottom)),int(abs(birds[0].x-(pipes_see[-1].x+52))),int(abs(birds[0].y -pipes_see[-1].height)),int(birds[0].vel+9))
			#s_ = (int(birds[0].y/N),int(pipes_see[-1].bottom/N),int(pipes_see[-1].height/N))
			#s_ = (int(abs(birds[0].y -pipes_see[-1].bottom)),int(abs(birds[0].x-(pipes_see[-1].x+52))),int(abs(birds[0].y -pipes_see[-1].height)),int(birds[0].vel+9))
			#print(int(abs(birds[0].x-(pipes_see[-1].x+52))))
			#s_ = (int(abs(birds[0].y - (pipes_see[-1].bottom))),int(abs(birds[0].y - (pipes_see[-1].height))),int(birds[0].y))
			#s_ = (int(abs(birds[0].y -(pipes_see[-1].bottom + pipes_see[-1].height)/2)),int(pipes_see[-1].x-100),int((birds[0].d+20)/2),above_bottom,above_top)
			#s_ = (int((birds[0].d+20)/2),above_bottom,above_top)
			#s_ = (int((abs(birds[0].y -(pipes_see[-1].bottom + pipes_see[-1].height)/2))/4),int(pipes_see[-1].x/4),int((birds[0].d+20)/2))
			s_ = (int(abs(birds[0].y -pipes_see[-1].bottom)/N),int(abs(birds[0].x-(pipes_see[-1].x+52))/2),int(abs(birds[0].y -pipes_see[-1].height)/N),int(birds[0].vel+9),above_bottom, above_top)

			if pipes[-1].x < birds[0].x - 52 : #cheka se o bird passou o pipe e gera novo pipe
					#pipe.passed = True
					add_pipe = True
					#print('novo')
				
			if add_pipe:
				#print('ponto')
				score += 1
				pipes.append(Pipe(WIN_WIDTH+10,birds[0].y)) #quanto menor o valor mas rapido aparece

			if pipes_see[-1].x < birds[0].x - 52 : #cheka se o bird passou o pipe e gera novo pipe
					#pipe.passed = True
					#print('vejo proximo')
					pipes_see.append(pipes[-1])

			for k,r in enumerate(rem):
				pipes.remove(r)
				pipes_see.remove(rem[k])

			#check se o bird caiu no chao, ou passou do teto
			if birds[0].y + birds[0].img.get_height() >= WIN_HEIGHT* 0.85 or birds[0].y < 0:
				collide_out = True

			base.move(begin)
			high_score = 0
			if not train_mode:
				draw_window_solo(win, birds, pipes, base, score, high_score)
			
			r = reward_function(a,score,collide,collide_out,birds,pipes_see,passed,j,above_top,above_bottom,above_center)
			total_reward += r

			if train_mode:
				update(r,a,s,s_,Q,lambda_,mu,experiences)

			weight_updates += 1

			if train_mode and score > 1:
				break

			if collide or collide_out:
				break

			j += 1

		#print(i)
		total_score += score
		if score > max_score:
			max_score = score
			#print(max_score)
		if score > 1:
			games += 1
		if i>0 and np.mod(i,50) == 0:
			#print('aqui') 
			data_game.append([i,games/50])
			if games/50 == 1:
				print('1.0')
			#	count += 1
			data_score.append([i,total_score/50])
			if(total_score/50 > max_reward):
				#np.save('Qmax',Q)
				max_score = total_score/50
				max_reward = total_score/50
				print(max_reward)
			data_reward.append([i,total_reward/50])
			mean_score = total_score/50
			total_reward = 0
			total_score = 0
			games = 0
			if train_mode:
				np.savetxt('estado/data_r_13.csv',data_reward,delimiter=',')
				np.savetxt('estado/data_s_13.csv',data_score,delimiter=',')
				np.savetxt('estado/data_g_13.csv',data_game,delimiter=',')
			else:
				np.savetxt('final/data_r_padrao_.csv',data_reward,delimiter=',')
				np.savetxt('final/data_s_padrao_.csv',data_score,delimiter=',')
				np.savetxt('final/data_g_padrao_.csv',data_game,delimiter=',')
	if train_mode:
		np.save('Q_padrao',Q)
  

def select_actions(actions, epsilon):

	rand = random.random()

	if rand > epsilon:
		#print('random')
		a = np.random.choice(np.array([0,1]))
	else:
		a = np.argmax(actions)
		
	return a

def update(r,a,s,s_,Q,lambda_,mu,experiences):
	

	Q_ = np.max(Q[s_])

	#Q[s][a] = Q[s][a] + (1/((1+experiences[s][a]/10)))*(r + lambda_*Q_ - Q[s][a])
	Q[s][a] = Q[s][a] + mu*(r + lambda_*Q_ - Q[s][a])

	experiences[s][a] += 1

def reward_function(a,score,collide,collide_out,birds,pipes,passed,j,above_top,above_bottom,above_center):

	r = 0
	#if passed:
		#r +=1000
	if collide:
		#if pipes[-1].x < 280:
		r -= 1000
		#else:
			#r -= (abs((birds[0].y - pipes[-1].height)**3) + abs((birds[0].y - pipes[-1].bottom)**3))/1000000 
	if collide_out:
		r -= 1000
	if above_top == 1 and above_bottom == 0:
		if abs(birds[0].y -(pipes[-1].bottom + pipes[-1].height)/2) < 40:
			r +=10
		#r += (800 - (abs(birds[0].y - pipes[-1].height) + abs(birds[0].y - pipes[-1].bottom))/2.0)/200
		#print(10 + j*1.2)
	#r += 1
	#if above_center == 1 and a == 1:
	#	r += 1
	#if above_center == 0 and a == 0:
	#	r += 1
	#print(r)
	return r

class Memory():

	N = 100000

	def __init__(self):
		self.memory = []
		self.index = 0

	def store(self,r,a,s,s_):
		cell = [s,r,a,s_]
		if(len(self.memory) < self.N):
			self.memory.append(cell)
		else:
			self.memory[self.index] = cell
			if(self.index < self.N - 1):
				self.index += 1
			else:
				self.index = 0

class Model():

	def __init__(self):
		self.actions=[[0,0]]
		keras = tf.keras
		layers = keras.layers
		self.model = keras.models.Sequential()
		self.model.add(layers.Dense(64, activation='relu',input_shape=(4,)))
		self.model.add(layers.Dense(64, activation='relu'))
		self.model.add(layers.Dense(2))
		self.model.compile(optimizer='rmsprop', loss=self.custom_loss, metrics=['mae'])

	def fit(self,D,lambda_):
		batch_size = 32
		X = []
		y = []
		self.actions = []

		if len(D.memory) > batch_size:
			samples = random.sample(D.memory,batch_size)
		else:
			samples = random.sample(D.memory,len(D.memory))

		for i,data in enumerate(samples):
			#print(data[0])
			if len(samples) > 1:
				X.append(data[0])
			else:
				X.append(data[0])
			actions_ = self.model.predict(np.array([data[-1]]))
			Q_ = np.max(actions_[0])
			#print(Q_)
			y.append(-data[1] + lambda_*Q_)
			self.actions.append([i,data[2]])
			#print(self.actions)

		#print(np.mean(y))
		#X = np.array(X)
		self.predict(np.array(X))
		self.model.fit(np.array(X),np.array(y),batch_size=batch_size,verbose=0)

	def predict(self,X):
		return self.model.predict(X)

	def custom_loss(self,y_true,y_pred):
		Q = tf.gather_nd(y_pred,self.actions)		
		custom_loss = (y_true - Q)*(y_true - Q)
		return custom_loss
		
def deep_q_learning(): #fitness function
	#Q = np.zeros((400,WIN_WIDTH+1,16,2,2,2))
	#experiences = np.zeros((400,WIN_WIDTH+1,16,2,2,2))
	#Q = np.zeros((400,20,2,2,2))
	#experiences = np.zeros((400,20,2,2,2))
	#Q = np.zeros((400,400,513,2))
	#experiences = np.zeros((400,400,513,2))
	N = 5
	#Q = np.zeros((int(500/N),104,int(500/N),20,2,2,2))
	#experiences = np.zeros((int(500/N),104,int(500/N),20,2,2,2))
	Q = np.zeros((int(500/N),int(500/N),int(500/N),2))
	experiences = np.zeros((int(500/N),int(500/N),int(500/N),2))
	#Q = np.zeros((int(500/N),20,2))
	#experiences = np.zeros((int(500/N),20,2))
	#Q = np.zeros((int(800/4+1),int(680/4+1),19,2))
	#experiences = np.zeros((int(800/4+1),int(680/4+1),19,2))
	#Q = np.load('Q_padrao.npy')
	print(Q)
	max_iter=200000
	mu = 0.7
	D = Memory()
	model = Model()
	lambda_ = .9
	epsilon = 1
	data_reward = []
	data_score = []
	data_game = []
	games = 0
	weight_updates = 0
	total_reward = 0
	total_score = 0
	max_reward = 20
	max_score = 0
	train_mode = True
	frames = 6
	if train_mode:
		epsilon = 0.5
	count = 0
	max_score = 0
	print('estado: '+str(13))
	for i in range(max_iter):
		#if np.mod(i,500)==0 and epsilon < 0.98:
		#	epsilon += 0.01
		if i > 1500 and epsilon < 1:
			if i%500 == 0:
				epsilon += 0.01
		collide = False
		collide_out = False
		birds = []
		y = random.randrange(int(WIN_HEIGHT*(0.85)*0.06),int(WIN_HEIGHT* 0.83))
		birds.append(Bird(int(WIN_WIDTH * 0.5),y))
		base = Base(WIN_HEIGHT* 0.85)
		pipes = [Pipe(WIN_WIDTH+10,birds[0].y)]
		pipes_see = pipes.copy()
		recorde = False
		#if abs(birds[0].y - (pipes_see[-1].bottom + pipes_see[-1].height)/2)>75:
		#	print('vai dar ruim')
		win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) #criar janela do pygame
		clock = pygame.time.Clock()
		run = True
		score = 0
		begin = time.time()
		j = 0
		mean_score = 0
		while run:
			passed = False
			if train_mode:
				clock.tick(60000)
			else:
				clock.tick(60000)

			above_bottom, above_top, above_center = check_above(birds[0].y,pipes_see[-1].bottom,pipes_see[-1].height)
			s = [abs(birds[0].y-pipes_see[-1].bottom),abs(birds[0].x-(pipes_see[-1].x+52)),abs(birds[0].y - pipes_see[-1].height),birds[0].vel]

			x = [s]
			actions = model.predict(np.array(x))
			a = select_actions(actions, epsilon)

			if a == 1:
				birds[0].jump()
			for event in pygame.event.get():
				#print('bird.y = '+str(birds[0].y))
				#print('d1 = '+str(abs(birds[0].y - pipes[-1].height)))
				#print('d2 = '+str(abs(birds[0].x - pipes[-1].x)))
				if event.type == pygame.QUIT or count > 5:
					if train_mode:
						np.save('Q_best',Q)
					run = False
					pygame.quit()
					quit()
			birds[0].move()
			#s_ = [int(birds[0].y),int(pipes[-1].height),int(pipes[-1].bottom)]
			#print(s)
			#precisamos agora move o bird de acordo com o seu net
			#definir qual o pipe estamos a ver
			#print(s)
			add_pipe = False
			rem = []
			rem_see = []
			for k,pipe in enumerate(pipes):
				if pipe.collide(birds[0]):
					collide = True
				if pipes_see[k].collide(birds[0]):
					pass
					#if s_[2]==0 and s_[3]==1 or s_[2]==1 and s_[3]==0:
						#print(s_)
				#		print(birds[0].y > (pipe.bottom) - 65)
				#		print(birds[0].y > (pipes_see[-1].bottom) - 65)
				#		print(pipe.bottom)
				#		print(pipe.height)
				#		print(pipe.height-pipe.bottom)
				#		if pipe.top_point:
				#			print('top')
				#		if pipe.bottom_point:
				#			print('bottom')
				#		print('bateu')
				if not pipe.passed and pipe.x < birds[0].x - 52 : #cheka se o bird passou o pipe e gera novo pipe
						pipe.passed = True
						#add_pipe = True
						passed = True
					#passed = True

				if pipe.x + pipe.PIPE_TOP.get_width() < 0: #pipe of the screen so need to remove
					rem.append(pipe)
				if k < len(pipes_see) and pipes_see[k].x + pipes_see[k].PIPE_TOP.get_width() < 0: #pipe of the screen so need to remove
					rem_see.append(pipes_see[k])
				
				vel = pipe.move(begin)
				if k < len(pipes_see):
					vel = pipes_see[k].move(begin)

			above_bottom, above_top, _ = check_above(birds[0].y,pipes_see[-1].bottom,pipes_see[-1].height)

			s_ = [abs(birds[0].y-pipes_see[-1].bottom),abs(birds[0].x-(pipes_see[-1].x+52)),abs(birds[0].y - pipes_see[-1].height),birds[0].vel]

			if pipes[-1].x < birds[0].x - 52 : #cheka se o bird passou o pipe e gera novo pipe
					#pipe.passed = True
					add_pipe = True
					#print('novo')
				
			if add_pipe:
				#print('ponto')
				score += 1
				pipes.append(Pipe(WIN_WIDTH+10,birds[0].y)) #quanto menor o valor mas rapido aparece

			if pipes_see[-1].x < birds[0].x - 52 : #cheka se o bird passou o pipe e gera novo pipe
					#pipe.passed = True
					#print('vejo proximo')
					pipes_see.append(pipes[-1])

			for k,r in enumerate(rem):
				pipes.remove(r)
				pipes_see.remove(rem[k])

			#check se o bird caiu no chao, ou passou do teto
			if birds[0].y + birds[0].img.get_height() >= WIN_HEIGHT* 0.85 or birds[0].y < 0:
				collide_out = True

			base.move(begin)
			high_score = 0
			if not train_mode:
				draw_window_solo(win, birds, pipes, base, score, high_score)
			
			r = reward_function(a,score,collide,collide_out,birds,pipes_see,passed,j,above_top,above_bottom,above_center)
			total_reward += r

			D.store(r,a,s,s_)

			if train_mode:
				if len(D.memory) > 5000 and np.mod(j,frames) == 0:
					#print(len(D.memory))
					weight_updates += 1
					model.fit(D,lambda_)

			weight_updates += 1

			if train_mode and score > 1:
				break

			if collide or collide_out:
				break

			j += 1

		#print(i)
		total_score += score
		if score > max_score:
			max_score = score
			#print(max_score)
		if score > 1:
			games += 1
		if i>0 and np.mod(i,50) == 0:
			#print('aqui') 
			data_game.append([i,games/50])
			if games/50 == 1:
				print('1.0')
			#	count += 1
			data_score.append([i,total_score/50])
			if(total_score/50 > max_reward):
				#np.save('Qmax',Q)
				max_score = total_score/50
				max_reward = total_score/50
				print(max_reward)
			data_reward.append([i,total_reward/50])
			mean_score = total_score/50
			total_reward = 0
			total_score = 0
			games = 0
			if train_mode:
				np.savetxt('data_deep_r.csv',data_reward,delimiter=',')
				np.savetxt('data_deep_s.csv',data_score,delimiter=',')
				np.savetxt('data_deep_g.csv',data_game,delimiter=',')
			else:
				np.savetxt('data_deep_r.csv',data_reward,delimiter=',')
				np.savetxt('data_deep_s.csv',data_score,delimiter=',')
				np.savetxt('data_deep_g.csv',data_game,delimiter=',')
	if train_mode:
		np.save('Q_padrao',Q)

def deep_q_learning_(): #fitness function
	#trocar de um bird para multiples birdows
	#basicamente um loop que vai criar todos os birds de uma poplação e também associar a cada um deles seu net 
	max_iter=10000
	lambda_ = 0.9 #0.4,0.6
	D = Memory()
	model = Model()
	#model.model.load_weights('weights')
	k = 6
	data = []
	total_reward = 0
	weight_updates = 0
	epsilon = 0.8
	games = 1
	for i in range(max_iter):
		#print(i)
		#if i > 200 and epsilon <= 0.95:
		#	epsilon += 0.5
		collide = False
		collide_out = False
		birds = []
		birds.append(Bird(230,350))
		base = Base(730)
		pipes = [Pipe(600)]
		recorde = False
		try:
			score_path = resource_path('data/score.txt')
			d = shelve.open(score_path)  # here you will save the score variable   
			high_score = d['score']         # thats all, now it is saved on disk.
			d.close()
		except:
			high_score = 0

		win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) #criar janela do pygame
		clock = pygame.time.Clock()
		run = True
		score = 0
		begin = time.time()
		j=1
		while run:
			passed = False
			clock.tick(240)
			#s = [int(birds[0].y),int(abs(birds[0].y - pipes[-1].height)),int(abs(birds[0].y - pipes[-1].bottom))]
			s = [birds[0].y,abs(birds[0].y - pipes[-1].height),abs(birds[0].y - pipes[-1].bottom),pipes[-1].x]
			#s = [birds[0].y,pipes[-1].height,pipes[-1].bottom]
			x = [s]
			actions = model.predict(np.array(x))
			a = select_actions(actions, epsilon)
			if a == 1:
				birds[0].jump()
			for event in pygame.event.get():
				#print('bird.y = '+str(birds[0].y))
				#print('d1 = '+str(abs(birds[0].y - pipes[-1].height)))
				#print('d2 = '+str(abs(birds[0].x - pipes[-1].x)))
				if event.type == pygame.QUIT:
					run = False
					model.model.save_weights('weights')
					pygame.quit()
					quit()
			birds[0].move()
			#s_ = [int(birds[0].y),int(abs(birds[0].y - pipes[-1].height)),int(abs(birds[0].y - pipes[-1].bottom))]
			s_ = [birds[0].y,abs(birds[0].y - pipes[-1].height),abs(birds[0].y - pipes[-1].bottom),pipes[-1].x]
			#s_ = [birds[0].y,pipes[-1].height,pipes[-1].bottom]
			#print(s)
			#precisamos agora move o bird de acordo com o seu net
			#definir qual o pipe estamos a ver
					
			add_pipe = False
			rem = []
			for pipe in pipes:
				if pipe.collide(birds[0]):
					collide = True
				if not pipe.passed and pipe.x < birds[0].x: #cheka se o bird passou o pipe e gera novo pipe
						passed = True
						pipe.passed = True
						add_pipe = True

				if pipe.x + pipe.PIPE_TOP.get_width() < 0: #pipe of the screen so need to remove
					rem.append(pipe)
				

				vel = pipe.move(begin)

			if add_pipe:
				score += 1
				if score > high_score:
					high_score = score
					recorde = True
				pipes.append(Pipe(600)) #quanto menor o valor mas rapido aparece

			for r in rem:
				pipes.remove(r)

			#check se o bird caiu no chao, ou passou do teto
			if birds[0].y + birds[0].img.get_height() >= 730 or birds[0].y < 0:
				collide_out = True

			base.move(begin)
			draw_window_solo(win, birds, pipes, base, score, high_score)
			
			r = reward_function(a,score,collide,collide_out,birds,pipes,passed,j)

			D.store(r,a,s,s_)
			#print(len(D.memory))
			#print(np.mod(j,k))
			if len(D.memory) > 5000 and np.mod(j,k) == 0:
					#print(len(D.memory))
					weight_updates += 1
					model.fit(D,lambda_)

			total_reward += r
				
			j+=1
			if weight_updates>0 and np.mod(weight_updates,100) == 0:
				#print(weight_updates)
				data.append([weight_updates,total_reward/games])
				total_reward = 0
				games = 1
				np.savetxt('data_height_64_min.csv',data,delimiter=',')
			if collide or collide_out:
				break
		if np.mod(i,250) == 0 and epsilon <= 0.95:
						epsilon += 0.01
						print('epsilon = ' + str(epsilon))
						print('games = '+ str(i))
		games += 1
	model.model.save_weights('weights') 

def run(config_path, pop, gen, win): #seta o neat de acordo com a config file
	global GEN
	GEN = 0
	if pop <= 1:
		pop = 2
	if gen <= 1:
		gen = 1
	poptext = str(pop)
	for line in fileinput.FileInput(config_path,inplace=1):
		if "pop_size              = " in line:
			line = line.rstrip()
			line = line.replace(line,"pop_size              = "+poptext+"\n")
		print (line, end = '')
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
					neat.DefaultSpeciesSet, neat.DefaultStagnation,
					config_path) 
	pop = neat.Population(config)
	pop.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	pop.add_reporter(stats)

	winner = pop.run(simula_ia, gen) #fitness func, roda por 50 gerações
	print('\nBest genome:\n{!s}'.format(winner))
	#saves best genome
	winner_path = resource_path('data/winner.pkl')
	with open(winner_path, "wb") as f:
		pickle.dump(winner, f)
		f.close()
	#load best genome
	end_simu_menu(config, win)

def end_simu_menu(config, win):
	clock = pygame.time.Clock()
	done = False
	global GEN
	while not done:
		win.blit(BACKGROUND_IMG, (0,0))
		click = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
				done = True
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True

		mx, my = pygame.mouse.get_pos() 

		text = STAT_FONT.render("Run best bird", 1, (255,255,255))
		button_test1 = pygame.Rect((WIN_WIDTH/2) - (text.get_width()/2)+110, 550,text.get_width()+20, 50)
		pygame.draw.rect(win, (144,238,144),button_test1)
		win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2)+120, 550))

		text = STAT_FONT.render("< Sim again", 1, (255,255,255))
		button_test2 = pygame.Rect(10, 550, text.get_width()+20, 50)
		pygame.draw.rect(win, (144,238,144),button_test2)
		win.blit(text, (10+10, 550))


		if button_test1.collidepoint((mx,my)):
			if click:
				winner_path = resource_path('data/winner.pkl')
				with open(winner_path, "rb") as f:
					genome = pickle.load(f)
				genomes = [(1, genome)]
				GEN = "Best Birdow"

				simula_ia(genomes, config)

		if button_test2.collidepoint((mx,my)):
			if click:
				ia_menu(win)

		pygame.display.update()
		clock.tick(60)

def lost_menu(win, bird, pipes, base, score, high_score, recorde):
	click = False
	mainClock = pygame.time.Clock()
	if recorde:
		pass
	while True:
		draw_window_solo(win, bird, pipes, base, score, high_score)
		text = STAT_FONT.render("Você perdeu!", 1, (255,255,255))
		win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), 150)) #(x,y)

		if not recorde:
			pass
			#text = STAT_FONT.render("Tu é ruim mesmo! Nem bateu seu recorde!", 1, (255,255,255))
			#win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), 300)) #(x,y)
		else:
			pass

		mx, my = pygame.mouse.get_pos() #verifica posição do mouse

		text = STAT_FONT.render("Play Again", 1, (255,255,255))
		button_test1 = pygame.Rect(25, 450, 175, 50)
		pygame.draw.rect(win, (144,238,144),button_test1)
		win.blit(text, ((25)+10, 450))
		
		text = STAT_FONT.render("Main Menu", 1, (255,255,255))
		button_test2 = pygame.Rect(25, 520, 175, 50)
		pygame.draw.rect(win, (144,238,144),button_test2) #desenha opcao 2
		win.blit(text, ((25)+10, 520))

		


		if button_test1.collidepoint((mx,my)):
			if click:
				jogo_solo()
		if button_test2.collidepoint((mx,my)):
			if click:
				main_menu()
		
		

		click = False
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
		pygame.display.update()
		mainClock.tick(15)

def player_ai_menu(win, bird, pipes, base, score, high_score, recorde, victory, genomes):
	click = False
	mainClock = pygame.time.Clock()
	if recorde:
		score_path = resource_path('data/score.txt')
		d = shelve.open(score_path)
		d['score'] = high_score   # the score is read from disk
		d.close()
	while True:
		if victory:
			draw_window_solo(win, bird, pipes, base, score, high_score)
			text = STAT_FONT.render("Você venceu! Deu sorte...", 1, (255,255,255))
			win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), 150)) #(x,y)
		else:
			draw_window_solo(win, bird, pipes, base, score, high_score)
			text = STAT_FONT.render("Você perdeu seu NABÃO!", 1, (255,255,255))
			win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), 150)) #(x,y)

		if not recorde:
			pass
			#text = STAT_FONT.render("Tu é ruim mesmo! Nem bateu seu recorde!", 1, (255,255,255))
			#win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), 300)) #(x,y)
		else:
			text = STAT_FONT.render("Parabéns!", 1, (255,255,255))
			win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), 290)) #(x,y)
			text = STAT_FONT.render("Você bateu o recorde!!!", 1, (255,255,255))
			win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), 330)) #(x,y)

		mx, my = pygame.mouse.get_pos() #verifica posição do mouse

		text = STAT_FONT.render("Play Again", 1, (255,255,255))
		button_test1 = pygame.Rect(25, 450, 175, 50)
		pygame.draw.rect(win, (144,238,144),button_test1)
		win.blit(text, ((25)+10, 450))
		
		text = STAT_FONT.render("Main Menu", 1, (255,255,255))
		button_test2 = pygame.Rect(25, 520, 175, 50)
		pygame.draw.rect(win, (144,238,144),button_test2) #desenha opcao 2
		win.blit(text, ((25)+10, 520))

		


		if button_test1.collidepoint((mx,my)):
			if click:
				player_vs_ai(genomes)
		if button_test2.collidepoint((mx,my)):
			if click:
				main_menu()
		
		

		click = False
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
		pygame.display.update()
		mainClock.tick(15)

def ia_menu(win):
	gen = 10
	pop = 15
	global MAX_SCORE
	MAX_SCORE = 20
	clock = pygame.time.Clock()
	input_box1 = InputBox(100, 100, 140, 32, "10") #pop
	input_box2 = InputBox(100, 200, 140, 32, "15") #gen
	#input_box3 = InputBox(100, 300, 140, 32, "20") #max_score
	input_boxes = [input_box1, input_box2]#, input_box3]
	done = False
	while not done:
		win.blit(BACKGROUND_IMG, (0,0))
		text = STAT_FONT.render("População", 1, (144,238,144))
		win.blit(text, (100, 55))
		text = STAT_FONT.render("Gerações", 1, (144,238,144))
		win.blit(text, (100, 155))
		#text = STAT_FONT.render("Max_Score", 1, (144,238,144))
		#win.blit(text, (100, 265))
		click = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
				done = True
			input_box1.handle_event(event)
			try:
				pop = int(input_box1.text)
			except:
				pop = 2
			input_box2.handle_event(event)
			try:
				gen = int(input_box2.text)
			except:
				gen = 1
			#input_box3.handle_event(event)
			#try:
			#	MAX_SCORE = int(input_box3.text)
			#except:
			#	MAX_SCORE = 1
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True

		mx, my = pygame.mouse.get_pos() 

		text = STAT_FONT.render("Run Sim >", 1, (255,255,255))
		button_test1 = pygame.Rect((WIN_WIDTH/2) - (text.get_width()/2)+130, 550,text.get_width()+20, 50)
		pygame.draw.rect(win, (144,238,144),button_test1)
		win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2)+140, 550))

		text = STAT_FONT.render("< Voltar", 1, (255,255,255))
		button_test2 = pygame.Rect(10, 550, text.get_width()+20, 50)
		pygame.draw.rect(win, (144,238,144),button_test2)
		win.blit(text, (10+10, 550))


		if button_test1.collidepoint((mx,my)):
			if click:
				#local_dir = os.path.dirname(__file__)
				#config_path = os.path.join(local_dir, "data/config-feedforward.txt")
				config_path = resource_path('data/config-feedforward.txt')
				run(config_path, pop, gen, win)

		if button_test2.collidepoint((mx,my)):
			if click:
				main_menu()
			


		for box in input_boxes:
			box.update()

		#screen.fill((30, 30, 30))
		for box in input_boxes:
			box.draw(win)
		pygame.display.update()
		clock.tick(60)

def player_vs_ai_menu():
	click = False
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	mainClock = pygame.time.Clock()
	bird = Bird(230,450)
	quit_game = False
	try:
		score_path = resource_path('data/score.txt')
		d = shelve.open(score_path)
		best_score = d['score'] 
		d.close()
	except:
		best_score = 0



	while True:
		win.blit(BACKGROUND_IMG, (0,0)) #desenha tela
		bird.draw(win)
		text = STAT_FONT.render("Player x IA", 1, (255,255,255))
		win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), 50)) #(x,y)

		mx, my = pygame.mouse.get_pos() #verifica posição do mouse

		if best_score >= 2 :
			text = STAT_FONT.render("Easy mode", 1, (255,255,255))
			button_test1 = pygame.Rect((WIN_WIDTH/2) - (text.get_width()/2), 150, text.get_width()+15, 50)
			pygame.draw.rect(win, (144,238,144),button_test1)
			win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2)+10, 150))
			easy_mode = True
		else:
			text = STAT_FONT.render("Easy mode", 1, (255,255,255))
			button_test1 = pygame.Rect((WIN_WIDTH/2) - (text.get_width()/2), 150, text.get_width()+15, 50)
			pygame.draw.rect(win, (156,168,156),button_test1) #desenha opcao 2
			win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2)+10, 150+10))
			text = STAT_FONT.render("unlocks at score 2", 1, (34,139,34))
			win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2)+10, 150+40))
			easy_mode = False

		
		if best_score >= 10 :
			text = STAT_FONT.render("Normal mode", 1, (255,255,255))
			button_test2 = pygame.Rect((WIN_WIDTH/2) - (text.get_width()/2), 240, text.get_width()+15, 50)
			pygame.draw.rect(win, (144,238,144),button_test2) #desenha opcao 2
			win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2)+10, 240))
			normal_mode = True
		else:
			text = STAT_FONT.render("Normal mode", 1, (255,255,255))
			button_test2 = pygame.Rect((WIN_WIDTH/2) - (text.get_width()/2), 240, text.get_width()+15, 50)
			pygame.draw.rect(win, (156,168,156),button_test2) #desenha opcao 2
			win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2)+10, 240))
			text = STAT_FONT.render("unlocks at score 10", 1, (34,139,34))
			win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2)+10, 240+40))
			normal_mode = False


		if best_score >= 25 :
			text = STAT_FONT.render("Impossible mode", 1, (255,255,255))
			button_test3 = pygame.Rect((WIN_WIDTH/2) - (text.get_width()/2), 330,text.get_width()+15, 50)
			pygame.draw.rect(win, (144,238,144),button_test3) #desenha opcao 2
			win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2)+10, 330))
			imp_mode = True
		else:
			text = STAT_FONT.render("Impossible mode", 1, (255,255,255))
			button_test3 = pygame.Rect((WIN_WIDTH/2) - (text.get_width()/2), 330, text.get_width()+15, 50)
			pygame.draw.rect(win, (156,168,156),button_test3) #desenha opcao 2
			win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2)+10, 330))
			text = STAT_FONT.render("unlocks at score 25", 1, (34,139,34))
			win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2)+10, 330+40))
			imp_mode = False


		text = STAT_FONT.render("< Voltar", 1, (255,255,255))
		button_test4 = pygame.Rect(10, 550, text.get_width()+20, 50)
		pygame.draw.rect(win, (144,238,144),button_test4)
		win.blit(text, (10+10, 550))

		if button_test1.collidepoint((mx,my)) and easy_mode:
			if click:
				easy_path = resource_path('data/easy.pkl')
				with open(easy_path, "rb") as f:
					genome = pickle.load(f)
					genomes = [(1, genome)]
				player_vs_ai(genomes)
		if button_test2.collidepoint((mx,my)) and normal_mode:
			if click:
				normal_path = resource_path('data/normal.pkl')
				with open(normal_path, "rb") as f:
					genome = pickle.load(f)
					genomes = [(1, genome)]
				player_vs_ai(genomes)
		if button_test3.collidepoint((mx,my)) and imp_mode:
			if click:
				imp_path = resource_path('data/impossible.pkl')
				with open(imp_path, "rb") as f:
					genome = pickle.load(f)
					genomes = [(1, genome)]
				player_vs_ai(genomes)
		if button_test4.collidepoint((mx,my)):
			if click:
				main_menu()
		
		click = False
		for event in pygame.event.get():
			if event.type == QUIT or quit_game:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
		pygame.display.update()
		mainClock.tick(60)


def main_menu():
	#disable_eager_execution()
	click = False
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	mainClock = pygame.time.Clock()
	bird = Bird(WIN_WIDTH/2,400)
	quit_game = False
	try:
		score_path = resource_path('data/score.txt')
		d = shelve.open('data/score.txt')
		best_score = d['score'] 
		d.close()
	except:
		best_score = 0


	while True:
		y_position = 50
		space = 70
		win.blit(BACKGROUND_IMG, (0,0)) #desenha tela
		bird.draw(win)
		text = STAT_FONT.render("AI plays Flappy Bird", 0.5, (255,255,255))
		win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), y_position)) #(x,y)
		y_position += space  
		mx, my = pygame.mouse.get_pos() #verifica posição do mouse

		text = STAT_FONT.render("Solo Mode", 1, (255,255,255))
		text_cent = text
		button_test1 = pygame.Rect((WIN_WIDTH/2) - (text.get_width()/2), y_position, text.get_width(), 40)
		pygame.draw.rect(win, (144,238,144),button_test1)
		win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), y_position))
		y_position += space
		
		#text = STAT_FONT.render("Simula AI", 1, (255,255,255))
		#button_test2 = pygame.Rect((WIN_WIDTH/2) - (text_cent.get_width()/2), 220, 175, 40)
		#pygame.draw.rect(win, (144,238,144),button_test2) #desenha opcao 2
		#win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), 220))
		#if best_score >= 2:
		#	text = STAT_FONT.render("Play vs AI", 1, (255,255,255))
		#	button_test4 = pygame.Rect((WIN_WIDTH/2) - (text_cent .get_width()/2), 290, 175, 40)
		#	pygame.draw.rect(win, (144,238,144),button_test4) #desenha opcao 2
		#	win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), 290))
		#	jogar_ai = True
		#else:
		#	text = STAT_FONT.render("Play vs AI", 1, (255,255,255))
		#	button_test4 = pygame.Rect((WIN_WIDTH/2) - (text_cent .get_width()/2), 290, 175, 40)
		#	pygame.draw.rect(win, (156,168,156),button_test4) #desenha opcao 2
		#	win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2)+10, 290))
		#	text = STAT_FONT.render("unlocks at score 2", 1, (34,139,34))
		#	win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), 290+40))
		#	jogar_ai = False

		text = STAT_FONT.render("Q Learning", 1, (255,255,255))
		text_cent = text
		button_test5 = pygame.Rect((WIN_WIDTH/2) - (text.get_width()/2), y_position, text.get_width(), 40)
		pygame.draw.rect(win, (144,238,144),button_test5)
		win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), y_position))
		y_position += space
		text = STAT_FONT.render("Deep Q Learning", 1, (255,255,255))
		text_cent = text
		button_test6 = pygame.Rect((WIN_WIDTH/2) - (text.get_width()/2), y_position, text.get_width(), 40)
		pygame.draw.rect(win, (156,168,156),button_test6)
		win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), y_position))
		y_position += space
		text = STAT_FONT.render("Quit Game", 1, (255,255,255))
		button_test3 = pygame.Rect((WIN_WIDTH/2) - (text.get_width()/2), y_position, text.get_width(), 40)
		pygame.draw.rect(win, (144,238,144),button_test3) #desenha opcao 2
		win.blit(text, ((WIN_WIDTH/2) - (text.get_width()/2), y_position))
		y_position += space

		if button_test1.collidepoint((mx,my)):
			if click:
				jogo_solo()
		#if button_test2.collidepoint((mx,my)):
		#	if click:
		#		ia_menu(win)
		if button_test3.collidepoint((mx,my)):
			if click:
				quit_game = True 
		#if button_test4.collidepoint((mx,my)) and jogar_ai:
		#	if click:
		#		player_vs_ai_menu()
		if button_test5.collidepoint((mx,my)):
			if click:
				q_learning()
		if button_test6.collidepoint((mx,my)):
			if click:
				deep_q_learning()

		
		click = False
		for event in pygame.event.get():
			if event.type == QUIT or quit_game:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
		pygame.display.update()
		mainClock.tick(60)
		
if __name__ == '__main__':
	main_menu()
