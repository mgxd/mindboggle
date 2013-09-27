#!/usr/bin/env python
"""
Plotting functions.

Authors:
    - Arno Klein, 2012-2013  (arno@mindboggle.info)  http://binarybottle.com

Contributors:
    - Hal Canary <http://cs.unc.edu/~hal>: vtkviewer.py called by vtkviewer()

Copyright 2013,  Mindboggle team (http://mindboggle.info), Apache v2.0 License

"""


# # Example Pysurfer plot of FreeSurfer surface + VTK scalars
# ipython
# %gui qt
# import numpy as np
# import surfer
# from mindboggle.utils.io_vtk import read_scalars as rs
# d,n=rs('/drop/MB/data/arno/shapes/travel_depth_rescaled.vtk')
# br = surfer.Brain('Twins-2-1', 'lh', 'inflated')
# br.add_data(np.array(d), min=0, max=1, alpha=0.5)


def vtkviewer(vtk_file_list, colormap_file=None):
    """
    Use vtkviewer to visualize one or more VTK surface files.

    Parameters
    ----------
    vtk_file_list : string or list of strings
        name of VTK surface mesh file or list of file names
    colormap_file : string
        name of Paraview-style XML colormap file

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.plots import vtkviewer
    >>> path = os.environ['MINDBOGGLE_DATA']
    >>> vtk_file = os.path.join(path, 'arno', 'labels', 'lh.labels.DKT31.manual.vtk')
    >>> colormap_file = os.path.join(os.environ['MINDBOGGLE_TOOLS'], 'colormap.xml')
    >>> vtkviewer(vtk_file, colormap_file)

    """
    import os
    import glob
    import mindboggle.utils.vtkviewer as vv

    if isinstance(vtk_file_list, str):
        vtk_file_list = [vtk_file_list]

    if colormap_file:
        vtk_colormap = vv.VTKViewer.LoadColorMap(colormap_file)
    else:
        vtk_colormap = None

    vtkviewer = vv.VTKViewer()
    for vtk_file in vtk_file_list:
        fileNames = glob.glob(vtk_file)
        if len(fileNames) == 0:
            print "what:", vtk_file
        else:
            for fileName in fileNames:
                if os.path.isfile(fileName):
                    vtkviewer.AddFile(fileName,vtk_colormap)
                else:
                    print "what:", fileName
    vtkviewer.Start()


def plot_surfaces(vtk_file, mask_file='', mask_background=-1,
                  masked_output='', program='vtkviewer', colormap_file=None,
                  background_value=-1):
    """
    Use vtkviewer or mayavi2 to visualize VTK surface mesh data.

    Parameters
    ----------
    vtk_file : string
        name of VTK surface mesh file
    mask_file : string
        name of VTK surface mesh file to mask vtk_file vertices
    mask_background : integer
        mask background value
    masked_output : string
        temporary masked output file name
    program : string {'vtkviewer', 'mayavi2'}
        program to visualize VTK file
    colormap_file : string
        name of Paraview-style XML colormap file (for use with vtkviewer)
    background_value : integer
        background value

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.plots import plot_surfaces
    >>> path = os.environ['MINDBOGGLE_DATA']
    >>> vtk_file = os.path.join(path, 'arno', 'shapes', 'lh.pial.travel_depth.vtk')
    >>> mask_file = ''#os.path.join(path, 'arno', 'features', 'folds.vtk')
    >>> mask_background = -1
    >>> masked_output = ''
    >>> program = 'vtkviewer'
    >>> colormap_file = None
    >>> plot_surfaces(vtk_file, mask_file, mask_background, masked_output, program, colormap_file)

    """
    from mindboggle.utils.io_vtk import read_scalars, rewrite_scalars
    from mindboggle.utils.utils import execute
    from mindboggle.utils.plots import vtkviewer

    if not program:
        program = 'vtkviewer'

    # Filter mesh with non-background values from a second (same-size) mesh:
    if mask_file:
        scalars, name = read_scalars(vtk_file, True, True)
        mask, name = read_scalars(mask_file, True, True)
        scalars[mask == mask_background] = -1
        if not masked_output:
            masked_output = 'temp.vtk'
        rewrite_scalars(vtk_file, masked_output, scalars) #, 'masked', mask)
        file_to_plot = masked_output
    else:
        file_to_plot = vtk_file

    # Display with vtkviewer.py:
    if program == 'vtkviewer':
        vtkviewer(file_to_plot, colormap_file)

    # Display with mayavi2:
    elif program == 'mayavi2':
        cmd = ["mayavi2", "-d", file_to_plot, "-m", "Surface", "&"]
        execute(cmd, 'os')


def plot_volumes(volume_files):
    """
    Use fslview to visualize image volume data.

    Parameters
    ----------
    volume_files : list of strings
        names of image volume files

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.plots import plot_volumes
    >>> path = os.environ['MINDBOGGLE_DATA']
    >>> volume_file1 = os.path.join(path, 'arno', 'mri', 't1weighted.nii.gz')
    >>> volume_file2 = os.path.join(path, 'arno', 'mri', 't1weighted_brain.nii.gz')
    >>> volume_files = [volume_file1, volume_file2]
    >>> plot_volumes(volume_files)

    """
    from mindboggle.utils.utils import execute

    if isinstance(volume_files, str):
        volume_files = [volume_files]
    elif not isinstance(volume_files, list):
        import sys
        sys.error('plot_volumes() requires volume_files to be a list or string.')

    cmd = ["fslview"]
    cmd.extend(volume_files)
    cmd.extend('&')
    execute(cmd, 'os')


def histogram_of_vtk_scalars(vtk_file, nbins=100):
    """
    Plot histogram of VTK surface mesh scalar values.

    Parameters
    ----------
    vtk_file : string
        name of VTK file with scalar values to plot
    nbins : integer
        number of histogram bins

    Examples
    --------
    >>> import os
    >>> from mindboggle.utils.plots import histogram_of_vtk_scalars
    >>> path = os.environ['MINDBOGGLE_DATA']
    >>> vtk_file = os.path.join(path, 'arno', 'shapes', 'lh.pial.mean_curvature.vtk')
    >>> histogram_of_vtk_scalars(vtk_file, nbins=500)

    """
    import matplotlib.pyplot as plt
    from mindboggle.utils.io_vtk import read_scalars

    # Load values:
    values, name = read_scalars(vtk_file)

    # Histogram:
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.hist(values, nbins, normed=False, facecolor='gray', alpha=0.5)
    plt.show()


def histograms_of_lists(columns, column_name='', ignore_columns=[],
                        nbins=100, axis_limits=[], titles=[]):
    """
    Construct a histogram for each table column.

    Parameters
    ----------
    columns : list of lists
        list of lists of floats or integers
    column_name :  string
        column name
    ignore_columns : list of integers
        indices to table columns or sublists to exclude
    nbins : integer
        number of histogram bins
    axis_limits : list of four integers
        range of x- and y-axis ranges: [x-low, x-high, y-low, y-high]
    y_lim : list of two integers
        range of y-axis values
    titles : list of strings (length = number of columns - 1)
        histogram titles (if empty, use column headers)

    Examples
    --------
    >>> from mindboggle.utils.plots import histograms_of_lists
    >>> columns = [[1,1,2,2,2,2,2,2,3,3,3,4,4,8],[2,2,3,3,3,3,5,6,7]]
    >>> column_name = 'label: thickness: median (weighted)'
    >>> ignore_columns = []
    >>> nbins = 100
    >>> axis_limits = []
    >>> titles = ['title1','title2']
    >>> histograms_of_lists(columns, column_name, ignore_columns, nbins, axis_limits, titles)

    """
    import numpy as np
    import matplotlib.pyplot as plt

    ncolumns = len(columns)
    if ncolumns < 9:
        nplotrows = 1
        nplotcols = ncolumns
    else:
        nplotrows = np.ceil(np.sqrt(ncolumns))
        nplotcols = nplotrows

    #-------------------------------------------------------------------------
    # Construct a histogram from each column and display:
    #-------------------------------------------------------------------------
    fig = plt.figure()
    for icolumn, column in enumerate(columns):
        if icolumn not in ignore_columns:
            ax = fig.add_subplot(nplotrows, nplotcols, icolumn + 1)
            column = [np.float(x) for x in column]
            ax.hist(column, nbins, normed=False, facecolor='gray', alpha=0.5)
            plt.xlabel(column_name, fontsize='small')
            if len(titles) == ncolumns:
                plt.title(titles[icolumn], fontsize='small')
            else:
                plt.title(column_name + ' histogram', fontsize='small')
            if axis_limits:
                ax.axis(axis_limits)
    plt.show()


def boxplots_of_lists(columns, xlabel='', ylabel='', ylimit=None, title=''):
    """
    Construct a box plot for each table column.

    Parameters
    ----------
    columns : list of lists
        list of lists of floats or integers
    xlabel : str
        x-axis label
    ylabel : str
        y-axis label
    ylimit : float
        maximum y-value
    title : str
        title

    Examples
    --------
    >>> from mindboggle.utils.plots import boxplots_of_lists
    >>> columns = [[1,1,2,2,2,2,2,2,3,3,3,4,4,8],[2,2,3,3,3,3,5,6,7],
    >>>            [2,2,2.5,2,2,2,3,3,3,3,5,6,7]]
    >>> xlabel = 'xlabel'
    >>> ylabel = 'ylabel'
    >>> ylimit = None
    >>> title = 'title'
    >>> boxplots_of_lists(columns, xlabel, ylabel, ylimit, title)

    """
    import matplotlib.pyplot as plt

    #-------------------------------------------------------------------------
    # Construct a box plot from each column and display:
    #-------------------------------------------------------------------------
    plt.figure()
    plt.boxplot(columns, 1)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.ylim([0,ylimit])
    plt.title(title)
    plt.show()


def scatterplot_lists(y_columns, x_column, ignore_columns=[], plot_line=True,
                      connect_markers=True, mstyle='o', msize=1,
                      title='', x_label='', y_label='',
                      legend=True, legend_labels=[]):
    """
    Scatter plot columns against the values of one of the columns.

    Parameters
    ----------
    y_columns : list of lists of numbers
        columns of data (all of the same length)
    x_column : list of numbers
        column of numbers against which other columns are plotted
    ignore_columns : list of integers
        indices to y_columns to exclude
    plot_line : Boolean
        plot identity line?
    connect_markers : Boolean
        connect markers?
    mstyle : string
        marker style
    msize : integer
        marker size
    title :  string
        title
    x_label : string
        description of x_column
    y_label : string
        description of y_columns
    legend : Boolean
        plot legend?
    legend_labels : list of strings (length = number of y_columns)
        legend labels

    Examples
    --------
    >>> from mindboggle.utils.plots import scatterplot_lists
    >>> y_columns = [[1,1,2,2,2,3,3,4,4,8],[2,2,3,3,3,3,5,6,7,7]]
    >>> x_column = [1,1.5,2.1,1.8,2.2,3,3.1,5,7,6]
    >>> ignore_columns = []
    >>> plot_line = True
    >>> connect_markers = True
    >>> mstyle = 'o'
    >>> msize = 10
    >>> title = 'title'
    >>> x_label = 'xlabel'
    >>> y_label = 'ylabel'
    >>> legend = True
    >>> legend_labels = ['mark1','mark2']
    >>> scatterplot_lists(y_columns, x_column, ignore_columns, plot_line, connect_markers, mstyle, msize, title, x_label, y_label, legend, legend_labels)

    """
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
    import matplotlib.cm as cm
    import numpy as np

    ncolumns = len(y_columns)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    #colors = ['b','r','c','m','k','g','y']
    colors = iter(cm.hsv(np.linspace(0, 1, ncolumns)))
    #-------------------------------------------------------------------------
    # Scatter plot:
    #-------------------------------------------------------------------------
    hold = True
    if plot_line:
        min_value = np.inf
        max_value = -np.inf
    for icolumn, column in enumerate(y_columns):
        column = [np.float(x) for x in column]
        if icolumn not in ignore_columns:
            color = next(colors)
            #color = colors[icolumn]
            if len(legend_labels) == ncolumns:
                color_text = legend_labels[icolumn]
                if connect_markers and not plot_line:
                    plt.plot(x_column, column, '-', marker=mstyle, s=msize,
                             facecolors='none', edgecolors=color, hold=hold,
                             label=color_text)
                else:
                    plt.scatter(x_column, column, marker=mstyle, s=msize,
                                facecolors='none', edgecolors=color, hold=hold,
                                label=color_text)
            else:
                if connect_markers and not plot_line:
                    plt.plot(x_column, column, '-', marker=mstyle, s=msize,
                             facecolors='none', edgecolors=color, hold=hold)
                else:
                    plt.scatter(x_column, column, marker=mstyle, s=msize,
                                facecolors='none', edgecolors=color, hold=hold)

        if plot_line:
            if min(column) < min_value:
                min_value = min(column)
            if max(column) > max_value:
                max_value = max(column)

    #-------------------------------------------------------------------------
    # Add legend and display:
    #-------------------------------------------------------------------------
    if plot_line:
        plt.plot(range(int(min_value), int(max_value) + 2))
    if legend:
        fontP = FontProperties()
        fontP.set_size('small')
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc='lower right', prop=fontP)
    ax.grid()
    if x_label:
        plt.xlabel(x_label)
    if y_label:
        plt.ylabel(y_label)
    plt.title(title)
    plt.show()


def scatterplot_list_pairs(columns, ignore_first_column=False, plot_line=True,
                           connect_markers=True, mstyle='o', msize=1,
                           mcolor='', title='', x_label='', y_label='',
                           limit=None, legend=True, legend_labels=[]):
    """
    Scatter plot pairs of columns.

    Parameters
    ----------
    columns : list of lists of numbers
        alternating columns of data (all of the same length)
    ignore_first_column : Boolean
        exclude first column?
    plot_line : Boolean
        plot identity line?
    connect_markers : Boolean
        connect markers?
    mstyle : string
        marker style
    msize : integer
        marker size
    mcolor : string
        marker color (if empty, generate range of colors)
    title :  string
        title
    x_label : string
        description of x_column
    y_label : string
        description of other columns
    limit : float
        x- and y-axis extent
    legend : Boolean
        plot legend?
    legend_labels : list of strings (length = number of columns)
        legend labels

    Examples
    --------
    >>> from mindboggle.utils.plots import scatterplot_list_pairs
    >>> columns = [['labels'], [1,1,2,2,2,3,3,4,4,8],[2,2,3,3,3,3,5,6,7,7],
    >>>            [1,1.5,2.1,1.8,2.2,3,3.1,5,7,6],
    >>>            [1.2,0.5,2,1.3,1.2,3,1,5.2,4,4.5]]
    >>> ignore_first_column = True
    >>> plot_line = True
    >>> connect_markers = True
    >>> mstyle = 'o'
    >>> msize = 10
    >>> mcolor = ''
    >>> title = 'title'
    >>> x_label = 'xlabel'
    >>> y_label = 'ylabel'
    >>> limit = None
    >>> legend = True
    >>> legend_labels = ['mark1','mark2']
    >>> scatterplot_list_pairs(columns, ignore_first_column, plot_line, connect_markers, mstyle, msize, mcolor, title, x_label, y_label, limit, legend, legend_labels)

    """
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    from matplotlib.font_manager import FontProperties
    import numpy as np

    ncolumns = len(columns)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    if not mcolor:
        colors = iter(cm.hsv(np.linspace(0, 1, ncolumns)))
    #-------------------------------------------------------------------------
    # Scatter plot:
    #-------------------------------------------------------------------------
    hold = True
    if plot_line:
        min_value = np.inf
        max_value = -np.inf
    if ignore_first_column:
        columns = columns[1::]
    columns1 = [x for i,x in enumerate(columns) if np.mod(i,2) == 1]
    columns2 = [x for i,x in enumerate(columns) if np.mod(i,2) == 0]
    if not limit:
        limit = np.ceil(np.max([np.max(columns1), np.max(columns1)]))
    for icolumn, column1 in enumerate(columns1):
        column2 = columns2[icolumn]
        column1 = [np.float(x) for x in column1]
        column2 = [np.float(x) for x in column2]
        if mcolor:
            color = mcolor
        else:
            color = next(colors)
        if len(legend_labels) == ncolumns:
            if connect_markers and not plot_line:
                plt.plot(column1, column2, '-', marker=mstyle,
                         color=color, hold=hold,
                         label=legend_labels[icolumn])
            else:
                plt.scatter(column1, column2, marker=mstyle, s=msize,
                            facecolors='none', edgecolors=color, hold=hold,
                            label=legend_labels[icolumn])
        else:
            if connect_markers and not plot_line:
                plt.plot(column1, column2, '-', marker=mstyle,
                         color=color, hold=hold)
            else:
                plt.scatter(column1, column2, marker=mstyle, s=msize,
                            facecolors='none', edgecolors=color, hold=hold)

        if plot_line:
            if min(column1) < min_value:
                min_value = min(column1)
            if max(column1) > max_value:
                max_value = max(column1)

    #-------------------------------------------------------------------------
    # Add legend and display:
    #-------------------------------------------------------------------------
    if plot_line:
        plt.plot(range(int(min_value), int(max_value) + 2))
    if legend:
        fontP = FontProperties()
        fontP.set_size('small')
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc='lower right', prop=fontP)
    plt.xlim([0,limit])
    plt.ylim([0,limit])
    ax.grid()
    ax.set_aspect(aspect='equal')
    if x_label:
        plt.xlabel(x_label)
    if y_label:
        plt.ylabel(y_label)
    plt.title(title)
    plt.show()


#-----------------------------------------------------------------------------
# Example: Plot scan-rescan thickness values from table (alternating columns)
#-----------------------------------------------------------------------------
if __name__== '__main__':

    import os
    import numpy as np
    from mindboggle.utils.plots import scatterplot_list_pairs
    from mindboggle.utils.plots import boxplots_of_lists
    from mindboggle.utils.plots import histograms_of_lists

    #-------------------------------------------------------------------------
    # Load thickness values from table (alternating columns are scan-rescan):
    #-------------------------------------------------------------------------
    tablename = '/drop/LAB/thickness_outputs/thicknesses.csv'
    title = 'Thickasabrick (62 labels, 40 EMBARC controls)'

    f1 = open(tablename,'r')
    f1 = f1.readlines()
    columns = [[] for x in f1[0].split()]
    for row in f1:
        row = row.split()
        for icolumn, column in enumerate(row):
            columns[icolumn].append(np.float(column))
    columns1 = [columns[0]]
    for i in range(1, len(columns)):
        if np.mod(i,2) == 1:
            columns1.append(columns[i])

    #-------------------------------------------------------------------------
    # Scatter plot:
    #-------------------------------------------------------------------------
    scat = True
    if scat:
        ignore_first_column = True
        plot_line = False
        connect_markers = False
        mstyle = 'o'
        msize = 10
        mcolor = 'black'
        xlabel = 'scan thickness (mm)'
        ylabel = 'rescan thickness (mm)'
        limit = 6.5
        legend = True
        legend_labels = ['mark1','mark2']
        scatterplot_list_pairs(columns, ignore_first_column, plot_line,
                               connect_markers, mstyle, msize, mcolor, title,
                               xlabel, ylabel, limit, legend, legend_labels)

    #-------------------------------------------------------------------------
    # Box plot per label:
    #-------------------------------------------------------------------------
    box_per_label = True
    if box_per_label:
        rows1 = []
        for row in f1:
            rows1.append([np.float(x) for x in row.split()[1::]])
        xlabel = 'label index'
        ylabel = 'thickness (mm)'
        ylimit = 6.5
        boxplots_of_lists(rows1, xlabel, ylabel, ylimit, title)

    #-------------------------------------------------------------------------
    # Box plot per scan:
    #-------------------------------------------------------------------------
    box_per_scan = False
    if box_per_scan:
        xlabel = 'scan index'
        ylabel = 'thickness (mm)'
        ylimit = 6.5
        boxplots_of_lists(columns1[1::], xlabel, ylabel, ylimit, title)

    #-------------------------------------------------------------------------
    # Histogram:
    #-------------------------------------------------------------------------
    hist = False
    if hist:
        ignore_columns = [0]
        nbins = 10
        axis_limits = [0, 5, 0, 10]
        titles = []
        histograms_of_lists(columns, 'thickness', ignore_columns, nbins,
                            axis_limits, titles)
