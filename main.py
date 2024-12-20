import os, sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
import matplotlib.ticker
import xspec


def make_plot(plot, energies, modelValues, compValues, kind='mo'):

    if len(compValues) > 1:
        for i in range(len(compValues)):
            plot.plot(energies, compValues[i], lw=1, ls='--', c='C{}'.format(i+1))

    plot.plot(energies, modelValues, lw=2, c='k')

    if 'eem' in kind:
        plot.set_ylabel(r'keV$^2$ (Photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$)')
    elif 'em' in kind:
        plot.set_ylabel(r'keV (Photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$)')
    else:
        plot.set_ylabel(r'Photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$')
    #plot.set_yticks([0.001,0.01,0.1,10.0,100.0])
    #plot.set_yticklabels(['0.001','0.01','0.1','10.0','100.0'])
    plot.set_xlim(0.095,105.0)
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
            slider.valtext.set_text(slider.valfmt % 10**slider.val)
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
        j = 0
        for i, componentName in enumerate(model.componentNames):
            if 'norm' in getattr(model, componentName).parameterNames:
                j+=1
        if j > 1:
            for i in range(j):
                compVals.append(xspec.Plot.addComp(i+1))
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

    # Make a larger grid for convolution models, and plot in a narrower range
    xspec.AllModels.setEnergies("0.05 500. 5000 log")

    plt1 = plt.axes([0.15, 0.45, 0.8, 0.5])
    type_sliders, sliders, plt_sliders = [], [], []
    params = []

    xspec.Plot.device = "/null"
    xspec.Plot.xAxis = "keV"
    xspec.Plot.add = True

    model = xspec.Model(ModelName)
    i = Nadditive = 0
    for cNumber, componentName in enumerate(model.componentNames):
        if 'norm' == getattr(model, componentName).parameterNames[-1]:
            Nadditive += 1
            Tadditive = True
        else:
            Tadditive = False

        for j, parameterName in enumerate(getattr(model, componentName).parameterNames):
            i += 1

            params.append(model(i).values[0])

            plt_sliders.append(plt.axes([0.15, 0.36-i*0.03, 0.6, 0.02]))

            if model(i).name == 'norm':
                model(i).values = [1, 0.01, 1e-3, 1e-3, 1e3, 1e3]
            if model(i).name == 'nH':
                model(i).values = [1, 0.01, 1e-4, 1e-4, 1e2, 1e2]
            if model(i).name == 'Tin':
                model(i).values = [1, 0.01, 1e-4, 1e-4, 1e2, 1e2]

            if model(i).values[2] > 0 and model(i).values[5] > 0:
                type_sliders.append('log')

                sliders.append(Slider(plt_sliders[-1],
                                   model(i).name,
                                   np.log10(model(i).values[3]),
                                   np.log10(model(i).values[4]),
                                   valinit=np.log10(model(i).values[0]),
                                   valfmt='%7.5f {}'.format(model(i).unit),
                                   color='C{}'.format(Nadditive) if Tadditive else 'gray'))
            else:
                type_sliders.append('lin')
                sliders.append(Slider(plt_sliders[-1],
                                      model(i).name,
                                      model(i).values[3],
                                      model(i).values[4],
                                      valinit=model(i).values[0],
                                      valfmt='%7.5f {}'.format(model(i+1).unit),
                                      color='C{}'.format(Nadditive) if Tadditive else 'gray'))
            sliders[-1].on_changed(update)

    update(0)
    plt.suptitle('Model: {}'.format(ModelName), y=0.99)
    plt.show()
