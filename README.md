# CE-UY 3013 Final Project

## Reinforced Concrete Footing Design Aid

### Project Purpose

This project is meant as a design aid for reinforced concrete footings, and 
can be used by students and professionals alike. (K, fine. Not really for 
professionals, but it sounded good). The project consists of a 
[source.py](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/source.py)
file, which packages all three classes used in the 
[ex1.py](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/ex1.py)
script, (said ex1.py file), and 
[this](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/input/ex1.json)
json file. To run this program, download this
[GitHub repository](https://github.com/aryeludmir/ceuy3013-final-project--footings.git),
follow the guidelines below when inputting the data, and run the command `python ex1.py`-
*make sure you're in the project directory*. 
<br />
<br />
*Note this program does not have any external dependencies. All you need is the
GitHub repository this README.md is part of.*

#### Input
To use this program, simply modify
[ex1.json](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/input/ex1.json)
to reflect the given data. ***This JSON file must have this same name and filepath:*** `input/ex1.json`.
(Unless of course you change the script file
[ex1.py](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/ex1.py)).
<br />
<br />
***The input must have the same syntax currently in `ex1.json`:***
<br />
```python
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
```
The order of the above dictionary, as well as the input values, need not 
be the same, but all the *keys* seen above must be included. Adding your
own keys won't affect the program's functionality, but it won't do anything either.
Here is a description of the user input:
<br />
<br />
`"id"` is simply meant to make it easy for the user to identify
which column is being designed. <br />
`"ftng_type"` is the footing type. The two possible inputs are
`"wall"` and `"column"`. <br />
`"width"` is the width if the wall or column in inches. Note that
for both walls *and* columns there is only one dimension input. *This
program only works for square cloumns*.<br />
`"dead_load"` and `"live_load"` are just that. For walls they're in 
kips/ft of wall, for columns they are just in kips.<br />
`"conc_type"` is the concrete type. The three possible inputs are 
`"nw"`, `"lw"` and `"s_lw"`, for normal-weight, lightweight, and sand-lightweight
concrete respectively. This is optional and the default value is `"nw"`.<br />
`"w_c"` and `"w_e"` are the densities of concrete (w_c) and earth (w_e) in pcf.
These are optional with default values of `150` and `100` pcf respectively.<br />
`"f_c"`, is the concrete compressive strength in psi. <br />
`"grade"` is the reinforcing steel grade. <br />
`"a_s_p"` ia the allowable soil pressure in psi. <br />
`"bottom_of_ftng"` is the bottom of the footing relative to 
the earth's surface in ft. This is optional with a defaukt value of `4` ft. <br />
`"wall_type"`. This only needs to have a value (other than null) if we are 
dealing with a wall footing. The two possible values are `"concrete"` and `"masonry"`. <br />
***NOTE*** that if nothing is entered for `"wall_type"` and it is a wall
footing design, the program will crash. This is not a robust program. It relies
on the user to input proper data. <br />

#### Output
### Limitations
The program has many limitations only some of which are mentioned here.
