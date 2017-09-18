from prediction import *

s = [0,0,0,0,0]
c = 0


rating_predictor = RatingPredictor(users_path='ml-100k/u.user',items_path='ml-100k/u.item',categories_path='ml-100k/u.genre',ratings_path='ml-100k/u.data')

# for user in rating_predictor.users:
# 	for item in rating_predictor.items:
# 		actual_value = rating_predictor.user_item_rating_matrix[user.index][item.index]
# 		if actual_value > 0:
# 			c += 1
# 			s[0] += abs(rating_predictor.prediction_explicit_user(user,item)-actual_value)
# 			s[1] += abs(rating_predictor.prediction_explicit_user_category_boosted(user,item)-actual_value)
# 			s[2] += abs(rating_predictor.prediction_implicit_user(user,item)-actual_value)
# 			s[3] += abs(rating_predictor.prediction_explicit_item(user,item)-actual_value)
# 			s[4] += abs(rating_predictor.prediction_implicit_item(user,item)-actual_value)
# 			print(s[0]/c,s[1]/c,s[2]/c,s[3]/c,s[4]/c)