#This is the last updated Term Project

#Laura Ochsner
#Spring 2017

# ********* Citations are listed at the bottom ************

#Pygame support was from --> Citation 1

from pygame.locals import *
import pygame, sys 

import time
import math
import string
import random
import cv2
import numpy as np
import imutils



background = pygame.image.load('background.jpg')
background = pygame.transform.scale(background, (640,400))
#picture comes from citation 14
pygame.mixer.init()
game_music = ["LiesMusic.wav", "Music2.wav", "YouChanged.wav", "JUICYHIGHER.wav"]
#This music comes from soundcloud 
# Citations 10 -> 13 for the music

#Colors
ORANGE = (255,100,0)
LIGHTORANGE = (255,180,100)
BLUE = (0,0,220)
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
LIGHTRED = (255,128,114)
GREEN = (0,255,0)
GREENTARGET = (60,100,50)
PURPLE = (255,0,255)



################################ RUN FUNCTION #############################

class gameManager(object):
    def __init__(self):
        pygame.init()
        
        #display settings
        self.font = pygame.font.Font(None,70)
        self.timeFont = pygame.font.Font("font3.ttf",70)
        self.timeFontLarge = pygame.font.Font("font3.ttf",80)
        self.gameFontSmall = pygame.font.Font("font2.ttf", 40)
        #this font comes from Citation 9
        self.gameFontVerySmall = pygame.font.Font("font2.ttf", 30)
        self.gameFont = pygame.font.Font("font2.ttf", 80)
        self.screenFill = BLACK
        self.screenWidth, self.screenHeight = 640, 400
        #1.6 ratio for screenHeight to screenWidth
        self.hitColor = BLUE
        self.GameOverFontSize = 80
        self.GameFontColor = (255,0,0)

        self.returnHomeColor = RED
        self.helpColor = ORANGE
        self.playColor = ORANGE
        self.newModeColor = ORANGE
        self.returnColor = ORANGE
        self.highScoreColor = ORANGE
        self.hColor = ORANGE

        #Game Logic
        self.mode = "Splash"
        self.gameModeChosen = None
        self.fps = 60 #how many times the computer is called each second
        self.targetRad = 65
        self.waitTime = 5.0 
        self.reactionDotTime = 2.0 #how long the dot stays up
        self.throwTracker = list() #keep track of all of the points for a trhow
        self.initForDot()
        self.initForReactionDot()
        self.hits = []

        #this keeps track of scores 
        self.setUpFiles()

        
        
        #OpenCV
        self.capture = cv2.VideoCapture(0)
        self.pixletoFT = None
        

        # Booleans 
        self.adjustedBallDims = None
        self.wallCollision = False
        self.prevXandY = None


        #Screen Calibration
        self.projectedWidthFT = 2.25#need to set these myself
        self.projectedHeightFT = 1.42 #need to set these when I do the projector
        self.ballType = "TennisBall"
        self.tennisRad = 0.10 #this is in feet
        self.feetToWall = 5.67


      
    def setUpFiles(self):
        #this is for the play Mode
        self.scores_File = open("highScores2.txt", 'r+') #Citation 5 
        self.scoreFile = self.scores_File.read()
        self.scores = None
        if len(self.scoreFile)>0:
            self.scores = getScores(self.scoreFile)

        #this is for the reation mode
        self.score_FileReaction = open("highScoresReaction.txt", 'r+') #Citation 5
        self.scoreFileReaction = self.score_FileReaction.read()
        if len(self.scoreFileReaction)>0:
            self.scoresReaction = getScores(self.scoreFileReaction)




    def initForDot(self):
        self.dotcx, self.dotcy, self.dotradius = getDotPosition(self.screenWidth,self.screenHeight, self.targetRad)
    
    def initForReactionDot(self):
        self.rdotcx, self.rdotcy, self.rdotradius, self.rdotColor = getReactionDot(self.screenWidth, self.screenHeight, self.targetRad, RED, GREENTARGET)

    def keyPressed(self, keyCode, modifier):
        if keyCode == pygame.K_q:
            self.capture.release() 
            cv2.destroyAllWindows()
            pygame.quit()
           

    def mousePressed(self, x , y ):
        if self.mode == "GameOver":
            if x> self.gx and x<(self.gx + self.gw) and y> self.gy and y<(self.gy + self.gh):
                self.restart() #the game begins again
            if x>self.gx1 and x<(self.gx1+self.gw1) and y> self.gy1 and y<(self.gy1 + self.gh1):
                self.mode = "HighScores"
        if self.mode == "Help":
            if (x>self.hx and x<(self.hx+self.hw) and y>self.hy and y<(self.hy+self.hh)):
                self.mode = "Splash" 
                return
        if self.mode == "Splash":
            if x>(self.bx) and x<(self.bx +self.bw) and y>self.by and y<(self.by+self.bh):
                self.mode = "Wait" 
                self.gameModeChosen = "Play"
                return
            if x>(self.bx1) and x<(self.bx1 + self.bw1) and y>self.by1 and y<(self.by1 +self.bh1):
                self.mode = "Help"
                return
            if x>self.bx2 and x<(self.bx2 + self.bw2) and y>self.by2 and y<(self.by2 + self.bh2):
                self.mode = "Wait"
                self.gameModeChosen = "PlayReaction"
                return 
        if self.mode == "HighScores":
            if (x> self.hReturnX and x<(self.hReturnX + self.hReturnW) 
                and y>self.hReturnY and y<(self.hReturnY + self.hReturnH)):
                self.mode = "GameOver"



    def mousePosition(self,mousepos):
        x,y = mousepos
        if self.mode == "GameOver":
            if x> self.gx and x<(self.gx + self.gw) and y> self.gy and y<(self.gy + self.gh):
                self.returnHomeColor = LIGHTRED
            elif (x>self.gx1 and x<(self.gx1+self.gw1) and y> self.gy1 and y<(self.gy1 + self.gh1)):
                self.highScoreColor = LIGHTORANGE
            else:
                self.highScoreColor = ORANGE
                self.returnHomeColor = RED
        if self.mode == "Help":
            if (x>self.hx) and (x<self.hx + self.hw) and y>self.hy and (y<self.hy+self.hh):
                self.returnColor = LIGHTORANGE
            else:
                self.returnColor = ORANGE

        if self.mode == "Splash":
            if (mousepos[0]>self.bx and mousepos[0]<(self.bx+self.bw) and 
                mousepos[1]>self.by and mousepos[1]<(self.by+self.bh)):
                self.playColor = LIGHTORANGE
                self.helpColor = ORANGE
                self.newModeColor = ORANGE
            elif (mousepos[0]>self.bx1 and mousepos[0]<(self.bx1+self.bw1) and 
                mousepos[1]>self.by1 and mousepos[1]<(self.by1+self.bh1)):
                self.helpColor = LIGHTORANGE
                self.playColor = ORANGE
                self.newModeColor = ORANGE
            elif (x > self.bx2) and x < (self.bx2 + self.bw2) and y>self.by2 and y<(self.by2+self.bh2):
                self.newModeColor = LIGHTORANGE
                self.helpColor = ORANGE
                self.playColor = ORANGE
            else:
                self.playColor = ORANGE
                self.helpColor = ORANGE
                self.newModeColor = ORANGE
        if self.mode == "HighScores":
            if (x> 5 and x<(5 + self.hReturnW) 
                and y>self.hReturnY and y<(self.hReturnY + self.hReturnH)):
                    self.hColor = LIGHTORANGE
            else:
                self.hColor = ORANGE
                  
    def text_objects(self,text,font):
        textSurface = font.render(text,True, (250,0,0))
        return textSurface, textSurface.get_rect()

    def manageMusic(self):
        if self.mode == "Play":
            pygame.mixer_music.pause()
        if self.mode == "Wait":
            pygame.mixer.music.pause()
        if self.mode == "GameOver":
            pygame.mixer_music.unpause() #the music continues to play

    def drawSplash(self,screen):
        screen.blit(background, (0,0))
        title = self.gameFont.render("Passer Pro", True, ORANGE)
        screen.blit(title, (self.screenWidth//2 -title.get_width()//2, 
                                self.screenHeight//2 - title.get_height()))


        #make the button to play
        w,h = self.screenWidth/4, self.screenHeight/9
        bx0, by0 =  self.screenWidth/1.5 - w//2, self.screenHeight/1.4 - h//2
        pygame.draw.rect(screen, self.playColor, (bx0, by0,w, h))
        mousepos = pygame.mouse.get_pos()
        startText = self.gameFontSmall.render("Time Mode",True, WHITE)
        

        #make the button for help
        w1,h1 = self.screenWidth/4, self.screenHeight / 9
        bx1,by1 = self.screenWidth/2 - w1//2, self.screenHeight/1.2 -h1/2
        pygame.draw.rect(screen, self.helpColor, (bx1,by1,w1,h1))
        helpText = self.gameFontSmall.render("Help", True, WHITE)

        #make button for reaction mode
        w2,h2 = self.screenWidth/4, self.screenHeight / 9
        bx2, by2 = self.screenWidth/3 - w2/2, self.screenHeight/1.4 - h2/2
        pygame.draw.rect(screen ,self.newModeColor, (bx2,by2, w2,h2))
        newModeText = self.gameFontSmall.render("Reaction", True, WHITE)
        


        #place the text here so that it is drawn over everything
        screen.blit(startText, (bx0,by0 + startText.get_height()//9))
        screen.blit(helpText, (bx1 + helpText.get_width()/2, by1 + helpText.get_width()//9))
        screen.blit(newModeText, (bx2 + newModeText.get_width()//10 , by2 + newModeText.get_height()//9))
    
    def initHButton(self,screen):
        self.hw, self.hh = self.screenWidth/4, self.screenHeight/9
        self.hx, self.hy =  self.screenWidth/5 - self.hw//2, self.screenHeight/1.1 - self.hh//2

    def initSplashButtons(self):
        #this allows me to change the colors of the buttons when
        #the mouse is over it
        w,h = self.screenWidth/4, self.screenHeight/9
        bx0, by0 =  self.screenWidth/1.5 - w//2, self.screenHeight/1.4 - h//2
        w1,h1 = self.screenWidth/4, self.screenHeight / 9
        bx1,by1 = self.screenWidth/2 - w1//2, self.screenHeight/1.2 -h1/2
        w2,h2 = self.screenWidth/4, self.screenHeight/9
        bx2, by2 = self.screenWidth/3 - w2/2, self.screenHeight/1.4 - h2/2
        self.bx,self.by,self.bw, self.bh = bx0,by0,w,h 
        self.bx1,self.by1,self.bw1, self.bh1 = bx1,by1,w1,h1
        self.bx2, self.by2, self.bw2, self.bh2 = bx2, by2, w2,h2

    def initHighScoreButtons(self):
        self.hReturnW, self.hReturnH =self.screenWidth/4 , self.screenHeight/9
        self.hReturnX, self.hReturnY = 5,5

    def drawHelp(self,screen):
        screen.fill(WHITE)
        text = self.gameFont.render("HELP", True, ORANGE)
        instructions = self.gameFontVerySmall.render("A series of Targets Will Appear", True, ORANGE)
        instructions2 = self.gameFontVerySmall.render("Throw the Ball At the Target", True, ORANGE)
        instructions3 = self.gameFontVerySmall.render("1 point per Accurate Hit", True, ORANGE)
        instructions4 = self.gameFontVerySmall.render("ONLY hit the Green Targets", True, ORANGE)
        instructions5 = self.gameFontVerySmall.render("The timer counts Down and Game is Over", True, ORANGE)
        screen.blit(instructions, (self.screenWidth//4 , self.screenHeight//3))
        screen.blit(instructions2, (self.screenWidth//4, self.screenHeight//2.4))
        screen.blit(instructions3, (self.screenWidth//4 , self.screenHeight//2))
        screen.blit(instructions4, (self.screenWidth//4 , self.screenHeight//1.7))
        screen.blit(instructions5, (self.screenWidth//4 - instructions5.get_width()//10, self.screenHeight//1.5))
        screen.blit(text, (self.screenWidth//2 - text.get_width()/2, self.screenHeight//9))

        #draw a button to go back
        w,h = self.screenWidth/4, self.screenHeight/9
        bx0, by0 =  self.screenWidth/5 - w//2, self.screenHeight/1.1 - h//2
        pygame.draw.rect(screen, self.returnColor, (bx0, by0,w, h))
        mousepos = pygame.mouse.get_pos()
        returnText = self.gameFontSmall.render("Return",True, WHITE)

        screen.blit(returnText, (bx0 + returnText.get_width()/4,by0))


    def drawWait(self, screen):
        #the time uses pygame.USEREVENT
        red, green,blue = 0,250,0
        timeLeft = self.waitTime
        if timeLeft == 0: #the game hsould begin
            red,green,blue = 0,0,255
            timeLeft = "Start!"
            text = self.timeFontLarge.render( timeLeft, True, (red,green,blue))
        else:
            red += 60*(5 - self.waitTime)
            green -= 75*(5- self.waitTime)
            if green <0:
                green = 0
            text = self.timeFontLarge.render( "%d" %timeLeft, True, (red,green,blue))
        radius = 1/3 * min(self.screenWidth, self.screenHeight)#make this flash?
        pygame.draw.circle(screen, (red,green, blue), (int(self.screenWidth/2) , int(self.screenHeight/2)) , int(radius), 8)
        screen.blit(text, (self.screenWidth//2 -text.get_width()//2, 
                                self.screenHeight//2 - text.get_height()//2))

    
    def drawPlayMode(self,screen):
        screen2 = pygame.display.set_mode((self.screenWidth,self.screenHeight))
        screen2.fill(self.screenFill) #this color will change based on hit or miss
        pygame.draw.circle(screen2,(60,100,50), (self.dotcx,self.dotcy),  self.dotradius)
        if self.adjustedBallDims != None:
            for ball in self.adjustedBallDims: #draws 
                x,y,w,h = ball
                radius = w/2
                if radius <25:
                    pygame.draw.circle(screen2, ORANGE, (int(x), int(y)), int(radius))
            if self.wallCollision == True:
                rad = self.ballRad_whenCollide 
                for ball in self.adjustedBallDims: #maybe make this only happen when it hits
                    x,y,w,h = ball
                    pygame.draw.circle(screen2, self.hitColor, (int(x),int(y)), int(rad)) 
                    #this dot will stay until the next dot hits the wall

        #draw where tried to hit
        for wallHit in self.hits:
            x,y,w,h = wallHit[0]
            pygame.draw.circle(screen2, RED, (int(x), int(y)), int(rad))

        timeText = self.timeFont.render("%s" %(str(self.player.time)), True, WHITE)
        score = self.gameFont.render(str(self.player.score), True, WHITE)
        screen2.blit(score, (20,20))
        screen2.blit(timeText,(self.screenWidth-90, 6/7 *self.screenHeight))
        
    def drawReactionMode(self,screen):
        screen.fill(self.screenFill)
        pygame.draw.circle(screen, self.rdotColor, (self.rdotcx,self.rdotcy), self.rdotradius)
        #drawing where tried to hit
        for wallHit in self.hits:
            rad = self.ballRad_whenCollide
            x,y,w,h = wallHit[0]
            pygame.draw.circle(screen, RED, (int(x), int(y)), int(rad))
        if self.player.score<0:
            absScore = self.player.score*-1
            symbol = self.font.render("-", True, WHITE)
            screen.blit(symbol, (15,30))
            score = self.gameFont.render(str(absScore), True, WHITE)
        else:
            score = self.gameFont.render(str(self.player.score), True, WHITE)
        screen.blit(score, (20,20))
        timeText = self.timeFont.render("%s" %(str(self.player.time)), True, WHITE)
        screen.blit(timeText,(self.screenWidth-90, 6/7 *self.screenHeight))
    
    def drawGameOver(self,screen3):
        screen3.fill(WHITE)
        colorlist = list()
        for color in self.GameFontColor:
            if color< 255:
                color += 1
            else:
                color-=255
            colorlist.append(color)
        self.GameFontColor = tuple(colorlist)
        self.gameFontChange = pygame.font.Font("font2.ttf", self.GameOverFontSize)
        text = self.gameFontChange.render("GameOver", True, self.GameFontColor)
        w = text.get_width()
        text2 = self.gameFontSmall.render("%s  %s" %(self.player.playerName, self.player.score), True, RED)
        w2 = text2.get_width()
        screen3.blit(text,(self.screenWidth//2 - w//2, self.screenHeight//3))
        screen3.blit(text2,(self.screenWidth//2 - w2//2, self.screenHeight//1.5))
        
        #make the button for home
        w1,h1 = self.screenWidth/4, self.screenHeight / 8
        bx1,by1 = self.screenWidth/2 - w1//2, self.screenHeight/8 -h1/1.5
        pygame.draw.rect(screen3, self.returnHomeColor, (bx1,by1,w1,h1))
        returnHomeText = self.gameFontSmall.render("Home", True, WHITE) 
        textW = returnHomeText.get_width()
        textH = returnHomeText.get_height()
        screen3.blit(returnHomeText, (self.screenWidth/2 - textW/2, self.screenHeight/9- textH/2))

        #make button for high scores
        w2,h2 = self.screenWidth/3.5, self.screenHeight / 8
        bx2,by2 = self.screenWidth/2 - w2//2, self.screenHeight/1.1 -h2/1.5
        pygame.draw.rect(screen3, self.highScoreColor, (bx2,by2, w2,h2))
        highScoreText = self.gameFontVerySmall.render("HIGH SCORES", True, WHITE)

        screen3.blit(highScoreText, (bx2 + highScoreText.get_width()/12 , by2 + highScoreText.get_height()/2))

        #set variables
        self.gx, self.gy = bx1,by1
        self.gw, self.gh = w1,h1

        self.gx1, self.gy1 = bx2, by2
        self.gw1, self.gh1  = w2,h2

    def drawHighScores(self,screen3):
        screen3.fill(WHITE)
        pygame.draw.line(screen3, ORANGE, (self.screenWidth//2,0), (self.screenWidth//2, self.screenHeight), 4)

        reactionText = self.gameFontSmall.render("Reaction", True, ORANGE)
        wText, hText = reactionText.get_width(), reactionText.get_height()

        playText = self.gameFontSmall.render("Time Mode", True, ORANGE)
        wText1, hText1 = playText.get_width(), playText.get_height()

        #draw return to gameOver
        w,h = self.screenWidth/4 , self.screenHeight/9
        x,y = 5, 5
        pygame.draw.rect(screen3, self.hColor, (x,y,w,h))
        returnText = self.gameFontSmall.render("return", True, WHITE)

        if self.scores_PlayMode != None: #there are entries
            #can keep track of hightest scores
            self.drawHighScoresPlayMode(screen3)
        if self.scores_ReactionMode!= None: #there are entries
            #can keep track of highest scores
            self.drawHighScoresReactionMode(screen3)

        screen3.blit(reactionText, (self.screenWidth/4 - wText/2, self.screenHeight/7))
        screen3.blit(playText, ((self.screenWidth*3)/4 - wText1/2, self.screenHeight/7))
        screen3.blit(returnText, (x +returnText.get_width()/4,y + returnText.get_height()/4))


    def drawHighScoresPlayMode(self,screen3):
        #uses dictionaries and a sorted list 
        #the keys in the dictionary and the values are the names
        #the sorted list of the highest scores 
        #is used as the keys to find the highest Score and Player
        scores = self.scores_PlayMode
        scoresAndPeople = self.scoreAndPlayer_PlayMode
        height = self.screenHeight//1.5
        count = 0
        for score in scores: # will go from lowest to highest
            #need to draw from bottom up 
            people = scoresAndPeople[score]
            for person in people:
                if count == 3:
                    break
                if person != None:
                    count +=1
                    text = self.gameFontSmall.render("%s" %(person),True, ORANGE)
                    screen3.blit(text,((self.screenWidth*3)//4 - 90, height))
                    text2 = self.gameFontSmall.render("%d" %score, True, ORANGE)
                    screen3.blit(text2, (self.screenWidth-60, height))
                    height -= 80


    
    def drawHighScoresReactionMode(self,screen3):
        #uses dictionaries and a sorted list 
        #the keys in the dictionary and the values are the names
        #the sorted list of the highest scores 
        #is used as the keys to find the highest Score and Player
        height2 = self.screenHeight//1.5
        scores2 = self.scores_ReactionMode
        scoresAndPeople2 = self.scoreAndPlayer_ReactionMode
        count2 = 0
        for s in scores2:
            people2 = scoresAndPeople2[s]
            for p in people2:
                if count2 == 3:
                    break
                if p!= None:
                    count2+=1
                    textReaction = self.gameFontSmall.render("%s"%p,True,ORANGE)
                    screen3.blit(textReaction,(self.screenWidth//10, height2))
                    textReaction2 = self.gameFontSmall.render("%d" %s, True, ORANGE)
                    screen3.blit(textReaction2, (self.screenWidth//2 - 40, height2))
                    height2 -= 80





    def redrawAll(self, screen):
        #this is claled last in the run loop
        screen3 = pygame.display.set_mode((self.screenWidth,self.screenHeight))
        screen4 = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        if self.mode == "Splash": 
            self.drawSplash(screen)
        if self.mode == "Help": 
            self.drawHelp(screen)
        elif self.mode == "Wait": self.drawWait(screen4)
        elif self.mode == "Play": 
            self.drawPlayMode(screen)
        elif self.mode == "PlayReaction":
            self.drawReactionMode(screen)
        elif self.mode =="GameOver": 
            self.drawGameOver(screen3)
        elif self.mode == "HighScores":
            self.drawHighScores(screen3)
            


    def timerFired(self, dt):
        pass

    def restart(self):
        game2 = gameManager() #calls init and creates a new game
        game2.run()


    def run(self):

        clock = pygame.time.Clock() #object to help keep track of time #Citation 2

        #the code for the timer was modeled after: Citation 4
            #only the structure for the USEREVENT and for loop were used
        

        screen = pygame.display.set_mode((self.screenWidth,self.screenHeight)) #this is the width and height
        playing = True 
        initball = False #only want to initialize the ball once so have to set this variable
        initTimer = False #this makes sure the timer is only initialized everytime the time changes
        initReactionTimer = False
        initPlayer = False
        originaldims = False #this has not been used yet
        reWriteScores = True
        pygame.mixer_music.load(getSong(game_music))
        pygame.mixer_music.play(-1)

        self.initSplashButtons()
        self.initHighScoreButtons()

        while playing == True:
            clock.tick(self.fps) #does this make it faster


            #this code helped for figuring out how to deal with the mouse clicks
            #http://stackoverflow.com/questions/10990137/pygame-mouse-clicking-detection
            
            self.manageMusic()

            mousepos = pygame.mouse.get_pos()
            self.mousePosition(mousepos) #changes color based on mouse

            self.keys = dict() #stores keys being heled down

            if self.mode == "Splash":
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP:
                       mx, my = pygame.mouse.get_pos()
                       self.mousePressed(mx,my)
                    if event.type == pygame.KEYDOWN: 
                        self.keys[event.key] = True
                        self.keyPressed(event.key,event.mod)
    
            if self.mode == "Wait":
                if initPlayer == False:
                    self.player = Player(1) #allows the user to input their name
                initPlayer = True

                if initTimer == False and initPlayer == True: #the timer starts to tick
                    timerWait = pygame.USEREVENT + 0
                    pygame.time.set_timer(timerWait, 1000) 
                    initTimer = True

                if initPlayer == True:
                    for event in pygame.event.get():
                        if event.type == pygame.USEREVENT +0 and self.mode == "Wait": #timer goes off
                            #one second is subtracted
                            if self.waitTime <= 0: #the game mode should change
                                self.mode = self.gameModeChosen
                                initTimer = False
                            self.waitTime -= 1
            
            if self.mode == "Help":
                screen = pygame.display.set_mode((self.screenWidth,self.screenHeight))
                self.initHButton(screen) #need to make the buttons from the screen
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP:
                       mx, my = pygame.mouse.get_pos()
                       self.mousePressed(mx,my)
                    if event.type == pygame.KEYDOWN: #why does this not work
                        self.keys[event.key] = True
                        self.keyPressed(event.key,event.mod)
            

            if self.mode =="Play" or self.mode == "PlayReaction":
                self.screenFill = BLACK
                self.hits = list() #every time that this is called the hit list is cleared
                pygame.mixer_music.pause()
                if initball == False:
                    self.ball = Ball() #this is what models the properties of the ball
                    self.enviornment = getEnviornment() #this is what models the rectangle and calibrates everything
                    initball = True
                    self.boundingRec = None #this is the frame where the projector will be

                    self.timer = pygame.USEREVENT + 1 #Citation 4
                    pygame.time.set_timer(self.timer, 1000)#do not use a magic number here 
                    

                self.ball.getModes() #sets up the windows to display
                self.enviornment.getModes() #this sets up the windows to make the rectangle

                self.enviornment.showWindows() #this is what actually displays the window
                self.ball.showWindows()

                if self.boundingRec == None: #this makes sure the rectangle is only made once
                    #this means that the screen is calibrated
                    self.boundingRec = self.enviornment.getRectangle()
                #this is called all of the other times when the rectangle is already determined
                elif self.boundingRec != None:
                    #this will draw the rectangle on the openCV screen
                    self.enviornment.drawRec()

                #Use the ball class to find this 
                self.ballcons = self.ball.getContours() #the ball contours (this is a list)
                self.balldims = self.ball.getBallDimensions() # returns[(x,y,w,h)] of the ball 
                self.ballDir = self.ball.getDirections(self.balldims) #this finds the averages of the past 2 data points to see if it is moving forwards or backwards


                if len(self.balldims) == 0:
                    self.prevXandY = None #there is no ball in the frame
                    self.player.throws+=1
                    self.throwTracker = list() #there is a new throw

                #the enviornment can only be displayed now
                self.enviornment.showWindows()

                #this finds the pixle to ft ratio to figure out how big the ball should be when it collides with the wall
                if self.pixletoFT == None and self.boundingRec != None:
                    x,y,wp,hp = self.boundingRec
                    wft = self.projectedWidthFT
                    hft = self.projectedHeightFT
                    self.pixletoFT = pixleToFeet(wp, hp,wft, hft) #p is for pixles ft is for feet
                    self.ballRad_whenCollide = calculateBallSizeinCollision(self.pixletoFT, self.tennisRad)


                if self.mode == "Play": #these are the things that are special to the play mode
                    self.screenFill = BLACK #need to make sure it resets

                    #Checking for collisions

                    if self.pixletoFT!=None and len(self.balldims)>0: #there is a bounding rectangle and a ball on the screen
                    
                   
                        #this checks for a collision on the wall and not on the target

                        #this deals with the transition from pygame to openCV screen
                        #had to figure out hte pixle to FT ratio and how many pixles the opnCV
                        #screen was seeing and how much of it was pygame
                        self.adjustedBallDims = ballinRectangleDims(self.boundingRec, self.balldims, self.screenWidth, self.screenHeight)
                        self.throwTracker.append((self.adjustedBallDims,self.ballDir)) 

                        #this finds out how close it is to the wall
                        Zposition = getZPosition(self.adjustedBallDims, self.pixletoFT, self.ballRad_whenCollide, self.feetToWall)

                        if math.fabs(Zposition) <= 0.4 or changeDirections(self.throwTracker) == True: #this means that it hit the wall
                            self.wallCollision = True
                            self.player.throws +=1
                            #self.screenFill = RED #assumes it is a miss

                            if math.fabs(Zposition)<= 0.4:
                                if checkForTargetCollision(self.boundingRec,self.dotcx,self.dotcy, self.targetRad, self.adjustedBallDims): #this would be if it hit the dot at that moment
                                    self.screenFill = GREEN
                                    self.hitColor = PURPLE
                                    self.initForDot()
                                    self.hits = list()
                                    self.player.score+=1

                            elif changeDirections(self.throwTracker) == True: #this means it was by Change in direction
                                self.hits.append(self.adjustedBallDims)
                                #now checking for colliding
                                prevBallDimensions = self.throwTracker[-2][0] #this is the second to last one 
                                yapproxYHit = approximatingHitY(prevBallDimensions, self.adjustedBallDims, self.pixletoFT, self.ballRad_whenCollide, self.feetToWall)
                                xapproxXHit = approximatingHitx(prevBallDimensions,self.adjustedBallDims)
                                #use circle collision to figure out 
                                if circleCollision(xapproxXHit,yapproxYHit, self.ballRad_whenCollide, self.dotcx,self.dotcy, self.targetRad): #approximated hit 
                                    self.wallCollision == True
                                    self.hitColor = RED
                                    self.initForDot()
                                    self.hits = list() #clears all of the times you tried for a target
                                    self.player.score +=1
                                    self.screenFill = GREEN
                                elif checkForTargetCollision(self.boundingRec,self.dotcx,self.dotcy, self.targetRad, self.adjustedBallDims): #this would be if it hit the dot at that moment
                                    self.screenFill = GREEN
                                    self.hitColor = PURPLE
                                    self.initForDot()
                                    self.hits = list()
                                    self.player.score+=1
                        x,y,w,h = self.adjustedBallDims[0]

                if self.mode == "PlayReaction":

                    self.screenFill = BLACK

                    #since this mode is based on reaction the dot is called every second to display a new target despite hit or miss

                    if initReactionTimer == False:
                        reactionTime = pygame.USEREVENT + 2 
                        pygame.time.set_timer(reactionTime,750) #every  2 seconds a new dot should display
                        initReactionTimer = True



                    if self.pixletoFT!=None and len(self.balldims)>0: #there is a bounding rectangle and a ball on the screen
                    
                        #this checks for a collision on the wall and not on the target

                        #this deals with the transition from pygame to openCV screen
                        self.adjustedBallDims = ballinRectangleDims(self.boundingRec, self.balldims, self.screenWidth, self.screenHeight)
                        self.throwTracker.append((self.adjustedBallDims,self.ballDir))
                        Zposition = getZPosition(self.adjustedBallDims, self.pixletoFT, self.ballRad_whenCollide, self.feetToWall)
                        if math.fabs(Zposition) <= 0.4 or changeDirections(self.throwTracker) == True: #this means that it hit the wall
                            self.wallCollision = True
                            self.player.throws +=1
                            #self.screenFill = RED
                            #check for target collision using circle collision
                                #if it hits the ball but it is red (-1 point)
                                #otherwise +1 point
                            if math.fabs(Zposition)<= 0.4:
                                if checkForTargetCollision(self.boundingRec,self.rdotcx,self.rdotcy, self.targetRad, self.adjustedBallDims): #this would be if it hit the dot at that moment
                                    # if the color is not green then take off a point
                                    print(self.rdotColor)
                                    if self.rdotColor == GREENTARGET:
                                        self.screenFill = GREEN
                                        self.hitColor = PURPLE
                                        self.initForReactionDot()
                                        initReactionTimer = False #reset the timer
                                        self.player.score+=1
                                    else: #make sure this is working
                                        self.screenFill = PURPLE
                                        print("hi")
                                        self.player.score-=5 # they hit a dot that was not green
                                    self.hits = list()
                                    

                            elif changeDirections(self.throwTracker) == True: #this means it was by Change in direction
                                self.hits.append(self.adjustedBallDims)
                                #now checking for colliding
                                prevBallDimensions = self.throwTracker[-2][0] #this is the second to last one 

                                if checkForTargetCollision(self.boundingRec,self.rdotcx,self.rdotcy, self.targetRad, self.adjustedBallDims): #this would be if it hit the dot at that moment
                                    self.screenFill = GREEN
                                    self.hitColor = PURPLE
                                    self.initForReactionDot()
                                    initReactionTimer = False #reset the timer
                                    self.hits = list()
                                    self.player.score+=1
                        


                #this takes care of the timing commands in the modes "Play" and "PlayReaction"
                for event in pygame.event.get():
                    if self.mode == "PlayReaction" and event.type == (reactionTime):
                        self.initForReactionDot()
                        self.hits = list() #when the target switches take out the hits list
                        initReactionTimer = False
                    elif event.type == (pygame.USEREVENT + 1) and (self.mode == "Play" or self.mode=="PlayReaction"): #timer goes off
                        self.mode = self.player.updateTimer(self.mode)


            if self.mode == "GameOver":
                if reWriteScores == True:
                    self.scores_PlayMode = None # i do not know if i need this
                    self.scoreAndPlayer_PlayMode = None #need to reset everytime new Game
                    self.scores_ReactionMode = None
                    self.scoreAndPlayer_ReactionMode = None

                    reWriteScores = False
                    if len(self.scoreFile)>0: #this is for the Play/Normal Mode
                        #the file was updated
                        if self.gameModeChosen == "Play": #only update if player chose this made
                            self.scores_File = self.scores_File.write("%s:%s" %(self.player.playerName, self.player.score)+",")
                            self.scores_File = open("highScores2.txt", 'r+') #Citation 5 
                            self.scoreFile = self.scores_File.read()
                        self.scores = getScores(self.scoreFile) #update the scores after someone plays
                        if self.scores_PlayMode == None:
                            scoreAndPlayer, highestScores  = getHighestScoresMode(self.scores)
                            self.scoreAndPlayer_PlayMode = scoreAndPlayer
                            self.scores_PlayMode = sorted(highestScores)
                        #scoreandPlayer is a dict w/ the score --> list of people
                        #highestScores is a set with the incrementing highest scores

                    if len(self.scoreFileReaction)>0: #this is for the reaction mode
                        #this updates the file
                        if self.gameModeChosen == "PlayReaction": #only update with player if chose this mode
                            self.score_FileReaction = self.score_FileReaction.write("%s:%s" %(self.player.playerName, self.player.score) + ",")
                            self.score_FileReaction = open("highScoresReaction.txt", 'r+') #Citation 5
                            self.scoreFileReaction = self.score_FileReaction.read()
                        self.scoresReaction = getScores(self.scoreFileReaction) #--> this part is correct
                        if self.scores_ReactionMode == None:
                            scoreAndPlayer2, highestScores2 = getHighestScoresModeReaction(self.scoresReaction)
                            self.scoreAndPlayer_ReactionMode = scoreAndPlayer2
                            self.scores_ReactionMode = sorted(highestScores2)



            #this takes care of general commands
            self.keys = dict()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN: #why does this not work
                    self.keys[event.key] = True
                    self.keyPressed(event.key,event.mod)
                if event.type == pygame.MOUSEBUTTONUP:
                    mx, my = pygame.mouse.get_pos()
                    self.mousePressed(mx,my)
             
    
                       
            self.redrawAll(screen)

            pygame.display.flip()
        pygame.quit()


####################### CLASS FOR BALL ############################
# In order to use openCV I needed a lot of hlep and the citation below was where it came from
#this website was helpful with figuring out how to threshold certain colors and draw
#on an openCV Screen
#Citation 3

class Ball(object):


    def __init__(self):
        self.screenWidth, self.screenHeight = 640,400
        self.capture = cv2.VideoCapture(0)
        self.move = None
        self.prevRad = None
        self.prevDir = None
        self.avgCount = 0 #for a range
        self.Radii = 0 #for for a range

  


    def getModes(self):

        self.grabbed, self.frame = self.capture.read()
        self.frame = imutils.resize(self.frame,self.screenWidth+50,self.screenHeight+50)
        #self.frame = cv2.flip(self.frame,1) #if I flip the screen it messes with the data points on the wall
        self.blur  = cv2.GaussianBlur(self.frame,(3,3),0)
        self.hsv = cv2.cvtColor(self.blur,cv2.COLOR_BGR2HSV)
        self.mask = self.colorBounds(self.hsv)


    def colorBounds(self,other):
        greenlower = (29,86,6)
        greenupper = (64,180,180) #used to be 64, 200, 200
        mask1 = cv2.inRange(other,greenlower,greenupper)
        mask2 = cv2.erode(mask1,None, iterations = 3)
        return cv2.dilate(mask2,None,iterations = 10)

    def showWindows(self):
        cv2.imshow("Frame", self.frame)
        #cv2.imshow("Mask", self.mask)


    def getContours(self):
        cons =cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        self.contours = cons
        return cons

    def getBallDimensions(self):
        contourdims = list()
        maxBallRadius = 0

        for c in self.contours:
            x,y,w,h = cv2.boundingRect(c)
            radius = w/2
            if radius > maxBallRadius and radius > 3:
                contourdims = [(x,y,w,h)] #so it returns the largest ball
        return contourdims


    def getDirections(self,other):
        #need to use an averaging system
        if len(other) > 0:
            newballDims = other[0]
            x,y,w,h = newballDims
            newRad = w/2
            if self.avgCount == 1: #the average count makes sure that it is not just a fluke in openCV
                averageRad = self.Radii/self.avgCount
                self.avgCount = 0
                self.Radii = 0
                if self.prevRad == None:
                    self.prevRad = w/2
                else:
                    if averageRad-self.prevRad>3: #when the ball is being thrown the radius cahnges a lot
                        self.prevRad = averageRad
                        self.prevDir = "AwayFromWall"
                        return "AwayFromWall" #this is with reference to the wall
                    elif self.prevRad-averageRad>3:
                        self.prevRad = averageRad
                        self.prevDir = "TowardsWall"
                        return "TowardsWall"
                    else:
                        self.prevRad = averageRad
                        self.prevDir = "Still"
                        return "Still" #this means it is not moving
            else:
                self.avgCount +=1
                self.Radii += newRad
                return self.prevDir
                



########################## PLAYER INFORMATION CLASS #####################

class Player(object):
    def __init__(self, number): #number 1 or 2 depending on how many players there are
        self.number = number
        self.score = 0
        self.time = 15.0 #need to change back
        self.throws = 0
        self.playerName = str(input("Player " + str(number)+ " Type Your Name"))
    
    def updateTimer(self,other):
        prevMode = other
        self.time -= 1 #the timer function is called every 1000 milliseconds
        if self.time<= 0:
            return "GameOver"
        else:
            return prevMode

    def getAccuracy(self):
        return str(self.score/self.throws *100) 

        
     
class getEnviornment(object):
    #again Citation 3 helped figure out how to threshold the video
    #and only track what was needed ot be tracked

    def __init__(self):
        self.screenWidth, self.screenHeight = 640,400 
        self.capture = cv2.VideoCapture(0)
        self.finalrecs = None
    
    def getModes(self):
        self.grabbed, self.frame = self.capture.read()
        self.frame = imutils.resize(self.frame,self.screenWidth+50,self.screenHeight+50)
        #self.frame = cv2.flip(self.frame,1) #do not have to flip the camera
        self.blur  = cv2.GaussianBlur(self.frame,(3,3),0)
        self.hsv = cv2.cvtColor(self.blur,cv2.COLOR_BGR2HSV)
        self.mask = self.colorBounds(self.hsv)

    def colorBounds(self,other):
        greenlower = (29,80,0)
        greenupper = (130, 230, 230) #255 B 
        mask1 = cv2.inRange(other,greenlower,greenupper)
        mask2 = cv2.erode(mask1,None, iterations = 3)
        self.mask2  = mask2
        return cv2.dilate(mask2,None,iterations = 10)

    def showWindows(self):
        cv2.imshow("Frame", self.frame)

    #this part is all of my own code 
    # Citation 3 was not helpful with this
    def getRectangle(self): #this gets the rectangle that surrounds the projected screen
        rectangles = list()
        prevArea = 0
        contours = cv2.findContours(self.mask2,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        if self.finalrecs == None:
            for cnt in contours:
                x,y,w,h = cv2.boundingRect(cnt)
                area = (x+w) *(y+h)
                if w>10 and prevArea < area:
                    rectangles += [(x,y,w,h)]
                    cv2.rectangle(self.frame, (x,y), (x+w,y+h), (0,0,255),2)
            if len(rectangles) ==2:
                self.finalrecs = rectangles
                rec0 = self.finalrecs[0]
                rec1 = self.finalrecs[1]
                x0,y0,w0,h0 = rec0
                x1,y1,w1,h1 = rec1
                self.recWidth = int(math.fabs(x0-x1)) #is this a roudning error?
                self.recHeight = int(math.fabs(y0-y1))
                self.upperLeftx = int(min(x0,x1))
                self.upperLefty = int(min(y0,y1))
            return None
        else:
            return (self.upperLeftx,self.upperLefty,self.recWidth,self.recHeight) #these values are in reference to what the OpenCV can see

    def drawRec(self): #this draws on the openCV frame
        return cv2.rectangle(self.frame, (self.upperLeftx,self.upperLefty), (self.upperLeftx + self.recWidth, self.upperLefty + self.recHeight), (255,0,255),2)


########################## HELPER FUNCTIONS####################

def getScores(scoreFile):
    scores = dict()
    for i in scoreFile.split(","): #need to unwrap file
        if len(i)<1:
            break
        name,score = i.split(":")
        score = int(score)
        if name in scores:
            if score>scores[name]:
                scores[name] = score #keeping best score 
        else:
            scores[name] = score
    return scores

#use recursion to get the top 3 scores in the Play Mode
#RECURSION
def getHighestScoresMode(scoreDict, count = 0, scoreAndPlayer = dict(), bestScores = set()):
    highest = 0 
    highestPerson = None
    if count == 3 or len(scoreDict) ==0 : 
        return scoreAndPlayer, bestScores
    else:
        for person in scoreDict:
            if scoreDict[person] > highest:
                highest = scoreDict[person]
                highestPerson = person
        if highest in scoreAndPlayer:
            scoreAndPlayer[highest].append(highestPerson) #what happens if 3 people share the same score?
        else:
            scoreAndPlayer[highest] = [highestPerson] #adding to a dictionary
        bestScores.add(highest) 
        #will add the last score they came to if a tie
        if highestPerson != None:
            del scoreDict[highestPerson] #Citation 6 --> this takes out the key only if it is in the set
        count +=1 
        return getHighestScoresMode(scoreDict, count, scoreAndPlayer, bestScores)
            

#same function as above but just used for reaction mode
def getHighestScoresModeReaction(scoreDict, count = 0 , scoreAndPlayer = dict(), bestScores = set()):
    highest = 0 
    highestPerson = None
    if count == 3 or len(scoreDict) ==0 : 
        return scoreAndPlayer, bestScores
    else:
        for person in scoreDict:
            if scoreDict[person] > highest:
                highest = scoreDict[person]
                highestPerson = person
        if highest in scoreAndPlayer:
            scoreAndPlayer[highest].append(highestPerson) #what happens if 3 people share the same score?
        else:
            scoreAndPlayer[highest] = [highestPerson] #adding to a dictionary
        bestScores.add(highest) 
        #will add the last score they came to if a tie
        if highestPerson != None:
            del scoreDict[highestPerson] #Citation 6 --> this takes out the key only if it is in the set
        count +=1 
        return getHighestScoresModeReaction(scoreDict, count, scoreAndPlayer, bestScores)

#this is a function that returns a random tuple and radius of where the dot is 
def getDotPosition(width, height, radius): #will need to change the radius to fit pixles when 12ft away
    #want to randomly generate a target
    screenwidth = width
    screenheight = height
    xrange = screenwidth - radius 
    yrange = screenheight -radius
    ballx = random.randint(0+radius,xrange)
    bally = random.randint(0+radius,yrange) #check this 
    return (ballx, bally, radius)


def getReactionDot(screenWidth, screenHeight, targetRad, RED, GREENTARGET):
    #want to randomly generate a target
    colors = [RED,ORANGE, BLUE, GREENTARGET, GREENTARGET, GREENTARGET,GREENTARGET,GREENTARGET] #3/4 chance get a green dot
    xrange = screenWidth - targetRad
    yrange = screenHeight - targetRad
    ballx = random.randint(0+targetRad, xrange)
    bally = random.randint(0+targetRad, yrange)
    ballColor = random.choice(colors)
    return (ballx, bally, targetRad, ballColor)

def getSong(game_Music):
    #this is a list of music
    song = random.choice(game_Music)
    return song #this is a string 
        
def pixleToFeet(pixlewidth,pixleheight,ftwidth,ftheigth):
    w = pixlewidth/ftwidth
    h = pixleheight/ftheigth
    return (w+h)/2 #this is the avg pixle/ft ratio which will help us figure out when to look for a collision

def calculateBallSizeinCollision(ptoftRatio, ballRad):
    collisionrad = ptoftRatio * ballRad 
    return collisionrad

def almostEqual(x,y,epsilon = 5): #returns true or false
    return (math.fabs(x-y)<=epsilon)


#this is where the adjusted ball dimensions are calculated
def ballinRectangleDims(rectangle, balldims, pygameScreenWidth,pygameScreenHeight):
    #pygameScreenWidth and pygameScreenHeight are with respect  to pygame
    #balldims are with respect to openCV screen
    #rectangle is with respect to openCV screen


    upperleftX, upperleftY, recWidth,recHeight = rectangle
    x,y,w,h = balldims[0]

    screenRatio = (pygameScreenWidth/recWidth + pygameScreenHeight/recHeight)/2
    
    ballInRecX, ballInRecY = x - upperleftX, y - upperleftY

    ballinPygameX, ballinPygameY = ballInRecX*screenRatio, ballInRecY*screenRatio
    return [(ballinPygameX,ballinPygameY,w,h)] #radius and height are not subjective they are absolute

def changeDirections(throwTracker): #the throw tracker should reset each time that a ball leaves the frame 
    # throw tracker-->this would be [([x,y,w,h], "Direction"), ["x2,y2,w2,h2,], "direction"]
    prevDir = throwTracker[0][1]
    if len(throwTracker) > 1: #there has been two points
        for throw in throwTracker:
            direction = throw[1]
            if prevDir == None:
                prevDir = direction
            else:
                if direction == None:
                    continue #this data point may just be faulty
                elif direction == "AwayFromWall" and prevDir == "TowardsWall":
                    return True
                elif direction == "AwayFromWall" and prevDir == "Still":
                    return True 
                prevDir = direction
    return False

def getZPosition(balldimensions, ptoFtRatio, expectedRadWall, distanceFromProjectorToWall):
    #if you are looking at something from 2 times the distance it is half the size
    #these are the ball dimensions that are adjusted to the rectangle 
    #distance to projector (in feet)
    x,y,w,h = balldimensions[0]
    currentRad = w/2 #this is in pixles
    #expected rad is also in pixles

    radiusRatio = expectedRadWall/currentRad
    distanceFromProjector = distanceFromProjectorToWall * radiusRatio
    distanceToWall = distanceFromProjectorToWall - distanceFromProjector #want this value to be 0 which means
    #it would hae hit the wall
    return distanceToWall #want this value to be 0

def approximatingHitY(prevBallDims, currentBallDims, ptoFTRatio, expectedRadWall, distanceFromProjectorToWall):
	x1,y1,w1,h1 = prevBallDims[0] #this is the ball moving towards the wall
	prevRad = w1/2
	z1 = getZPosition(prevBallDims, ptoFTRatio, expectedRadWall, distanceFromProjectorToWall)

	x2,y2,w2,h2 = currentBallDims[0] #this ball is moving away from the wall
	currRad = w2/2
	z2 = getZPosition(currentBallDims, ptoFTRatio, expectedRadWall,distanceFromProjectorToWall)

	distancey = math.fabs(y1 - y2)
	
	#gemoetry
	x = (z2*distancey)/(z1+z2) #this required a lot of geometry
	dhit = y1 + x #where x is the point relative to y1 and y2 where the ball hit

	return dhit #this is the y poistion on the pygame screen where it hit

def approximatingHitx(prevBallDims, currentBallDims): #why does this not work?
    x1,y1,w1,h1 = prevBallDims[0] #this is the ball moving towards the wall
    x2,y2,w2,h2 = currentBallDims[0] #this ball is moving away from the wall
    averageX = (x1+x2)/2
    return averageX


def checkForCollisions(actualdims,expectedRad):
    x,y,w,h = actualdims[0] #tuple inside a list
    #want to use almost equal because there is a lot of uncertainty
    return almostEqual( (w/2), expectedRad)



def checkForTargetCollision(rectangle,targetX,targetY,targetRad, adjustedballdims):
    #rectangle --> upperleftx, upperlefty, w,h
    #balldims --> balldims[0] = x,y,w,h

    #all of these dimensions are in pixles
    #get tennis ball dimensions with respect to rectangle

    tX,tY,tWidth,tHeight = adjustedballdims[0]
    tRad = tWidth/2

    #Circle Collision without average
    distance2 = ((targetX - tX)**2 + (targetY - tY)**2)**0.5
    remainder2 = (targetRad + tRad) - distance2

    
    return (remainder2>=0) #if they are touching or hitting

def circleCollision(xapproxXHit,yapproxYHit, ballRad,cx,cy,targetRad):
    dx = math.fabs(xapproxXHit - cx)
    dy = math.fabs(yapproxYHit - cy)
    distance = ( dx**2 +dy**2)**0.5
    radTotal = ballRad + targetRad
    return (radTotal>=distance)

   


def main():
    game = gameManager() #calls init
    game.run()

if __name__ == '__main__':
    main()



    ################# CITATIONS ################

    # (1) https://github.com/LBPeraza/Pygame-Asteroids/blob/master/Examples/DotExample.py
    # (2) https://codereview.stackexchange.com/questions/104929/countdown-clock-in-python
    # (3) http://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
    # (4) http://stackoverflow.com/questions/15056444/pygame-time-set-timer-confusion
    # (5) http://www.pythonforbeginners.com/files/reading-and-writing-files-in-python
    # (6) http://www.cs.cmu.edu/~112/notes/notes-maps.html
    # (7) https://www.python.org/doc/av/
        # --> This was used for the pygame audio
    # The basic format of my code used this following citation as an example 
    #(8) https://github.com/LBPeraza/Pygame-Asteroids/blob/master/Examples/DotExample.py
        # (Note none of this code was copy and pasted or copied direclty)

        #Graphics Citations

    # (9) http://www.dafont.com/28-days-later.font
    # (10) https://soundcloud.com/user-508724476/sets/my-beats
        # --> Song IAMJ "Lies"
    # (11) https://soundcloud.com/user-508724476/sets/my-beats
        # --> Song "If You'll Ever"
    # (12) https://soundcloud.com/flume/higher-flume-remix
        # --> Song Ta-ku "Higher Remix"
    # (13) https://soundcloud.com/joeypecoraro/you-changed
        # --> Song "You Changed"
    # (14) https://www.pinterest.com/pin/54958057924147481/
        # --> Basketball Background Picture

    
    
    
    
    
    
