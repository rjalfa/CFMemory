from prediction import *
from sys import argv
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
	rating_predictors.append(RatingPredictor(users_path=DATASET+'/u.user',items_path=DATASET+'/u.item',categories_path=DATASET+'/u.genre',ratings_path=DATASET+'/u'+str(i)+'.base'))
# print("[END] Creating Predictors")

def run_test(rating_predictor, testset_path, method='explicit_user'):
	# Get Test Data
	test_ratings = parse_ratings(testset_path)
	# print("\t[INFO] Number of tests: ", len(test_ratings))
	#MAE error
	#max_error = 0
	#min_error = 1000
	mean_error = 0
	count = 0
	#print(len(rating_predictor.users),len(rating_predictor.items))
	for rating in test_ratings:
		count += 1
		predicted_value = 0

		if method == 'explicit_user':
			predicted_value = rating_predictor.prediction_explicit_user(rating_predictor.users[rating.user_id - 1], rating_predictor.items[rating.movie_id - 1])
		elif method == 'implicit_user':
			predicted_value = rating_predictor.prediction_implicit_user(rating_predictor.users[rating.user_id - 1], rating_predictor.items[rating.movie_id - 1])
		elif method == 'explicit_item':
			predicted_value = rating_predictor.prediction_explicit_item(rating_predictor.users[rating.user_id - 1], rating_predictor.items[rating.movie_id - 1])
		elif method == 'implicit_item':
			predicted_value = rating_predictor.prediction_implicit_item(rating_predictor.users[rating.user_id - 1], rating_predictor.items[rating.movie_id - 1])
		elif method == 'significance_weight':
			predicted_value = rating_predictor.prediction_significance_weight(rating_predictor.users[rating.user_id - 1], rating_predictor.items[rating.movie_id - 1], num_neighbors)
		elif method == 'variance_weight':
			predicted_value = rating_predictor.prediction_variance_weight(rating_predictor.users[rating.user_id - 1], rating_predictor.items[rating.movie_id - 1])
		elif method == 'nearest_neighbor':
			predicted_value = rating_predictor.prediction_nearest_neighbor(rating_predictor.users[rating.user_id - 1], rating_predictor.items[rating.movie_id - 1], threshold, num_neighbors)
		else:
			predicted_value = rating_predictor.prediction_random(rating_predictor.users[rating.user_id - 1], rating_predictor.items[rating.movie_id - 1])
		
		actual_value = rating.rating
		#max_error = max(max_error,abs(predicted_value-actual_value))
		#min_error = min(min_error,abs(predicted_value-actual_value))
		mean_error += abs(predicted_value-actual_value)
		# if count % 10000 == 0:
			# print("\t\t[INFO] Count: ",count)
	return mean_error / (count * (5 - 1))


# Run tests
test_results = []
for i in range(5):
	# print("[START] testset %d" % (i))
	test_result = run_test(rating_predictors[i],DATASET+'/u'+str(i + 1)+'.test',method)
	# print("[END] testset %d, NMAE: %.6f" % (i, test_result))
	test_results.append(test_result)

cross_validation_error = sum(test_results) / len(test_results)
test_results.append(cross_validation_error)
print(','.join(list(map(str,test_results))))
# print("Average NMAE: ", cross_validation_error)
