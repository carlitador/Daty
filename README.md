# Daty v1.0
Data manipulation toolbox.

## Dependancies
- pyVeo (optional)

## Examples
### Grid
#### Basics
- Read from CSV file:
```python
grid = Grid(pathToFile) # Data types (list, str, float, bool and None) will be assigned automatically.
```
- Initialize from list of lists:
```python
grid = Grid(some_list)
```
- Print header:
```python
print grid.header
```
#### Querying data
- Get a list with all "Total_Fx" column values:
```python
total_fx = grid['Total_Fx']
```
- Get the 3rd grid row:
```python
thrid_row = grid[2]
```
- Note that all grid rows are GridRow objects, which are similar to dicts:
```python
print thrid_row['Total_Fx']
```
#### Filtering data
- Get rows that match a specific value for one of its columns:
```python
important_Fx = grid[{'Total_Fx':'5'}]
```
- Get rows that are smaller than a specific value for one of its columns:
```python
small_Fx = grid[{'Total_Fx':'<5'}]
```
- Get rows that return True to the given filtering function:
```python
some_Fx = grid[{'funcs':lambda row:row['Total_Fx']+row['Total_Fy'] > 1000}]
```
- Note that filtering actions return a Grid object, therefore filters can be concatenated:
```python
some_small_important_Fx = grid[{'funcs':lambda row:row['Total_Fx']+row['Total_Fy'] > 1000}][{'Total_Fx':'<5'}]grid[{'Total_Fx':'5'}]
```
#### Adding data
- Add a new column with all values set to 0:
```python
grid['new_column'] = 0
```
- Add a new column with a list of values:
```python
grid['new_column'] = a_list_of_values # Length of 'a_list_of_values' must match gird length.
```
- Add a new column by combining the values of other columns:
```python
grid['new_column'] = lambda row: (row['Total_Fy'] + row['Total_Fz'])**2
```
#### Plotting (requires pyVeo)
- Line plot:
```python
gird.plot_line('speed','Total_Fx')
```
- 2D Contour plot:
```python
gird.plot_contour('speed','leeway','Total_Fx')
```
- 3D Surface plot:
```python
gird.plot_surface('speed','leeway','Total_Fx')
```