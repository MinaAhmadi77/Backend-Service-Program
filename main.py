from flask import *
import json
import jwt
import connectToDB
from flask import make_response
server = Flask(__name__)
connection = connectToDB.get_connection_to_DB()


def check_role(req):
  try:
    # print(req.headers)
    token = req.headers['Authorization']
    encoded=token.split(" ")[1]
    result = jwt.decode(encoded, "secret", algorithms=["HS256"])
    print(result)
  except Exception as e:
    print(e)
    return "guest"
  return result['role'], result['id']  


@server.route("/admin/movie", methods=["POST"])
def add_new_movie():
  role, _ = check_role(request)
  print(role)
  if role == 0:
    request_json = request.get_json()  
    name = str(request_json["name"])
    description = str(request_json["description"])
    rating = str(0)
    # print(request_json)
    if ("rating" in request_json):
      rating = str(request_json["rating"])

    # print(type(rating))

    if float(rating) < 0 or float(rating) > 1:

       return Response("{description:Bad request}", status=400, mimetype="application/json")

    try:
      mycursor = connection.cursor()

      sql = "INSERT INTO movies (name, description, rating) VALUES (%s, %s, %s)"
      val = (name, description, rating)
      mycursor.execute(sql, val)

      connection.commit()
    except Exception as e:
      print(e)
      return Response("{description:Bad request}", status=400, mimetype="application/json")

    return Response("{description: OK}", status=204, mimetype="application/json") 
  else:
    return Response("{description: Unauthorized}", status=401, mimetype="application/json")


@server.route("/admin/movie/<mid>", methods=["PUT"])
def edit_movie(mid):
  role, _ = check_role(request)
  if role == 0:
    request_json = request.get_json()  
    name = str(request_json["name"])
    description = str(request_json["description"])
    rating = str(0)
    if ("rating" in request_json):
      rating = str(request_json["rating"])

    if float(rating) < 0 or float(rating) > 1:

       return Response("{description: Bad request}", status=400, mimetype="application/json")

    try:
      mycursor = connection.cursor()

      sql = "UPDATE movies SET name=%s,description=%s,rating=%s WHERE id=%s"
      val = (name,description, rating, mid)
      mycursor.execute(sql, val)

      connection.commit()
    except Exception as e:
      print(e)
      return Response("{description: Bad request}", status=400, mimetype="application/json")

    return Response("{description: OK}", status=204, mimetype="application/json") 
  else:
    return Response("{description: Unauthorized}", status=401, mimetype="application/json")

@server.route("/admin/movie/<mid>", methods=["DELETE"])
def delete_movie(mid):
  role, _ = check_role(request)
  if role == 0:
    request_json = request.get_json()  
   
    try:
      mycursor = connection.cursor()

      sql = "DELETE FROM movies WHERE id = %s"
      val = (mid,)
      mycursor.execute(sql, val)

      connection.commit()
    except Exception as e:
      print(e)     
      return Response("{description: Bad request}", status=400, mimetype="application/json")

    return Response("{description: OK}", status=204, mimetype="application/json") 
  else:
    return Response("{description: Unauthorized}", status=401, mimetype="application/json")


@server.route("/user/vote", methods=["POST"])
def vote_movie():
  role, uid = check_role(request)
  user_id = str(uid)
  if role == 1:
    request_json = request.get_json()  
    vote = str(request_json["vote"])
    movie_id = str(request_json["movie_id"])

    if float(vote) < 0 or float(vote) > 10:

       return Response("{description: Bad request}", status=400, mimetype="application/json")

    try:
      mycursor = connection.cursor()

      sql = "INSERT INTO vote (user_id, rating, movieID) VALUES (%s, %s, %s)"
      val = (user_id, vote, movie_id)
      mycursor.execute(sql, val)

      connection.commit()

    except Exception as e:
      print(e)     
      return Response("{description: Bad request}", status=400, mimetype="application/json")

    return Response("{description: OK}", status=204, mimetype="application/json") 
  else:
    return Response("{description: Unauthorized}", status=401, mimetype="application/json")

@server.route("/user/comment", methods=["POST"])
def add_new_comment():
  role, uid = check_role(request)
  user_id = str(uid)
  if role == 1:
    request_json = request.get_json()  
    comment_body = str(request_json["comment_body"])
    movie_id = str(request_json["movie_id"])


    try:
      mycursor = connection.cursor()

      sql = "INSERT INTO comments (user_id, comment, movieID) VALUES (%s, %s, %s)"
      val = (user_id, comment_body, movie_id)
      mycursor.execute(sql, val)

      connection.commit()
    except Exception as e:
      return Response("{description: Bad request}", status=400, mimetype="application/json")

    return Response("{description: OK}", status=200, mimetype="application/json") 
  else:
    return Response("{description: Unauthorized}", status=401, mimetype="application/json")


@server.route("/movies", methods=["GET"])
def get_movies():
  html = ""
  try:
    data = []
    cur = connection.cursor()
    cur.execute( "SELECT * FROM movies" )
    for movie_id,name,description,rating in cur.fetchall() :
        data.append({
          "movie_id":movie_id,
          "name":name,
          "description":description,
          "rating":rating
        })
        
        html += "<h3>" + str(movie_id)+"  |"+ str(name)+"  |" + str(description)+"  |" + str(rating) + "</h3></br>"
  except Exception as e:
    print(e)
    return Response("{description: Bad request}", status=400, mimetype="application/json")

  return Response(response=json.dumps(data), status=200, mimetype="application/json") 

@server.route("/comments", methods=["GET"])
def get_comments():
  # movieID = request.args.get("movieID")
  html = ""
  try:
    data = []
    cur = connection.cursor()
    cur.execute( "SELECT users.username,comments.comment,movies.name FROM users INNER JOIN comments INNER JOIN movies WHERE comments.user_id = users.id and comments.movieID = movies.id" )
    for username,comment,name in cur.fetchall() :
        data.append(
          {
            "username":username,
            "comment_body":comment,
            "movie_name":name
          }
        )
        html += "<h3>" + str(username)+"  |"+ str(comment)+"  |" + str(name) + "</h3></br>"
  except Exception as e:
    print(e)
    return Response("{description: Bad request}", status=400, mimetype="application/json")
  return Response( response=json.dumps(data), status=200, mimetype="application/json") 

@server.route("/movie/<mid>", methods=["GET"])
def get_movie(mid):
  mid = str(mid)
  
  html = ""
  try:
      data = []
      cur = connection.cursor()
      cur.execute( "SELECT * FROM movies WHERE id = %s", (mid,) )
      for movie_id,name,description,rating in cur.fetchall() :
          data.append(
            {
              "movie_id":movie_id,
              "movie_name":name,
              "description":description,
              "rating": rating
            }
          )
          html += "<h3>" + str(movie_id)+"  |"+ str(name)+"  |" + str(description)+"  |" + str(rating) + "</h3></br>"
  except Exception as e:
    print(e)
    return Response("{description: Bad request}", status=400, mimetype="application/json")

  return Response(response=json.dumps(data), status=200, mimetype="application/json") 

if __name__ == '__main__':
    server.run(debug=True)
    connection.close()
