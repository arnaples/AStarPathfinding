from pygame import display, draw, event, key, locals, mouse, Rect, surface
import pygame
import queue

pygame.init()

BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (128,128,128)
PINK = (255,0,127)
BLUE = (21,244,238)
GREEN = (57,255,20)

rows, columns = 50,50
SQUARE_SIZE = sWIDTH,sHEIGHT = 15,15
straightCost, diagonalCost = 10,14

size = WIDTH, HEIGHT = columns*sWIDTH,rows*sHEIGHT
squares,current_selection_of_squares,open_list,closed_list = [],[],[],[]
end_points = [None,None]
setStart = True
showSteps = False
screen = display.set_mode(size)
screen.fill(BLACK)

def getIndex(coords:tuple):
    x,y = coords
    return (WIDTH//sWIDTH) * x + y
class Square:
    isStart:bool = False
    isEnd:bool = False
    isWall:bool = False
    color:tuple = WHITE
    uId:int = None
    children:list = []
    parent:int = None
    h_value:int = None
    g_value:int = 0
    f_value:int = 0
    def __init__(self,x:int,y:int):
        self.gridLoc = self.x, self.y = x, y
        
        self.uId = getIndex((x,y))
        self.coords = x*sHEIGHT,y*sWIDTH
        self.surf = surface.Surface(SQUARE_SIZE)
        self.rect = Rect(self.coords,SQUARE_SIZE)
    def __str__(self):
        return 'Grid ID: {}; Grid Location: {},{}; Movement Values: ({},{},{})'.format(self.uId,self.x,self.y,self.h_value,self.g_value,self.f_value)
    def __eq__(self,other):
        if type(other) == tuple and len(other) == 2:
            return self.rect.collidepoint(other)
        elif type(other) == pygame.Rect:
            return self.rect.colliderect(other)
        elif type(other) == Square:
            return self.__cmp__(other)
        else:
            raise Exception('shouldn\'t be here. Found Type {}'.format(type(other)))
    def __cmp__(self,other):
        
        if self.uId < other.uId:
            return -1
        elif self.uId == other.uId:
            return 0
        elif self.uId > other.uId:
            return 1
    
    def set_h(self, endCoords:tuple):
        x,y = endCoords
        self.h_value = abs((x-self.x)) + abs((y-self.y))
    def set_g(self,value):
        self.g_value = value
        self.f_value = value + self.h_value
    
    def setChildren(self,surroundingSquares:list):
        self.children.clear()
        for square in surroundingSquares:
            square:Square
            gToSquare = self.calculateGValue(square) + self.g_value
            if square.g_value == 0 or gToSquare < square.g_value:
                square.parent = self.uId
                square.set_g(gToSquare)
                self.children.append(square)
    def calculateGValue(self,other):
        diffTotal = abs((other.x-self.x)) + abs((other.y-self.y))
        if diffTotal == 2:
            return diagonalCost+self.g_value
        elif diffTotal == 1:
            return straightCost+self.g_value
        else:
            raise Exception('DiffTotal: {}; Self: ({},{}); Other: ({},{})'.format(diffTotal,self.x,self.y,other.x,other.y))
    
    def setEndPoint(self,isStart:bool):
        self.isWall = False
        if isStart: self.isStart = True
        else: self.isEnd = True
        self.draw(PINK)
    def unsetEndPoint(self):
        self.isStart = False
        self.isEnd = False
        self.draw()
    
    def onSelect(self):
        self.draw(GRAY)
        self.isWall = True
        #draw.rect(screen,BLACK,self.rect)
        display.flip()
    def draw(self,color=WHITE):
        self.color = color
        self.surf.fill(self.color)
        screen.blit(self.surf,self.coords)
    def highLight(self):
        self.draw(BLUE)
    def clear(self):
        self.isStart = False
        self.isEnd = False
        self.isWall = False
        self.children.clear()
        self.g_value = 0
        self.h_value = 0
        self.f_value = 0
        self.parent = None
        self.draw()
def clearAll():
    open_list.clear()
    closed_list.clear()
    for square in squares:
        square.clear()
    display.flip()
def setEndPoints(setStart:bool):
    mouseCoords = mouse.get_pos()
    square = squares[squares.index(mouseCoords)]
    index = 0 if setStart else 1
    endPoint = end_points[index]
    if endPoint is not None:
        endPoint.unsetEndPoint()
    endPoint = square
    endPoint.setEndPoint(setStart)
    
    end_points[index] = endPoint

    display.flip()
def getClickedSquare():
    if mouse.get_pressed()[0]:
        mouseCoords = mouse.get_pos()
        square = squares[squares.index(mouseCoords)]
        if mouseCoords not in current_selection_of_squares and not square.isStart and not square.isEnd:
            current_selection_of_squares.append(square)
            square.onSelect()
def getSurroundingSquares(thisSquare:Square):
    surroundingSquares = []
    for x in range(-1,2):
        for y in range(-1,2):
            if (thisSquare.y == 0 and y == -1) or (thisSquare.x == 0 and x == -1) or (thisSquare.y + y == columns) or (thisSquare.x + x == rows):
                continue
            index = getIndex((thisSquare.x+x,thisSquare.y+y))
            if index in closed_list or index < 0 or index >= len(squares):
                continue
            surroundingSquares.append(squares[index])
    return surroundingSquares
def checkForFinal(callingSquareId, surroundingSquares):
    for square in surroundingSquares:
        square:Square
        if square.uId == end_points[1].uId: 
            end_points[1].parent = callingSquareId
            return True
    return False
def highlightPath(square:Square):
    if square.parent is None:
        return False
    parent = squares[square.parent]
    if parent.isStart:
        return True
    parent.highLight()
    if highlightPath(parent):
        return True
    return False

for x in range(HEIGHT//sHEIGHT):
    for y in range(WIDTH//sWIDTH):
        thisSquare = Square(x,y)
        squares.append(thisSquare)
        thisSquare.draw()
display.flip()

while not key.get_pressed()[locals.K_ESCAPE]:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if mouse.get_pressed()[2]:
                setEndPoints(setStart)
                setStart = not setStart
        if event.type == pygame.MOUSEMOTION:
            getClickedSquare()
        if event.type == pygame.MOUSEBUTTONUP:
            current_selection_of_squares.clear()
        if event.type == pygame.KEYDOWN:
            if key.get_pressed()[locals.K_c]:
                clearAll()
            if key.get_pressed()[locals.K_s]:
                showSteps = not showSteps
            if key.get_pressed()[locals.K_SPACE]:
                q = queue.PriorityQueue()
                q.put((0,end_points[0]))
                for square in squares:
                    if square.isWall:
                        closed_list.append(square.uId)
                    else:
                        square.set_h(end_points[1].gridLoc)
                while True:
                    if q.empty(): break
                    thisSquare:Square = q.get()[1]
                    if showSteps and thisSquare.uId != end_points[0].uId:
                        thisSquare.draw(GREEN)
                        display.flip()
                    closed_list.append(thisSquare.uId)
                    x,y = thisSquare.x, thisSquare.y
                    surroundingSquares = getSurroundingSquares(thisSquare)
                    if checkForFinal(thisSquare.uId,surroundingSquares): break
                    
                    thisSquare.setChildren(surroundingSquares)
                    for square in thisSquare.children:
                        square:Square
                        q.put((square.f_value,square))
                    q.task_done()
                highlightPath(end_points[1])
                display.flip()