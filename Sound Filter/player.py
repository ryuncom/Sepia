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
        self.data = self.wav.readframes(1)
        self.start = 0
        self.end = self.wav.getnframes()

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
        tempFFT = fft.fft(energy,norm=None)
        energyFFT = list()
        for i in range(0,1023):
            energyFFT.append(tempFFT[i].real**2+tempFFT[i].imag**2)
        return energyFFT
    
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
        self.stream = self.py.open(format = self.py.get_format_from_width(self.wav.getsampwidth()),  
                    channels = self.wav.getnchannels(),  
                    rate = int(self.wav.getframerate()*speed),  
                    output = True)
        
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