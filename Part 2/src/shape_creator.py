import pymunk as pm
# Импортируем класс DooFree из файла doo.py
from doo import DooFree

class ShapeCreator():
	'''
	Класс, содержащий методы для создания и удаления объектов разных типов.'''

	def __init__(self, world, space):
		# В качестве атрибутов задаем пространство симуляции и игровую область.
		self.world = world
		self.space = space
		

	def create_free_doo(self, x, y):
		'''
		Функция для создания свободного Ду.'''
		free_doo = DooFree(x,y)
		# В основе Ду лежит динамическое тело, поэтому
		# в пространство симуляции добавляем и тело, и его форму.
		self.space.add(free_doo.body,free_doo)
		# Добавляем нового Ду в массив free_do для дальнейшего использования
		self.world.free_doos.append(free_doo)

	def remove_escaped_doos(self):
		'''
		Функция для удаления Ду, вышедших за границы игровой области.'''
		for doo in self.world.free_doos:
			if doo.body.position.x < 0 or doo.body.position.x > self.world.width:
				# Необходимо удалить и тело (Body) и его форму. Автоматически форма не удалится.
				self.world.free_doos.remove(doo)
				self.space.remove(doo.body, doo)
			elif doo.body.position.y > self.world.height:
				self.world.free_doos.remove(doo)
				self.space.remove(doo.body, doo)

	def remove_all_doos(self):
		'''
		Функция для удаления всех Ду. Используется для рестарта игры.'''
		# Очищаем переменную shape_being_dragged
		self.world.shape_being_dragged = None

		# Удаляем созданных Ду
		for free_doo in self.world.free_doos:
			# Удаляем Ду из физической симуляции
			self.space.remove(free_doo.body, free_doo)
		# Очищаем список
		self.world.free_doos.clear()

	def create_static_floor(self,height=15,friction=10):
		'''
		Создания пола, т.е. нижней границы игровой области.'''
		# Создаем статичное тело (т.к. пол не будет двигаться)
		body = pm.Body(body_type = pm.Body.STATIC)
		body.position = [self.world.width/2, self.world.ground_y]
		semiwidth = self.world.width/2
		# Вершины многоугольника
		vs = [(-semiwidth,0),(semiwidth,0),(-semiwidth,height),(semiwidth,height)]
		# Создаем объект Poly и привязываем его к статичному телу
		poly = pm.Poly(body,vs)
		# Переопределяем некоторые параметры
		poly.friction = friction
		poly.collision_type = 2
		# Добавляем пол в пространство симуляции (в игру). ТОЛЬКО форму Poly.
		# Для статических тел объект класса Body не добавляется в пространство симуляции!
		self.space.add(poly)

	def create_static_wall(self, x, y, width=1, friction=100):
		'''
		Функция для создания вертикальных стен, которые буду боковыми границами
		игровой области.'''
		body = pm.Body(body_type = pm.Body.STATIC)
		body.position = [x,y]
		# Стены будут отрезками линий, для этого создадим форму pm.Segment
		line = pm.Segment(body,(0,0),(0,-self.world.height), width)
		line.friction = friction
		line.collision_type = 3
		self.space.add(line)