<<<<<<< HEAD
# Automatic Image Difference Comparison Tool

## How to Run

### Necessary Library Installation
To get started, proceed with installing the following utilizing the package manager [pip](https://pip.pypa.io/en/stable/installation/). See documentation here.
```bash
pip install Pillow matplotlib opencv-python numpy pandas tkinter os
```

### Inputs for Program
```python
#designate file path for the two file directories
images1 = ' '
images2 = ' '

#Utilizing findROI.ipynb, designate necessary coordinates for different zones as needed. Example provided below.
zones = {
  'Time': [900, 1024, 0, 50], #input col1, col2, row1, row2
  'Version': [785, 900, 0, 50],
  'Language': [0, 200, 0, 50],
  'Entire Image': [0, 1024, 0, 768] 
} 
```

### Command to Run
Go to your current directory and provide the following line in the terminal.

```bash
python imageComparison.py
```

## Output/Result
With the following inputs, we can visualize the zones defined above in the output image **example zone.png**. 

![alt text](https://github.com/ryanrae7/ImageComparison/blob/9413647d9bde4f56dfebce53186bc1e672cb65e1/example%20zone.png)

Observe the file **Zone.xlsx** to get data outputs for the percentage differences in each zone and the name of the files that it is exported. For the output overlay comparison, observe the **downloads** folder in your file directory to see the outputs.

## License
[MIT](https://mit-license.org/)
=======
# Automatic Image Difference Comparison Tool

## How to Run

### Necessary Library Installation
To get started, proceed with installing the following utilizing the package manager [pip](https://pip.pypa.io/en/stable/installation/).
```bash
pip install Pillow matplotlib opencv-python numpy pandas tkinter os
```

### Inputs for Program
```python
#designate file path for the two file directories
images1 = ' '
images2 = ' '

#Utilizing findROI.ipynb, designate necessary coordinates for different zones as needed. Example provided below.
zones = {
  'Time': [900, 1024, 0, 50], #input col1, col2, row1, row2
  'Version': [785, 900, 0, 50],
  'Language': [0, 200, 0, 50],
  'Entire Image': [0, 1024, 0, 768] 
} 
```

### Command to Run
Go to your current directory and provide the following line in the terminal.

```bash
python imageComparison.py
```

## Output/Result
With the following inputs, we can visualize the zones defined above in the output image **example zone.png**. 

![alt text](https://github.com/ryanrae7/ImageComparison/blob/9413647d9bde4f56dfebce53186bc1e672cb65e1/example%20zone.png)

Observe the file **Zone.xlsx** to get data outputs for the percentage differences in each zone and the name of the files that it is exported. For the output overlay comparison, observe the **downloads** folder in your file directory to see the outputs.

## License
[MIT](https://mit-license.org/)
>>>>>>> 4edcf9904c38a51fa6fa363a68de848cd5f1a8b3
