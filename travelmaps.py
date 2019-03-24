
# coding: utf-8

# # `travelmaps`: Functions and settings to create beautiful global and local travel maps
# 
# [Blog](http://werthmuller.org/blog)
# [Repo](http://github.com/prisae/blog-notebooks)
# 
# See the blog post [Travel Maps](http://werthmuller.org/blog/2015/travelmap) for more explanations and some examples.
# 
# - country : Plot/fill countries.
# - city : Plot and annotate cities.
# - arrow : Plot arrows from city to city.
# 
# These functions are very basic, and include almost no checking or similar at all. Feel free to fork and improve them!

# In[2]:

import shapefile
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams, patheffects
from matplotlib.collections import LineCollection


# In[3]:

# Customized plt.xkcd()-settings
# http://jakevdp.github.io/blog/2013/07/10/XKCD-plots-in-matplotlib
rcParams['font.family'] = ['Humor Sans', 'Comic Sans MS']
rcParams['font.size'] = 8.0
rcParams['path.sketch'] = (1, 100, 2)
rcParams['path.effects'] = [patheffects.withStroke(linewidth=2, foreground="w")]
rcParams['axes.linewidth'] = 1.0
rcParams['lines.linewidth'] = 1.0
rcParams['figure.facecolor'] = 'white'
rcParams['grid.linewidth'] = 0.0
rcParams['axes.unicode_minus'] = False

# *Bayesian Methods for Hackers*-colour-cylce
# (https://github.com/pkgpl/PythonProcessing/blob/master/results/matplotlibrc.bmh.txt)
rcParams['axes.color_cycle'] = ['#348ABD', '#A60628', '#7A68A6', '#467821', '#D55E00',
                                 '#CC79A7', '#56B4E9', '#009E73', '#F0E442', '#0072B2']

# Adjust dpi, so figure on screen and savefig looks the same
rcParams['figure.dpi'] = 300
rcParams['savefig.dpi'] = 300


# In[4]:

def country(countries, bmap, fc=None, ec='none', lw=1, alpha=1, adm=0, gadmpath='data/TravelMap/'):
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
                lines.set_facecolors(next(cax._get_lines.color_cycle))

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

def city(city, name, bmap, mfc=None, color='b', offs=[.1, .1], halign='left'):
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
    
    # Get current axis
    cax = plt.gca()
    
    # Plot dot
    # If mfc is provided, use; else cycle through colours
    if not mfc:
        mfc = next(cax._get_patches_for_fill.color_cycle)
    bmap.plot(city[1], city[0], 'o', mfc=mfc, ms=4, mew=1, latlon=True)
    
    # Annotate name
    cax.annotate(name, bmap(city[1]+offs[0], city[0]+offs[1]),
                 horizontalalignment=halign, color=color, fontsize=7, zorder=10)


# In[6]:

def arrow(start, end, bmap, ec="k", fc="w", rad=-.3):
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

