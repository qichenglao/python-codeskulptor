import simplegui, random, math

class Image:
    def __init__(self, url, size):
        self.url = url
        self.size = size
        self.image = simplegui.load_image(self.url)
        
    def draw(self, canvas, pos, col, size):
        center = (self.size[0] * (col + 0.5), self.size[1] * 0.5)
        canvas.draw_image(self.image, center, self.size, pos, size)
        
TILE = Image('https://dl.dropboxusercontent.com/u/10977446/2048.png?dl=1', (100, 100))
GRID = Image('https://dl.dropboxusercontent.com/u/10977446/grid.png?dl=1', (490, 490))
STEP = {'up':(0, -1), 'down':(0, 1), 'left':(-1, 0), 'right':(1, 0)}
ORDER = {'up':   [(i,j) for i in [0,1,2,3] for j in [0,1,2,3]],
         'down': [(i,j) for i in [0,1,2,3] for j in [3,2,1,0]],
         'left': [(i,j) for j in [0,1,2,3] for i in [0,1,2,3]],
         'right':[(i,j) for j in [0,1,2,3] for i in [3,2,1,0]]}

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.value = random.choice([2,2,2,2,2,2,2,2,4])
        self.size = 50
        self.bump = 0
        self.pos = [x * 100 + 95, y * 100 + 95]

    def merge(self):
        self.value *= 2
        self.bump = 1

    def update_size(self):
        # appear animation
        if self.size < 100:
            self.size += (105 - self.size) / 6
            
        # merge animation stretch
        elif self.bump == 1:
            self.size += (115 - self.size) / 6
            if self.size == 110:
                self.bump = -1
                
        # merge animation shrink
        elif self.bump == -1:
            self.size += (95 - self.size) / 6
            if self.size == 100:
                self.bump = 0

    def draw(self, canvas):
        self.update_size()
        TILE.draw(canvas, self.pos, math.log(self.value, 2) - 1, [self.size] * 2)

class Game:
    def __init__(self):
        self.frame = simplegui.create_frame('2048', 490, 490)
        self.frame.add_button('New Game', self.start)
        self.frame.set_keydown_handler(self.keydown)
        self.frame.set_draw_handler(self.draw)
        self.text = self.frame.add_label('')
        self.frame.start()
    
    def start(self):
        self.text.set_text('Use Arrow Keys to Move')
        self.grid = [[None for x in range(4)] for x in range(4)]
        self.moving_tiles = []
        self.merged_tiles = []
        self.new_tile()
        self.new_tile()
        
    def new_tile(self):
        x, y = random.choice([(i, j) for (i, j) in ORDER['up'] if not self.grid[i][j]])
        self.grid[x][y] = Tile(x, y)
        
    def keydown(self, key):
        self.text.set_text('')
        if not self.moving_tiles:
            for i in ['up','down','left','right']:
                if key == simplegui.KEY_MAP[i]:
                    self.merger = None # keep track of last merger in case merge twice
                    for (x, y) in ORDER[i]:
                        if self.grid[x][y]:
                            self.move_tile(x, y, STEP[i])
                        
    def move_tile(self, x, y, step):
        tile = self.grid[x][y]
        
        # find the destination of current tile by updating x and y
        while 0 <= x + step[0] <= 3 and 0 <= y + step[1] <= 3:
            new_tile = self.grid[x + step[0]][y + step[1]]
            if new_tile == None:
                x += step[0]
                y += step[1]
            elif (new_tile.value == tile.value) and (new_tile != self.merger):
                x += step[0]
                y += step[1]
                self.merger = tile # will merge but stay
                self.merged_tiles.append(new_tile) # will be merged and removed
                break
            else: break
                
        # update moving tile list, grid, and tile itself
        if x != tile.x or y != tile.y:
            self.moving_tiles.append(tile)
            self.grid[tile.x][tile.y] = None
            self.grid[x][y] = tile
            tile.vel_list = [((x-tile.x)*i, (y-tile.y)*i) for i in [10, 20, 40, 20, 10]]
            tile.x, tile.y = x, y
    
    def draw(self, canvas):
        # draw board
        GRID.draw(canvas, (245, 245), 0, GRID.size)
        
        # draw tiles
        for row in self.grid:
            for tile in row:
                if tile: tile.draw(canvas)
                    
        # draw merged tiles
        if self.merged_tiles:
            for tile in self.merged_tiles:
                tile.draw(canvas)
        
        # update moving tiles
        if self.moving_tiles:
            self.update_moving_tiles()
                        
    def update_moving_tiles(self):
        if self.moving_tiles[0].vel_list:
            for tile in self.moving_tiles:
                vel = tile.vel_list.pop()
                tile.pos = [tile.pos[0] + vel[0], tile.pos[1] + vel[1]]
        else:
            for tile in self.merged_tiles:
                self.grid[tile.x][tile.y].merge()
                if self.grid[tile.x][tile.y].value == 2048:
                    self.text.set_text('You Win! Go Beyond?')
            self.merged_tiles = []
            self.moving_tiles = []
            self.new_tile()
            
game = Game()
game.start()
