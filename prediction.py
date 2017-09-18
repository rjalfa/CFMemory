from classes import *
from functools import reduce
from math import sqrt

def cosine(a, b):
	dot_product = sum(map(lambda x:x[0]*x[1],zip(a,b)))
	mod_a = sqrt(reduce(lambda x,y: x + y*y, a, 0.0))
	mod_b = sqrt(reduce(lambda x,y: x + y*y,b, 0.0))
	if mod_a == 0 or mod_b == 0:
		return 0
	return dot_product / (mod_a * mod_b)

#Calculates the pearson correlation coefficient of two lists with given means
def pearson_correlation_ext(a, b, a_bar, b_bar, c = []):
	if len(a) != len(b):
		return 0
	n = len(a)
	if n == 0:
		return 0
	c_len = len(c)
	numerator = 0
	denominator1 = 0
	denominator2 = 0
	for i in range(n):
		if c_len != 0:
			numerator += c[i] * (a[i] - a_bar) * (b[i] - b_bar)
		else:
			numerator += (a[i] - a_bar) * (b[i] - b_bar)
		denominator1 += (a[i] - a_bar)**2
		denominator2 += (b[i] - b_bar)**2
	try:
		# print(numerator, (sqrt(denominator1) * sqrt(denominator2)))
		return numerator / (sqrt(denominator1) * sqrt(denominator2))
	except:
		return 0

#Calculates the pearson correlation coefficient of two lists
def pearson_correlation(a, b, c = []):
	#return cosine(a,b)
	
	if len(a) != len(b):
		return 0
	n = len(a)
	if n == 0:
		return 0
	a_bar = sum(a) / len(a)
	b_bar = sum(b) / len(b)
	return pearson_correlation_ext(a, b, a_bar, b_bar, c)

def clamp(a,b,c):
	if a > c:
		return c
	elif a < b:
		return b
	return a

class RatingPredictor:
	users = []
	items = []
	ratings = []
	categories = []
	item_variance = []
	# For Speed!!!
	user_average_rating_cache = {}
	item_average_rating_cache = {}
	similarity_explicit_user_cache = {}
	similarity_implicit_user_cache = {}
	similarity_explicit_item_cache = {}
	similarity_implicit_item_cache = {}
	significance_weight_cache = {}
	variance_weight_cache = {}
	def __init__(self, users_path, items_path,  categories_path, ratings_path):
		# Import data
		self.users = parse_users(users_path)
		self.items = parse_movies(items_path)
		self.ratings = parse_ratings(ratings_path)
		self.categories = list(map(lambda x: x.split('|')[0], open(categories_path).readlines()))
		# Create User-item rating matrix
		self.user_item_rating_matrix = user_item_matrix(self.users, self.items, self.ratings)
		# Create User-category matrix
		self.user_category_rating_matrix = user_category_matrix(self.users, self.items, self.ratings, self.categories)
		# Create Item-category matrix
		self.item_category_rating_matrix = item_category_matrix(self.items)
		# Create Normalized Item Variance
		self.item_variance = [self.item_variance_rating(item) for item in self.items]
		max_item_variance = max(self.item_variance)
		min_item_variance = min(self.item_variance)
		self.item_variance = list(map(lambda x: (x-min_item_variance)/max_item_variance, self.item_variance))

	def user_average_rating(self,user_x):
		if user_x.index not in self.user_average_rating_cache:
			l = list(filter(lambda x:x>0, self.user_item_rating_matrix[user_x.index]))
			if len(l) == 0:
				self.user_average_rating_cache[user_x.index] = 3
			else:
				self.user_average_rating_cache[user_x.index] = sum(l)/len(l)
		return self.user_average_rating_cache[user_x.index]

	def user_average_rating_category(self,user_x,item_y):
		l = []
		for i in range(len(self.user_item_rating_matrix[user_x.index])):
			if self.user_item_rating_matrix[user_x.index][i] > 0 and cosine(self.item_category_rating_matrix[i],self.item_category_rating_matrix[item_y.index]) > 0:
				l.append(self.user_item_rating_matrix[user_x.index][i])
		if len(l) == 0:
			return 3
		return sum(l)/len(l)

	def item_average_rating(self,item_y):
		if item_y.index not in self.item_average_rating_cache:
			l = list(filter(lambda x:x>0, [self.user_item_rating_matrix[i][item_y.index] for i in range(len(self.user_item_rating_matrix))]))
			if len(l) == 0:
				self.item_average_rating_cache[item_y.index] = 3
			else:
				self.item_average_rating_cache[item_y.index] = sum(l)/len(l)
		return self.item_average_rating_cache[item_y.index]

	def item_variance_rating(self,item_y):
		l = list(filter(lambda x:x>0, [self.user_item_rating_matrix[i][item_y.index] for i in range(len(self.user_item_rating_matrix))]))
		r_bar = self.item_average_rating(item_y)
		s = 0
		for i in l:
			s += (i-r_bar)**2
		if len(l) < 2:
			return 0
		else:
			return sqrt(s/(len(l)-1))

	# Similarity Metrics
	# User based, Explicit Rating
	def similarity_explicit_user(self,user_x, user_y):
		if user_x.index > user_y.index:
			return self.similarity_explicit_user(user_y, user_x)
		if (user_x.index,user_y.index) not in self.similarity_explicit_user_cache:
			user_x_explicit_ratings = []
			user_y_explicit_ratings = []
			user_x_mean = self.user_average_rating(user_x)
			user_y_mean = self.user_average_rating(user_y)
			n = len(self.user_item_rating_matrix[user_x.index])
			for i in range(n):
				# If both have rated
				if self.user_item_rating_matrix[user_x.index][i] > 0 and self.user_item_rating_matrix[user_y.index][i] > 0:
					user_x_explicit_ratings.append(self.user_item_rating_matrix[user_x.index][i])
					user_y_explicit_ratings.append(self.user_item_rating_matrix[user_y.index][i])
			self.similarity_explicit_user_cache[(user_x.index,user_y.index)] = pearson_correlation(user_x_explicit_ratings, user_y_explicit_ratings)#, user_x_mean, user_y_mean)
		return self.similarity_explicit_user_cache[(user_x.index,user_y.index)]

	# User based, Implicit Rating
	def similarity_implicit_user(self, user_x, user_y):
		if user_x.index > user_y.index:
			return self.similarity_implicit_user(user_y, user_x)
		if (user_x.index,user_y.index) not in self.similarity_implicit_user_cache:
			user_x_implicit_ratings = []
			user_y_implicit_ratings = []
			for i in range(len(self.user_category_rating_matrix[user_x.index])):
				cxy_1 = self.user_category_rating_matrix[user_x.index][i][0] + self.user_category_rating_matrix[user_x.index][i][1]
				cxy_2 = self.user_category_rating_matrix[user_y.index][i][0] + self.user_category_rating_matrix[user_y.index][i][1]
				if cxy_1 > 0:
					user_x_implicit_ratings.append(self.user_category_rating_matrix[user_x.index][i][0]/cxy_1 * 10)
				else:
					user_x_implicit_ratings.append(5.5)
				if cxy_2 > 0:
					user_y_implicit_ratings.append(self.user_category_rating_matrix[user_y.index][i][0]/cxy_2 * 10)
				else:
					user_y_implicit_ratings.append(5.5)
			self.similarity_implicit_user_cache[(user_x.index,user_y.index)] = pearson_correlation(user_x_implicit_ratings, user_y_implicit_ratings)
		return self.similarity_implicit_user_cache[(user_x.index,user_y.index)]

	# Item based, Explicit Rating
	def similarity_explicit_item(self, item_x, item_y):
		if item_x.index > item_y.index:
			return self.similarity_explicit_item(item_y, item_x)
		if (item_x.index,item_y.index) not in self.similarity_explicit_item_cache:
			item_x_explicit_ratings = []
			item_y_explicit_ratings = []
			item_x_mean = self.item_average_rating(item_x)
			item_y_mean = self.item_average_rating(item_y)
			n = len(self.user_item_rating_matrix)
			for i in range(n):
				# If both have rated
				if self.user_item_rating_matrix[i][item_x.index] > 0 and self.user_item_rating_matrix[i][item_y.index] > 0:
					item_x_explicit_ratings.append(self.user_item_rating_matrix[i][item_x.index])
					item_y_explicit_ratings.append(self.user_item_rating_matrix[i][item_y.index])
			self.similarity_explicit_item_cache[(item_x.index,item_y.index)] = pearson_correlation_ext(item_x_explicit_ratings, item_y_explicit_ratings, item_x_mean, item_y_mean)
		return self.similarity_explicit_item_cache[(item_x.index,item_y.index)]

	# Item based, Implicit Rating
	def similarity_implicit_item(self, item_x, item_y):
		if item_x.index > item_y.index:
			return self.similarity_implicit_item(item_y, item_x)
		if (item_x.index,item_y.index) not in self.similarity_implicit_item_cache:
			item_x_implicit_ratings = []
			item_y_implicit_ratings = []
			for i in range(len(self.item_category_rating_matrix[item_x.index])):
				item_x_implicit_ratings.append(self.item_category_rating_matrix[item_x.index][i])
				item_y_implicit_ratings.append(self.item_category_rating_matrix[item_y.index][i])
			self.similarity_implicit_item_cache[(item_x.index,item_y.index)] = pearson_correlation(item_x_implicit_ratings, item_y_implicit_ratings)
		return self.similarity_implicit_item_cache[(item_x.index,item_y.index)]

	# Significance Weight of User Y and User X
	def significance_weight(self, user_x, user_y):
		if user_x.index > user_y.index:
			return self.significance_weight(user_y, user_x)
		if (user_x.index,user_y.index) not in self.significance_weight_cache:
			count = 0
			for i in range(len(self.user_item_rating_matrix[user_x.index])):
				if self.user_item_rating_matrix[user_x.index][i] > 0 and self.user_item_rating_matrix[user_y.index][i] > 0:
					count += 1
			self.significance_weight_cache[(user_x.index,user_y.index)] = self.similarity_explicit_user(user_x, user_y)*clamp(count/50, 0, 1)
		return self.significance_weight_cache[(user_x.index,user_y.index)]

	# Variance Weight of User Y and User X
	def variance_weight(self,user_x, user_y):
		if user_x.index > user_y.index:
			return self.variance_weight(user_y, user_x)
		if (user_x.index,user_y.index) not in self.variance_weight_cache:
			user_x_explicit_ratings = []
			user_y_explicit_ratings = []
			common_item_variance_ratings = []
			user_x_mean = self.user_average_rating(user_x)
			user_y_mean = self.user_average_rating(user_y)
			n = len(self.user_item_rating_matrix[user_x.index])
			for i in range(n):
				# If both have rated
				if self.user_item_rating_matrix[user_x.index][i] > 0 and self.user_item_rating_matrix[user_y.index][i] > 0:
					user_x_explicit_ratings.append(self.user_item_rating_matrix[user_x.index][i])
					user_y_explicit_ratings.append(self.user_item_rating_matrix[user_y.index][i])
					common_item_variance_ratings.append(self.item_variance[i])
			if sum(common_item_variance_ratings) == 0:
				self.variance_weight_cache[(user_x.index,user_y.index)] = 0
			else:
				self.variance_weight_cache[(user_x.index,user_y.index)] = pearson_correlation_ext(user_x_explicit_ratings, user_y_explicit_ratings, user_x_mean, user_y_mean, common_item_variance_ratings)/sum(common_item_variance_ratings)
		return self.variance_weight_cache[(user_x.index,user_y.index)]

	# Filter Neighbors based on weight_threshold and number of neighbors reqd.
	def nearest_neighbors(self, user_x, item_y, weight_threshold, num_neighbors):
		sm = []
		for i in range(len(self.users)):
			if i == user_x.index:
				continue
			if self.user_item_rating_matrix[i][item_y.index] == 0:
				continue
			s = abs(self.significance_weight(user_x, self.users[i]))
			if s >= weight_threshold:
				sm.append((s,i))
		sm.sort(reverse=True)
		sm = sm[:num_neighbors]
		ret = []
		for (x,y) in sm:
			ret.append(y)
		return ret


	# Prediction Metrics
	# Random
	def prediction_random(self, user_x, item_y):
		import random
		return random.uniform(1,5)

	# UB-ER
	def prediction_explicit_user(self, user_x, item_y):
		r_ux = self.user_average_rating(user_x)
		
		numerator = 0
		denominator = 0
		n = len(self.user_item_rating_matrix)
		for i in range(n):
			if i == user_x.index:
				continue
			# If the user has rated the item
			if self.user_item_rating_matrix[i][item_y.index] > 0:
				kah = self.similarity_explicit_user(user_x,self.users[i])
				denominator += abs(kah)
				r_uh = self.user_average_rating(self.users[i])
				numerator += kah * (self.user_item_rating_matrix[i][item_y.index] - r_uh)
		if denominator == 0:
			return clamp(r_ux,1,5)
		return clamp(r_ux + (numerator / denominator), 1, 5)

	# UB-ER-CB
	def prediction_explicit_user_category_boosted(self, user_x, item_y):
		r_ux = self.user_average_rating(user_x)
		
		numerator = 0
		denominator = 0
		n = len(self.user_item_rating_matrix)
		for i in range(n):
			if i == user_x.index:
				continue
			# If the user has rated the item and the items in average has one of the categories as the active item
			if self.user_item_rating_matrix[i][item_y.index] > 0:
				kah = self.similarity_explicit_user(user_x,self.users[i])
				denominator += abs(kah)
				r_uh = self.user_average_rating_category(self.users[i], item_y)
				numerator += kah * (self.user_item_rating_matrix[i][item_y.index] - r_uh)
		if denominator == 0:
			return clamp(r_ux,1,5)
		return clamp(r_ux + (numerator / denominator), 1, 5)
	
	# UB-IR
	def prediction_implicit_user(self, user_x, item_y):
		r_ux = self.user_average_rating(user_x)
		
		numerator = 0
		denominator = 0
		n = len(self.user_item_rating_matrix)
		for i in range(n):
			if i == user_x.index:
				continue
			# If the user has rated the item
			if self.user_item_rating_matrix[i][item_y.index] > 0:
				kah = self.similarity_implicit_user(user_x,self.users[i])
				denominator += abs(kah)
				r_uh = self.user_average_rating(self.users[i])
				numerator += kah * (self.user_item_rating_matrix[i][item_y.index] - r_uh)
		if denominator == 0:
			return clamp(r_ux,1,5)
		return clamp(r_ux + (numerator / denominator),1,5)

	# IB-ER
	def prediction_explicit_item(self, user_x, item_y):
		r_iy = self.item_average_rating(item_y)
		r_ua = self.user_average_rating(user_x)
		numerator = 0
		denominator = 0
		n = len(self.user_item_rating_matrix[0])
		for i in range(n):
			# If the user has rated the item
			if self.user_item_rating_matrix[user_x.index][i] > 0:
				kah = self.similarity_explicit_item(item_y,self.items[i])
				denominator += abs(kah)
				numerator += kah * (self.user_item_rating_matrix[user_x.index][i] - r_ua)
		if denominator == 0:
			return clamp(r_iy,1,5)
		return clamp(r_iy + (numerator / denominator), 1, 5)

	# IB-IR
	def prediction_implicit_item(self, user_x, item_y):
		r_iy = self.item_average_rating(item_y)
		r_ua = self.user_average_rating(user_x)
		numerator = 0
		denominator = 0
		n = len(self.user_item_rating_matrix[0])
		for i in range(n):
			# If the user has rated the item
			if self.user_item_rating_matrix[user_x.index][i] > 0:
				kah = self.similarity_implicit_item(item_y,self.items[i])
				denominator += abs(kah)
				numerator += kah * (self.user_item_rating_matrix[user_x.index][i] - r_ua)
		if denominator == 0:
			return clamp(r_iy,1,5)
		return clamp(r_iy + (numerator / denominator), 1, 5)

	# Significance Weighting
	def prediction_significance_weight(self, user_x, item_y, num_threshold = 50):
		r_ux = self.user_average_rating(user_x)
		
		numerator = 0
		denominator = 0
		for i in self.nearest_neighbors(user_x, item_y, 0, num_threshold):
			if i == user_x.index:
				continue
			# If the user has rated the item
			if self.user_item_rating_matrix[i][item_y.index] > 0:
				kah = self.significance_weight(user_x,self.users[i])
				denominator += abs(kah)
				r_uh = self.user_average_rating(self.users[i])
				numerator += kah * (self.user_item_rating_matrix[i][item_y.index] - r_uh)
		if denominator == 0:
			return clamp(r_ux,1,5)
		return clamp(r_ux + (numerator / denominator), 1, 5)

	# Variance Weighting
	def prediction_variance_weight(self, user_x, item_y):
		r_ux = self.user_average_rating(user_x)
		
		numerator = 0
		denominator = 0
		for i in range(len(self.users)):
			if i == user_x.index:
				continue
			# If the user has rated the item
			if self.user_item_rating_matrix[i][item_y.index] > 0:
				kah = self.variance_weight(user_x,self.users[i])
				denominator += abs(kah)
				r_uh = self.user_average_rating(self.users[i])
				numerator += kah * (self.user_item_rating_matrix[i][item_y.index] - r_uh)
		if denominator == 0:
			return clamp(r_ux,1,5)
		return clamp(r_ux + (numerator / denominator), 1, 5)

	# Nearest Neighbor
	def prediction_nearest_neighbor(self, user_x, item_y, weight_threshold = 0.1, num_neighbors = 20):
		r_ux = self.user_average_rating(user_x)
		numerator = 0
		denominator = 0
		nearest_neighbors_x = self.nearest_neighbors(user_x, item_y, weight_threshold, num_neighbors)
		# print(nearest_neighbors_x)
		for i in nearest_neighbors_x:
			# If the user has rated the item
			if self.user_item_rating_matrix[i][item_y.index] > 0:
				kah = self.similarity_explicit_user(user_x,self.users[i])
				denominator += abs(kah)
				r_uh = self.user_average_rating(self.users[i])
				numerator += kah * (self.user_item_rating_matrix[i][item_y.index] - r_uh)
		if denominator == 0:
			return clamp(r_ux,1,5)
		return clamp(r_ux + (numerator / denominator), 1, 5)
