# %% --- header ---

# author: sheila saia
# date created: 2024-07-05
# email: sheila.saia@tetratech.com

# script name: plet_functions.py

# script description: this script contains functions needed to run the 
# plet module

# notes:
# all calculations are assumed to be at an annual timestep
# sediment load is in units of tons
# nutrient load (nitrogen and phosphorous) is in units of lbs
# runoff volumnes (all water quantity stuff) are in units of acre-feet

# to do:


# %% ---- general functions ----
# precipitation
def calc_p(gdf):
    '''
    description:
    calculate rainfall per event (p) in units of inches.

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            aa_rain (float): average annual rainfall (inches)
            r_cor (float): rainfall correction factor
            rain_days (float): average number of rainy days per year
            rd_cor (float): rain day correction factor

    returns:
        p (float): rainfall per event (inches), as a new column in gdf
    '''
    # calculate p
    gdf['p'] = (gdf['aa_rain'] * gdf['r_cor'])/(gdf['rain_days'] * gdf['rd_cor'])

    # return
    return gdf

# potential maximum water retention after runoff begins
def calc_s(gdf):
    '''
    description:
    calculate the potential maximum water retention after runoff 
    begins (inches)

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            cn (int): curve number for specific land cover/land use and
            it's associated condition (e.g., good or poor)

    returns:
        s (float): potential maximum water retention after runoff 
        begins (inches), as a new column in gpf
    '''
    # calculate p
    gdf['s'] = (1000 / gdf['cn_value']) - 10

    # return
    return gdf

# runoff
def calc_q(gdf):
    '''
    description:
    calculate runoff (inches/day)

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            p (float): rainfall per event (inches), see calc_p function
            s (float): potential maximum water retention after runoff 
            begins (inches), see calc_s function

    returns:
        q (float): runoff (inches/day), as a new column in gdf
    '''
    # calculate p
    gdf['q'] = (gdf['p']**2)/(gdf['p'] + gdf['s'])

    # return
    return gdf

# irrigation runoff (q_irr)
# hold off on this for now until verify with esmc that it's needed
# use equation 2 in the user guide but water depth per irrigation (in)
# is used instead of rainfall (P) and annual runoff volume from
# cropland is sum of surface runoff volume and irrigation volume


# %% ---- baseline functions ----
# baseline runoff volume
def calc_base_run_v(gdf):
    '''
    description:
    calculate baseline condition runoff volume (acre-feet)

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            q (float): runoff (inches/day), see calc_q function
        (this depends on calc_p and calc_s functions as well)
            area_ac (float): area of field (acres)
            rain_days (float): average number of rainy days per year
            rd_cor (float): rain day correction factor

    returns:
        b_run_v (float): runoff volume (acre-feet), 
        as a new column in gdf
    '''
    # convert inches to feet
    q_ft = gdf['q']/12

    # calculate p
    gdf['b_run_v'] = q_ft * gdf['area_ac'] * (gdf['rain_days'] * gdf['rd_cor'])

    # return
    return gdf

# baseline irrigation runoff volume (b_irr_v)
# hold off on this for now until verify with esmc that it's needed

# baseline groundwater infiltration volume
def calc_base_gw_v(gdf):
    '''
    description:
    calculate baseline shallow groundwater infilatration
    volume (acre-feet)

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            gw_infil_frac (float): infiltration fraction
            p (float): rainfall per event (inches), see calc_p function
            area_ac (float): area of field (acres)
            rain_days (float): average number of rainy days per year
            rd_cor (float): rain day correction factor

    returns:
        b_in_v (float): baseline shallow groundwater infilatration
        runoff volume (acre-feet), as a new column in gdf
    '''
    # infiltration depth
    infil = gdf['gw_infil_frac'] * gdf['p']

    # convert inches to feet
    infil_ft = infil/12
    
    # baseline groundwater infiltraiton volume
    gdf['b_in_v'] = infil_ft * gdf['area_ac'] * (gdf['rain_days'] * gdf['rd_cor'])

    # return
    return gdf

# baseline runoff nutrient load (for n or p)
def calc_base_run_nl(b_run_v, n_months, conc, conc_m):
    '''
    description:
    calculate baseline annual runoff nutrient load (lbs), can be used 
    to calculate nutrient load for either nitrogen or phosphorus and for
    either cropped land or grazed land/pastureland

    parameters:
        b_run_v (float): runoff volume (acre-feet)
        n_months (float): number of months manure is applied
        conc (float): concentration of the nutrients (either nitrogen or
        phosphorus) in runoff *not* during manure application (mg/L)
        conc_m (float): concentration of the nutrients (either nitrogen
        or phosphorus) in runoff *during* manure application (mg/L)

    returns:
        b_run_nl (float): baseline annual runoff load for *either* 
        nitrogen or phosphorus (lbs)
    '''
    # compute manure fraction
    # (number of months/year that manure is applied)
    m_frac = n_months/12 # 12 months in a year

    # baseline runoff nutrient load
    b_run_nl = b_run_v * ((1 - m_frac) * conc + m_frac * conc_m) * (4047 * 0.3048/1000 * 2.2)
    # this can be calculated individually for nitrogen and phosphorus

    # return
    return b_run_nl

# sediment loss due to erosion
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
    calculate baseline sediment load in runoff due to sheet and rill
    erosion (tons/year)

    parameters:
        erosion (float): sediment loss due to erosion (tons/year), 
        see calc_e function
        area (float): area of field (acres??)

    returns:
        b_run_sl (float): baseline sediment loss in runoff due to
        sheet and rill erosion (tons/year)
    '''
    # area cutoff
    area_cutoff = 200 # TODO acres?? - check units!

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

# TODO need a baseline version of calc_prac_sed_nl()

# %% ---- practice change functions ----
# practice change runoff volume
def calc_prac_run_v(q, area, rain_days, rd_cor):
    '''
    description:
    calculate practice change condition runoff volume (acre-feet)

    parameters:
        q (float): runoff (inches/day), see calc_q function
        (this depends on calc_p and calc_s functions as well, where
        cn is for the practice change)
        area (float): area of field (acres)
        rain_days (float): average number of rainy days per year
        rd_cor (float): rain day correction factor

    returns:
        b_run_v (float): runoff volume (acre-feet)
    '''
    # convert inches to feet
    q_ft = q/12

    # calculate p
    p_run_v = q_ft * area * (rain_days * rd_cor)

    # return
    return p_run_v

# practice change sediment-bound nutrient load (reduction)
def calc_prac_sed_nl(b_run_nl, erosion, area, bmp_eff, soil_conc):
    '''
    description:
    calculate practice change condition sediment-bound nutrient load
    (lbs), can be used to calculate nutrient load for either nitrogen or 
    phosphorus and for either cropped land or grazed land/pastureland

    parameters:
        b_run_nl (float): baseline annual runoff load for *either* 
        nitrogen or phosphorus (lbs)
        erosion (float): sediment loss due to sheet and rill 
        erosion (tons/year), see erosion function
        area (float): area of field (acres)
        bmp_eff (float): bmp efficiency
        soil_conc (float): soil nutrient concentration for *either*
        nitrogen or phosphorus (decimal percent)

    returns:
        p_sed_nl (float): practice change sediment-bound nutrient
        load (lbs)
    '''
    # area cutoff
    area_cutoff = 200 # TODO acres?? - check units!

    # sediment delivery ratio
    # if less than area_cutoff
    if area <= area_cutoff:
        del_ratio = 0.42 * area**(-0.125)
        
    # else if greater than area_cutoff
    else:
        del_ratio = (0.417662 * area**(-0.134958)) - 0.127097

    # TODO check if separate calc for pasture vs crop!

    # convert tons to lbs
    e_lbs = erosion * 2000

    # calculate
    p_sed_nl = e_lbs * del_ratio * (1 - bmp_eff) * soil_conc

# practice change nutrient load (reduction)
def calc_prac_run_nl(b_run_nl, bmp_eff, p_sed_nl):
    '''
    description:
    calculate practice change condition runoff nutrient load (lbs),
    can be used to calculate nutrient load for either nitrogen or 
    phosphorus and for either cropped land or grazed land/pastureland

    parameters:
        b_run_nl (float): baseline annual runoff load for *either* 
        nitrogen or phosphorus (lbs)
        bmp_eff (float): bmp efficiency
        p_sed_nl (float): sediment-bound nutrient load, 
        see calc_prac_sed_nl function

    returns:
        p_run_nl (float): practice change runoff nutrient load (lbs)
    '''
    # calculate
    p_run_nl = b_run_nl * bmp_eff + p_sed_nl # TODO check this!


