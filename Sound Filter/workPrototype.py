import sys
import msvcrt
import player
import numpy as np

class PseudoTTY(object):
    def __init__(self, underlying):
        self.__underlying = underlying
    def __getattr__(self, name):
        return getattr(self.__underlying, name)
    def isatty(self):
        return True

low = raw_input("lo-fi?\n")

noise = raw_input("noise?\n")

loop = raw_input("loop?\n")

person = input("speed?\n")
print(person)

sys.stdin = PseudoTTY(sys.stdin)

player = player.Player("C:\Users\Ryun an\Downloads\Heaven_Sent_and_Ecstasy_-_Rapping_With_My_Subconsc.wav",person,1024)

inputChar='a'
floatBuffer = 0.0
behindZero = False;
beZeroNum = 1;
energyBuffer = [[0 for x in range(32)] for y in range(43)]
average = [0 for x in range(32)]
threshold = 3
counter = 0
removeCounter = 0;

print "start Playing"

while player.returnData():
    
    tempBuffer = [0 for x in range(32)]
    
    if low=='y':
        player.lofiPlay()
    elif noise == 'y':
        player.noisePlay()
    else:
        X = player.play()
        
    for i in range(0,31):
        for j in range(i*32,(i+1)*32):
            tempBuffer[i] = tempBuffer[i] + X[j]
        tempBuffer[i] = 32*tempBuffer[i]/1024
        if tempBuffer[i] > average[i] and i<6:
            print "beat in range ",i  
        average[i] = average[i] + ((tempBuffer[i] - energyBuffer[counter%43][i])/32)    
        energyBuffer[counter%43][i] = tempBuffer[i]
    
    if loop=='y':
        player.loop()
    
    if msvcrt.kbhit():
        inputChar = msvcrt.getch();
        print inputChar
        if inputChar.isdigit():
            if behindZero==False:
                floatBuffer = floatBuffer*10 + int(inputChar)
            else:
                print "beZeroNum: ",beZeroNum
                floatBuffer = floatBuffer + (float(inputChar)/(10**beZeroNum))
                beZeroNum = beZeroNum + 1
            print "Input: ", inputChar, " / current buffer: ",floatBuffer
        elif inputChar == '.':
            print "change in digit"
            behindZero = True
        elif inputChar == " ":
            if floatBuffer != 0.0:     
                print "Restart with speed: ",floatBuffer
                player.reset(floatBuffer)
                behindZero = False
                floatBuffer = 0.0
                beZeroNum = 1
        elif inputChar == "s":
            print "Set Start Position at ",player.wav.tell()
            player.setStart()
        elif inputChar == "e":
            print "Set Start Position at ",player.wav.tell()
            player.setEnd()
        elif inputChar == "i":
            print "Start and End Position Reinitialized"
            player.reinitialize()
        elif inputChar == "z":
            print "Rewind to the start of the song"
            player.backToStartPos()
        elif inputChar == "r":
            player.rewind()
        elif inputChar == "f":
            player.fastForward()
        elif inputChar == "q":
            print "Quit"
            break;
    counter = counter+1
     
player.close()
print("done")