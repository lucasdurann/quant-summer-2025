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