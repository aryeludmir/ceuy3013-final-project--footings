# CE-UY 3013 Final Project

## Reinforced Concrete Footing Design Aid

### Project Purpose

This project is meant as a design aid for reinforced concrete footings, and 
can be used by students and professionals alike. (K, fine. Not really for 
professionals, but it sounded good). The project consists of a 
[`source.py`](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/source.py)
file, which packages all three classes used in the 
[`ex1.py`](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/ex1.py)
script, (said ex1.py file), and 
[this](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/input/ex1.json)
JSON file. To run this program, download [this
GitHub repository](https://github.com/aryeludmir/ceuy3013-final-project--footings.git),
follow the guidelines below when inputting the data, and run the command `python ex1.py`-
*make sure you're in the project directory*. 
<br />
<br />
*Note this program does not have any external dependencies. All you need is the
GitHub repository this README.md is part of.*

#### Input
To use this program, simply modify
[`ex1.json`](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/input/ex1.json)
to reflect the given data. ***This JSON file must have this same name and filepath:*** `input/ex1.json`.
(Unless of course you change the script file
[`ex1.py`](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/ex1.py)).
<br />
<br />
***The input must have the same syntax currently in `ex1.json`:***
<br />
```python
[
    {
        "id": "col_175_175_7",
        "ftng_type": "column",
        "width": 18.0, # inches
        "dead_load": 175.0, # kips for column, kips/ft for walls
        "live_load": 175.0, # kips for column, kips/ft for walls
        "conc_type": "nw", # optional; default value is "nw"
        "w_c": 150.0, # pcf; optional; defualt value 150.0
        "w_e": 100.0, # pcf; optional; defualt value 100.0
        "f_c": 3000.0, # psi
        "grade": 60,
        "a_s_p": 5000.0, # psi
        "bottom_of_ftng": 4.0, # ft; optional; defualt value 4
        "wall_type": null, # only applicable to walls
        "width_restriction": 7.0, # ft; only applicable to columns
        "col_loc": "interior", # optional; default value "interior"
        "precision": 0.5 # optional
    }
]
```
The order of the above dictionary, as well as the input values, need not 
be the same, but all the *keys* seen above must be included. Adding your
own keys won't affect the program's functionality, but it won't do anything either.
The is no limit to the amount of dictionaries (separate footing design criteria) 
that can be placed in the list.
<br />
<br />
Here is a description of the user input:
<br />
* `"id"` is simply meant to make it easy for the user to identify
which column is being designed.
* `"ftng_type"` is the footing type. The two possible inputs are
`"wall"` and `"column"`.
* `"width"` is the width of the wall or column in ***inches***. Note that
for both walls *and* columns there is only one dimension input. *This
program only works for square cloumns*.
* `"dead_load"` is in ***kips/ft*** of wall for wall footings, and ***kips***
 for column footings.
* `"live_load"` is in ***kips/ft*** of wall for wall footings, and ***kips***
for column footings.
* `"conc_type"` is the concrete type. The three possible inputs are 
`"nw"`, `"lw"` and `"s_lw"`, for normal-weight, lightweight, and sand-lightweight
concrete respectively. This is optional and the default value is `"nw"`.
* `"w_c"` is the density of concrete in ***pcf***. This is optional with default 
 value of 150.0.
* `"w_e"` is the density of earth in ***pcf***. This is optional with default 
 value of 100.0.
* `"f_c"`, is the concrete compressive strength in ***psi***.
* `"grade"` is the reinforcing steel grade.
* `"a_s_p"` is the allowable soil pressure in ***psi***.
* `"bottom_of_ftng"` is the bottom of the footing relative to 
the earth's surface in ***ft***. This is optional with a default value of `4` ft.
* `"wall_type"`. This only needs to have a value (other than null) if we are 
dealing with a wall footing. The two possible values are `"concrete"` and `"masonry"`.
<br />***NOTE***: if nothing is entered for `"wall_type"` and it is a wall
footing design, the program will crash. This is not a robust program. It relies
on the user to input proper data.
* `"width_restriction"` only applies if there is an upper limit to the footing width 
in one direction. If there is, here is where the restriction is input in ***ft***.
* `"col_loc"` is optional. It refers to the column location on the footing. The three 
possible inputs are `"interior"` - this is the default value - `"edge"` and `"corner"`.
* `"precision"` is also optional. There are situations where a user may only 
 want footing dimensions rounded to the nearest quarter-foot, or third-foot. 
 When this is the case, the user will use the `"precision"` key to hold this value.
 So, for the user who wants quarter-foot precision the value would be `0.25`, third-foot precision
 would be `0.33333` (that was an arbitrary amount of decimal places) and so on. The
 default precision is `0.08333333333`, or 1/12 of a foot.

#### Output
For each footing dictionary in `ex1.json` there are two separate outputs.
##### Output 1
The first output will be similar to
[`output.json`](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/output/output.json).
The file will contain a list of footing design dictionaries, one for each footing.
The `key:value` pairs are slightly different for walls and columns. Below is a sample
of a column output 
([click here](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/output/output.json)
for a full sample file including wall footings):
```python
[       
    {
        "id": "col_175_175_7",
        "ftng_dimensions": "11.5 ft x 7.0 ft",
        "ftng_depth": "2.083 ft",
        "minimum_steel_length": "5.998 sq in",
        "minimum_steel_width": "6.21 sq in"
    }
]
```
Note that in the case above, the footing is rectangular, so the minimum steel area
for the length and width are different. In case of a square column, the `keys`
will remain the same even though the length will be the same as the width. For walls,
there will only be one dimension (width), hence there will only be one required steel
`key:value` pair.
##### Output 2
The second output is a text file. Each footing will have its own designated text file
with naming convention `id.txt`. (Say the input had `"id" : "col_200_124"`, the text file for that footing
would be `col_200_124.txt`).<br /> 
This second output goes step by step through the design process. The file indicates
what is being claculated (say, `Calculating effective depth d`) and then prints the value 
(`d = 20 in.`). For a complete example text file, check out 
[col_175_175_7.txt](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/output/col_175_175_7.txt).
<br /> 
<br /> 
Both outputs wil be in the output directory located in the program directory.
### Limitations
The program has many limitations only some of which are mentioned here.
TO DO...
