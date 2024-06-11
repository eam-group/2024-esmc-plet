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
cn_lookup_path = data_path + "hydrology/cn_lookup.csv"

# read data
cn_lookup = pandas.read_csv(cn_lookup_path)  # use full path

# check data
# cn_lookup.head()
# cn_lookup.columns

# %% --- define inputs ---

# unique options
# crop_vals = numpy.unique(cn_lookup['crop'])
# practice_vals = numpy.unique(cn_lookup['practice'])
# hydro_cond_vals = numpy.unique(cn_lookup['hydro_condition'].dropna())
# hsg_vals = numpy.unique(cn_lookup['hsg'])

# user defined inputs
my_crop_type = "Row Crop"
my_practice = "Straight row"
my_hydro_cond = "Poor"
my_hsg = "C"

# find cn for user defined inputs
sel_data = cn_lookup[
    (cn_lookup["crop"] == my_crop_type)
    & (cn_lookup["practice"] == my_practice)
    & (cn_lookup["hydro_condition"] == my_hydro_cond)
    & (cn_lookup["hsg"] == my_hsg)
]

# get cn value
cn_val = sel_data["cn"].iloc[0]

# %% --- make a function to get cn ---


def get_cn_val(cn_lookup, crop_type, practice, hsg, hydro_cond=None):
    # optional arg: hydro_cond

    # bare soil has no hydro_cond so separate this out
    if practice == "Bare soil":
        # use values to filter cn_lookup
        sel_data = cn_lookup[
            (cn_lookup["crop"] == crop_type)
            & (cn_lookup["practice"] == practice)
            & (cn_lookup["hsg"] == hsg)
        ]

    # if not bare soil
    else:
        # use values to filter cn_lookup
        sel_data = cn_lookup[
            (cn_lookup["crop"] == crop_type)
            & (cn_lookup["practice"] == practice)
            & (cn_lookup["hydro_condition"] == hydro_cond)
            & (cn_lookup["hsg"] == hsg)
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
    cn_lookup=cn_lookup,
    crop_type="Small Grains",
    practice="Contoured",
    hydro_cond="Good",
    hsg="B",
)
cn_val_1  # returns 73, checks out!

# test one more time
# Fallow,Bare soil,,D,94
cn_val_2 = get_cn_val(
    cn_lookup=cn_lookup, 
    crop_type="Fallow", 
    practice="Bare soil", 
    hsg="D"
)
cn_val_2  # returns 94, checks out!

# %% --- next step here ---

# get initial abstraction (in)
ia_val_inches = (1000 / cn_val) - 10
