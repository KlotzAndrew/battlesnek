import os
import random
import math

import cherrypy


class Battlesnake(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return {
            "apiversion": "1",
            "author": "",  # TODO: Your Battlesnake Username
            "color": "#01937c",  # TODO: Personalize
            "head": "tiger-king",  # TODO: Personalize
            "tail": "tiger-tail",  # TODO: Personalize
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        data = cherrypy.request.json
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        data = cherrypy.request.json

        possible_moves = ["up", "down", "left", "right"]
        move = random.choice(possible_moves)

        size = data["board"]["height"]
        you = data["you"]

        grid = Matrix = [[0 for x in range(size)] for y in range(size)]

        id = you["id"]

        head = data["you"]["head"]
        body = data["you"]["body"]
        tail = body[len(body)-1]
        for point in body:
            x = point["x"]
            y = point["y"]
            grid[x][y] = 1

        snakes = data["board"]["snakes"]
        for snake in snakes:
            snakeID = snake["id"]
            print("SNAKE IDS", id, snakeID, id == snakeID)
            if snakeID == id:
                continue

            print("enemy", snake)
            enemyBody = snake["body"]
            for p in enemyBody:
                x = p["x"]
                y = p["y"]
                grid[x][y] = 1

            h = snake["head"]
            x = h["x"]
            y = h["y"]

            if y+1 < size: grid[x][y+1] = 1
            if y-1 >= 0: grid[x][y-1] = 1
            if x-1 >= 0:  grid[x-1][y] = 1
            if x+1 < size: grid[x+1][y] = 1

        visited = []
        queue = []

        current = [head["x"], head["y"]]
        headPoint = [head["x"], head["y"]]
        goal = [tail["x"], tail["y"]]

        parents = {}

        queue.append(current)
        visited.append(current)

        parent = []
        while queue:
            current = queue.pop(0)
            top = [current[0], current[1]+1]
            bottom = [current[0], current[1]-1]
            left = [current[0]-1, current[1]]
            right = [current[0]+1, current[1]]

            for point in [top, bottom, left, right]:
                if point == goal:
                    parent = point
                    parents[pointToID(point, size)] = current

                if valid(point, size, visited, grid):
                    parents[pointToID(point, size)] = current

                    queue.append(point)
                    visited.append(point)


        print([top, bottom, left, right])
        health = you["health"]

        nextPath = moveFromPath(parent, parents, headPoint, size)
        next = nextPath[0]
        path = nextPath[1]

        nextPoint = idToPoint(next, size)
        turn = data["turn"]
        print("path ===>", turn, nextPoint, path)

        try:
            if health < 20:
                foods = data["board"]["food"]
                nextMeal = 0
                mealLength = size * size + 1
                keyerr = 0
                for food in foods:
                    f = [food["x"], food["y"]]
                    try:
                        nextPath = moveFromPath(f, parents, headPoint, size)
                        if len(nextPath[1]) < mealLength:
                            nextMeal = f
                            mealLength = len(nextPath[1])
                            nextPoint = idToPoint(nextPath[0], size)
                    except KeyError as e:
                        keyerr += 1
                        continue

                print("found a new meal", nextMeal, keyerr, len(foods))

        except Exception as e:
            print(data)
            raise e

        motion = ""
        if nextPoint[0] < headPoint[0]:
            motion = "left"
        elif nextPoint[0] > headPoint[0]:
            motion = "right"
        elif nextPoint[1] > headPoint[1]:
            motion = "up"
        elif nextPoint[1] < headPoint[1]:
            motion = "down"

        print(f"MOVE: {motion}")
        return {"move": motion}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        data = cherrypy.request.json
        return "ok"

def moveFromPath(parent, parents, headPoint, size):
    path = [parent]
    while parent != headPoint:
        next = pointToID(parent, size)
        if next != headPoint:
            parent = parents[next]
            path.append(parent)

    return [next, path]

def pointToID(point, size):
    return point[0] * size + point[1]

def idToPoint(id, size):
    return [math.floor(id/size), id % size]

def valid(point, size, visited, grid):
    if point[0] < 0 or point[1] < 0 or point[0] >= size or point[1] >= size:
        return False

    if point in visited:
        return False

    if grid[point[0]][point[1]] == 1:
        return False

    return True


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
