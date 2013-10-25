import pickle
import sys
sys.setrecursionlimit(50000)

__author__ = "Marcus Bjerg Gregersen"

USE_CACHE = True

if not USE_CACHE:
	import MySQLdb as mdb



SQL_GET_RATED_ACTORS = """
	SELECT * FROM (
		SELECT actor_id, COUNT(*) as count FROM actors
		JOIN `roles`
		ON actors.`id` = roles.`actor_id`
			JOIN `movies`
			ON movies.`id` = `movie_id`
		WHERE rank IS NOT NULL
		GROUP BY actor_id) a
	WHERE a.count >= 20;

"""

SQL_GET_TOP_2_RANKED_MOVIES = """
	SELECT actor_id, first_name, last_name, name FROM actors
	JOIN `roles`
	ON actors.`id` = roles.`actor_id`
		JOIN `movies`
		ON movies.`id` = `movie_id`
	WHERE rank IS NOT NULL AND actor_id = %s
	ORDER BY rank DESC
	limit 2;
"""

class Vertex(object):
	"""docstring for Vertex"""
	def __init__(self, name):
		super(Vertex, self).__init__()
		self.name = name
		self.adjacent_edges = []

	def add_edge(self, edge):
		self.adjacent_edges.append(edge)

	def __str__(self):
		return self.name

class Edge(object):
	"""docstring for Edge"""
	def __init__(self, name, v, u):
		super(Edge, self).__init__()
		self.name = name
		self.u = u
		self.v = v
		u.add_edge(self)
		v.add_edge(self)

def get_data():
	vertices = {}
	edges = []
	con = mdb.connect('127.0.0.1', 'root', '', 'imdb');
	with con:
		cur = con.cursor()
		cur.execute(SQL_GET_RATED_ACTORS)
		rows = cur.fetchall()
		for row in rows:
			actor_id = long(row[0])
			cur_two = con.cursor()
			stat = SQL_GET_TOP_2_RANKED_MOVIES % str(actor_id)
			cur_two.execute(stat)
			rows_two = cur_two.fetchall()
			first_row = rows_two[0]
			
			#actor_id, first_name, last_name, name
			actor_id = str(long(first_row[0]))
			first_name = str(first_row[1])
			last_name = str(first_row[2])
			first_movie_name = str(first_row[3])
			second_movie_name = str(rows_two[1][3])

			if first_movie_name in vertices:
				first_movie_vert = vertices[first_movie_name]
			else:
				first_movie_vert = Vertex(first_movie_name)
				vertices[first_movie_name] = first_movie_vert

			if second_movie_name in vertices:
				second_movie_vert = vertices[second_movie_name]
			else:
				second_movie_vert = Vertex(second_movie_name)
				vertices[second_movie_name] = second_movie_vert

			unique_actor_name = actor_id + "_" + first_name + "_" + last_name

			actor_edge = Edge(unique_actor_name, first_movie_vert, second_movie_vert)
			edges.append(actor_edge)

	return (vertices, edges)

def approx_vertex_cover(edges):
	""" Implementation of APPROX-VERTEX-COVER from CLRS 3rd. edt. pp. 1109 """
	vertex_cover = []
	while len(edges) > 0:
		this_edge = edges.pop()

		if this_edge.u not in vertex_cover:
			vertex_cover.append(this_edge.u)

		if this_edge.v not in vertex_cover:
			vertex_cover.append(this_edge.v)

		other_edges = this_edge.u.adjacent_edges
		other_edges.append(this_edge.v.adjacent_edges)
		this_edge.v.adjacent_edges = []
		this_edge.u.adjacent_edges = []

		#Other edges contains every incident edge of u, and v. 
		for edge in other_edges:
			if edge in edges:
				edges.remove(edge)
	return vertex_cover

if not USE_CACHE:
	data = get_data()
	with open('cached.pickle', 'wb') as handle:
		pickle.dump(data, handle)
else:
	with open('cached.pickle', 'rb') as handle:
		data = pickle.load(handle)

(v,e) = data
#print len(v)

res = approx_vertex_cover(e)
#print len(res)


#Printing a vertex cover
for vert in res:
	print vert


