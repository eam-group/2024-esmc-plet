# %% --- header ---

# author: sheila saia
# date created: 2024-01-14
# email:  sheila.saia@tetratech.com

# script name: wqn_script.py

# script description: wqn calculator excel sheet translated into python

# to do:


# %% --- set up ---

# import libraries
import pandas

# define project path
data_path = "C:/Users/sheila.saia/OneDrive - Tetra Tech, Inc/Documents/github/2024-esmc-plet/data/"

# %% --- read in data ---

# path to data
cn_data_path = data_path + "cn_data.csv"

# read data
# cn_data = pandas.read_csv("data/cn_data.csv") # use relative path
cn_data = pandas.read_csv(cn_data_path)  # use full path

# check data
# cn_data.head()
# cn_data.columns

# %% --- define inputs ---

# unique options
# crop_vals = numpy.unique(cn_data['crop'])
# practice_vals = numpy.unique(cn_data['practice'])
# hydro_cond_vals = numpy.unique(cn_data['hydro_condition'].dropna())
# hsg_vals = numpy.unique(cn_data['hsg'])

# user defined inputs
my_crop_type = "Row Crop"
my_practice = "Straight row"
my_hydro_cond = "Poor"
my_hsg = "C"

# find cn for user defined inputs
sel_data = cn_data[
    (cn_data["crop"] == my_crop_type)
    & (cn_data["practice"] == my_practice)
    & (cn_data["hydro_condition"] == my_hydro_cond)
    & (cn_data["hsg"] == my_hsg)
]

# get cn value
cn_val = sel_data["cn"].iloc[0]

# %% --- make a function to get cn ---


def get_cn_val(cn_data, crop_type, practice, hsg, hydro_cond=None):
    # optional arg: hydro_cond

    # bare soil has no hydro_cond so separate this out
    if practice == "Bare soil":
        # use values to filter cn_data
        sel_data = cn_data[
            (cn_data["crop"] == crop_type)
            & (cn_data["practice"] == practice)
            & (cn_data["hsg"] == hsg)
        ]

    # if not bare soil
    else:
        # use values to filter cn_data
        sel_data = cn_data[
            (cn_data["crop"] == crop_type)
            & (cn_data["practice"] == practice)
            & (cn_data["hydro_condition"] == hydro_cond)
            & (cn_data["hsg"] == hsg)
        ]

    # check size
    if len(sel_data.index) == 1:
        # get cn value
        cn_val = sel_data["cn"].iloc[0]

        # return
        return cn_val

    # if no values then return nan
    else:
        return "NaN"


# %% --- test the function ---

# test the function
# Small Grains,Contoured,Good,B,73
cn_val_1 = get_cn_val(
    cn_data=cn_data,
    crop_type="Small Grains",
    practice="Contoured",
    hydro_cond="Good",
    hsg="B",
)
cn_val_1  # returns 73, checks out!

# test one more time
# Fallow,Bare soil,,D,94
cn_val_2 = get_cn_val(
    cn_data=cn_data, 
    crop_type="Fallow", 
    practice="Bare soil", 
    hsg="D"
)
cn_val_2  # returns 94, checks out!

# %% --- next step here ---

# get initial abstraction (in)
ia_val_inches = (1000 / cn_val) - 10
