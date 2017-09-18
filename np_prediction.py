from classes import *
from functools import reduce
from math import sqrt
import numpy as np

def cosine(A):
	cross = np.dot(A, A.T)
	norm = np.sqrt(np.diag(cross))
	c = []
	with np.errstate(divide='ignore', invalid='ignore'):
		c = np.true_divide(cross, np.outer(norm, norm))
		c[ ~ np.isfinite( c )] = 0 
	return c

def significant(A, t = 50):
	B = (A > 0).astype(int)
	cross = np.dot(B, B.T)
	cross[cross > t] = t
	cross = cross / t
	return cross * cosine(A)

class RatingPredictor:
	users = []
	items = []
	ratings = []
	categories = []
	item_variance = []
	user_user_similarity = None
	user_significant_similarity = None
	item_item_similarity = None
	def __init__(self, users_path, items_path,  categories_path, ratings_path):
		# Import data
		self.users = parse_users(users_path)
		self.items = parse_movies(items_path)
		self.ratings = parse_ratings(ratings_path)
		self.categories = list(map(lambda x: x.split('|')[0], open(categories_path).readlines()))
		# Create User-item rating matrix
		self.user_item_rating_matrix = np.array(user_item_matrix(self.users, self.items, self.ratings))
		self.user_item_mask_matrix = self.user_item_rating_matrix > 0
		self.item_user_rating_matrix = self.user_item_rating_matrix.T
		self.item_user_mask_matrix = self.user_item_mask_matrix.T
		# Create User-category matrix
		self.user_category_rating_matrix = np.array(user_category_matrix(self.users, self.items, self.ratings, self.categories))
		# Create Item-category matrix
		self.item_category_rating_matrix = np.array(item_category_matrix(self.items))

		# Calculate User average matrix
		self.user_average_rating = np.ma.mean(np.ma.MaskedArray(self.user_item_rating_matrix, ~self.user_item_mask_matrix),axis=1)
		# Calculate Item average matrix
		self.item_average_rating = np.ma.mean(np.ma.MaskedArray(self.item_user_rating_matrix, ~self.item_user_mask_matrix),axis=1)
	
	def user_explicit(self, userid, itemid):
		if self.user_user_similarity is None:
			# Calculate User-User similarity
			self.user_user_similarity = cosine(self.user_item_rating_matrix)

		if self.user_item_rating_matrix[userid][itemid] > 0:
			return self.user_item_rating_matrix[userid][itemid]
		#Set default
		rating = self.user_average_rating[userid]
		#Neighborhood
		mask = self.item_user_mask_matrix[itemid].astype(int)
		
		k = mask * self.user_user_similarity[userid]
		v = mask * (self.item_user_rating_matrix[itemid] - rating)
		
		if np.sum(np.absolute(k)) > 0:
			rating += np.dot(k,v) / np.sum(np.absolute(k))
		if rating < 1:
			return 1
		if rating > 5:
			return 5
		return rating

	def user_significance(self, userid, itemid, threshold):
		if self.user_significant_similarity is None:
			# Calculate User-User significance similarity
			self.user_significant_similarity = significant(self.user_item_rating_matrix, threshold)

		if self.user_item_rating_matrix[userid][itemid] > 0:
			return self.user_item_rating_matrix[userid][itemid]
		#Set default
		rating = self.user_average_rating[userid]
		#Neighborhood
		mask = self.item_user_mask_matrix[itemid].astype(int)
		
		k = mask * self.user_significant_similarity[userid]
		v = mask * (self.item_user_rating_matrix[itemid] - rating)
		
		if np.sum(np.absolute(k)) > 0:
			rating += np.dot(k,v) / np.sum(np.absolute(k))
		if rating < 1:
			return 1
		if rating > 5:
			return 5
		return rating

	def item_explicit(self, userid, itemid):
		if self.item_item_similarity is None:
			# Calculate Item-Item similarity
			self.item_item_similarity = cosine(self.user_item_rating_matrix.T)
		
		if self.user_item_rating_matrix[userid][itemid] > 0:
			return self.user_item_rating_matrix[userid][itemid]
		#Set default
		rating = self.item_average_rating[userid]
		#Neighborhood
		mask = np.dot(self.item_user_mask_matrix[itemid].astype(int),self.user_item_mask_matrix)
		mask = (mask == np.sum(self.item_user_mask_matrix[itemid].astype(int)))
		
		k = mask * self.item_item_similarity[itemid]
		v = mask * (self.user_item_rating_matrix[userid] - rating)
		
		if np.sum(np.absolute(k)) > 0:
			rating += np.dot(k,v) / np.sum(np.absolute(k))
		if rating < 1:
			return 1
		if rating > 5:
			return 5
		return rating

