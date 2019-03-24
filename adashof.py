
# coding: utf-8

# # `adashof`: Functions used in the notebooks of the blog
# 
# [Blog](http://werthmuller.org/blog)
# [Repo](http://github.com/prisae/blog-notebooks)
# 
# - circle : Create circle on figure with axes of different sizes.
# - move_sn_y : Move scientific notation exponent from top to the side.
# - fillgrid : Fill rectangular grid with colours or a colour and transparency.
# - checksize : Check size of pdf figure, and adjust if required.
# - cm2in : Convert centimetres to inches

# In[1]:

import numpy as np
import matplotlib as mpl
from matplotlib import cm
import matplotlib.pyplot as plt


# In[2]:

def circle(xy, radius, kwargs=None):
    """Create circle on figure with axes of different sizes.

    Plots a circle on the current axes using `plt.Circle`, taking into account
    the figure size and the axes units.

    It is done by plotting in the figure coordinate system, taking the aspect
    ratio into account. In this way, the data dimensions do not matter.
    However, if you adjust `xlim` or `ylim` after plotting `circle`, it will
    screw them up; set `plt.axis` before calling `circle`.

    Parameters
    ----------
    xy, radius, kwars :
        As required for `plt.Circle`.
    """

    # Get current figure and axis
    fig = mpl.pyplot.gcf()
    ax = fig.gca()

    # Calculate figure dimension ratio width/height
    pr = fig.get_figwidth()/fig.get_figheight()

    # Get the transScale (important if one of the axis is in log-scale)
    tscale = ax.transScale + (ax.transLimits + ax.transAxes)
    ctscale = tscale.transform_point(xy)
    cfig = fig.transFigure.inverted().transform(ctscale)

    # Create circle
    if kwargs == None:
        circ = mpl.patches.Ellipse(cfig, radius, radius*pr,
                transform=fig.transFigure)
    else:
        circ = mpl.patches.Ellipse(cfig, radius, radius*pr,
                transform=fig.transFigure, **kwargs)

    # Draw circle
    ax.add_artist(circ)


# In[3]:

def move_sn_y(offs=0, dig=0, side='left', omit_last=False):
    """Move scientific notation exponent from top to the side.
    
    Additionally, one can set the number of digits after the comma
    for the y-ticks, hence if it should state 1, 1.0, 1.00 and so forth.

    Parameters
    ----------
    offs : float, optional; <0>
        Horizontal movement additional to default.
    dig : int, optional; <0>
        Number of decimals after the comma.
    side : string, optional; {<'left'>, 'right'}
        To choose the side of the y-axis notation.
    omit_last : bool, optional; <False>
        If True, the top y-axis-label is omitted.

    Returns
    -------
    locs : list
        List of y-tick locations.

    Note
    ----
    This is kind of a non-satisfying hack, which should be handled more
    properly. But it works. Functions to look at for a better implementation:
    ax.ticklabel_format
    ax.yaxis.major.formatter.set_offset_string
    """

    # Get the ticks
    locs, _ = mpl.pyplot.yticks()

    # Put the last entry into a string, ensuring it is in scientific notation
    # E.g: 123456789 => '1.235e+08'
    llocs = '%.3e' % locs[-1]

    # Get the magnitude, hence the number after the 'e'
    # E.g: '1.235e+08' => 8
    yoff = int(str(llocs).split('e')[1])

    # If omit_last, remove last entry
    if omit_last:
        slocs = locs[:-1]
    else:
        slocs = locs

    # Set ticks to the requested precision
    form = r'$%.'+str(dig)+'f$'
    mpl.pyplot.yticks(locs, list(map(lambda x: form % x, slocs/(10**yoff))))

    # Define offset depending on the side
    if side == 'left':
        offs = -.18 - offs # Default left: -0.18
    elif side == 'right':
        offs = 1 + offs    # Default right: 1.0
        
    # Plot the exponent
    mpl.pyplot.text(offs, .98, r'$\times10^{%i}$' % yoff, transform =
            mpl.pyplot.gca().transAxes, verticalalignment='top')

    # Return the locs
    return locs


# In[4]:

def fillgrid(xval, yval, values, style='colour', cmap=cm.Spectral,
             unicol='#000000', lc='k', lw=0.5):
    """Fill rectangular grid with colours or a colour and transparency.

    Parameters
    ----------
    xval, yval : array
        Grid-points in x- and in y-direction.
    values : array, dimension: (x-1)-by-(y-1)
        Values between 0 and 1
    style : string, optional; {<'colour'>, 'alpha'}
        Defines if values represent colour or alpha.
    cmap : mpl.cm-element, optional
        `Colormap` colours are chosen from; only used if style='colour'
    unicol : HEX-colour
        Colour used with transparency; only used if style='alpha'
    lc, lw : optional
        Line colour and width, as in standard plots.

    Returns
    -------
    rct : list
        List of plotted polygon patches.
    """
         
    # Ravel values, and set NaN's to zero
    rval = values.ravel()
    rvalnan = np.isnan(rval)
    rval[rvalnan] = 0
    
    # Define colour depending on style
    if style == 'alpha':
        # Create RGB from HEX
        unicol = mpl.colors.colorConverter.to_rgb(unicol)
        # Repeat colour for all values,
        # filling the value into the transparency column
        colour = np.vstack((np.repeat(unicol, len(rval)).reshape(3, -1),
                            rval)).transpose()
    else:
        # Split cmap into 101 points from 0 to 1
        cmcol = cmap(np.linspace(0, 1, 101))
        # Map the values onto these
        colour = cmcol[list(map(int, 100*rval))]
        # Set transparency to 0 for NaN's
        colour[rvalnan, -1] = 0

    # Draw all rectangles at once
    xxval = np.array([xval[:-1], xval[:-1], xval[1:], xval[1:]]).repeat(
            len(yval)-1, axis=1).reshape(4, -1)
    yyval = np.array([yval[:-1], yval[1:], yval[1:], yval[:-1]]).repeat(
            len(xval)-1, axis=0).reshape(4, -1)
    rct = mpl.pyplot.gca().fill(xxval, yyval, lw=lw, ec=lc)
    
    # Map the colour onto a list
    cls = list(map(mpl.colors.rgb2hex, colour))
    
    # Adjust colour and transparency for all cells
    for ind in range(len(rct)):
        rct[ind].set_facecolor(cls[ind])
        rct[ind].set_alpha(colour[ind, -1])

    return rct


# In[5]:

def checksize(fhndl, name, dsize, precision=0.01, extent=0.05, kwargs={}, _cf=False):
    """Print figure with 'name.pdf', check size, compare with dsize, and adjust if required

    Parameters
    ----------
    fhndl : figure-handle
        Figure handle of the figure to be saved.
    name : string
        Figure name.
    dsize : list of two floats
        Desired size of pdf in cm.
    precision : float, optional; <0.01>
        Desired precision in cm of the dimension, defaults to 1 mm.
    extent : float or list of floats, optional; <0.01>
        - If float, then bbox_inches is set to tight, and pad_inches=extent.
        - If it is an array of two numbers it sets the percentaged extent-width,
          `Bbox.expanded`.
        - If it is an array of four numbers it sets [x0, y0, x1, y1] of Bbox.
    kwargs : dict
        Other input arguments that will be passed on to `plt.savefig`; e.g. dpi or facecolor.
    _cf : Internal parameter for recursion and adjustment.
    """

    # Import PyPDF2
    from PyPDF2 import PdfFileReader    
    
    # Check `extent` input and set bbox_inches and pad_inches accordingly
    if np.size(extent) == 1:
        bbox_inches = 'tight'
        pad_inches = extent
    else:
        fext = fhndl.gca().get_window_extent().transformed(
                fhndl.dpi_scale_trans.inverted())
        if np.size(extent) == 2:
            bbox_inches = fext.expanded(extent[0], extent[1])
        elif np.size(extent) == 4:
            fext.x0, fext.y0, fext.x1, fext.y1 = extent
            extent = [1, 1] # set extent to [1, 1] for recursion
            bbox_inches = fext
        pad_inches=0
        
    # Save the figure
    fhndl.savefig(name+'.pdf', bbox_inches=bbox_inches, pad_inches=pad_inches, **kwargs)

    # Get pdf-dimensions in cm
    pdffile = PdfFileReader(open(name+'.pdf', mode='rb'))
    pdfsize = np.array([float(pdffile.getPage(0).mediaBox[2]),
               float(pdffile.getPage(0).mediaBox[3])])
    pdfdim = pdfsize*2.54/72. # points to cm
        
    # Define `print`-precision on desired precision
    pprec = abs(int(('%.1e' % precision).split('e')[1]))+1
    
    # Get difference btw desired and actual size
    diff = dsize-pdfdim
    
    # If diff>precision, adjust, else finish
    if np.any(abs(diff) > precision):
        if not _cf:
            _cf = [1, 1]
        
        # Be verbose
        print('  resize...')
        
        # Adjust width
        if (abs(diff[0]) > precision):
            print('        X-diff:', np.round(diff[0], pprec), 'cm')
            
            # Set new factor to old factor times (desired size)/(actual size)
            _cf[0] = _cf[0]*dsize[0]/pdfdim[0]
            
            # Set new figure width
            fhndl.set_figwidth(_cf[0]*dsize[0]/2.54) # cm2in

        # Adjust height
        if (abs(diff[1]) > precision):
            print('        Y-diff:', np.round(diff[1], pprec), 'cm')
            
            # Set new factor to old factor times (desired size)/(actual size)
            _cf[1] = _cf[1]*dsize[1]/pdfdim[1]
            
            # Set new figure height
            fhndl.set_figheight(_cf[1]*dsize[1]/2.54) #cm2in
        
        # Call the function again, with new factor _cf
        figsize = checksize(fhndl, name, dsize, precision, extent, kwargs, _cf)

        return figsize

    else: # Print some info if the desired dimensions are reached
        
        # Print figure name and pdf dimensions
        print('Figure saved to '+name +'.pdf;',
              np.round(pdfdim[0], pprec), 'x',
              np.round(pdfdim[1], pprec), 'cm.')
        
        # Print the new figsize if it had to be adjusted
        if _cf:
            print('     => NEW FIG-SIZE: figsize=('+
                  str(np.round(fhndl.get_size_inches()[0], 2*pprec))+', '+
                  str(np.round(fhndl.get_size_inches()[1], 2*pprec))+')')
            
        # Return figsize
        return fhndl.get_size_inches()


# In[6]:

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

