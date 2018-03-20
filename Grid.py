# Standard library
from copy import copy, deepcopy
from collections import OrderedDict
import json
from numbers import Number
# Utils
from utils import dynamicTyped

'''
To Do:
	-fix .addColumn behaviour that does not let add new columns of different length than current grid length.
'''

class GridRow(object):
	'''
	Abstract list-like object of which Grid objects are made of.
	This object is similar to an ordered dict, but with some modified builtins, few extra methods and a safe immutable design.
	
	To be used by Grid, do not instiantate directly.
	
	GridRow is designed with safety in mind so it is inmutable form outside. Hence, all objects that are given as arguments or returned
	by gridrow methods are deepcopied.
	'''
	def __init__(self,elements,header):
		self._elements = deepcopy(elements)
		self._header = deepcopy(header)
		# create dict matching each field with its column index
		self._fieldIndexDict = dict([(item,i) for i,item in enumerate(self._header)])

	# Properties

	@property
	def header(self):
		'''
		Return gridrow header.
		A copy is returned so that actual gridrow header is not modified by accident.
		'''
		return deepcopy(self._header) # 

	@header.setter
	def header(self, newHeader):
		'''
		Header setter updates header and fieldIndex dict.
		'''
		self._header = deepcopy(newHeader) # copy given header so that it is not modified from outside gridrow by accident.
		self._fieldIndexDict = dict([(item,i) for i,item in enumerate(self._header)])

	@property
	def elements(self):
		'''
		Return gridrow elements.
		A copy is returned so that actual gridrow elements are not modified by accident.
		'''
		return deepcopy(self._elements)

	@elements.setter
	def elements(self,newElements):
		'''
		Set all elements to new values.
		'''
		if len(newElements) == len(self._elements):
			self._elements = deepcopy(newElements)
		else:
			raise IndexError('ERROR: [Grid|elements.setter]: New elements differ in length from current elements')

	# Built-in

	def __getitem__(self,field):
		'''
		Return value corresponding to given header entry.
		Field can be specified by column index or header name.
		'''
		fieldIndex = self._fieldIndex(field)
		return deepcopy(self._elements[fieldIndex])

	def __setitem__(self,field,value):
		'''
		[Description]
			Set field value. If field does not exist, it is added.
		[Arguments]
			field (str/int):
			value (misc):
		'''
		# field name given
		if type(field) == str:
			# field exists, lookup index
			if field in self._fieldIndexDict.keys():
				fieldIndex = self._fieldIndexDict[field]
			# field does not exist, set index to current last field + 1 
			else:
				fieldIndex = len(self.header)
		# field index given
		else:
			fieldIndex = field
		# element exists
		if fieldIndex < len(self.header):
			self._elements[fieldIndex] = deepcopy(value)
		# add new element
		elif fieldIndex == len(self.header):
			self._elements.append(deepcopy(value))
			newHeader = self.header
			newHeader.append(field)
			self.header = newHeader
		else:
			raise IndexError('[Grid|__setitem__]: GridRow does not have index field '+str(fieldIndex))

	def __repr__(self):
		'''
		Treat GridRow as a list of elements.
		'''
		return ', '.join([str(element) for element in self._elements])

	def __eq__(self,other):
		'''
		A GridRow is equal to another one if all elements are equal.
		'''
		if isinstance(other,GridRow):
			if len(self) == len(other):
				for i,element in enumerate(self.elements):
					if element != other[i]:
						return False
			else:
				return False
			return True
		else:
			print '[GridRow|__eq__]: Non compatible types',self.__class__,'and',other.__class__

	def __iter__(self):
		'''
		Gridrow is treated as a list of elements.
		'''
		return self._elements.__iter__()

	def __len__(self):
		'''
		Gridrow is treated as a list of elements.
		'''
		return len(self._elements)

	# Private

	def _fieldIndex(self,field):
		'''
		Return field position based on its name.
		'''
		if type(field) == str:
			return self._fieldIndexDict[field]
		else:
			return field

	# Public

	def pop(self,field):
		'''
		Delete element and corresponding header entry.
		'''
		index = self.header.index(field)
		self._elements.pop(index)
		newHeader = self.header
		newHeader.pop(index)
		self.header = newHeader
		# # this function could be simplified as:
		# self.header.pop(self._fieldIndexDict[field])
		# self._elements.pop(self._fieldIndexDict[field])

	def index(self,element):
		'''
		Return the index of an element.
		'''
		return self._elements.index(element)

	def round(self,precision):
		'''
		Return a copy of GridRow with numeric elements rounded to specified precision.
		'''
		rounded = []
		for element in self._elements:
			# check if element is a number (note that True/False are also Numbers in python so a second check is added)
			if isinstance(element, Number) and not isinstance(element, bool):
				rounded.append(round(element,precision))
			else:
				rounded.append(element)
		return GridRow(rounded,self.header)

	def asDict(self):
		'''
		Return ordered dict representation of GridRow.
		'''
		gridRowDict = OrderedDict()
		for key in self.header:
			gridRowDict[key] = self[key]
		return gridRowDict

	def asString(self,listSeparator=';'):
		'''
		Return string representation of GridRow elements.
		'''
		textElements = []
		for element in self:
			if type(element) == list:
				textElements.append('['+listSeparator.join([str(e) for e in element])+']')
			else:
				textElements.append(str(element))
		return ','.join(textElements)

	def moveField(self,field,newIndex):
		'''
		[Description]
			Move a field from one position (index) to another.
		[Arguments]
			field (str): Name of field to move.
			newIndex (int): New field position.
		'''
		# get current index
		currentIndex = self._fieldIndex(field)
		# check if new position is last element to choose between append or insert.
		if newIndex < len(self.header)-1:
			# move elements
			self._elements.insert(newIndex, self._elements.pop(currentIndex))
			# update header
			self._header.insert(newIndex, self._header.pop(currentIndex))
		elif newIndex == len(self.header):
			self._elements.append(self._elements.pop(currentIndex))
			self._header.append(self._header.pop(currentIndex))
		else:
			raise IndexError('ERROR [Grid|moveField]: Cannot move field to a position greater than GridRow length')

class Grid(object):
	'''
	Class for 2D grid analysis and manipulation.
	Each row in Grid is a GridRow object.
	Structure:
		header 1,	header 2,	header 3,	...,	header N 	(fields === columns)
		r1c1,		r1c2,		r1c3,		...,	r1cN		(row)
		r2c1,		r2c2,		r2c3,		...,	r2cN
		...
		rNc1,		rNc2,		rNc3,		...,	rNcN
	'''

	# built-ins

	def __init__(self,grid,header=True,**kwargs):
		'''
		[Arguments]
			grid (str/list[list[misc]]): Path to file containing grid or grid given directly as a list of lists.
			header (list[str]/bool): Set to True when header is given on first grid row.
										Set to False when grid has no header ('col1', 'col2', ..., 'colN' header names will be given).
										Set to list of strings to use as header. List length must match number grid columns.
			**kwargs (dict): Kwargs passed to _parse() method in charge of parsing grid from a file.
		'''
		# path to grid given. Read file and parse.
		if type(grid) == str:
			with open(grid,'r') as f: grid = f.readlines()
			self.grid = self._parse(grid,**kwargs)
		# grid given as a list of lists. Grid is assigned to gridrows directly.
		elif type(grid) == list:
			self.grid = grid
		else:
			raise TypeError('ERROR [pyDSO.Grid]: Unkown grid format.')
		# initialize header
		self._initHeader(header)
		# create grid as a list of GridRows
		self.grid = [GridRow(row,self.header) for row in self.grid]
		# default settings
		self.defaultFilterRule = 'OR'

	def __add__(self,newRow,fill_value=None):
		'''
		[Description]
			Add row or Grid to current grid.
			Differing header entries are matched with missing values set to fill_value.
		[Arguments]
			newRow (list/GridRow/Grid): List, GridRow or Grid to add to grid.
			*fill_value (float / float list): Value to be used for filling unmatched columns.
		'''
		newRow = deepcopy(newRow)
		# add gridrow to grid
		if isinstance(newRow,GridRow):
			#match headers
			self.match(newRow,fill_value)
			#add row to grid.
			self.grid.append(newRow)
		# list given, assume both headers match
		elif isinstance(newRow,list):
			if len(newRow) == len(self.header):
				self.grid.append(GridRow(newRow,self.header))
			else:
				raise IndexError('New row ('+str(len(newRow))+') does not have compatible length with Grid ('+str(len(self.header))+')')
		# Grid given, add all its gridrows to grid
		elif isinstance(newRow, Grid):
			for row in newRow:
				#match headers
				self.match(row,fill_value)
				#add row to grid.
				self.grid.append(row)
		else:
			raise TypeError('[Grid|__add__]: Not implemented yet for type '+str(type(newRow)))

	def __getitem__(self,index):
		'''
		[Description]
			Return all values of a given field (full column), a subset of Grid or a single GridRow, depending on type of input argument.
		[Arguments]
			index (str): Field name -> return a list with all field values.
			index (int): Row index -> return a sinlge GridRow.
			index (dict): Filter -> return Grid subset that passes the given filters.
			index (list[int]: Row indices -> return Grid containing such GridRows.
			index (list[str]: Field names -> return Grid containing such columns.
			index (list[dict]): Filters -> return Grid subset that passes the given filters.
			index (slice[int]): Row indices slice -> return Grid containing such GridRows.
			index (slice[str]): Field names slice -> return Grid containing such columns.
			index (callable): Function f(gridrow) = value -> return list with all modified field values.
			->return (list/GridRow/Grid): List with all field values, GridRow or Grid, depending on index type. 
		'''
		if type(index) == str:
			return self._field(index)
		elif type(index) == int:
			return self.grid[index]
		elif type(index) == dict:
			return self.filter(index)
		elif type(index) == list:
			if type(index[0]) == int:
				return Grid([self.grid[e].elements for e in index],header=self.header)
			elif type(index[0]) == str:
				newGrid = map(list, zip(*[self[field] for field in index])) 
				return Grid(newGrid,header=index)
			elif type(index[0]) == dict:
				return self.filter(index)
		elif type(index) == slice:
			if type(index.start) == int:
				return Grid([gridrow.elements for gridrow in self.grid[index]],header=self.header)
			elif type(index.start) == str:
				raise KeyError('Type'+str(type(index))+'not supported.')
		elif callable(index):
			return [index(gridrow) for gridrow in self]

		raise KeyError('[Grid|__getitem__]: Type'+str(type(index))+'not supported.')

	def __setitem__(self,field,newValue):
		'''
		[Description]
			Modify all the values of given field. Newvalue can be specified with a constant, list or callable.
			If field does not exist, it is appended as a new column.
		[Arguments]
			field (str): Name of field to modify.
			newValue (list/callable/other): Value of new column rows specified as:
												List --> Assumes each element corresponds to one row.
												Callable --> A function that is given each row and returns the new value.
												Other --> Fixed value for all columns (can be Float, String, Bool, None, etc).
		'''
		assert(type(field) == str) # check a field is given.
		for i,row in enumerate(self.grid):
			#assign list corresponding value
			if type(newValue) == list:
				row[field] = newValue[i]
			#calculate value with function
			elif callable(newValue):
				row[field] = newValue(row)
			#constant value
			else:
				row[field] = newValue
		# if field does not exist, append to header
		if field not in self.header:
			newHeader = self.header
			newHeader.append(field)
			self.header = newHeader

	def __iter__(self):
		'''
		Iterate across all GridRows.
		'''
		return self.grid.__iter__()

	def __len__(self):
		'''
		Returns length as number of GridRows.
		'''
		return len(self.grid)

	def __repr__(self):
		'''
		Represent grid as a header followed by its GridRows elements.
		'''
		return ','.join(self.header)+'\n'+'\n'.join([str(i)+' '+str(row) for i,row in enumerate(self.grid)])

	def __sub__(self,row):
		'''
		[Description]
			Delete row from grid. To delete a row by index use .pop()
		[Arguments]:
			row (GridRow): GridRow to delete.
		'''
		self.grid.remove(row)

	# private methods

	def _parse(self,grid,dynamicType=True,noneEmpty=True,sep=',',listSep=';'):
		'''
		[Description]
			Parse the raw contents of a text file containing grid.
		[Arguments]
			grid (lits[str]): List of strings, each one corresponding to a grid row with all comma separated elements.
			*dynamicType (bool): Convert elements to python type automatically.
			*noneEmpty (bool): Set empty values to None.
			*sep (str): Element separator.
			*listSep (str/None): A separator to identify elements that belong to a list.
		'''
		grid = [row.strip().split(sep) for row in grid]
		# set empty values to None
		if noneEmpty == True:
			newGrid = []
			for row in grid:
				newRow = []
				for element in row:
					if element == '':
						newRow.append(None)
					else: newRow.append(element)
				newGrid.append(newRow)
			grid = newGrid
		# parse lists
		if listSep != None:
			newGrid = []
			for row in grid:
				newRow = []
				for element in row:
					if len(element.split(listSep)) > 1:
						if element[0] == '[' and element[-1] == ']':
							element = element[1:-1]
						newRow.append(element.split(listSep))
					else: newRow.append(element)
				newGrid.append(newRow)
			grid = newGrid
		# set values type automatically
		if dynamicType == True:
			grid = [dynamicTyped(row) for row in grid]
		return grid

	def _initHeader(self,header):
		'''
		[Description]
			Parse header to create the 'fieldIndex' dict which relates header entries with column index.
			This dict allows to acess grid by header name (field name) as: self.grid[row][self.headerIndex[fieldName]]
		[Arguments]
			header (bool/list[str]):
		'''
		#grid does not have header. Assign header name as colN where N is the column index, e.g. col0,col1,..,colN
		if header == False:
			header = ['col'+str(i) for i in range(len(self.grid[0]))]
		#header is given in first row
		elif header == True:
			header = self.grid.pop(0)
		if len(self.grid) > 0:
			assert(len(header) == len(self.grid[0]))
		self.fieldIndex = dict([(item,i) for i,item in enumerate(header)])
		self._header = header

	def _field(self,field):
		'''
		Return all values of a given field (full column).
		'''
		if type(field) == str: field = self.fieldIndex[field]
		return [row[field] for row in self.grid]

	@property
	def header(self):
		'''
		Header contains column names.
		'''
		return deepcopy(self._header)

	@header.setter
	def header(self, newHeader):
		'''
		Header setter updates header, fieldIndex dict and GridRows header.
		'''
		self._header = newHeader
		self.fieldIndex = dict([(item,i) for i,item in enumerate(newHeader)])
		for row in self:
			row.header = newHeader

	def bounds(self,field):
		'''
		Returns the bounds of a given field as a tuple (min,max).
		'''
		return min(self._field(field)),max(self._field(field))

	def copy(self):
		'''
		Return copy of grid.
		'''
		return deepcopy(self)

	def dynamicTyped(self):
		'''
		Guess the grid type of each grid entry.
		'''
		self.header = [dynamicTyped(k) for k in self.header]
		for i,j in enumerate(self.grid):
			self.grid[i] = GridRow([dynamicTyped(k) for k in self.grid[i]],self.header)
		#recreate fieldIndex dict with corrected types
		self._initHeader(self.header)

	def fieldRange(self,field):
		'''
		Return all different values of a given field.
		Field can be specified by column index or name.
		'''
		vals = []
		for val in self._field(field):
			if val not in vals: vals.append(val)
		return vals

	def round(self,precision):
		'''
		Return a copy of self.grid with numeric elements in GridRows rounded to specified precision.
		'''
		return [row.round(precision) for row in self.grid]

	def save(self,path,columns=None,header=True,listSeparator=';'):
		'''
		[Description]
			Save grid to file in csv format.
		[Arguments]
			path (str): Path to save file.
			*columns (list[str]/slice): Columns to save. By default all columns are saved.
			*header (bool): Include header.
			*listSeparator (bool): Separator for lists.
		'''
		if columns != None:
			gridToSave = self[columns]
		else:
			gridToSave = self
		sep = ','
		append = '\n'
		aFile = open(path,'w+')
		if header == True:
			gridToSave = [gridToSave.header]+gridToSave.grid
		else:
			gridToSave = gridToSave.grid
		for i,line in enumerate(gridToSave):
			parsedLine = []
			#check if item is a list and parse it accordingly to avoid quote marks.
			for item in line:
				if type(item) == list:
					parsedLine.append('['+listSeparator.join([str(i) for i in item])+']')
				else:
					parsedLine.append(str(item))
			parsedLine[-1] += append
			aFile.write(sep.join(parsedLine))
		aFile.close()

	def shape(self):
		'''
		Return nRows x nCols.
		'''
		return (len(self.grid),len(self.grid[0]))

	def sort(self,field,reverse=False):
		'''
		Sort grid by given field.
		Field can be given as header name or index.
		'''
		field = self.fieldIndex[field]
		self.grid.sort(key=lambda x:x[field],reverse=reverse)

	def head(self,nRows=4):
		'''
		Unix-like command, shows the first 5 rows of grid.
		'''
		for row in self.grid[0:nRows]:
			print row

	def tail(self):
		'''
		Unix-like command, shows the last 5 rows of grid.
		'''
		for row in self.grid[-4:]:
			print row

	# transform

	def asGridFrame(self):
		'''
		Returns a pandas.GridFrame representation of Grid
		'''
		pass

	def asJson(self,roundFloats=None):
		'''
		Return Grid in json format as:
			gridAsJson = [
							{'row':i,'TWS':10,'TWA':45,'Vs':12,...},
							{'row':i,'TWS':10,'TWA':45,'Vs':12,...},
							{'row':i,'TWS':10,'TWA':45,'Vs':12,...}
						]
					
		'''
		gridAsJson = []
		if roundFloats == None:
			gridAsJson = [row.asDict() for row in self]
		else:
			gridAsJson = [row.round(roundFloats).asDict() for row in self]
		return gridAsJson

	def asList(self):
		'''
		Return a list representation of Grid.
		'''
		return [gridrow.elements for gridrow in self]

	# row (GridRow) manipulation

	def index(self,row,reverse=False):
		'''
		Returns the index of a given row.
		If there are duplicates, only the first one found is returned.
		'''
		if reverse == False:
			for i,j in enumerate(self.grid):
				if j == row:
					return i
		else:
			for i,j in enumerate(reversed(self.grid)):
				if j == row:
					return i			

	def match(self,gridRow,fill_value=None):
		'''
		[Description]
			Match the entries of a GridRow header with the Grid header.
			Missing fields are populated with fill_value.
		[Arguments]
			gridRow (GridRow): GridRow to be matched to Grid.
			*fill_value (None/misc): Value to set missing fields at. 
		'''
		# compare to self.header and add missing header entries to GridRow header.
		for i,field in enumerate(self.header):
			if field not in gridRow.header:
				gridRow[field] = fill_value
		# modify self.header and set new columns to fill_value for the rest of GridRows.
		for i,field in enumerate(gridRow.header):
			if field not in self.header:
				print '[Grid|match]: Adding header',field
				self.addColumn(field,fill_value)
		# sort GridRow header to match Grid header order.
		tmp = dict(zip(gridRow.header,gridRow.elements))
		gridRow.header = sorted(gridRow.header,key=self.header.index)
		gridRow.elements = [tmp[header] for header in gridRow.header]

	def removeNone(self):
		'''
		Remove rows with None values.
		'''
		return Grid([row.elements for row in self.grid if None not in row.elements],header=self.header)

	def removeRow(self,index):
		'''
		Remove row by index.
		'''
		self.grid.pop(index)

	def row(self,index):
		'''
		Return GridRow by index
		'''
		return self.grid[index]

	def replace(self,old,new,fill_value=0.0):
		'''
		[Description]
			Replace GridRow with a new one.
		[Arguments]:
			old (index/GridRow): GridRow to replace of index in self.grid.
		'''
		if isinstance(new,GridRow):
			#match headers
			self.match(new,fill_value)
			#add row to grid. This raises ERROR if index is not found.
			if type(old) != int: old = self.index(old)
			self.grid[old] = new
			# print 'Warning [Grid.replace]: Grid could not find', old
		#if a list is given directly, assume both headers match
		elif isinstance(new,list):
			self.grid[self.index(old)] = GridRow(new,self.header)
		else:
			print '[Grid|replace]: '+type(new)+' replacement not implemented yet'

	# column (field) manipulation

	def addColumn(self,newHeaderEntry,newValue=None,newIndex=-1):
		'''
		[Description]
			Adds a new column to grid.
		[Arguments]
			newHeaderEntry (str):
			*newValue (list/callable/other): Value of new column rows specified as:
												List --> Assumes each element corresponds to one row.
												Callable --> A function that is given each row and returns the new value.
												Other --> Fixed value for all columns (can be Float, String, Bool, None, etc).
			*newIndex (int/str): Position to insert new column. If a field name is given, the column will be moved to its position.
									Set to -1 for appending as last element
		'''
		# create new field
		self[newHeaderEntry] = newValue
		# move to desired position
		if newIndex != -1:
			self.moveColumn(newHeaderEntry, newIndex)			

	def removeColumn(self,fields):
		'''
		Removes column (or columns) from grid.
		'''
		if type(fields) != list:
			fields = [fields]
		for field in fields:
			#delete field from each GridRow
			for row in self.grid:		
				row.pop(field)
			#update header
			index = self.header.index(field)
			newHeader = self.header
			newHeader.pop(index)
			self.header = newHeader

	def moveColumn(self,field,newIndex):
		'''
		[Description]
			Move column to new position.
		[Arguments]
			field (str): Field name of column to move.
			newIndex (int/str): Position to move column. If a field name is given, the column will be moved to its current position.
		'''
		if type(newIndex) == str:
			newIndex = self.header.index(newIndex)
		# update rows
		for row in self:
			row.moveField(field,newIndex)
		# update Grid header with a gridrow header
		self.header = row.header

	def renameColumn(self,oldName,newName):
		'''
		Rename field.
		'''
		self.header[self.header.index(oldName)] = newName
		for row in self:
			row.header[row.header.index(oldName)] = newName

	# filters

	def filter(self,filters,rule=None):
		'''
		[Description]
			Retruns a subset of the grid that satisfies the given filters.
		[Arguments]
			filters (dict): Filters (see _filter_value, _filter_function and _filter_expression for details).
			rule (None/str): Set to OR for filtering in points that pass ANY of the filters.
								Set to AND for filtering in points that pass ALL of the filters.
								Set to None for using defaultFilterRule.
		'''
		if rule == None:
			rule = self.defaultFilterRule
		#ensure filters values are lists
		for key in filters:
			if type(filters[key]) != list:
				filters[key] = [filters[key]]
		#determine filter type
		filterSample = filters[filters.keys()[0]][0]
		if type(filterSample) == str:
			#check if filter is value or expression
			if filterSample[0] == '>' or filterSample[0] == '<' or filterSample[0:2] == '!=':
				filterFunc = '_filter_expression'
			else:
				filterFunc = '_filter_value'
		elif callable(filterSample):
			filterFunc = '_filter_function'
		else:
			filterFunc = '_filter_value'
		#
		if rule == 'OR':
			return self.__getattribute__(filterFunc)(filters)
		elif rule == 'AND':
			for i,afilter in enumerate(filters):
				if i == 0:
					grid = self.__getattribute__(filterFunc)({afilter:filters[afilter]})
				else:
					grid = grid.__getattribute__(filterFunc)({afilter:filters[afilter]})
			return Grid(grid.asList(),header=self.header)

	def _filter_value(self,filters):
		'''
		[Description]
			Retruns a subset of the grid that matches the given value.
		Arguments:
			filters (dict): Filters defined as {field1/index:[value1, value2, value3], field2/index:[value1]}.
		'''
		#filter grid
		filteredGrid = []
		for row in self.grid:
			exit = False
			i = 0
			while i < len(filters) and exit == False:
				field = filters.keys()[i]
				for val in filters[field]:
					if row[field] == val:
						filteredGrid.append(row.elements)
						exit = True
				i += 1
		return Grid(filteredGrid,header=self.header)

	def _filter_function(self,funcs,*args):
		'''
		[Description]
			Retruns a subset of the grid that satisfiess the given functions.
		[Arguments]:
			funcs (dict['funcs':[funcs],'args':[args]]): List of functions. Functions are given GridRows and should return True
														if row is to be kept.
			funcs (list[funcs]):
			*args (list[misc]):
		'''
		if type(funcs) == dict:
			args = funcs.get('args',[])
			funcs = funcs['funcs']
		filteredGrid = []
		for row in self.grid:
			for func in funcs:
				if func(row,*args) == True:
					filteredGrid.append(row.elements)
					break
		return Grid(filteredGrid,header=self.header)

	def _filter_expression(self,filters):
		'''
		[Description]
			Returns a subset of the grid that satisfies the given expressions.
		[Arguments]
			filters (dict): {field/index:[expressions]}. Expressions are strings to be concatenated with
								grid row field value to produce an expression that is evaluated.
								E.g. expression = '<5' and corresponding grid row value = 10 will yield 10<5 which
								would return False and therefore such row would not be appended to filtered grid.
		'''
		#filter grid
		filteredGrid = []
		for row in self.grid:
			exit = False
			i = 0
			while i < len(filters) and exit == False:
				field = filters.keys()[i]
				for expression in filters[field]:
					if eval(str(row[field])+expression) == True:
						filteredGrid.append(row.elements)
						exit = True
				i += 1
		return Grid(filteredGrid,header=self.header)

	# plotting

	def plot_2d(self,xFields,yFields,*args,**kwargs):
		'''
		[Description]
			Basic 2d line plot of given fields.
		[Arguments]
			xFields (list[str]/str): Name of field (or list of field names) to use as X values.
			yFields (list[str]/str): Name of field (or list of field names) to use as Y values.
			*args (misc): Args passed to pyVeo.basic2D()
			**kwargs (misc): Kwargs passed to pyVeo.basic2D()
			->return (matplotlib.ax): Matplotlib figure axes.
		'''
		from pyVeo import pyVeo
		if type(xFields) != list:
			xFields = [xFields]
		if type(yFields) != list:
			yFields = [yFields]
		xFields = [self[field] for field in xFields]
		yFields = [self[field] for field in yFields]
		return pyVeo.basic2D(xFields,yFields,*args,**kwargs)

	def plot_contour(self,xField,yField,zField,*args,**kwargs):
		'''
		[Description]
			Basic contour plot of given fields.
		[Arguments]
			xField (str): Name of field to use as X values.		
			yField (str): Name of field to use as Y values.
			zField (str): Name of field to use as Z values.			
			*args (misc): Args passed to pyVeo.contour()
			**kwargs (misc): Kwargs passed to pyVeo.contour()
			->return (matplotlib.ax): Matplotlib figure axes.
		'''
		from pyVeo import pyVeo
		return pyVeo.contour(self[xField], self[yField], self[zField],*args,**kwargs)

	def plot_3d(self,xField,yField,zField,*args,**kwargs):
		'''
		[Description]
			Basic 3D plot of given fields.
		[Arguments]
			xField (str): Name of field to use as X values.		
			yField (str): Name of field to use as Y values.
			zField (str): Name of field to use as Z values.
			*args (misc): Args passed to pyVeo.basic3D()
			**kwargs (misc): Kwargs passed to pyVeo.basic3D()
			->return (matplotlib.ax): Matplotlib figure axes.
		'''
		from pyVeo import pyVeo
		return pyVeo.basic3D(self[xField], self[yField], self[zField],*args,**kwargs)

if __name__ == '__main__':

	import os
	path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'tests','grid-samples','simulation.csv')

	grid = Grid(path)

	# move colmun
	"""
	print grid[0]
	print grid[0].header
	print grid.header
	grid.moveColumn('free', 'TWA')
	print grid[0]
	print grid[0].header
	print grid.header

	# add column
	print grid[0]
	print grid[0].header
	print grid.header
	grid.addColumn('derp')
	print grid[0]
	print grid[0].header
	print grid.header
	"""
	
	print grid.header
	print grid.fieldRange('TWS')
	print grid[{'TWA': grid.fieldRange('TWA')[0]}]

	grid[{'TWA':grid.fieldRange('TWA')[0]}].plot_2d('TWS','Vs')

	# #load file
	# pathToGrid = '/home/tomas/MEGA/Work/49er/VPP/results/5DoF.csv'
	# grid = Grid(pathToGrid)

	# # print type(grid['Vs']),grid['Vs']
	# # print type(grid[0]),grid[0]
	# # print type(grid[0:5]),grid[0:5]
	# # print type(grid[[0,1,2,3,4,5]]),grid[[0,1,2,3,4,5]]
	# # print type(grid[lambda row:row['Vs']/0.51444]),grid[lambda row:row['Vs']/0.51444]
	# # print type(grid[['Vs','leeway']]),grid[['Vs','leeway']]

	# print type(grid[{'Vs':'<2.5'}]),grid[{'Vs':'<2.5'}]
	# print type(grid[{'config':'upwind'}]),grid[{'config':'upwind'}][0]
	# print type(grid[{'funcs':lambda row:row['Vs']>2.5}]),grid[{'funcs':lambda row:row['Vs']>2.5}]

	# # dr = grid[0]
	# print dr.header
	# print dr
	# dr.pop('Vs')
	# print dr.header
	# print dr



	# print grid.header
	# grid.removeColumn('Vs')


	#UNIT TESTING
	# #load file
	# pathToGrid = '/home/tomas/Synology/Work/49er/VPP/results/4DoF.csv'
	# grid = Grid(pathToGrid)

	#show grid
	#print grid

	# #show hedaer and first 5 lines
	# print grid.header
	# grid.head()

	#filter by exact value
	#print grid.filter({'TWS':[8.231,6.687]})

	#filter by expression
	# print grid.expressionFilter({'TWS':['>5']})


	# #retrieve gridrow 5 from grid
	# row = grid.grid[5]
	# print row

	# #look for index of previous row
	# print grid.index(row)


	#TEST 2 GROUPING AND PLOTTING
	# #load cases and add column to identyfy them
	# #1
	# pathToGrid = '/home/work/D3084-SKIN-Project/CFD/Singlephase/Skin/results/results.csv'
	# grid1 = Grid(pathToGrid)
	# grid1.sort('AOA')
	# grid1.addColumn('Type', 'Skin')
	# #2
	# pathToGrid = '/home/work/D3084-SKIN-Project/CFD/Singlephase/Flat/results/results.csv'
	# grid2 = Grid(pathToGrid)
	# grid2.sort('AOA')
	# grid2.addColumn('Type', 'Flat')
	# #group
	# grid1 + grid2
	# # print grid1

	# #Compare plots
	# # grid1.plot_compare2d('AOA','Cd Monitor: Cd Monitor',['Type','SPEED'])
	# # grid1.plot_compare2d('AOA','Cl Monitor: Cl Monitor',['Type','SPEED'])
	# # ata1.plot_compare2d('AOA','Cl/Cd Monitor: Cl/Cd Monitor',['Type','SPEED'])
	# # grid1.plot_compare2d('AOA','Cl2/Cd Monitor: Cl2/Cd Monitor',['Type','SPEED'])

	# #Multiple compare plot
	# plots = [
	# 		{'func':grid1.plot_compare2d,'args':['AOA','Cd Monitor: Cd Monitor',['Type','SPEED']]},
	# 		{'func':grid1.plot_compare2d,'args':['AOA','Cl Monitor: Cl Monitor',['Type','SPEED']]},
	# 		{'func':grid1.plot_compare2d,'args':['AOA','Cl/Cd Monitor: Cl/Cd Monitor',['Type','SPEED']]},
	# 		{'func':grid1.plot_compare2d,'args':['AOA','Cl2/Cd Monitor: Cl2/Cd Monitor',['Type','SPEED']]}
	# 	]
	# pyVeo.smartSubplots(plots)

	#contour plot
	#grid1.plot_contour('AOA', 'SPEED', 'Cd Monitor: Cd Monitor')

	#3D plot
	# grid1.plot_3d('AOA', 'SPEED', 'Cd Monitor: Cd Monitor')
	# plt.close()



	# dr = GridRow([5,9,10], ['a','b','c'])

	# h = dr.header

	# print h

	# h[0] = 5

	# print h
	# print dr.header
