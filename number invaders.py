#!/usr/bin/env python

'''
Number Invaders v0.2
(originally created by CASIO)

by Takis Tsiberis
http://takira.freehosting.net/
takira_gr@yahoo.com

Copyright (C) 2007 Panagiotis Tsiberis
This program is free software;
you can redistribute it and/or
modify it under the terms of the
GNU General Public License
as published by the
Free Software Foundation;
either version 2 of the License,
or (at your option) any later version.

This version works for both Linux and Windows.

Now, thanks to my brother Simon (who was a proud owner
of one of Casio's watches) with authentic gameplay.

Started coding at 7/6/2007
Finished at 7/22/2007

Version 0.2.1
Martin Ahnelov (a pygamer) has made some suggestions.

Version 0.2.2
The game had a performance bug.

Version 0.3
No real changes. I changed the name of the game.
'''

#-------------------Imports-------------------
import pygame
from pygame.locals import *
from os import path
from random import randint

#-------------------Constants-------------------
VERSION = '0.3'
SIZE = (800,200)
PALE_YELLOW = (255,255,205)
BLACK = (0,0,0)
RED =(100,0,0)
_FONT = 'MgOpenModernaBoldOblique.ttf'
data_folder = 'ni_data'

#-------------------Global functions-------------------
def load_image(name, colorkey=None):
    fullname = path.join(data_folder, name)
    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is -1:
        colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image

def load_sound(name):
    return pygame.mixer.Sound(path.join(data_folder, name))

def display_some_text(text,size,p,b,centered=0):
    font = pygame.font.Font(path.join(data_folder,_FONT), size)
    t = font.render(text, 1, BLACK)
    trect = t.get_rect()
    if centered:
        trect.centerx = p[0]
        trect.centery = p[1]
    else:
        trect.left = p[0]
        trect.top = p[1]
    b.blit(t, trect)

#-------------------Classes-------------------
class simple_button(pygame.sprite.Sprite):
    def __init__(self,x,y,title,screen,background):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image('button.png')
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x
        self.status = 0
        # Draw some shadow lines
        screen.lock()
        pygame.draw.line(background,BLACK,(x+1,y+self.rect.height),\
                         (x+self.rect.width-1,y+self.rect.height)) #horizontal
        pygame.draw.line(background,BLACK,(x+self.rect.width,y+1),\
                         (x+self.rect.width,y+self.rect.height)) #vertical
        screen.unlock()
        # Display some text
        display_some_text(title,18,(60,15),self.image,1)
    def press(self):
        self.rect.inflate_ip(-2,-2)
        self.status = 1
    def unpress(self):
        self.rect.inflate_ip(2,2)
        self.status = 0
    def is_focused(self,x,y):
        return self.rect.collidepoint(x,y)

class digit(pygame.sprite.Sprite):
    imagelist = ['blank.png','one.png','two.png','three.png','four.png','five.png',\
                 'six.png','seven.png','eight.png','nine.png','zero.png','ufo.png']
    def __init__(self,x,y,_index,number=0):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image('blank.png',-1)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.left = x
        self.rect.top = y
        self.number = number
        self._index = _index
    def update(self,a):
        if self.number != a:
            self.number = a
            self.image = load_image(self.imagelist[self.number],-1)
            self.rect = self.image.get_rect()
            self.rect.left = self.x
            self.rect.top = self.y

class radio_button(pygame.sprite.Sprite):
    def __init__(self,screen,text,topleft):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.image2 = pygame.Surface((80, 20)).convert()
        self.image2.fill(PALE_YELLOW)
        display_some_text(text, 18, (20,0), self.image2)
        self.image = self.image2
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        if text == 'On' or text == 'Right':
            self.is_clicked = 1
        else:
            self.is_clicked = 0
        self.is_dirty = 1
        self.update()
    def draw_a_square(self,filled):
        self.screen.lock()
        pygame.draw.rect(self.image2, PALE_YELLOW, (0,4,12,12))
        if filled:
            f = 0
        else:
            f = 2
        pygame.draw.rect(self.image2, BLACK, (0,4,12,12), f)
        self.screen.unlock()
    def update(self):
        if self.is_dirty:
            if self.is_clicked:
                self.draw_a_square(1)
            elif not self.is_clicked:
                self.draw_a_square(0)
            self.is_dirty = 0
    def is_focused(self,x,y):
        return self.rect.collidepoint(x,y)

class radio_button_holder:
    def __init__(self,title,choices,place,screen,background):
        self.title = title
        self.place = place
        self.screen = screen
        self.background = background
        self.a = radio_button(screen,choices[0],[self.place[0],self.place[1]])
        self.b = radio_button(screen,choices[1],[self.place[0],self.place[1] + 20])
        display_some_text(self.title,18,[self.place[0],self.place[1] - 20],self.background,0)
        self.var = 0
    def update(self):
        if self.a.is_clicked and self.a.is_dirty:
            self.b.is_clicked = 0
            self.b.is_dirty = 1
            self.var = 0
        elif self.b.is_clicked and self.b.is_dirty:
            self.a.is_clicked = 0
            self.a.is_dirty = 1
            self.var = 1
        self.a.update()
        self.b.update()

class gameplay:
    def __init__(self,screen,background,music_is_off):
        self.screen = screen
        self.background = background
        self.digit0 = digit(65,10,0,0)
        self.digit1 = digit(135,10,0,0)
        self.digit2 = digit(205,10,0,0)
        self.digit3 = digit(275,10,0,0)
        self.digit4 = digit(345,10,0,0)
        self.digit5 = digit(415,10,0,0)
        self.digit6 = digit(485,10,0,0)
        self.digit7 = digit(555,10,0,0)
        self.digit8 = digit(700,10,0,0)
        self.group = [self.digit0,self.digit1,self.digit2,\
                      self.digit3,self.digit4,self.digit5,\
                      self.digit6,self.digit7,self.digit8]
        self.allsprites = pygame.sprite.RenderPlain(self.group)
        self.loop = 0
        self.count = 0
        self.numberlist = [0,0,0,0,0,0,0,0]
        self.seven_times = 1
        self.numbers = 0
        self.killed_numbers = 0
        self._sum = 0
        self.ufos = 0
        self.indent = 0
        self.sound1 = load_sound('msg.wav')
        self.sound2 = load_sound('can25.wav')
        self.sound1.set_volume(0.4)
        self.sound2.set_volume(0.2)
        self.music_is_off = music_is_off
        self.sum_list = []
    def update(self,a):
        # update the last digit
        if self.killed_numbers < 15:
            self.digit8.update(a)
        # update the variables
        elif self.killed_numbers == 15:
            self.killed_numbers = 0
            self.seven_times += 1
            if self.seven_times == 8:
                self.seven_times = 1
                if self.indent == 0:
                    self.indent = 1
                else:
                    self.indent = 0
            self.loop = 0
            self.count = 0
            self.numbers = 0
            self._sum = 0
            self.ufos = 0
            self.sum_list = []
        # update the rest of the group
        for x in range(8):
            self.group[x].update(self.numberlist[x])
        # update the numberlist
        self.loop += 1
        if self.loop == 115 - (self.seven_times * 10):
            self.loop = 0
            for x in range(self.count,0,-1):
                z = 7 - x - self.indent
                self.numberlist[z] = self.numberlist[z+1]
            if self.numbers == 15:
                self.numberlist[7 - self.indent] = 0
            elif self.sum_list and self.sum_list[0] % 10 == 0 and self.sum_list[0] > 10 * self.ufos:
                self.numberlist[7 - self.indent] = 11
                self.ufos += 1
                self._sum = 10 * self.ufos
                self.numbers += 1
                if not self.music_is_off:
                    self.sound2.play()
            else:
                self.numberlist[7 - self.indent] = randint(1,10)
                self.numbers += 1
            if self.sum_list:
                self.sum_list.remove(self.sum_list[0])
            self.count += 1
        return self.count == 9 - self.indent

class flowing_text(pygame.sprite.Sprite):
    def __init__(self,screen,background):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen
        self.background = background
        text_file = path.join(data_folder,'info.txt')
        in_file = open(text_file,"r")
        self.text = in_file.read()
        in_file.close()
        font = pygame.font.Font(path.join(data_folder,_FONT), 40)
        self.image = font.render(self.text, 1, BLACK, PALE_YELLOW).convert()
        self.rect = self.image.get_rect()
        self.rect.top = 140
        self.rect.left = 800
        self.size = self.rect.width
        self.x = SIZE[0]
    def update(self,a):
        self.x -= a
        self.rect.left = (self.x)
        if self.rect.left <= -self.size:
            self.x = SIZE[0]

class game:
    def __init__(self,screen,background,a,b):
        score = play(screen,background,a,b)
        after_play_var = after_play(score,screen,background,b)
        while after_play_var == 1:
            score = play(screen,background,a,b)
            after_play_var = after_play(score,screen,background,b)
        pygame.quit()

#-------------------Game functions-------------------
def welcome_screen(screen,background):
    bestx = 40
    image = load_image('pygame_icon.png',-1)
    background.blit(image,(20 + bestx,20))
    display_some_text('Some settings first',28,[400 + bestx,40],background,1)
    a = radio_button_holder('Handed',['Right','Left'],[240 + bestx,100],screen,background)
    b = radio_button_holder('Music/Sound',['On','Off'],[460 + bestx,100],screen,background)
    c = simple_button(660,150,'Proceed',screen,background)
    group = (a.a,a.b,b.a,b.b,c)
    allsprites = pygame.sprite.RenderPlain(group)

    run = 1
    _exit = 0
    while run:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                _exit = 1
                run = 0
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                for x in group[:4]:
                    if x.is_focused(event.pos[0],event.pos[1]) and not x.is_clicked:
                        x.is_clicked = 1
                        x.is_dirty = 1
                        a.update()
                        b.update()
                if c.is_focused(event.pos[0],event.pos[1]):
                    c.press()
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if c.status:
                    c.unpress()
                    run = 0

        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.update()

    if _exit:
        pygame.quit()
    else:
        background.fill(PALE_YELLOW)
        allsprites.remove(group)
        _game = game(screen,background,a.var,b.var)

def play(screen,background,left_handed,music_is_off):

    # Adjust the keyboard settings
    if not left_handed:
        key_var1 = K_RCTRL
        key_var2 = K_LCTRL
        key_str1 = 'Aim'
        key_str2 = 'Shoot'
    else:
        key_var1 = K_LCTRL
        key_var2 = K_RCTRL
        key_str1 = 'Shoot'
        key_str2 = 'Aim'

    # Play some music
    if not music_is_off:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        musicfile = path.join(data_folder,'jt_strng.xm')
        pygame.mixer.music.load(musicfile)
        pygame.mixer.music.play(-1)

    # Draw the backstage
    screen.lock()
    pygame.draw.line(background,BLACK,(65 - 3,150),(620 + 2,150))
    pygame.draw.line(background,BLACK,(700,150),(765,150))
    for x in range(9):
        distance = 70 * x
        pygame.draw.line(background,BLACK,(65 - 3 + distance,150),(65 - 3 + distance,145))
    pygame.draw.line(background,BLACK,(700,150),(700,145))
    pygame.draw.line(background,BLACK,(765,150),(765,145))
    screen.unlock()
    display_some_text('Left <Ctrl> to ' + key_str1,18,[47,170],background)
    display_some_text('<Space> to pause',18,[251,170],background)
    display_some_text('Right <Ctrl> to ' + key_str2,18,[460,170],background)
    display_some_text('Score = 0',18,[683,170],background)

    # Game begins
    a = gameplay(screen,background,music_is_off)
    clock = pygame.time.Clock()

    score = 0
    run = 1
    counter = 0
    pause = 0
    scoreground = pygame.Surface((100,30))
    scoreground.fill(PALE_YELLOW)

    while run:
        clock.tick(100)
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                run = 0
            elif event.type == KEYDOWN and event.key == key_var1 and not pause: # Right CTRL gets pressed
                if a.digit8.number in a.numberlist and a.digit8.number != 0:
                    if a.digit8.number == 11:
                        score += 10
                        if not music_is_off:
                            a.sound2.play()
                    else:
                        if a.digit8.number != 10:
                            a._sum += a.digit8.number
                            a.sum_list.append(a._sum)
                        score += 1
                        if not music_is_off:
                            a.sound1.play()
                    if score == 1000:
                        score = 0
                    a.numberlist.remove(a.digit8.number)
                    a.numberlist.insert(0,0)
                    a.count -= 1
                    a.killed_numbers += 1
                    background.blit(scoreground,(752,165))
                    display_some_text(str(score),18,(755,170),background)
            elif event.type == KEYDOWN and event.key == key_var2 and not pause: # Left CTRL gets pressed
                counter = a.digit8.number
                if counter > 10:
                    counter = 1
                else:
                    counter += 1
            elif event.type == KEYDOWN and event.key == K_SPACE: # Space gets pressed
                if pause == 1:
                    pause = 0
                elif pause == 0:
                    pause = 1
        if not pause:
            screen.blit(background, (0, 0))
            u = a.update(counter)
            a.allsprites.draw(screen)
            pygame.display.update()
            if u: run = 0

    a.allsprites.remove(a.group)
    background.fill(PALE_YELLOW)
    screen.blit(background, (0, 0))
    pygame.display.update()
    return score

def after_play(score,screen,background,music_is_off):

    if not music_is_off:
        pygame.mixer.music.stop()
        musicfile = path.join(data_folder,'jt_letgo.xm')
        pygame.mixer.music.load(musicfile)
        pygame.mixer.music.play(-1)

    display_some_text('Final score is ' + str(score),40,[400,50],background,1)
    display_some_text('<Space> for fast forward',15,[400,95],background,1)

    b1 = simple_button(100,80,'Play',screen,background)
    b2 = simple_button(570,80,'Later',screen,background)
    f1 = flowing_text(screen,background)
    group = (b1,b2,f1)
    allsprites = pygame.sprite.RenderPlain(group)

    clock = pygame.time.Clock()
    run = 1
    after_play_var = 0
    speed = 1

    while run:
        clock.tick(160)
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                run = 0
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if b1.is_focused(event.pos[0],event.pos[1]):
                    b1.press()
                elif b2.is_focused(event.pos[0],event.pos[1]):
                    b2.press()
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if b1.status:
                    b1.unpress()
                    after_play_var = 1
                    run = 0
                elif b2.status:
                    b2.unpress()
                    run = 0
            elif event.type == KEYDOWN and event.key == K_SPACE:
                speed = 10
            elif event.type == KEYUP and event.key == K_SPACE:
                speed = 1

        screen.blit(background, (0, 0))
        f1.update(speed)
        allsprites.draw(screen)
        pygame.display.update()

    background.fill(PALE_YELLOW)
    allsprites.remove(group)
    return after_play_var

def main():
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    pygame.display.set_caption("Number Invaders v" + VERSION)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(PALE_YELLOW)
    screen.blit(background,(0,0))
    pygame.display.update()

    welcome_screen(screen, background)

if __name__ == "__main__": main()
