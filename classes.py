# Class for User
class User:
	def __init__(self, index, user_id,age,gender,occupation,zip_code):
		self.index = index
		self.user_id = user_id
		self.age = age
		self.gender = gender
		self.occupation = occupation
		self.zip_code = zip_code

# Class for Movie
class Movie:
	def __init__(self,index, movie_id,title,release_date, video_release_date,imdb_url,genre_vector):
		self.index = index
		self.movie_id = movie_id
		self.title = title
		self.release_date = release_date
		self.video_release_date = video_release_date
		self.imdb_url = imdb_url
		self.genre_vector = genre_vector

# Class for association
class Rating:
	def __init__(self, user_id, movie_id, rating, timestamp):
		self.user_id = user_id
		self.movie_id = movie_id
		self.rating = rating
		self.timestamp = timestamp

# Parse user data , returns list of User objects
def parse_users(filename):
	users = []
	with open(filename, encoding='iso-8859-1') as f:
		for row in f.readlines():
			row = row.strip('\n')
			r = row.split('|')
			users.append(User(len(users),int(r[0]),int(r[1]),r[2],r[3],r[4]))
	return users

# Parse movie data , returns list of movie objects
def parse_movies(filename):
	movies = []
	with open(filename, encoding='iso-8859-1') as f:
		for row in f.readlines():
			row = row.strip('\n')
			r = row.split('|')
			movies.append(Movie(len(movies),int(r[0]),r[1],r[2],r[3],r[4],list(map(int,r[5:]))))
	return movies

# Parse rating data , returns list of rating objects
def parse_ratings(filename):
	ratings = []
	with open(filename, encoding='iso-8859-1') as f:
		for row in f.readlines():
			row = row.strip('\n')
			r = row.split('\t')
			ratings.append(Rating(int(r[0]),int(r[1]),int(r[2]), int(r[3])))
	return ratings

def user_item_matrix(users, movies, ratings):
	d_users = {}
	d_movies = {}
	for user in users:
		d_users[user.user_id] = user
	for movie in movies:
		d_movies[movie.movie_id] = movie

	matrix = [[0 for i in range(len(movies))] for i in range(len(users))]
	for rating in ratings:
		matrix[d_users[rating.user_id].index][d_movies[rating.movie_id].index] = rating.rating
	return matrix

def user_category_matrix(users, movies, ratings, categories):
	d_users = {}
	d_movies = {}
	for user in users:
		d_users[user.user_id] = user
	for movie in movies:
		d_movies[movie.movie_id] = movie

	matrix = [[[0,0] for i in range(len(categories))] for i in range(len(users))]
	for rating in ratings:
		user_index = d_users[rating.user_id].index
		for i in range(len(d_movies[rating.movie_id].genre_vector)):
			if d_movies[rating.movie_id].genre_vector[i] == 1:
				if rating.rating >= 3:
					matrix[user_index][i][0] += 1
				else:
					matrix[user_index][i][1] += 1
	return matrix

def item_category_matrix(movies):
	return list(map(lambda x: x.genre_vector, movies))