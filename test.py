#TEST
import np_prediction as pred
import numpy as np
from sys import argv
from scipy.spatial.distance import cosine as cos

method = 'random'
num_neighbors = 50
threshold = 0.5
DATASET = 'ml-100k'
if len(argv) > 1:
	method = argv[1]
if len(argv) > 2:
	num_neighbors = int(argv[2])
if len(argv) > 3:
	threshold = float(argv[3])

# Rating Predictors
rating_predictors = []
# print("[START] Creating Predictors")
for i in range(1,6):
	rating_predictors.append(pred.RatingPredictor(users_path=DATASET+'/u.user',items_path=DATASET+'/u.item',categories_path=DATASET+'/u.genre',ratings_path=DATASET+'/u'+str(i)+'.base'))


def run_test(rating_predictor, testset_path, method='explicit_user'):
	# Get Test Data
	test_ratings = pred.parse_ratings(testset_path)
	mean_error = 0
	count = 0
	for rating in test_ratings:
		count += 1
		predicted_value = 0

		if method == 'explicit_user':
			predicted_value = rating_predictor.user_explicit(rating.user_id - 1,rating.movie_id - 1)
		elif method == 'explicit_item':
			predicted_value = rating_predictor.item_explicit(rating.user_id - 1,rating.movie_id - 1)
		elif method == 'significance_weight':
			predicted_value = rating_predictor.user_significance(rating.user_id - 1,rating.movie_id - 1, 50)

		actual_value = rating.rating

		mean_error += abs(predicted_value-actual_value)
	return mean_error / (count * (5 - 1))

#Run tests
test_results = []
for i in range(5):
	print("[START] testset %d" % (i))
	test_result = run_test(rating_predictors[i],DATASET+'/u'+str(i + 1)+'.test',method)
	print("[END] testset %d, NMAE: %.6f" % (i, test_result))
	test_results.append(test_result)

cross_validation_error = sum(test_results) / len(test_results)
test_results.append(cross_validation_error)
#print(','.join(list(map(str,test_results))))
print("Average NMAE: ", cross_validation_error)