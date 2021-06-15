import os, sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
import matplotlib.ticker
import xspec


# https://stackoverflow.com/questions/39960791/logarithmic-slider-with-matplotlib
class Sliderlog(Slider):
    """Logarithmic slider.
        Takes in every method and function of the matplotlib's slider.
        Set slider to *val* visually so the slider still is lineat but display 10**val next to the slider.
        Return 10**val to the update function (func)"""

    def set_val(self, val):
        xy = self.poly.xy
        if self.orientation == 'vertical':
            xy[1] = 0, val
            xy[2] = 1, val
        else:
            xy[2] = val, 1
            xy[3] = val, 0
        self.poly.xy = xy
        self.valtext.set_text(self.valfmt % 10**val)   # Modified to display 10**val instead of val
        if self.drawon:
            self.ax.figure.canvas.draw_idle()
        self.val = val
        if not self.eventson:
            return
        for cid, func in self.observers.items():
                func(10**val)


def make_plot(plot, energies, modelValues, compValues, kind='mo'):

    if len(compValues) > 1:
        for i in range(len(compValues)):
            plot.plot(energies, compValues[i], lw=1, ls='--')

    plot.plot(energies, modelValues, lw=3)

    if 'eem' in kind:
        plot.set_ylabel(r'keV$^2$ (Photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$)')
    elif 'em' in kind:
        plot.set_ylabel(r'keV (Photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$)')
    else:
        plot.set_ylabel(r'Photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$')
    #plot.set_yticks([0.001,0.01,0.1,10.0,100.0])
    #plot.set_yticklabels(['0.001','0.01','0.1','10.0','100.0'])
    plot.set_xlim(0.95*energies[0],1.05*energies[-1])
    plot.set_ylim(max(min(modelValues), 1.2e-3*max(modelValues)), 1.2*max(modelValues))
    plot.set_xscale('log')
    plot.get_xaxis().set_major_formatter(matplotlib.ticker.FormatStrFormatter("%g"))
    plot.set_yscale('log')
    plot.set_xlabel('Energy (keV)')
    plot.grid()
    return plot


def read_sliders(list_sliders, type_sliders):
    params = []
    for i, (slider, type_slider) in enumerate(zip(list_sliders, type_sliders)):
        if 'log' in type_slider:
            params.append(10**slider.val)
        else:
            params.append(slider.val)
    return params


def evaluate_model(params, model, kind):
    model.setPars(*params)
    xspec.Plot(kind)
    xVals = xspec.Plot.x()
    modVals = xspec.Plot.model()
    compVals = []
    if len(model.componentNames) > 1:
        j = 1
        for i, componentName in enumerate(model.componentNames):
            if 'norm' in getattr(model, componentName).parameterNames:
                compVals.append(xspec.Plot.addComp(j))
                j+=1
    return xVals, modVals, compVals


def update(a):
    params = read_sliders(sliders, type_sliders)
    energies, modelValues, compValues = evaluate_model(params, model, kind)

    plt.sca(plt1)
    plt1.cla()
    plt_plot_1 = make_plot(plt1, energies, modelValues, compValues, kind)
    plt.draw()


if __name__ == "__main__":

    if len(sys.argv) > 2:
        ModelName = sys.argv[1]
        kind = sys.argv[2]
    elif len(sys.argv) > 1:
        ModelName = sys.argv[1]
        kind = "mo"
    else:
        ModelName = "bbodyrad+nthcomp"
        kind = "mo"

    xspec.AllModels.setEnergies(".2 100. 5000 log")

    plt1 = plt.axes([0.15, 0.40, 0.8, 0.5])
    type_sliders, sliders, plt_sliders = [], [], []
    params = []

    xspec.Plot.device = "/null"
    xspec.Plot.xAxis = "keV"
    xspec.Plot.add = True

    model = xspec.Model(ModelName)
    for i in range(model.nParameters):
        params.append(model(i+1).values[0])

        plt_sliders.append(plt.axes([0.15, 0.25-i*0.03, 0.6, 0.02]))

        if model(i+1).name == 'norm':
            model(i+1).values = [1, 0.01, 1e-3, 1e-3, 1e3, 1e3]
        if model(i+1).name == 'nH':
            model(i+1).values = [1, 0.01, 1e-4, 1e-4, 1e2, 1e2]

        if model(i+1).values[2] > 0 and model(i+1).values[5] > 0:
            type_sliders.append('log')

            sliders.append(Sliderlog(plt_sliders[i],
                                  model(i+1).name,
                                  np.log10(model(i+1).values[3]),
                                  np.log10(model(i+1).values[4]),
                                  valinit=np.log10(model(i+1).values[0]),
                                  valfmt='%7.5f {}'.format(model(i+1).unit)))
        else:
            type_sliders.append('lin')
            sliders.append(Slider(plt_sliders[i],
                                  model(i+1).name,
                                  model(i+1).values[3],
                                  model(i+1).values[4],
                                  valinit=model(i+1).values[0],
                                  valfmt='%7.5f {}'.format(model(i+1).unit)))
        sliders[i].on_changed(update)

    update(0)
    plt.suptitle('Model: {}'.format(ModelName), y=0.99)
    plt.show()
