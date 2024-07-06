# %% --- header ---

# author: sheila saia
# date created: 2024-07-05
# email: sheila.saia@tetratech.com

# script name: 00_functions.py

# script description: this script contains functions needed to run the 
# plet module

# to do:

# %% --- plet module functions ----

# precipitation
def calc_p(aa_rain, r_cor, rain_days, rd_cor):
    '''
    description:
    calculate rainfall per event (p) in units of inches.

    parameters:
        aa_rain (float): average annual rainfall (inches)
        r_cor (float): rainfall correction factor
        rain_days (float): average number of rainy days per year
        rd_cor (float): rain day correction factor

    returns:
        p(float): rainfall per event (inches)
    '''
    # calculate p
    p = (aa_rain * r_cor)/(rain_days * rd_cor)

    # return
    return p

# potential maximum water retention after runoff begins
def calc_s(cn):
    '''
    description:
    calculate the potential maximum water retention after runoff 
    begins (inches)

    parameters:
        cn (int): curve number for specific land cover/land use and
        it's associated condition (e.g., good or poor)

    returns:
        s (float): potential maximum water retention after runoff 
        begins (inches)
    '''
    # calculate p
    s = (1000/cn) - 10

    # return
    return s

# runoff
def calc_q(p, s):
    '''
    description:
    calculate runoff (inches/day)

    parameters:
        p (float): rainfall per event (inches), see calc_p function
        s (float): potential maximum water retention after runoff 
        begins (inches), see calc_s function

    returns:
        q (float): runoff (inches/day)
    '''
    # calculate p
    q = (p**2)/(p + s)

    # return
    return q

# irrigation runoff (q_irr)
# hold off on this for now until verify with esmc that it's needed

# baseline runoff volume
def calc_base_runoff_v(q, area, rain_days, rd_cor):
    '''
    description:
    calculate baseline condition runoff volume (acre-feet)

    parameters:
        q (float): runoff (inches/day), see calc_q function
        area (float): area of field (acres)
        rain_days (float): average number of rainy days per year
        rd_cor (float): rain day correction factor

    returns:
        b_run_v (float): runoff volume (acre-feet)
    '''
    # calculate p
    b_run_v = (q/12) * area * (rain_days * rd_cor)

    # return
    return b_run_v

# baseline irrigation runoff volume (b_irr_v)
# hold off on this for now until verify with esmc that it's needed

# baseline groundwater infiltration volume
def calc_base_gw_v(inf_frac, p, area, rain_days, rd_cor):
    '''
    description:
    calculate baseline shallow groundwater infilatration
    volume (acre-feet)

    parameters:
        inf_frac (float): infiltration fraction
        p (float): rainfall per event (inches), see calc_p function
        area (float): area of field (acres)
        rain_days (float): average number of rainy days per year
        rd_cor (float): rain day correction factor

    returns:
        b_in_v (float): baseline shallow groundwater infilatration
        runoff volume (acre-feet)
    '''
    # infiltration depth
    infil = inf_frac * p
    
    # baseline groundwater infiltraiton volume
    b_in_v = (infil/12) * area * (rain_days, rd_cor)

    # return
    return b_in_v

# baseline runoff nutrient load (for n or p)
def calc_base_run_nl(b_run_v, nm, conc, conc_m):
    '''
    description:
    calculate baseline annual runoff nutrient load (lbs), can be used 
    to calculate nutrient load for either nitrogen or phosphorus and for
    either cropped land or grazed land/pastureland

    parameters:
        b_run_v (float): runoff volume (acre-feet)
        nm (float): number of months manure is applied
        conc (float): concentration of the nutrients (either nitrogen or
        phosphorus) in runoff *not* during manure application
        conc_m (float): concentration of the nutrients (either nitrogen
        or phosphorus) in runoff *during* manure application

    returns:
        b_run_nl (float): baseline annual runoff load for *either* 
        nitrogen or phosphorus (lbs)
    '''
    # baseline runoff nutrient load
    b_run_nl = b_run_v * ((1 - (nm/12)) * conc + (nm/12) * conc_m) * (4047 * 0.3048/1000 * 2.2)
    # this can be calculated individually for nitrogen and phosphorus

    # return
    return b_run_nl

# sediment loss
def calc_e(r_fact, k_fact, ls_fact, c_fact, p_fact, area):
    '''
    description:
    calculate sediment loss due to sheet and rill erosion (tons/year)

    parameters:
        r_fact (float): RUSLE rainfall factor
        k_fact (float): RUSLE soil erodibility factor
        ls_fact (float): RUSLE topographic factor
        c_fact (float): RUSLE cropping management factor
        p_fact (float): RUSLE erosion control practice factor
        area (float): area of field (acres??)

    returns:
        erosion (float): sediment loss due to sheet and rill 
        erosion (tons/year)
    '''
    # sediment erosion
    erosion = r_fact * k_fact * ls_fact * c_fact * p_fact * area

# baseline runoff sediment load
def calc_base_run_sl(erosion, area):
    '''
    description:
    calculate baseline sediment loss in runoff due to sheet and rill
    erosion (tons/year)

    parameters:
        erosion (float): sediment loss due to sheet and rill 
        erosion (tons/year), see calc_e function
        area (float): area of field (acres??)

    returns:
        b_run_sl (float): baseline sediment loss in runoff due to
        sheet and rill erosion (tons/year)
    '''
    # area cutoff
    area_cutoff = 200 # acres?? - check units!

    # sediment delivery ratio
    # if less than area_cutoff
    if area <= area_cutoff:
        del_ratio = 0.42 * area**(-0.125)
        
    # else if greater than area_cutoff
    else:
        del_ratio = (0.417662 * area**(-0.134958)) - 0.127097

    # sediment erosion
    b_run_sl = erosion * del_ratio

    # return
    return b_run_sl




