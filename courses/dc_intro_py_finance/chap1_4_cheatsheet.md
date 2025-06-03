## Key take-aways (Chapter 1)

* **Python as a calculator** – you can perform basic arithmetic (`+ – * / ** // %`) directly in a code cell; parentheses control order of operations just like on paper.
* **Variables are simply names that point to objects** – assignment (`revenue_1 = 229.23`) stores a value in memory and lets you reuse it; variable names should be lowercase_with_underscores and start with a letter.
* **Core data types matter** – `int`, `float`, `str`, and `bool` each behave differently; use `type(x)` to inspect and `str(…), int(…), float(…)` to convert.
* **Combining data types requires conversion** – concatenating strings and numbers raises `TypeError`; convert numbers with `str()` or use formatted strings (`f"{revenue:.2f}"`) to build readable sentences.
* **The print function is your debugging ally** – `print()` shows intermediate values so you can verify that calculations (e.g., totals or averages) are correct before moving on.

## Key take-aways (Chapter 2)

- **What is a list?**  
  An ordered, mutable sequence that can hold mixed types. 

```python
stocks = ['AAPL', 'MSFT', 'GOOG']
prices = [172.5, 310.0, 128.4]
# Creating Lists
data = [stocks, prices]

# Indexing & Slicing
stocks[0]     # 'AAPL'
stocks[-1]    # last element
stocks[1:3]   # from idx 1 up to (not incl.) 3
prices[:2]    # first two items
prices[::2]   # every other item

# Nested indexing
data[0][1]     # 2nd element of stocks
data[1][2]     # 3rd element of prices

# List methods
# Adding
L.append(x)         # adds one element
L.extend([a, b])    # concatenates another list
L.insert(i, x)      # inserts at index i

# Removing
L.pop()             # removes & returns last
L.pop(i)            # removes & returns at i
L.remove(x)         # removes first occurrence of x
L.clear()           # empties list

# Reordering and copying
L.sort()            # sorts in-place
L.reverse()         # reverses order
L2 = L.copy()       # shallow copy
```

## Key take-aways (Chapter 3)
- **What is a NumPy array?**  
  A fast, fixed-type, multidimensional container for numerical data. It supports vectorized operations and broadcasting.

- **Creating arrays**  
  - `np.array([1, 2, 3])` → create a 1D array  
  - `np.array([[1, 2], [3, 4]])` → create a 2D array  

- **Elementwise operations**  
  - Arithmetic like `array1 / array2` or `array * scalar` applies element by element (broadcasted).  
  - Useful for financial metrics like `price / earnings = PE ratio`.

- **Subsetting (Indexing & Slicing)**  
  - `array[0:3]` → first 3 elements  
  - `array[-3:]` → last 3 elements  
  - `array[::2]` → every other element  
  - `array_2d[:, 0]` → all rows of first column  
  - `array_2d[0, :]` → all columns of first row  

- **Array shape and size**  
  - `array.shape` → returns tuple (rows, columns)  
  - `array.size` → total number of elements  

- **Transposing**  
  - `array.T` or `np.transpose(array)` → flips rows and columns  

- **Generating sequences**  
  - `np.arange(start, stop, step)` → creates evenly spaced values  
  - Example: `np.arange(1, 8, 2)` → `[1, 3, 5, 7]`

- **Statistical functions**  
  - `np.mean(array)` → average  
  - `np.std(array)` → standard deviation  

- **Boolean masking**  
  - `(array > threshold)` → returns boolean array  
  - `array[mask]` → filters array with condition  
  - Example: `prices[prices > prices.mean()]` → select prices above average

## Key take-aways (Chapter 4)
- **matplotlib.pyplot is the standard for plots**
Use import matplotlib.pyplot as plt to unlock Python’s core plotting library.

- **Basic plotting: plt.plot(x, y)**
Creates a line plot from two lists or arrays. Customize with parameters like color=, linestyle=, and marker=.

- **Add labels and titles**
Use plt.xlabel(), plt.ylabel(), and plt.title() to annotate your chart.

- **Plot multiple series**
Just call plt.plot() multiple times before plt.show() to overlay lines.

- **Use plt.scatter() for point plots**
Especially useful when plotting two variables without a connecting trend line.

- **plt.hist() builds histograms**
Visualize distribution with bins= to control granularity and alpha= for transparency in overlaps.

- **Legends clarify data sources**
Use plt.legend() with label= set inside plot calls to distinguish multiple series.