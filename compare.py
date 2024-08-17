import os, sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
import matplotlib.ticker
import xspec

if True:
    xspec.AllModels.lmod("relxill", "/opt/relxill/relxill")
    xspec.AllModels.lmod("rnthcomp", "~/github/rnthcomp/")
    xspec.AllModels.lmod("nthratio", "~/github/nthratio/")

def make_plot(plot, energies, modelValues1, modelValues2, renorm=5.0):

    modelValues1 = np.array(energies)*np.array(modelValues1)
    modelValues2 = np.array(energies)*np.array(modelValues2)

    if renorm > 0:
        arg = np.argmin(np.abs(np.array(energies)-renorm))
        modelValues1 /= modelValues1[arg]
        modelValues2 /= modelValues2[arg]

    #plot.plot(energies, modelValues1, lw=3, c='C0')
    #plot.plot(energies, modelValues2, lw=3, c='C1')
    plt.plot(energies, modelValues1/modelValues2, lw=3, c='black')

    plot.set_xlim(0.095,105.0)
    plot.set_ylim(max(min(min(modelValues1),min(modelValues2)), max(1.2e-3*max(modelValues1),1.2e-3*max(modelValues2))), max(1.2*max(modelValues1),1.2*1.2*max(modelValues2)))
    plot.set_ylim(0.5,1.5)
    #plot.set_ylim(0.1,10.)
    plot.set_xscale('log')
    plot.get_xaxis().set_major_formatter(matplotlib.ticker.FormatStrFormatter("%g"))
    #plot.set_yscale('log')
    plot.set_ylabel(r'keV(Photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$)')
    #plot.set_ylabel(r'Photons cm$^{-2}$ s$^{-1}$ keV$^{-1}$')
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


def update(a):
    params1 = read_sliders(sliders1, type_sliders1)
    params2 = read_sliders(sliders2, type_sliders2)

    model1 = xspec.Model(ModelName1)
    model1.setPars(*params1)
    modelValues1 = model1.values(0)

    model2 = xspec.Model(ModelName2)
    model2.setPars(*params2)
    modelValues2 = model2.values(0)

    xspec.Plot("model")
    energies = xspec.Plot.x()

    plt.sca(plt1)
    plt1.cla()
    plt_plot_1 = make_plot(plt1, energies, modelValues1, modelValues2)
    plt.draw()


if __name__ == "__main__":

    if len(sys.argv) > 2:
        ModelName1 = sys.argv[1]
        ModelName2 = sys.argv[2]
    else:
        ModelName1 = "bbodyrad"
        ModelName2 = "diskbb"

    # Make a larger grid for convolution models, and plot in a narrower range
    xspec.AllModels.setEnergies("0.01 1000. 500 log")

    plt1 = plt.axes([0.15, 0.45, 0.8, 0.5])
    type_sliders1, sliders1, plt_sliders1 = [], [], []
    type_sliders2, sliders2, plt_sliders2 = [], [], []
    params1, params2 = [], []

    xspec.Plot.device = "/null"
    xspec.Plot.xAxis = "keV"
    xspec.Plot.add = True

    model1 = xspec.Model(ModelName1)
    for i in range(model1.nParameters):
        params1.append(model1(i+1).values[0])

        plt_sliders1.append(plt.axes([0.15, 0.35-i*0.017, 0.20, 0.02]))

        if model1(i+1).name == 'norm':
            model1(i+1).values = [1, 0.01, 1e-3, 1e-3, 1e3, 1e3]
        if model1(i+1).name == 'nH':
            model1(i+1).values = [1, 0.01, 1e-4, 1e-4, 1e2, 1e2]
        if model1(i+1).name == 'Tin':
            model1(i+1).values = [1, 0.01, 1e-4, 1e-4, 1e2, 1e2]

        if model1(i+1).name == 'kTbb' or model1(i+1).name == 'kT_bb':
            model1(i+1).values = [0.5, 0.01, 0.01, 0.01, 3, 3]
        if model1(i+1).name == 'kTe' or model1(i+1).name == 'kT_e':
            model1(i+1).values = [60, 0.01, 10, 10, 3e2, 3e2]
        if model1(i+1).name == 'gamma' or model1(i+1).name == 'Gamma':
            model1(i+1).values = [2.31, 0.01, 1.5, 1.5, 3.5, 3.5]
        if model1(i+1).name == 'gamma':
            model1(i+1).values = [2.31, 0.01, 1.5, 1.5, 3.5, 3.5]

        if False:
            pass
            # model1(i+1).values[2] > 0 and model1(i+1).values[5] > 0:
            # type_sliders1.append('log')
            #
            # sliders1.append(Sliderlog(plt_sliders1[i],
            #                       model1(i+1).name,
            #                       np.log10(model1(i+1).values[3]),
            #                       np.log10(model1(i+1).values[4]),
            #                       valinit=np.log10(model1(i+1).values[0]),
            #                       valfmt='%7.5f {}'.format(model1(i+1).unit),
            #                       color='C0'))
        else:
            type_sliders1.append('lin')
            sliders1.append(Slider(plt_sliders1[i],
                                  model1(i+1).name,
                                  model1(i+1).values[3],
                                  model1(i+1).values[4],
                                  valinit=model1(i+1).values[0],
                                  valfmt='%7.5f {}'.format(model1(i+1).unit),
                                  color='C0'))
        sliders1[i].on_changed(update)

    model2 = xspec.Model(ModelName2)
    for i in range(model2.nParameters):
        params2.append(model2(i+1).values[0])

        plt_sliders2.append(plt.axes([0.65, 0.35-i*0.017, 0.20, 0.02]))

        FlagLog = False

        if model2(i+1).name == 'norm':
            model2(i+1).values = [1, 0.01, 1e-3, 1e-3, 1e3, 1e3]
        if model2(i+1).name == 'nH':
            model2(i+1).values = [1, 0.01, 1e-4, 1e-4, 2, 2]
        if model2(i+1).name == 'Tin':
            model2(i+1).values = [1, 0.01, 1e-4, 1e-4, 1e2, 1e2]
        if model2(i+1).name == 'Density':
            FlagLog = True
        if model2(i+1).name == 'Xi':
            FlagLog = True

        if FlagLog:
            # model2(i+1).values[2] > 0 and model2(i+1).values[5] > 0:
            type_sliders2.append('log')
            sliders2.append(Slider(plt_sliders2[i],
                               model2(i+1).name,
                               np.log10(model2(i+1).values[3]),
                               np.log10(model2(i+1).values[4]),
                               valinit=np.log10(model2(i+1).values[0]),
                               valfmt='%7.5f {}'.format(model2(i+1).unit),
                               color='C1'))
        else:
            type_sliders2.append('lin')
            sliders2.append(Slider(plt_sliders2[i],
                                  model2(i+1).name,
                                  model2(i+1).values[3],
                                  model2(i+1).values[4],
                                  valinit=model2(i+1).values[0],
                                  valfmt='%7.5f {}'.format(model2(i+1).unit),
                                  color='C1'))
        sliders2[i].on_changed(update)

    update(0)
    plt.suptitle('Models: {}  vs  {}'.format(ModelName1, ModelName2), y=0.99)
    plt.show()
