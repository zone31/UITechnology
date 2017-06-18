import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import operator
import itertools

top=[
[570, 954, 508, 263],
[590, 946, 587, 522],
[606, 944, 640, 515],
[610, 924, 565, 501],
[639, 934, 671, 588],
[631, 928, 504, 581],
[605, 928, 455, 466],
[627, 946, 346, 602],
[654, 954, 594, 368],
[671, 954, 484, 574],
[608, 927, 445, 489],
[588, 931, 462, 501],
[603, 955, 361, 591],
[592, 958, 414, 594],
[630, 905, 452, 580],
[608, 895, 422, 621],
[648, 887, 562, 429],
[630, 934, 511, 474],
[631, 847, 542, 503],
[641, 688, 501, 505],
[618, 880, 490, 534],
[655, 675, 550, 593],
[611, 862, 518, 630],
[606, 830, 476, 536],
[635, 876, 555, 567]]

left=[
[733, 483, 647, 931],
[703, 435, 653, 927],
[668, 475, 441, 937],
[702, 462, 651, 913],
[728, 534, 578, 920],
[730, 507, 635, 938],
[609, 443, 490, 918],
[671, 641, 567, 876],
[703, 533, 570, 930],
[633, 593, 564, 913],
[617, 647, 614, 888],
[614, 670, 541, 890],
[675, 448, 429, 897],
[587, 489, 626, 813],
[587, 438, 445, 891],
[658, 484, 571, 869],
[651, 573, 506, 916],
[641, 575, 653, 915],
[616, 559, 545, 920],
[656, 547, 512, 911],
[605, 428, 373, 894],
[613, 783, 522, 920],
[551, 546, 426, 899],
[592, 623, 453, 877],
[674, 334, 442, 862]]

right = [
[597, 468, 941, 335],
[528, 489, 843, 587],
[563, 494, 920, 465],
[635, 481, 942, 398],
[584, 437, 929, 413],
[571, 664, 915, 562],
[584, 492, 842, 436],
[693, 547, 840, 332],
[639, 520, 795, 543],
[528, 488, 687, 489],
[570, 486, 767, 525],
[474, 506, 820, 520],
[556, 597, 915, 414],
[555, 644, 901, 418],
[564, 567, 869, 367],
[553, 667, 899, 508],
[447, 511, 892, 603],
[636, 664, 900, 560],
[629, 437, 910, 579],
[588, 486, 914, 245],
[524, 553, 928, 494],
[724, 505, 843, 289],
[631, 514, 891, 220],
[720, 463, 835, 319],
[635, 461, 927, 448]]


back = [
[899, 508, 413, 623],
[853, 494, 513, 569],
[889, 453, 615, 540],
[906, 443, 492, 430],
[897, 434, 469, 538],
[897, 427, 501, 538],
[837, 484, 531, 496],
[734, 467, 724, 586],
[838, 536, 690, 394],
[892, 431, 547, 577],
[956, 597, 375, 709],
[861, 473, 331, 647],
[902, 421, 577, 356],
[894, 421, 411, 449],
[876, 567, 347, 502],
[884, 557, 420, 494],
[887, 463, 413, 464],
[902, 453, 571, 519],
[854, 566, 486, 514],
[878, 439, 813, 496],
[907, 457, 554, 467],
[914, 510, 667, 569],
[913, 543, 450, 574],
[862, 498, 594, 371],
[837, 545, 585, 724]]

sensors = ["Bottom","Top","Right","Left"]
poses = ["On back","On belly","On right","On left"]
colors = ['r','g','b','y']
data = [back,top,right,left]
f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex='col', sharey='row')
subplots = [ax1,ax2,ax3,ax4]
handlearr = []
pdfs = []
for plotID,subplot in enumerate(subplots):
    pdfar = []
    for sensID,name in enumerate(sensors):
        h = [i[sensID] for i in data[plotID]]
        h.sort()
        hmean = np.mean(h)
        hstd = np.std(h)
        pdf = stats.norm.pdf(h, hmean, hstd)
        pdfar.append(pdf)
        subplt, = subplots[plotID].plot(h, pdf,label=sensors[sensID],color=colors[sensID])
        handlearr.append(subplt)
        subplots[plotID].title.set_text(poses[plotID])
        print("--")
        print(sum(pdf))
    pdfs.append(pdfar)
    scope = [val for sens in data[plotID] for i,val in enumerate(sens) if i == plotID]
    other = [val for sens in data[plotID] for i,val in enumerate(sens) if i != plotID]
    side1 = max(other)
    side2 = min(scope)
    # print(scope)
    # print(sum(pdfar[0]))
    if(side1<side2):
        subplots[plotID].axvspan(side1, side2, facecolor='green', alpha=0.3)
    else:
        subplots[plotID].axvspan(side1, side2, facecolor='red', alpha=0.3)


for axtemp in [ax1,ax3]:
    vals = axtemp.get_yticks()
    axtemp.set_yticklabels(['{:3.2f}%'.format(x*100) for x in vals])
f.legend(handles = handlearr,labels = sensors, ncol=4,loc="lower center")
f.savefig('test.', dpi = 300,bbox_inches='tight')
plt.show()



