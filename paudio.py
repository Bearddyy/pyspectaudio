import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.core.window import Window
import random
import pyaudio
import threading
import time
import numpy as np

class Spectrogram(BoxLayout):
    def __init__(self, **kwargs):
        super(Spectrogram, self).__init__(**kwargs)
        self.terminateAudioThread = False
        self.dfft = np.zeros(127)
        self.updateSize()

        col = (49,107,131, 256)
        col = [i/255 for i in col]
        #Color(rgba=col)
        Window.clearcolor = col
        
        event = Clock.schedule_interval(self.drawSpect, 1 / 30.)

        threading.Thread(target=self.audioThread).start()

    def audioThread(self):
        """
        thread that constantly monitors the audio input and updates the spectrogram
        """
        FORMAT = pyaudio.paInt16 # We use 16bit format per sample
        CHANNELS = 1
        RATE = int(44100)
        CHUNK = 4086 #2048 # 1024bytes of data red from a buffer

        OFFSET = 3
        LEN = 4 #500 # 4
        
        p = pyaudio.PyAudio()
        np.seterr(divide = 'ignore')
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        while not self.terminateAudioThread:
            data = stream.read(CHUNK)
            audio_data = np.fromstring(data, np.int16)
            # Fast Fourier Transform, 10*log10(abs) is to scale it to dB
            # and make sure it's not imaginary
            try:
                dfft = abs(np.fft.rfft(audio_data))#10*np.log10(abs(np.fft.rfft(audio_data)))
                dfft = np.ceil(dfft, LEN)
                print(len(self.dfft))
                dfft = dfft.reshape(-1, LEN).mean(axis=1)
                #dfft = dfft[OFFSET:OFFSET+LEN]
                try:
                    self.dfft = [((self.dfft[i]*0.8) + (dfft[i] * 0.2) )for i in range(len(dfft))]
                except:
                    self.dfft = dfft
            except:
                pass
            

    def updateSize(self):
        size = Window.size
        self.windowWidth = size[0]
        self.windowHeight = size[1]
        self.centerline = self.windowHeight / 2
        self.pad = 1
        self.rows = 200
        self.specWidth = (self.windowWidth/127) 
    
    def drawSpect(self, dt=None):
        self.updateSize()
        layout = BoxLayout(orientation='vertical')  
        with self.canvas:
            self.canvas.clear()
            for i in range(len(self.dfft)):
                height = self.dfft[i] #random.randint(10, self.rows) 
                self.specWidth = (self.windowWidth/len(self.dfft))
                try:
                    scaledHeight = (height / 10 )
                    halfHeight = int(scaledHeight / 2)
                    RoundedRectangle(size=(self.specWidth - self.pad, scaledHeight), pos=(i*self.specWidth, int(self.centerline- (halfHeight)) ) )
                except:
                    pass



class Paudio(App):
    def build(self):
        self.spectrogram = Spectrogram()
        return  self.spectrogram 

    


if __name__ == '__main__':
    paudio = Paudio()
    paudio.run()
    paudio.spectrogram.terminateAudioThread = True


