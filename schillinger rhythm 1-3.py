#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import pygame
from midiutil.MidiFile import MIDIFile



class Midi():
    """docstring for Midi"""

    def __init__(self):
        self.MyMIDI = MIDIFile(1)
        track,time = 0,0
        self.MyMIDI.addTrackName(track,time,"Sample Track")
        self.MyMIDI.addTempo(track,time,120)
         
    def note_add(self, pitch, time, duration):
        self.MyMIDI.addNote(0,0, pitch, time, duration, 100)

    def file_play(self):
        binfile = open("output.mid", 'wb')
        self.MyMIDI.writeFile(binfile)
        binfile.close()

        file = 'output.mid'
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy(): 
            pygame.time.Clock().tick(1)

class Part(object):
    """docstring for Rhythm"""
    def __init__(self, periods, semetry):
        
        self.tic = 1
        self.periods = periods
        self.Notes = []

        # Создание карты периодичностей
        Maps = [[] for x in periods] 
        while True:
            s=0
            for i, period in enumerate(periods): 
                if self.tic % period == 0: Maps[i]+=[1]; s +=1
                else: Maps[i]+=[0]
            if s == len(periods): break
            self.tic+=1

        if semetry == True: # если симметричная 
            new_Maps = []
            max_shift = (max(periods)**2-periods[0]*periods[1])/max(periods)
            shifts = [(max_shift-x, x) for x in range(max_shift+1)]
            self.tic += max(periods)*max_shift
            for shift in shifts:
                for Map in Maps:
                    new_Maps += [[2] * (max(periods)*shift[0]) + Map + [2] * (max(periods)*shift[1])]
            new_Maps.reverse()
            Maps = new_Maps

        # создание результирующей периодичности
        Digs = []
        for tic in range(self.tic):
            if 1 in [Map[tic] for Map in Maps]: Digs += [1]
            else: Digs += [0]

        # вычисление длительностей
        self.Rhythm, dur = [], 0
        for dig in Digs:
            dur+=1
            if dig == 1: self.Rhythm += [dur]; dur = 0
            
    def sync_notes(self, notes):
        # синхронизация ритма и нот
        self.Notes = notes
        tic = 1
        while True:
            if tic % len(self.Notes) == 0 and tic % len(self.Rhythm) == 0: break
            tic+=1
        self.Rhythm *= tic/len(self.Rhythm)
        self.Notes *= tic/len(self.Notes)
        self.tic = sum(self.Rhythm)


class Menu(object):
    """docstring for Menu"""
    def __init__(self):
        self.layers = {}
        self.intro()

    def intro(self):
        print u'╔══════════════════════════════════════════════════════════╗'
        print u'║ МУЗЫКАЛЬНАЯ АКАДЕМИЯ ШИЛЛИНГЕРА                          ║'
        print u'║ Теория ритма #1-1                                        ║'
        print u'╚══════════════════════════════════════════════════════════╝'
        print u'┌──────────────────────────────────────────────────────────┐'
        print u'│ Вычисление интерферениции мономиальных периодичностей    │'
        print u'└──────────────────────────────────────────────────────────┘'
        print 

    def clear(self):
        os.system(['clear','cls'][os.name == 'nt'])
        self.intro()
        self.rend() 

    def new_part(self):
        
        while True:
            try:
                self.clear()
                print u'Задайте номер дорожки:' 
                layer = input('>')
                if self.layers.has_key(layer): self.layers[layer] += []
                else: self.layers[layer] = []
                break
            except: raw_input('Error'); pass
        
        while True:
            try:
                self.clear()
                d, c = 'd', 'c'
                print u'Введите периодичности через запятую\n- d для деления\n- c для контртемы' 
                periods = input('>') 
                if type(periods) == int: periods = tuple([periods])
                break
            except: raw_input('Error'); pass
        
        # контртема
        if periods[-1] == 'c':
            periods = periods[:-1] 
            m = 1
            for x in periods: m*=x
            periods = tuple([m/x for x in periods])
        
        # симметрия
        if periods[-1] == 'd': 
            periods = periods[:-1] 
            semetry = True 
        else: semetry = False

        # создаем часть
        self.layers[layer] += [Part(periods, semetry)]
        
        while True:
            try:
                self.clear()
                print u'Введите ноты через запятую:' 
                notes = input('>')
                if type(notes) == int: notes = tuple([notes])
                break
            except: raw_input('Error'); pass
        self.layers[layer][-1].sync_notes(notes)

        self.clear()

    def rend(self):
        for layer in self.layers:
            print u'\nДОРОЖКА', layer, '\n'
            for i, part in enumerate(self.layers[layer]):
                result = ''
                for dur in part.Rhythm: result += '|_' + '__'*(dur-1)
                print u'Часть:'+str(i), u' периоды:'+str(part.periods), u' тиков:'+str(part.tic), u' атак:'+str(len(part.Rhythm))
                print result, u'\nРитм:', part.Rhythm, u'\nНоты:', part.Notes
                print 

    def play(self):
        try:
            dir = os.path.abspath(os.curdir)
            os.path.join(r'dir', 'output.mid')
            os.remove('output.mid')
        except:pass
        self.midi = Midi()

        while True:
            try:
                self.clear()
                for layer in self.layers:
                    time = 0  
                    for part in self.layers[layer]:
                        for duration, note in zip(part.Rhythm, part.Notes):          
                            self.midi.note_add(note, time, duration)
                            time += duration
                print u'midi файл записан','\n'
                self.midi.file_play()
                self.clear()
                break
            except: raw_input('Error'); pass

    def balance(self):
        while True:
            try:
                self.clear()
                print u'Введите индексы:\n(например [дорожка,часть],[дорожка])'
                parts = input('>')

                tics = []
                if len(parts[0]) == 1: tics += [sum([part.tic for part in self.layers[parts[0][0]]])]
                else: tics += [self.layers[parts[0][0]][parts[0][1]]]
                if len(parts[1]) == 1: tics += [sum([part.tic for part in self.layers[parts[1][0]]])]
                else: tics += [self.layers[parts[1][0]][parts[1][1]]]
                
                new_dur = max(tics)-min(tics)
                i_min_part = tics.index(min(tics))
                if len(parts[i_min_part]) == 1:
                    for part in self.layers[parts[i_min_part][0]]:
                      part.Rhythm += [new_dur]  
                else: self.layers[parts[i_min_part][0]][parts[i_min_part][1]].Rhythm += [new_dur]

                self.clear()
                break
            except: raw_input('Error')

    def sync_parts(self):
        while True:
            try:
                self.clear()
                a = 'all'
                print u'Введите номера дорожек для синхронизации (a - для всех):'
                layers = input('>')

                if layers == 'all': layers = [layer for layer in self.layers]

                total_tics = 0
                while True:
                    attacks = []
                    total_tics += 1
                    for layer in layers:
                        layer_tic = sum([part.tic for part in self.layers[layer]])
                        attacks += [1 if total_tics%layer_tic == 0 else 0]
                    if 0 not in attacks: break

                for layer in layers:
                    for part in self.layers[layer]:
                        part.Rhythm *= total_tics/sum([part.tic for part in self.layers[layer]])
                        part.Notes *= total_tics/sum([part.tic for part in self.layers[layer]])
                        part.tic *=  total_tics/sum([part.tic for part in self.layers[layer]])
                self.clear()
                break
            except: raw_input('Error')

    def delete(self):
        while True:
            try:
                self.clear()
                print u'Введите дорожку и часть через запятую:'
                part = input('>')

                del self.layers[part[0]][part[1]]
                if len(self.layers[part[0]]) == 0: del self.layers[part[0]]
                self.clear()
                break
            except: raw_input('Error')


# ////////////////////////////////////////////////////////////////////////////


m = Menu()
m.new_part()
while True:    
    while True:
        try:
            print u'1 - создать новую часть\n2 - синхронизировать\n3 - баланс\n4 - записать и послушать midi\n5 - удалить часть'
            ask = input('>')
            if ask == 1: m.new_part()
            elif ask == 2: m.sync_parts()
            elif ask == 3: m.balance()
            elif ask == 4: break
            elif ask == 5: m.delete()
            else: ask['Error']
        except: raw_input('Error1'); m.clear()

    while True:
        try:
            m.play()
            print u'1 - прослушать еще раз\n2 - продолжить'
            ask = input('>') 
            if ask == 1: pass
            elif ask == 2: m.clear(); break
            else: ask['error']
        except: raw_input('Error'); m.clear()