from xspec import *
import matplotlib.pyplot as plt

### Add un try para leer el XCM y si no puede, agregarle la
### línea con #PyXspec: Output generated from Xset.save().  DO NOT MODIFY. y volver a probar y si vuelve a fallar, pedir espectro y modelo.

# Let's chat with the user

try:
    Xset.restore(input("Input XCM file: "))
    m1 = AllModels(1)
except:
    print("Could not load XCM file. Let's try spectrum+model.\n")
    try:
        s1 = Spectrum(input("Input spectrum file: "))
        m1 = Model(input("Input model expression: "))

        m1.setPars(0.29, 2.11, 3.07, "0.193, 0.01", 0, 0, 1.097)         
    except:
        print("Could not load spectrum-model. Exiting...\n")
        exit(1)

try:
    print("Spectrum and Model loaded succesfully.\n")
   
    chain = input("Input chain file: ")
    AllChains += chain
except:
    print("Could not load the chain file. Exiting...\n")
    exit(1)


# Magical code starts here...

FitManager.perform(100)

Xset.chatter = 0
Plot.device = '/null'
Plot.xAxis = "keV"

N=1000

for i in range(N):
    m1.setPars(ModelManager.simpars(m1))
    Plot('data')

    chans = Plot.x()
    chanserr = Plot.xErr()
    rates = Plot.y()
    rateserr = Plot.yErr()
    folded = Plot.model()

    plt.plot(chans,folded,c='gray',alpha=10./N)
    
plt.errorbar(chans, rates, rateserr, chanserr, fmt='none', c='r')
plt.plot(chans, rates, 'ro', chans, folded)

plt.xscale('log')
plt.yscale('log')
plt.xlabel('Energy')
plt.ylabel('counts/cm^2/s/keV')

Xset.chatter = 10

plt.show()

