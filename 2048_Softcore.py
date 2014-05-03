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

    def copy(self):
        tile = Tile(self.x, self.y)
        tile.value = self.value
        return tile
    
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
        self.frame.add_button('New Game', self.start, 100)
        self.frame.set_keydown_handler(self.keydown)
        self.frame.set_draw_handler(self.draw)
        self.text = self.frame.add_label('')
        self.frame.add_button('Undo', self.undo, 100)
        self.frame.add_button('Bot Move', self.bot_move, 100)
        self.frame.start()
    
    def start(self):
        self.text.set_text('Arrow Keys or Bot')
        self.grid = [[None for x in range(4)] for x in range(4)]
        self.moving_tiles = []
        self.merged_tiles = []
        self.new_tile()
        self.new_tile()
        self.history = None
        
    def new_tile(self):
        x, y = random.choice([(i, j) for (i, j) in ORDER['up'] if not self.grid[i][j]])
        self.grid[x][y] = Tile(x, y)
        
    def copy(self):
        return [[x.copy() if x else None for x in col] for col in self.grid]
    
    def keydown(self, key):
        self.text.set_text('')
        if not self.moving_tiles:
            history = self.copy()
            for i in ['up','down','left','right']:
                if key == simplegui.KEY_MAP[i]:
                    if self.is_moved(self.grid, i, True):
                        self.history = history
                    
    def is_moved(self, grid, how, is_real):
        moved = False
        merger = None # keep track of last merger in case merge twice
        for x, y in ORDER[how]:
            if grid[x][y]:
                a, b = x, y # scouts of x and y
                i, j = STEP[how]
                tile1 = grid[x][y]
                
                # find the destination of tile1 by updating a & b
                while 0 <= a+i <= 3 and 0 <= b+j <= 3:
                    tile2 = grid[a+i][b+j]
                    if tile2 == None:
                        a += i
                        b += j
                    elif tile2.value == tile1.value and tile2 != merger:
                        a += i
                        b += j
                        merger = tile1
                        if is_real:
                            self.merged_tiles.append(tile2)
                        else:
                            tile1.value *= 2
                        break
                    else: break
                    
                # move tile1 (update grid)
                if x != a or y != b:
                    moved = True
                    grid[x][y] = None
                    grid[a][b] = tile1
                    tile1.x, tile1.y = a, b
                    if is_real:
                        self.moving_tiles.append(tile1)
                        tile1.vel_list = [((a-x)*i, (b-y)*i) for i in [10,20,40,20,10]]
        return moved

    def draw(self, canvas):
        # draw board
        GRID.draw(canvas, (245, 245), 0, GRID.size)
        
        # draw tiles
        for col in self.grid:
            for tile in col:
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
            
    def undo(self):
        if self.history:
            self.grid = self.history
            
    def bot_move(self):
        min_entro = float('inf')
        direction = ''
        for i in ['up','down','left','right']:
            grid = self.copy()
            if self.is_moved(grid, i, False):
                entropy = self.grid_entropy(grid)
                if min_entro >= entropy:
                    min_entro = entropy
                    direction = i
        if direction:
            self.keydown(simplegui.KEY_MAP[direction])
            
    def grid_entropy(self, grid):
        '''sum of each tile's degree of disorder'''
        return sum([sum([self.tile_entropy(x, grid) for x in col if x]) for col in grid])
    
    def tile_entropy(self, tile, grid):
        '''sum of value differences between given tile and its neighbors'''
        return sum([self.diff(tile, x) for x in self.neibor(tile, grid)])
    
    def diff(self, tile1, tile2):
        '''return value difference of two tiles'''
        if tile2 == None:
            return math.log(tile1.value, 2)
        return math.fabs(math.log(tile1.value, 2) - math.log(tile2.value, 2))
    
    def neibor(self, tile, grid):
        '''return up-down-left-right neighbors of given tile'''
        x, y = tile.x, tile.y
        return [grid[x+i][y+j] for i,j in STEP.values() if 0<=x+i<=3 and 0<=y+j<=3]
            
game = Game()
game.start()
