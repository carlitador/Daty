import os
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.mlab import griddata
from mpl_toolkits.mplot3d import Axes3D
try:
	import matplotlib.style
	matplotlib.style.use('ggplot')
except:
	print "WARNING [plotting]: Cannot use ggplot style due to Matplotlib version being too low."
import pylab
import math
import numpy as np
try:
	from scipy import interpolate
	_CAN_INTERPOLATE = True
except:
	_CAN_INTERPOLATE = False
	print "WARNING [plotting]: Scipy package missing, spline interpolation will not be available."
from collections import Counter

# Utilities

def fitSpline(x,y,nPoints):
	'''
	[Description]
		Interpolate set of points with a spline.
	[Arguments]
		x (list[flota]): X data points.
		y (list[float]): Y data points.
		nPoints (int): Number of (equally spaced) interpolation points.
		->return (tuple[list[float],list[float]]): Interpolated X and Y data points.
	'''
	if _CAN_INTERPOLATE:
		try:
			#check for duplicated entries
			dups = [k for k,v in Counter(x).items() if v>1]
			if len(dups) > 0:
				print 'Warning, duplicated X values found in data when fitting spline: ',dups
			#sort by x
			x,y = zip(*list(sorted(zip(x,y))))
			#interpolate
			tck = interpolate.splrep(x, y,s=0)
			xnew = np.linspace(min(x),max(x),nPoints)
			ynew = interpolate.splev(xnew, tck, der=0)
			return xnew,ynew.tolist()
		except:
			print 'WARNING [plotting]: Spline interpolation failed.'
			return x,y
	else:
		print 'WARNING [plotting]: Scipy package missing, spline interpolation aborted.'
		return x,y

def arrangeSubplots(number_of_subplots,transpose=True):
	'''
	[Description]
		Creates square grid for creating a multiple plot image.
	[Arguments]
		number_of_subplots (int): Total number of subplots.
		*transpose (bool): Transpose height by width to fit PC computer better.
		->return (tuple[float]): Number of plots to place vertically and horizontally.
	'''
	gridWidth = int(math.sqrt(number_of_subplots))
	missingSpace = number_of_subplots-gridWidth*gridWidth
	additionalRows = int(missingSpace/gridWidth)
	if gridWidth*gridWidth < number_of_subplots and number_of_subplots%2 == 1 and number_of_subplots > 3:  
		gridHeigth = gridWidth+additionalRows+1
	else:
		gridHeigth = gridWidth+additionalRows
	if transpose == True:
		aux = gridHeigth
		gridHeigth = gridWidth
		gridWidth = aux
	return (gridHeigth,gridWidth)

# Default formatting for plots.
lines = ['-','--','-.',':']
titleFont = {'family':'serif','color':'black','weight':'normal','size':12}
labelFont = {'family':'serif','color':'black','weight':'normal','size':10}
textFont = {'family':'serif','color':'black','weight':'normal','size':10}
fancyColors = ['dodgerblue','tomato','mediumseagreen','orange','dimgray','springgreen','navy','gold','teal','aqua','MediumOrchid','green','blue','red','black']

# Plotting functions.

def plot_line(xArray,yArray,ax=None,splineDensity=0,xLabel='X',yLabel='Y',title='',label=None,color='b',line='-',marker='o',save=False,show='auto'):
	'''
	[Description]
		Create 2d line plot.
	[Arguments]
		xArray (list[float]): X axis data points.
		yArray (list[float]): Y axis data points.
		*ax (matplotlib.ax): Matplotlib ax to draw plot onto. By default a new figure and axes are created.
		*splineDensity (int): Numbers of points to use for building and interpolation spline. By default deactivated (splineDensity = 0).
		*xLabel (str): X axis label.
		*yLabel (str): Y axis label.
		*title (str): title label.
		*label (None/str): Legend name of current line being plot.
		*color (None/str): Color of current line being plot.
		*line (None/str): Line type of current line being plot.
		*marker (str): Marker type of current line being plot.
		*save (bool/str): Full path to save plot hardcopy (including file extension). By default is 'False' so no image is saved.
		*show (bool/str): Show plot upon creation. By default is set to 'auto' so that the plot is only shown when ax = None.
		->return (matplotlib.ax): Axes containing generated plot.
	'''
	if ax == None:
		ax = plt.figure().gca()
		if show == 'auto':
			show = True
	if splineDensity > 0:
		# Fit spline to points.
		nPoints = len(xArray)*splineDensity-1
		xArrayS,yArrayS = fitSpline(xArray,yArray,nPoints)
		ax.plot(xArrayS,yArrayS,color=color,label=label,lw=1.0,ls=line) # Splined line.
		ax.plot(xArray,yArray,color=color,linestyle='None',ms=3.0,marker=marker) # Data markers.
	else:
		ax.plot(xArray,yArray,color=color,label=label,ms=3.0,marker=marker,lw=1.0,linestyle=line)
	ax.set_title(title, fontdict=titleFont)
	ax.set_xlabel(xLabel, fontdict=labelFont)
	ax.set_ylabel(yLabel, fontdict=labelFont)
	ax.grid(True)
	ax.legend()
	if save != False:
		pylab.savefig(save, bbox_inches='tight')
	if show == True:
		plt.show()
	return ax

def smartSubplots(plots,legendSize=6,save=False,size=None,tight=True,show=True):
	'''
	[Description]
		Create plot with multiple subplots.
		Plots are arrenged automatically to form a square grid.
	[Arguments]
		plots (list[dict]): A list of dicts corresponding to each plot. The dicts have the following format:
							plots = [
										{'func':function used for plotting,'args':arguments required by func}, # First subplot.
										{'func':function used for plotting,'args':arguments required by func}, # Second subplot.
										...
									]
		
	'''
	if size != None:
		fig = plt.figure(figsize=size)
	else:
		fig = plt.figure()
	number_of_subplots = len(plots)
	gridHeigth,gridWidth = arrangeSubplots(number_of_subplots)
	for i in range(len(plots)):
		subAx = fig.add_subplot(gridHeigth,gridWidth,i+1)
		plots[i]['func'](*plots[i]['args'],ax=subAx)
		subAx.legend(prop={'size':legendSize})
	if save != False:
		pylab.savefig(save, bbox_inches='tight')
	else:
		if tight == True:
			plt.tight_layout()
	if show == True:
		plt.show()
	return fig

def plot_contour(xArray,yArray,zArray,ax=None,xLabel='X',yLabel='Y',title='',
			levels=20,density='auto',scatter=False,grid=True,
			interpolation='linear',save=True,show='auto'):
	'''
	[Description]
		2D contour plot.
	[Arguments]
		xArray (list[float]): X axis data points.
		yArray (list[float]): Y axis data points.
		zArray (list[float]): Z axis data points.
		*ax (matplotlib.ax): Matplotlib ax to draw plot onto. By default a new figure and axes are created.
		*xLabel (str): X axis label.
		*yLabel (str): Y axis label.
		*title (str): title label.
		*levels (int): Number of contour levels.
		*density (str/int): Density of interpolated regular grid (defined as number of points used in each dimension).
							By default it is set to 'auto' so that a number of points equal to the total number of given
							data points is used.
		*scatter (bool): Show data points on top of contour.
		*grid (bool): Interpolate given data to a regular grid.
		*interpolation (str): Interpolation method to interpolate given data to a regular grid from nn, linear or cubic.
		*save (bool/str): Full path to save plot hardcopy (including file extension). By default is 'False' so no image is saved.
		*show (bool/str): Show plot upon creation. By default is set to 'auto' so that the plot is only shown when ax = None.
		->return (matplotlib.ax): Axes containing generated plot.
	'''
	if ax == None:
		fig = plt.figure()
		ax = fig.gca()
		if show == 'auto':
			show = True
	# Create regular 2D mesh with data points.
	if grid == True:
		xi = np.linspace(min(xArray), max(xArray), density)
		yi = np.linspace(min(yArray), max(yArray), density)
		X, Y = np.meshgrid(xi, yi)
		Z = griddata(xArray, yArray, zArray, xi, yi, interp=interpolation)
	else:
		X, Y, Z = xArray, yArray, zArray
	# Contour fill color.
	cax = ax.contourf(X,Y,Z,levels,cmap=cm.nipy_spectral,origin='lower',alpha=0.7)
	# Make a colorbar for the contour lines.
	CB = plt.colorbar(cax)
	# Contour lines with labels.
	cax = ax.contour(X,Y,Z,levels, colors='k',alpha=0.8)
	plt.clabel(cax, colors='k', inline=1, fontsize=8)
	# Scatter data points.
	if scatter == True:
		ax.scatter(xArray,yArray,s=5,c='k',alpha=0.35)
	# Set CB position.
	l, b, w, h = ax.get_position().bounds
	ll, bb, ww, hh = CB.ax.get_position().bounds
	CB.ax.set_position([ll, b + 0.02*h, ww, h])
	ax.set_title(title, fontdict=titleFont)
	ax.set_xlabel(xLabel, fontdict=labelFont)
	ax.set_ylabel(yLabel, fontdict=labelFont)
	ax.grid(True)
	if save != False:
		pylab.savefig(save, bbox_inches='tight')
	if show == True:
		plt.show()
	return ax

def plot_surface(xArray, yArray, zArray, ax=None, xLabel='X', yLabel='Y', zLabel='Z', title='',
			view=None, contourLines=True, density=10, scatter=False, grid=True,
			interpolation='linear', save=False, show='auto'):
	'''
	[Description]
		3D surface plot.
	[Arguments]
		xArray (list[float]): X axis data points.
		yArray (list[float]): Y axis data points.
		zArray (list[float]): Z axis data points.
		*ax (matplotlib.ax): Matplotlib ax to draw plot onto. By default a new figure and axes are created.
		*xLabel (str): X axis label.
		*yLabel (str): Y axis label.
		*title (str): title label.
		*view (float): Camera azimuth angle.
		*contourLines (bool): Wether to draw or not the contour lines.
		*density (str/int): Density of interpolated regular grid (defined as number of points used in each dimension).
							By default it is set to 'auto' so that a number of points equal to the total number of given
							data points is used.
		*scatter (bool): Show data points on top of contour.
		*grid (bool): Interpolate given data to a regular grid.
		*interpolation (str): Interpolation method to interpolate given data to a regular grid from nn, linear or cubic.
		*save (bool/str): Full path to save plot hardcopy (including file extension). By default is 'False' so no image is saved.
		*show (bool/str): Show plot upon creation. By default is set to 'auto' so that the plot is only shown when ax = None.
		->return (matplotlib.ax): Axes containing generated plot.
	'''
	colormap = cm.nipy_spectral
	# Create regular 2D mesh with data points.
	if grid == True:
		xi = np.linspace(min(xArray), max(xArray), density)
		yi = np.linspace(min(yArray), max(yArray), density)
		X, Y = np.meshgrid(xi, yi)
		Z = griddata(xArray, yArray, zArray, xi, yi, interp=interpolation)
	else:
		X, Y, Z = xArray, yArray, zArray
	if ax == None:
		ax = plt.figure().gca(projection='3d')
		if show == 'auto':
			show = True
	ax.plot_surface(X, Y, Z, rstride=4, cstride=4, alpha=0.5,color='steelblue',linewidth=5.0)
	ax.plot_wireframe(X, Y, Z, rstride=4, cstride=4,color='black',linewidth=0.4)
	ax.contourf(X, Y, Z, zdir='z', offset=np.amin(zArray), cmap=colormap,alpha=0.4)
	ax.contour(X, Y, Z, zdir='z', offset=np.amin(zArray), colors='k',alpha=0.4)
	if scatter == True:
		ax.scatter(xArray,yArray,zArray,s=5,c='k')
	ax.set_title(title, fontdict=titleFont)
	ax.set_xlabel(xLabel, fontdict=labelFont)
	ax.set_ylabel(yLabel, fontdict=labelFont)
	ax.set_zlabel(zLabel, fontdict=labelFont)
	ax.grid(True)
	if view != None:
		ax.view_init(azim=view,elev=30)
	if save!=False:
		fig = plt.gcf()
		pylab.savefig(save+os.path.sep+str(title)+'.png', bbox_inches='tight')
	if show == True:
		plt.show()
	return ax
