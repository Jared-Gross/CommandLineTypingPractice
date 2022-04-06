import contextlib
from pydoc import ispackage
import random
from datetime import datetime
import os
import time
import threading

import msvcrt
from rich import print
from colorama import init, Fore, Back, Style

init(convert=True)

clear = lambda: os.system('cls')

CPM: int = 0
CP15Sec: int = 0
characterPresses: int = 0
characterPresses15Sec: int = 0
startTime = datetime.now()
startTime15Sec = datetime.now()

def timeHandler():
    global CPM, CP15Sec, startTime, startTime15Sec
    while True:
        diffTime = datetime.now() - startTime15Sec
        if diffTime.seconds > 15:
            startTime15Sec = datetime.now()
            characterPresses15Sec = 0
        try:
            CP15Sec = int(characterPresses/diffTime.seconds)
            CPM = int(characterPresses/((datetime.now()-startTime).seconds/60))
        except ZeroDivisionError:
            CP15Sec = 0
            CPM = 0
        time.sleep(1)

class TypingTest():
    def __init__(self):
        self.wordsList: list[str] = []
        self.selectedWords: list[str] = []
        self.loadWords()
        self.generateWordsList()
        self.currentWord: str = ''
        self.playerInputString: str = ''
        self.playerInputList: list[str] = []
        self.isPlaying: bool = True
        self.display()
        self.getInput()
        
    def loadWords(self):
        with open('words.txt', 'r') as wordsFile:
            self.wordsList = [word.replace('\n', '') for word in wordsFile.readlines()]

    def generateWordsList(self):
        self.selectedWords = [self.selectNewWord() for _ in range(20)]

    def compareWords(self, u1: str, u2: str) -> int:
        try:
            s1 = unicode(u1)    
            s2 = unicode(u2)
        except:
            s1 = u1
            s2 = u2        
        if len(s1) < len(s2):
            return self.compareWords(u2, u1)
        if not s1:
            return len(s2)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
                deletions = current_row[j] + 1       # than s2
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]
    
    def selectNewWord(self) -> str:
        newWord = random.choice(self.wordsList)
        for word in self.selectedWords:
            if word is newWord:
                newWord = random.choice(self.wordsList)
        return newWord
    
    def display(self):
        self.compiled: str = ' '.join(self.selectedWords)
        self.currentWord = self.selectedWords[len(self.playerInputString.split(' '))-1]
        clear()
        self.compiled = self.compiled.replace(self.currentWord, Fore.GREEN + self.currentWord + Fore.WHITE)
        print(f'TOTAL CPM: {CPM}\tCP/15sec {CP15Sec}\n')
        print(f"{Fore.WHITE}{self.compiled}")
        lastWord: str = ''
        for index, wordInput in enumerate(self.playerInputString.split(' ')):
            wordInput = wordInput.replace('\n', '')
            if (index+1) == len(self.playerInputString.split(' ')):
                print(f"{Fore.BLUE}{wordInput} ", end='', flush=True)
                lastWord = wordInput
            elif self.compareWords(wordInput, self.selectedWords[index]) == 0:
                print(f"{Fore.GREEN}{wordInput} ", end='', flush=True)
            else:
                print(f"{Fore.RED}{wordInput} ", end='', flush=True)
                
        if len(self.playerInputString.split(' ')) > 4:
            self.selectedWords.pop(0)
            self.selectedWords.append(self.selectNewWord())
            self.playerInputList = ''.join(self.playerInputList).split(' ')
            self.playerInputList.pop(0)
            self.playerInputList = list(' '.join(self.playerInputList))
    

    def getInput(self):
        global characterPresses, characterPresses15Sec
        self.playerInputList: list[str] = []
        while self.isPlaying:
            x = msvcrt.getch()
            characterPresses += 1
            characterPresses15Sec += 1
            if x == b'\x1b': # Enter breaks the loop and heads onward with the input.
                break
            elif x == b'\x08': # Backspace
                try:
                    self.playerInputList.pop(-1)
                except Exception:
                    self.playerInputList = []
            else:
                with contextlib.suppress(UnicodeDecodeError):
                    self.playerInputList.append(x.decode("utf-8"))
            self.playerInputString = ''.join(self.playerInputList)
            self.display()
    
if __name__ == '__main__':
    threading.Thread(target=timeHandler).start()
    typingTest = TypingTest()