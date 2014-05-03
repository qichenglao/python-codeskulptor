import simplegui, random, math

GRID = 24, 24
SIZE = 20

class Image:
    def __init__(self, url, size):
        self.url = url
        self.size = size
        self.image = simplegui.load_image(self.url)
        
    def draw(self, canvas, pos, frame=0):
        center = [self.size[0] * (frame % 7 + 0.5), self.size[1] * (frame // 7 + 0.5)]
        canvas.draw_image(self.image, center, self.size, pos, self.size)
        
pitt = Image('https://dl.dropboxusercontent.com/u/10977446/pitt.png?dl=1', (480, 480))
play = Image('https://dl.dropboxusercontent.com/u/10977446/play.png?dl=1', (480, 480))
keys = Image('https://dl.dropboxusercontent.com/u/10977446/keys.png?dl=1', (480, 480))
paus = Image('https://dl.dropboxusercontent.com/u/10977446/paus.png?dl=1', (188, 480))
tile = Image('https://dl.dropboxusercontent.com/u/10977446/tile.png?dl=1', (40, 40))
tetri_dict = {'J':[(0,0), (0,-1), (0,1), (-1,1)], 'L':[(0,0), (0,-1), (0,1), (1,1)], 
              'I':[(0,0), (0,-1), (0,1),  (0,2)], 'T':[(0,0), (-1,0), (1,0), (0,1)], 
              'S':[(0,0),  (1,0), (0,1), (-1,1)], 'Z':[(0,0), (-1,0), (0,1), (1,1)], 
              'O':[(0,0),  (1,0), (1,1),  (0,1)]}
hinge_color = {0:'rgba(255, 162, 179, 0.8)', 1:'rgba(255,  98,  98, 0.8)', 
               2:'rgba(255, 186,  59, 0.8)', 3:'rgba(255, 255,  20, 0.8)', 
               4:'rgba(157, 232,  57, 0.8)', 5:'rgba( 90, 214, 255, 0.8)', 
               6:'rgba(169, 141, 210, 0.8)'}
width, height = GRID[0] * SIZE, GRID[1] * SIZE
center = width / 2, height / 2

# five helper functions
def pos(x, y):
    ''' return pixel position for the center of grid(x,y) '''
    return [(x - 0.5) * SIZE, (y - 0.5) * SIZE]

def hinge(x1, y1, x2, y2):
    ''' return the hinge line between two grids '''
    if x1 == x2 and math.fabs(y1 - y2) == 1:
        return [[[(x1 - 0.95) * SIZE, min(y1, y2) * SIZE],
                 [(x1 - 0.05) * SIZE, min(y1, y2) * SIZE]]]
    elif y1 == y2 and math.fabs(x1 - x2) == 1:
        return [[[min(x1, x2) * SIZE, (y1 - 0.95) * SIZE],
                 [min(x1, x2) * SIZE, (y1 - 0.05) * SIZE]]]
    else:
        return []

def find_hinge(tiles):
    ''' return a list of hinge lines from several tiles '''
    found = []
    if len(tiles) >= 2:
        for i in range(len(tiles) - 1):
            for j in range(i + 1, len(tiles)):
                found += hinge(tiles[i].x, tiles[i].y, tiles[j].x, tiles[j].y)
    return found

def new_tetri(x, y):
    ''' return a random new tetrimino '''
    shape = random.choice(tetri_dict.keys())
    angle = random.randrange(4)
    tiles = [Tile(x + i[0], y + i[1]) for i in tetri_dict[shape]]
    for tile in tiles:
        for i in range(angle):
            tile.move(0, (x, y))
    return Tetrimino(tiles, random.randrange(7))

def sec2time(sec):
    m = sec // 60
    s = sec % 60
    s = str(s) if s > 9 else '0' + str(s)
    return str(m) + ':' + s

# three classes: Tile, Tetrimino, Game
class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pos = pos(x, y)
        
    def jump(self, u, v):
        self.x += u
        self.y += v
        self.pos = pos(self.x, self.y)
        
    def move(self, how, center):
        if how == 2:   # down
            self.y += 1
        if how == -1:  # left
            self.x -= 1
        if how == 1:   # right
            self.x += 1
        if how == 0:   # rotate
            x = center[0] - (self.y - center[1])
            y = center[1] + (self.x - center[0])
            self.x = x
            self.y = y
        self.pos = pos(self.x, self.y)
        
    def can_move(self, how, center, pile, tetri):
        scout = Tile(self.x, self.y)
        scout.move(how, center)
        if tetri.has(scout.x, scout.y):
            return True
        elif scout.x < 8 or scout.x > 17 or scout.y > 23:
            return False
        elif pile.has(scout.x, scout.y):
            return False
        else:
            return True
            
    def draw(self, canvas, color):
        tile.draw(canvas, self.pos, color)
        
class Tetrimino:
    def __init__(self, tiles, color):
        self.tiles = tiles
        self.color = color
        self.hinge = find_hinge(tiles)
        
    def has(self, x, y):
        for tile in self.tiles:
            if tile.x == x and tile.y == y:
                return True
        return False
        
    def jump_to(self, x, y):
        u = x - self.tiles[0].x
        v = y - self.tiles[0].y
        for tile in self.tiles:
            tile.jump(u, v)
        self.hinge = find_hinge(self.tiles)
        
    def move(self, how):
        for tile in self.tiles:
            tile.move(how, (self.tiles[0].x, self.tiles[0].y))
        self.hinge = find_hinge(self.tiles)
            
    def can_move(self, how, pile):
        for tile in self.tiles:
            if not tile.can_move(how, (self.tiles[0].x, self.tiles[0].y), pile, self):
                return False
        return True
    
    def pop(self, row):
        upper, lower, mid = [], [], []
        for tile in self.tiles:
            if tile.y < row:
                upper.append(tile)
            elif tile.y > row:
                lower.append(tile)
            else:
                mid.append(tile)
        return Tetrimino(upper, self.color), \
               Tetrimino(lower, self.color), \
               Tetrimino(mid, self.color+7)
            
    def draw(self, canvas):
        for hinge in self.hinge:
            canvas.draw_polyline(hinge, 2, hinge_color[self.color % 7])
        for tile in self.tiles:
            tile.draw(canvas, self.color)
            
class Pile:
    def __init__(self):
        self.tight = set([]) # tetriminos can't fall
        self.loose = set([]) # tetriminos can fall
        self.trash = set([]) # tetriminos to remove
        self.row_tetri = {}  # tetriminos on a row
        self.row_colmn = {}  # occupied grids on a row
        self.full_rows = set([])
        self.last_full = 0
        
    def has(self, x, y):
        return y in self.row_colmn and x in self.row_colmn[y]
        
    def fulls_add(self, row):
        if len(self.row_colmn[row]) == 10:
            self.full_rows.add(row)
            if self.last_full < row:
                self.last_full = row
        
    def add(self, tetri):
        tetri.color -= 7
        self.tight.add(tetri)
        for tile in tetri.tiles:
            col, row = tile.x, tile.y
            if row in self.row_colmn:
                self.row_tetri[row].add(tetri)
                self.row_colmn[row].add(col)
                self.fulls_add(row)
            else:
                self.row_tetri[row] = set([tetri])
                self.row_colmn[row] = set([col])
                
    def pop(self, tetri):
        tetri.color += 7
        self.tight.discard(tetri)
        self.loose.add(tetri)
        for tile in tetri.tiles:
            col, row = tile.x, tile.y
            self.row_tetri[row].discard(tetri)
            self.row_colmn[row].discard(col)

    def pop_fulls(self):
        for row in self.full_rows:
            for tetri in self.row_tetri[row]:
                self.tight.discard(tetri)
                upper, lower, mid = tetri.pop(row)
                for new_tetri in [upper, lower]:
                    if new_tetri.tiles:
                        self.tight.add(new_tetri)
                        for tile in new_tetri.tiles:
                            self.row_tetri[tile.y].discard(tetri)
                            self.row_tetri[tile.y].add(new_tetri)
                self.trash.add(mid)
            self.row_tetri.pop(row)
            self.row_colmn.pop(row)
            
    def find_loose(self):
        ''' scan tight for loose '''
        temp = set([])
        for row in self.row_tetri:
            if row <= self.last_full + 1:
                for tetri in self.row_tetri[row]:
                    if tetri.can_move(2, self):
                        temp.add(tetri)
        for tetri in temp:
            self.pop(tetri)
            
    def down(self):
        ''' loose down and scan loose for tight'''
        for tetri in self.loose:
            tetri.move(2)
            if not tetri.can_move(2, self):
                self.loose.discard(tetri)
                self.add(tetri)

    def draw(self, canvas):
        for pile in [self.tight, self.loose, self.trash]:
            for tetri in pile:
                tetri.draw(canvas)

class Game:
    def __init__(self):
        self.tetris = {}
        self.pile = Pile()
        self.time = 0
        self.state = 0
        self.score = 0
        self.chain = 0
        self.points = []
        self.move_dict = {}
        self.best = 0
        self.time1 = simplegui.create_timer(500, self.tetri_down)
        self.time2 = simplegui.create_timer( 20, self.tetri_down)
        self.time3 = simplegui.create_timer(120, self.pile_update)
        self.timer = simplegui.create_timer(1000, self.count_down)
        self.frame = simplegui.create_frame('Tetris', width, height)
        
    def run(self):
        self.frame.set_mouseclick_handler(self.click)
        self.frame.set_keydown_handler(self.keydown)
        self.frame.set_keyup_handler(self.keyup)
        self.frame.set_draw_handler(self.draw)
        self.frame.start()
        
    def start(self):
        self.tetris = {0: new_tetri(13, 4), 1: new_tetri(21, 4)}
        self.pile = Pile()
        self.time = 7 * 60
        self.state = 1
        self.score = 0
        self.chain = 0
        self.points = []
        self.move_dict = {}
        self.time1.start()
        self.timer.start()
        self.tetris[0].color += 7
        
    def end(self):
        self.state = 3
        self.time1.stop()
        self.time2.stop()
        self.time3.stop()
        self.timer.stop()
        
    def count_down(self):
        self.time -= 1
        if self.time == 0:
            self.end()
        
    def tetri_down(self):
        if self.state == 1:
            if 1 not in self.tetris:
                self.tetris[1] = new_tetri(21, 4)
            if self.tetris[0].can_move(2, self.pile):
                self.tetris[0].move(2)
            else:
                self.pile.add(self.tetris[0])
                if 6 in self.pile.row_tetri:
                    self.end()
                    return
                self.tetris[0] = self.tetris.pop(1)
                self.tetris[0].jump_to(13, 4)
                self.tetris[0].color += 7
                if self.pile.full_rows:
                    self.time1.stop()
                    self.time2.stop()
                    self.time3.start()
            
    def pile_update(self):
        if self.state == 1:
            if self.pile.loose:
                self.pile.down()
                self.pile.find_loose()
            elif self.pile.full_rows:
                self.pile.pop_fulls()
                self.points_update()
            elif self.pile.trash:
                self.pile.trash = set([])
                self.pile.find_loose()
            else:
                self.chain = 0
                self.time3.stop()
                self.time1.start()
                
    def points_update(self):
        pts = len(self.pile.full_rows) ** 2 * 2 ** self.chain
        pos = [213, 20 * (self.pile.full_rows.pop() - 1)]
        self.points.append([pts, pos, 0])
        self.chain += 1
        self.pile.full_rows = set([])
            
    def rotate(self):
        if self.tetris[0].can_move(0, self.pile):
            self.tetris[0].move(0)
        elif self.tetris[0].tiles[0].x < 10 and self.tetris[0].can_move(1, self.pile):
            self.tetris[0].move(1)
            self.rotate()
        elif self.tetris[0].tiles[0].x > 15 and self.tetris[0].can_move(-1, self.pile):
            self.tetris[0].move(-1)
            self.rotate()

    def move(self):
        if self.state == 1:
            for i in self.move_dict:
                if self.move_dict[i]:
                    self.move_dict[i] += 1
                    if self.move_dict[i] % 7 == 2 and self.tetris[0].can_move(i, self.pile):
                        self.tetris[0].move(i)
                    
    def hold(self):
        if 2 in self.tetris:
            self.tetris[2], self.tetris[0] = self.tetris[0], self.tetris[2]
        else:
            self.tetris[2], self.tetris[0] = self.tetris[0], self.tetris.pop(1)
        self.tetris[0].jump_to(13, 4)
        self.tetris[2].jump_to(4, 4)
        self.tetris[2].color -= 7
        self.tetris[0].color += 7
        
    def click(self, pos):
        if self.state == 0 or self.state == 3:
            if 200 < pos[0] < 280 and 160 < pos[1] < 240:
                self.start()
        
    def keydown(self, key):
        if 0 < self.state < 3 and key == simplegui.KEY_MAP['space']:
            self.state = 2 if self.state == 1 else 1
        if self.state == 1 and not self.time3.is_running():
            if key == simplegui.KEY_MAP['down']:
                self.time1.stop()
                self.time2.start()
            if key == simplegui.KEY_MAP['up']:
                self.rotate()
            if key == simplegui.KEY_MAP['left']:
                self.move_dict[-1] = 1
            if key == simplegui.KEY_MAP['right']:
                self.move_dict[1] = 1
            if key == simplegui.KEY_MAP['h']:
                self.hold()

    def keyup(self, key):
        if self.state == 1 and not self.time3.is_running():
            if key == simplegui.KEY_MAP['down']:
                self.time2.stop()
                self.time1.start()
            if key == simplegui.KEY_MAP['left']:
                self.move_dict[-1] = 0
            if key == simplegui.KEY_MAP['right']:
                self.move_dict[1] = 0
            
    def draw(self, canvas):
        # update left or right control
        self.move()
        
        # draw pile
        self.pile.draw(canvas)
        
        # draw all tetriminos
        for i in self.tetris:
            self.tetris[i].draw(canvas)
            
        # draw splash
        if self.state == 0:
            play.draw(canvas, center)
            keys.draw(canvas, center)
        elif self.state == 2:
            paus.draw(canvas, center)
        elif self.state == 3:
            play.draw(canvas, center)
            if self.score > 613:
                txt1 = 'Congratulations! You beat me!'
                txt2 = 'Genius, email this screen shot to qiukunfeng@gmail.com'
                txt3 = 'I will update the record to yours.'
                canvas.draw_text(txt1, (159, 50), 12, 'Black', 'sans-serif')
                canvas.draw_text(txt2, ( 88, 70), 12, 'Black', 'sans-serif')
                canvas.draw_text(txt3, (154, 90), 12, 'Black', 'sans-serif')
            else:
                txt1 = "Game's end. You didn't beat Kunfeng."
                txt2 = "Chain reaction double scoring."
                txt3 = "Play again?"
                canvas.draw_text(txt1, (139,  50), 12, 'Black', 'sans-serif')
                canvas.draw_text(txt2, (149,  80), 12, 'Black', 'sans-serif')
                canvas.draw_text(txt3, (209, 140), 12, 'Black', 'sans-serif')
        
        # draw frame picture
        pitt.draw(canvas, center)
        
        # draw time, score, best
        canvas.draw_text(sec2time(self.time), (107, 14), 12, 'White', 'sans-serif')
        canvas.draw_text(str(self.score),     (213, 14), 12, 'White', 'sans-serif')
        canvas.draw_text(str(self.best),      (306, 14), 12, 'White', 'sans-serif')
        
        # draw points just scored, update total score and best
        if self.points:
            temp = False
            for i in self.points:
                if i[2] < 70:
                    i[2] += 1
                    i[1][1] -= 1
                    canvas.draw_text('+' + str(i[0]), i[1], 16, 'White', 'sans-serif')
                else:
                    temp = True
            if temp:
                self.score += self.points.pop(0)[0]
                if self.score > self.best:
                    self.best = self.score
        
game = Game()
game.run()
