# Daty v1.0
Data manipulation toolbox.

## Dependancies
- Matplotlib (optional, for easy plotting).
- Numpy (optional, for easy plotting).
- Scipy (optional, for plotting splines).

## Usage Guide: Grid
#### Basics
- Initialize Grid:
```python
# Read from csv file (data types (list, str, float, bool and None) will be assigned automatically):
grid = Grid(pathToFile)
# or, initialize direct from list of lists:
grid = Grid(some_list_of_lists)
# or, initialize emtpy with a header:
grid = Grid([],['speed','leeway','Total_Fx','Total_Fy'])
```
- Get data info:
```python
print grid.header               # Data header (column names).
print len(grid)                 # Number of rows.
print grid.shape()              # Number of rows x Number of columns.
print grid.head()               # Grid first 4 rows (can pass any other number of rows as argument).
print grid.tail()               # Grid last 4 rows (can pass any other number of rows as argmuent).
print grid.bounds('Total_Fx')   # Min anx max bounds of 'Total_Fx' field (column).
print grid.fieldRange('speed')  # All distinct values of 'speed' field (column).
```
#### Querying data
- Get grid fields (columns):
```python
grid['Total_Fx']                # List with all "Total_Fx" column values.
grid['speed':'Total_Fx']        # List of lists with all column values of fields "speed" to "Total_Fx".
grid[['Total_Fx','Total_Fy']]   # List of lists with all "Total_Fx" and "Total_Fy" column valuess.

```
- Get grid rows:
```python
grid[2]         # 3rd grid row.
grid[1:10]      # 1st to 10th rows (list).
grid[[1,3,8]]   # 1st, 3rd and 8th rows (list).
```
- Note that all grid rows are GridRow objects, which are similar to OrderedDicts but with some additional methods: 
```python
some_row = grid[2]
some_row['Total_Fx']      # Access "Total_Fx" value.
some_row.values()         # Get all row values as a list.
some_row.keys()           # Get all row fields as a list.
some_row.pop('Total_Fx')  # Remove field field from row (does not affect original Grid).
some_row.round(2)         # Row values with floats rounded to 2 decimal places.
some_row.asDict()         # OrdereDict equivalent of row.

```
#### Filtering data
- Grid rows can be filtered using curly brakets {}:
```python
grid[{'Total_Fx':'5'}]                                              # Get rows that match a specific value for one of its columns.
grid[{'Total_Fx':'<5'}]                                             # Get rows that are smaller than a specific value for one of its columns.
grid[{'funcs':lambda row:row['Total_Fx']+row['Total_Fy'] > 1000}]   # Get rows that return True to the given filtering function:
```
- Filtering operations return a Grid object, therefore filters can be concatenated:
```python
grid[{'Total_Fx':'10'}]grid[{'Total_Fx':'>2'}][{'funcs':lambda row:row['Total_Fx']+row['Total_Fy'] > 1000}]
```
#### Adding data to grid
```python
grid['new_column'] = 0                                                  # Add a new column with all values set to 0.
grid['new_column'] = a_list_of_values                                   # Add a new column with a list of values.
grid['new_column'] = lambda row: (row['Total_Fy'] + row['Total_Fz'])**2 # Add a new column by combining the values of other columns.
```
#### Plotting (requires Matplotlib and Numpy).
- Basic plotting capabilities are provided:
```python
gird.plot_line('speed','Total_Fx')              # Line plot
gird.plot_contour('speed','leeway','Total_Fx')  # 2D Contour plot
gird.plot_surface('speed','leeway','Total_Fx')  # 3D Surface plot
```
- It is also possible to plot on an existing matplotlib plot:
```python
ax = plt.figure().gca()
gird.plot_line('speed','Total_Fx',ax=ax) # Line plot
```
- Plotting functions take several arguments to control formatting (see pyVeo):
```python
gird.plot_line('speed','Total_Fx',title='Force [N]',color='r',marker='o',splineDensity=100) # Line plot
```

## Usage Guide: SmartJson
#### Basics
- Initialize SmartJson:
```python
# Initialize from folder structure:
sjson = SmartJson(pathToFolder)
# or, initialize from JSON file:
sjson = Grid(pathToFile)
```