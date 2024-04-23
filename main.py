import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.clock import Clock
from rtlsdr import RtlSdr
import matplotlib.mlab as mlab
from matplotlib.mlab import psd

class MainApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        sdr = RtlSdr()

        # configure device
        sdr.sample_rate = 2.8e6
        sdr.center_freq = 100e6
        sdr.gain = 'auto'
        sdr.bandwidth = 100e6
        sdr.freq_correction= 200

        # parametros para la animación
        NUM_SAMPLES_PER_SCAN = 15*4096
        NUM_SCANS_PER_UPDATE = 10

        # Configurar la figura y el eje para la animación
        graph = Graph(xlabel='Frequency (MHz)', ylabel='Relative Power (dB)',
                      x_ticks_minor=25, x_ticks_major= (512e6 - 470e6) / 2, y_ticks_major=1,
                      y_grid_label=True, x_grid_label=True, padding=5,
                      x_grid=True, y_grid=True, xmin=0,xmax=(sdr.sample_rate/1e6)/2 , ymin=-65, ymax=10) #xmax = 512
                      #x_grid=True, y_grid=True, xmin=sdr.center_freq-(sdr.bandwidth/2)/1e6, xmax=sdr.center_freq+(sdr.bandwidth/2)/1e6, ymin=-70, ymax=10) #x_ticks_major= (sdr.sample_rate/1e6)/2
                      # Añadir etiquetas de frecuencia al eje x
        
        # Create a list to store frequency labels
        #frequency_labels = [str(freq) for freq in range(0, int(sdr.sample_rate//1e6)//2, 25)]
        plot = MeshLinePlot(color=[1, 0, 0, 2])
        plot.points = [(x / 10., 0) for x in range(0, NUM_SAMPLES_PER_SCAN)]
        graph.add_plot(plot)

        # Create a start button
        start_button = Button(text='Escanear', size_hint=(0.2, 0.1))
        stop_button = Button(text='Detener', size_hint=(0.2, 0.1))  # Create a stop button
        freq_input = TextInput(text=str(sdr.center_freq/1e6), size_hint=(0.2, 0.1))  # Create a text input for the center frequency

        def update(dt):
            #leer muestra del SDR
            samples = sdr.read_samples(NUM_SAMPLES_PER_SCAN)

            #densidad espectral de potencia
            psd_scan, f = psd(samples, pad_to= 1024, NFFT=4096, Fs= sdr.sample_rate/1e6,window=mlab.window_hanning, noverlap=512, scale_by_freq=True )

            # Actualizar la linea con los nuevos datos
            plot.points = [(f[i], 10*np.log10(psd_scan[i])) for i in range(min(NUM_SAMPLES_PER_SCAN, len(psd_scan)))]


        def start_button_clicked(instance):          
            # Set the center frequency from the text input
            sdr.center_freq=float(freq_input.text)*1e6
            #Configurar la animación
            Clock.schedule_interval(update, 1.0 / NUM_SCANS_PER_UPDATE)


        def stop_button_clicked(instance):
            # Stop the animation
            Clock.unschedule(update)

        start_button.bind(on_press=start_button_clicked)
        stop_button.bind(on_press=stop_button_clicked)  # Bind the stop button click event

        # add to the layout
        #control_layout = BoxLayout(orientation='horizontal')
        layout.add_widget(start_button)
        layout.add_widget(stop_button)  # Add the stop button to the layout
        layout.add_widget(freq_input)  # Add the frequency input to the layout
        #layout.add_widget(control_layout)
        layout.add_widget(graph)

        return layout

if __name__ == '__main__':
    MainApp().run()

