import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
import random
import pyaudio
import threading
import time
import numpy as np

class Spectrogram(BoxLayout):
    def __init__(self, **kwargs):
        super(Spectrogram, self).__init__(**kwargs)
        self.windowWidth = 750
        self.windowHeight = 500
        self.centerline = self.windowHeight / 2
        self.pad = 2
        self.cols = 129
        self.rows = 200
        self.specWidth = (self.windowWidth/self.cols) 
        self.terminateAudioThread = False
        self.dfft = np.zeros(self.cols)
        
        event = Clock.schedule_interval(self.drawSpect, 1 / 30.)

        threading.Thread(target=self.audioThread).start()

    def audioThread(self):
        """
        thread that constantly monitors the audio input and updates the spectrogram
        """
        FORMAT = pyaudio.paInt16 # We use 16bit format per sample
        CHANNELS = 1
        RATE = 44100
        CHUNK = 256 # 1024bytes of data red from a buffer
        RECORD_SECONDS = 2
        p = pyaudio.PyAudio()
        np.seterr(divide = 'ignore')
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        while not self.terminateAudioThread:
            data = stream.read(CHUNK)
            audio_data = np.fromstring(data, np.int16)
            # Fast Fourier Transform, 10*log10(abs) is to scale it to dB
            # and make sure it's not imaginary
            try:
                self.dfft = 10*np.log10(abs(np.fft.rfft(audio_data)))
            except:
                pass
            time.sleep(1/30)
            print(len(self.dfft))


    
    def drawSpect(self, dt=None):
        layout = BoxLayout(orientation='vertical')  
        with self.canvas:
            self.canvas.clear()
            for i in range(len(self.dfft)):
                height = self.dfft[i] #random.randint(10, self.rows) 
                try:
                    halfHeight = int(height / 2)
                    rect = RoundedRectangle(size=(self.specWidth - self.pad, height), pos=(i*self.specWidth, int(self.centerline- (halfHeight)) ))
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


