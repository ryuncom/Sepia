import wave
import pyaudio
import struct
import numpy.fft as fft

class Player:
    
    def __init__(self, stringInput,speed,chunk):
        self.wav = wave.open(stringInput, mode='rb')
        self.py = pyaudio.PyAudio()
        self.stream = self.py.open(format = self.py.get_format_from_width(self.wav.getsampwidth()),  
                channels = self.wav.getnchannels(),  
                rate = (int)(self.wav.getframerate()*speed),  
                output = True)
        self.chunk = chunk
        self.curSpeed = speed
        self.data = self.wav.readframes(1)
        self.start = 0
        self.counter = 0
        self.end = self.wav.getnframes()
        self.bandWidth = list()
        self.threshold = 1.3
        self.varThreshold = 150
        
        bandNum = 64
        firstWidth = 2
        
        self.energies = [[0.0 for x in range(self.wav.getframerate()/self.chunk)] for y in range(bandNum)]
        self.average = [0 for x in range(len(self.energies))]
        self.variance = [0 for x in range(len(self.energies))]
        self.peaks = [list() for x in range(bandNum)]
        
        a = 2.0*((float(self.chunk)-float(bandNum*firstWidth))/float(bandNum*(bandNum-1)))
        b = float(firstWidth) - a
        summation = 0;
        for i in range(1,bandNum):
            temp = int(round(a*(i)+b))
            self.bandWidth.append(temp)
            summation = summation+temp
        self.bandWidth.append(self.chunk-summation)

    def play(self):           
        data = self.wav.readframes(self.chunk)
        num = len(data)
        energy = list()
        temp=''
        for i in range(0,num):
            temp = temp+data[i]
            if(i%4==1):   
                getL = struct.unpack("<H",temp[::-1])
                temp=''
            elif(i%4==3):
                getR = struct.unpack("<H",temp[::-1])
                energy.append(getL[0]+getR[0]*1j)
                temp=''
        self.stream.write(data)
    
    def getRawEnergy(self, data):
        num = len(data)
        checkPoint = 0
        energy = list()
        temp=''
        for i in range(0,num):
            temp = temp+data[i]
            if(i%4==1):   
                getL = struct.unpack("<H",temp[::-1])
                temp=''
            elif(i%4==3):
                getR = struct.unpack("<H",temp[::-1])
                energy.append(getL[0]+getR[0]*1j)
                checkPoint = checkPoint+1
                temp=''
        tempFFT = fft.fft(energy,norm=None)
        energyFFT = list()
        for i in range(0,checkPoint):
            energyFFT.append(tempFFT[i].real**2+tempFFT[i].imag**2)
        return energyFFT
        
    def peakDetect(self, energyFFT):
        Es = [0 for x in range(len(self.energies))]
        index = 0
        for i in range(0,len(self.energies)):
            for j in range(index,index+self.bandWidth[i]):
                Es[i] = Es[i] + energyFFT[j]
            Es[i] = self.bandWidth[i]*Es[i]/self.chunk
            index = index+self.bandWidth[i]
        
        divisor = 0
        if self.counter<len(self.energies[0]):
            divisor = self.counter+1
        else:
            divisor = len(self.energies[0])
        
        for i in range(0,len(self.energies)):
            if index<len(self.energies[0]):
                self.average[i] = ((self.counter*self.average[i])+Es[i])/divisor
            else:
                self.average[i] = ((divisor*self.average[i])-self.energies[i][self.counter%len(self.energies[0])]+Es[i])/divisor    
            
        self.varReset()    
        
        for i in range(0,len(self.energies)):
            for j in range(0,divisor):
                self.variance[i] = self.variance[i] + ((self.energies[i][j]-self.average[i])**2)
            self.variance[i] = self.variance[i]/divisor
        
        for i in range(0,len(self.energies)):
            if Es[i] > self.threshold*self.average[i]:
                print "aaaa"
                if self.variance[i] > self.varThreshold:
                    print "bbbb"
                    self.peaks[i].append(self.wav.tell())
        
        for i in range(0,len(self.energies)):
            self.energies[i][(self.counter%len(self.energies[0]))] = Es[i]
        
        self.counter = self.counter+1
    
    def beatCal(self):
        while self.wav.tell() < self.wav.getnframes():
            data = self.wav.readframes(self.chunk)
            if self.wav.tell()%1000000 <2000:
                print self.wav.tell()
            if len(data) == 4*self.chunk:
                energyFFT = self.getRawEnergy(data)
                self.peakDetect(energyFFT)
        
        intervals = list()
        
        for i in range(0,len(self.peaks)):
            for j in range(0,len(self.peaks[i])):
                if j==0:
                    print "null"
                    #intervals.append(self.peaks[i][j])
                else:
                    jaamkaan = self.peaks[i][j]-self.peaks[i][j-1]
                    if jaamkaan >10000 and jaamkaan<30000:
                        intervals.append(jaamkaan)
        
        print intervals
        self.reset(self.curSpeed)
        self.wav.setpos(0)            
        
    def varReset(self):
        for i in range(len(self.variance)):
            self.variance[i] = 0.0    
        
        
    def lofiPlay(self):    
        data = self.wav.readframes(self.chunk)
        num = len(data)
        temp=''
        processedData=''
        counter=0
        for i in range(0,num):
            temp = temp+data[i]
            if(i%4==1):   
                getL = struct.unpack("<H",temp[::-1])
                temp=''
            elif(i%4==3): 
                getR = struct.unpack("<H",temp[::-1])
                temp=''
                if counter==0:
                    processedData = processedData+struct.pack(">H",getL[0])+struct.pack(">H",getR[0])
                elif counter%4==0:
                    processedData = processedData+struct.pack(">H",getL[0])+struct.pack(">H",getR[0])+struct.pack(">H",getL[0])+struct.pack(">H",getR[0])+struct.pack(">H",getL[0])+struct.pack(">H",getR[0])+struct.pack(">H",getL[0])+struct.pack(">H",getR[0])
                counter = counter+1
        self.stream.write(processedData)       
    
    def noisePlay(self):    
        data = self.wav.readframes(self.chunk)
        num = len(data)
        temp=''
        processedData=''
        bufferL = 0
        bufferR = 0
        referL = 0
        referR = 0
        size = 5
        counter=0
        for i in range(0,num):
            temp = temp+data[i]
            if(i%4==1):   
                getL = struct.unpack("<H",temp[::-1])
                temp=''
            elif(i%4==3):
                getR = struct.unpack("<H",temp[::-1])
                temp=''
                if counter==0:
                    processedData = processedData+struct.pack(">H",getL[0])+struct.pack(">H",getR[0])
                    referL = getL[0]
                    referR = getR[0]
                elif counter%2==1:
                    bufferL = getL[0]
                    bufferR = getR[0]
                elif counter%2==0:
                    if (referL+getL[0])/2 > bufferL and (referL !=0 or getL[0]!=0):
                        bufferL = bufferL + size
                        if bufferL > 65535:
                            bufferL = 65535
                    elif bufferL>size and (referL !=0 or getL[0]!=0):
                        bufferL = bufferL - size                    
                    if (referR+getR[0])/2 > bufferR and (referR !=0 or getR[0]!=0):
                        bufferR = bufferR + size
                        if bufferR > 65535:
                            bufferR = 65535
                    elif bufferR>size and (referR !=0 or getR[0]!=0):
                        bufferR = bufferR - size
                    processedData = processedData+struct.pack(">H",bufferL)+struct.pack(">H",bufferR)+struct.pack(">H",getL[0])+struct.pack(">H",getR[0])
                    referL = getL[0]
                    referR = getR[0]
                counter = counter+1
        self.stream.write(processedData)  
    
    def reset(self,speed):
        self.stream.close()
        self.stream = self.py.open(format = self.py.get_format_from_width(self.wav.getsampwidth()),  
                    channels = self.wav.getnchannels(),  
                    rate = int(self.wav.getframerate()*speed),  
                    output = True)
        self.curSpeed = speed
        
    def backToStartPos(self):
        self.wav.setpos(self.start)
        
    def rewind(self):
        temp = 0
        if (self.wav.tell()-220500) < 0:
            temp = 0;
        else:
            temp = self.wav.tell() - 220500
        self.wav.setpos(temp)

    def fastForward(self):
        temp = 0
        if(self.wav.tell()+220500)>self.wav.getnframes():
            temp = self.wav.getnframes()
        else:
            temp = self.wav.getnframes() + 220500
        self.wav.setpos(temp)
    
    def loop(self):
        if self.wav.tell() >= self.end:
            self.rewind()
    
    def reinitialize(self):
        self.start = 0
        self.end = self.wav.getnframes()
        
    def setStart(self):
        self.start = self.wav.tell()
        
    def setEnd(self):
        self.end = self.wav.tell()
    
    def returnData(self):
        return self.data
    
    def close(self):
        self.stream.stop_stream()  
        self.stream.close() 
        self.py.terminate()