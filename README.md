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
follow the guidelines below when inputting the data, and run the command `python ex1.py`. 
<br />
<br />
*Note this program does not have any external dependencies. All you need is the
GitHub repository this README.md is part of.*

#### Input
To use this program, simply change the inputs of
[ex1.json](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/input/ex1.json)
to reflect the given data.
<br />
<br />
***This json file must remain in the input folder it is currently in.***
(Unless you change the script file, 
[ex1.py](https://github.com/aryeludmir/ceuy3013-final-project--footings/blob/main/ex1.py)).
<br />
<br />
***The input must have the same syntax as the following:***
<br />
```python
{
        "id": "col_175_175_7",
        "ftng_type": "column",
        "width": 18.0,
        "dead_load": 175.0,
        "live_load": 175.0,
        "conc_type": "nw",
        "w_c": 150.0,
        "w_e": 100.0,
        "f_c": 3000.0,
        "grade": 60,
        "a_s_p": 5000.0,
        "bottom_of_ftng": 4.0,
        "wall_type": null,
        "width_restriction": 7.0,
        "col_loc": "interior",
        "precision": 0.5
    }
```
#### Output
### Limitations
The progrm has many limitations only some of which are mentioned here.
