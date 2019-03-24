
# coding: utf-8

# # `travelmaps2`: An updated version of `travelmaps`
# 
# I did not want to change `travelmaps`, as it is a blog entry.
# 
# These functions are very basic, and include almost no checking or similar at all. Feel free to fork and improve them!

# In[1]:

import shapefile
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib import rcParams, patheffects
from matplotlib.collections import LineCollection
get_ipython().magic('matplotlib inline')

# Disable DecompressionBombWarning
from PIL import Image
Image.MAX_IMAGE_PIXELS = None


# In[2]:

def setup(dpi=300, sketch=(1, 100, 2), theme='light'):
    """Setup travelmaps."""
    # Customized plt.xkcd()-settings
    # http://jakevdp.github.io/blog/2013/07/10/XKCD-plots-in-matplotlib
    rcParams['font.family'] = ['Humor Sans', 'Comic Sans MS']
    rcParams['font.size'] = 8.0
    rcParams['path.sketch'] = sketch
    rcParams['axes.linewidth'] = 1.0
    rcParams['lines.linewidth'] = 1.0
    rcParams['grid.linewidth'] = 0.0
    rcParams['axes.unicode_minus'] = False
    if theme=='dark':
        rcParams['path.effects'] = [patheffects.withStroke(linewidth=2, foreground="k")]
        rcParams['figure.facecolor'] = 'black'
        rcParams['figure.edgecolor'] = 'black'
        rcParams['lines.color'] = 'white'
        rcParams['patch.edgecolor'] = 'white'
        rcParams['text.color'] = 'white'
        rcParams['axes.facecolor'] = 'black'
        rcParams['axes.edgecolor'] = 'white'
        rcParams['axes.labelcolor'] = 'white'
        rcParams['xtick.color'] = 'white'
        rcParams['ytick.color'] = 'white'
        rcParams['grid.color'] = 'white'
        rcParams['savefig.facecolor'] = 'black'
        rcParams['savefig.edgecolor'] = 'black'
        
    else:
        rcParams['path.effects'] = [patheffects.withStroke(linewidth=2, foreground="w")]
        rcParams['figure.facecolor'] = 'white'
        rcParams['figure.edgecolor'] = 'white'
        rcParams['lines.color'] = 'black'
        rcParams['patch.edgecolor'] = 'black'
        rcParams['text.color'] = 'black'
        rcParams['axes.facecolor'] = 'white'
        rcParams['axes.edgecolor'] = 'black'
        rcParams['axes.labelcolor'] = 'black'
        rcParams['xtick.color'] = 'black'
        rcParams['ytick.color'] = 'black'
        rcParams['grid.color'] = 'black'
        rcParams['savefig.facecolor'] = 'white'
        rcParams['savefig.edgecolor'] = 'white'

    # *Bayesian Methods for Hackers*-colour-cylce
    # (https://github.com/pkgpl/PythonProcessing/blob/master/results/matplotlibrc.bmh.txt)
    rcParams['axes.prop_cycle'] = plt.cycler('color', ['#348ABD', '#A60628', '#7A68A6', '#467821', '#D55E00',
                                     '#CC79A7', '#56B4E9', '#009E73', '#F0E442', '#0072B2'])

    # Adjust dpi, so figure on screen and savefig looks the same
    rcParams['figure.dpi'] = dpi
    rcParams['savefig.dpi'] = dpi


# In[ ]:

def setup_noxkcd(dpi=300, theme='light'):
    """Setup Maps."""
    if theme=='dark':
        rcParams['figure.facecolor'] = 'black'
        rcParams['figure.edgecolor'] = 'black'
        rcParams['lines.color'] = 'white'
        rcParams['patch.edgecolor'] = 'white'
        rcParams['text.color'] = 'white'
        rcParams['axes.facecolor'] = 'black'
        rcParams['axes.edgecolor'] = 'white'
        rcParams['axes.labelcolor'] = 'white'
        rcParams['xtick.color'] = 'white'
        rcParams['ytick.color'] = 'white'
        rcParams['grid.color'] = 'white'
        rcParams['savefig.facecolor'] = 'black'
        rcParams['savefig.edgecolor'] = 'black'
        
    else:
        rcParams['figure.facecolor'] = 'white'
        rcParams['figure.edgecolor'] = 'white'
        rcParams['lines.color'] = 'black'
        rcParams['patch.edgecolor'] = 'black'
        rcParams['text.color'] = 'black'
        rcParams['axes.facecolor'] = 'white'
        rcParams['axes.edgecolor'] = 'black'
        rcParams['axes.labelcolor'] = 'black'
        rcParams['xtick.color'] = 'black'
        rcParams['ytick.color'] = 'black'
        rcParams['grid.color'] = 'black'
        rcParams['savefig.facecolor'] = 'white'
        rcParams['savefig.edgecolor'] = 'white'

    # *Bayesian Methods for Hackers*-colour-cylce
    # (https://github.com/pkgpl/PythonProcessing/blob/master/results/matplotlibrc.bmh.txt)
    rcParams['axes.prop_cycle'] = plt.cycler('color', ['#348ABD', '#A60628', '#7A68A6', '#467821', '#D55E00',
                                     '#CC79A7', '#56B4E9', '#009E73', '#F0E442', '#0072B2'])

    # Adjust dpi, so figure on screen and savefig looks the same
    rcParams['figure.dpi'] = dpi
    rcParams['savefig.dpi'] = dpi


# In[3]:

def cm2in(length, decimals=2):
    """Convert cm to inch.

    Parameters
    ----------
    length : scalar or vector
        Numbers to be converted.
    decimals : int, optional; <2>
        As in np.round, used to round the result.

    Returns
    -------
    cm2in : scalar or vector
        Converted numbers.

    Examples
    --------
    >>> from adashof import cm2in
    >>> cm2in(5)
    1.97

    """

    # Test input
    try:
        length = np.array(length, dtype='float')
        decimals = int(decimals)
    except ValueError:
        print("{length} must be a number, {decimals} an integer")

    return np.round(length/2.54, decimals)


# In[4]:

def country(countries, bmap, fc=None, ec='none', lw=1, alpha=1, adm=0, gadmpath='/home/dtr/Documents/Webpages/blog-notebooks/data/TravelMap/'):
    """Colour <countries> with a <bmap> projection.
    
    This script is adapted from:
    http://www.geophysique.be/2013/02/12/
                           matplotlib-basemap-tutorial-10-shapefiles-unleached-continued
                           
    I downloaded the countries shapefile from the *Global Administrative Areas*
    website, [gadm.org](http://gadm.org).
    => You have to use the same abbreviations for the countries as GADM does, or adjust the script.
    => You have to download the shapefiles from GADM, and extract them into the <gadmpath> directory.

    Of course, you can use any other shapfiles you have, and adjust the script accordingly.

    Parameters
    ----------
    countries : string or list of strings
        Countries to be plotted.
    bmap : handle
        As you get from bmap = Basemap().
    fc : None or colour, or list of colours; <None>
        Face-colour for country; if <None>, it will cycle through colour-cycle.
    ec : 'none' or colour (scalar or list); <'none'>
        Edge-colour for country.
    lw : scalar or list; <1>
        Linewidth for country.
    alpha: scalar or list; <1>
        Transparency.
    adm : {0, 1, 2, 3}; <0>
        Administrative area to choose.
    gadmpath : 'string'
        Absolut or relative path to shapefiles.
    """

    # Ensure countries is a list
    if not isinstance(countries, list):
        countries = [countries,]
        
    # Get current axis
    cax = plt.gca()

    # Loop through the countries
    for country in countries:
    
        # Get shapefile for the country; extract shapes and records
        r = shapefile.Reader(gadmpath+country+'_adm/'+country+'_adm'+str(adm))
        shapes = r.shapes()
        records = r.records()

        # Loop through the records; for adm0 this is only 1 run
        n = 0
        for record, shape in zip(records,shapes):
            lons,lats = zip(*shape.points)
            data = np.array(bmap(lons, lats)).T

            if len(shape.parts) == 1:
                segs = [data,]
            else:
                segs = []
                for i in range(1,len(shape.parts)):
                    index = shape.parts[i-1]
                    index2 = shape.parts[i]
                    segs.append(data[index:index2])
                segs.append(data[index2:])
            lines = LineCollection(segs,antialiaseds=(1,))
            
            # If facecolor is provided, use; else cycle through colours
            if fc:
                if not isinstance(fc, list):
                    lines.set_facecolors(fc)
                else:
                    lines.set_facecolors(fc[n])
            else:
                cycle = cax._get_lines.prop_cycler
                lines.set_facecolors(next(cycle)['color'])

            # Edge colour
            if not isinstance(ec, list):
                lines.set_edgecolors(ec)
            else:
                lines.set_edgecolors(ec[n])
            # Alpha
            if not isinstance(alpha, list):
                lines.set_alpha(alpha)
            else:
                lines.set_alpha(alpha[n])
            # Line width
            if not isinstance(lw, list):
                lines.set_linewidth(lw)
            else:
                lines.set_linewidth(lw[n])


            # Add to current plot
            cax.add_collection(lines)
            n += 1


# In[5]:

def city(city, name, bmap, mfc=None, mec=None, color='b', offs=[.1, .1], halign='left'):
    """Plot a circle at <city> and annotate with <name>, with a <bmap> projection.
    
    Parameters
    ----------
    city : List of two scalars
        [Northing, Easting].
    name : string
        name to be plotted with city.
    bmap : handle
        As you get from bmap = Basemap().
    mfc : None or colour; <None>
        Marker face-colour for city; if <None>, it will cycle through colour-cycle.
    colour : 'none' or colour; <'b'>
        Colour for <name>.
    offs : List of two scalars; <[.1, .1]>
        Offset for <name> from <city>.
    halign : {'left', 'right', 'center'}; <'left'>
        Alignment of <name> relative to <city>.    
    """
    
    # mec from rcParams, to respect theme (dark/light)
    if not mec:
        mec = rcParams['axes.edgecolor']

    # Get current axis
    cax = plt.gca()
    
    # Plot dot
    # If mfc is provided, use; else cycle through colours
    if not mfc:
        cycle = cax._get_patches_for_fill.prop_cycler
        mfc = next(cycle)['color']
        
    bmap.plot(city[1], city[0], 'o', mfc=mfc, mec=mec, ms=4, mew=1, latlon=True)
    
    # Annotate name
    cax.annotate(name, bmap(city[1]+offs[0], city[0]+offs[1]),
                 horizontalalignment=halign, color=color, fontsize=7, zorder=10)


# In[6]:

def arrow(start, end, bmap, ec=None, fc=None, rad=-.3):
    """Plot an arrow from <start> to <end>, with a <bmap> projection.
    
    Parameters
    ----------
    start : List of two scalars
        Start of arrow [Northing, Easting].
    end : List of two scalars
        End of arrow [Northing, Easting].
    bmap : handle
        As you get from bmap = Basemap().
    ec : 'none' or colour; <'k'>
        Edge-colour for arrow.
    fc : 'none' or colour; <w>
        Face-colour for arrow.
    rad : Scalar; <.3]>
        Curvature of arrow.
    """
    
    # ec & fc from rcParams, to respect theme (dark/light)
    if not ec:
        ec = rcParams['axes.edgecolor']
    if not fc:
        fc = rcParams['axes.facecolor']
    
    # Get current axis
    cax = plt.gca()
    
    # Plot arrow
    arrowstyle='Fancy, head_length=.6, head_width=.6, tail_width=.4'
    cax.annotate('', bmap(end[1], end[0]), bmap(start[1], start[0]),
                arrowprops=dict(arrowstyle=arrowstyle,
                                alpha=.6,
                                patchA=None,
                                patchB=None,
                                shrinkA=3,
                                shrinkB=3,
                                fc=fc, ec=ec,
                                connectionstyle="arc3, rad="+str(rad),
                                ))

