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

# % ---- load libraries ----
import numpy as np


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

# animal density and intensity
def calc_animal_stats(gdf, animal_type = 'beef_cattle'):
    '''
    description:
    calculate animal density (lbs/ac of live animal weight) and
    animal intensity (low, medium, high)

    notes:
    the usepa plet documentation defines low intensity as having an
    animal density of 1500 lbs/ac of live animal weight or less, medium
    intensity is defined as between 1500 and 2500 lbs/ac of live animal
    weight, and high intensity is over 2500 lbs/ac of live animal weight

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            n_animals (float): number of animals
            area_ac (float): area of field (acres)
            animal_type (str): type of anaimal

    returns:
        animal_den (float): animal density (lbs/ac of live animal
        weight), as a new column in gdf
        animal_inten (str): animal intensity (low, medium, high), a new
        column in the gdf
    '''
    # if animal type is beef cattle
    if(animal_type == 'beef_cattle'):
        # define standard beef cattle weight (lbs)
        animal_wt = 1000

        # calculate animal density
        gdf['animal_den'] = (gdf['n_animals'] * animal_wt) / gdf['area_ac']

        # calculate animal intensity
        gdf = gdf.reset_index(drop = True)
        for index, row in gdf.iterrows():
            if (row['animal_den'] <= 1500):
                gdf.loc[index, 'animal_inten'] = 'low'
            
            elif ((row['animal_den'] > 1500) | (row['animal_den'] < 2500)):
                gdf.loc[index, 'animal_inten'] = 'medium'

            elif (row['animal_den'] >= 2500):
                gdf.loc[index, 'animal_inten'] = 'high'

            else:
                gdf.loc[index, 'animal_inten'] = np.nan
                print("intensity is outside of defined range")

    # if not beef cattle
    else:
        gdf = gdf.reset_index(drop = True)
        for index, row in gdf.iterrows():
            if ((row['animal_den'] >= 0) | (row['animal_den'] <= 1500)):
                gdf.loc[index, 'animal_inten'] = np.nan
            
            elif ((row['animal_den'] > 1500) | (row['animal_den'] < 2500)):
                gdf.loc[index, 'animal_inten'] = np.nan

            elif (row['animal_den'] >= 2500):
                gdf.loc[index, 'animal_inten'] = np.nan

            else:
                gdf.loc[index, 'animal_inten'] = np.nan
                print("intensity is outside of defined range")

        print("only beef cattle is allowed at this time")

    # return
    return gdf


## %% ---- baseline functions ----
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

# baseline runoff nutrient load (for n and p)
def calc_base_run_nl(gdf):
    '''
    description:
    calculate baseline annual runoff nutrient load (lbs), can be used 
    to calculate nutrient load for either nitrogen or phosphorus and for
    either cropped land or grazed land/pastureland

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            b_run_v (float): runoff volume (acre-feet)
            n_months (float): number of months manure is applied
            conc_n (float): concentration of the nitrogen in runoff 
            *not* during manure application (mg/L)
            conc_p (float): concentration of phosphorus in runoff 
            *not* during manure application (mg/L)
            conc_mn (float): concentration of the nutrients (either nitrogen
            or phosphorus) in runoff *during* manure application (mg/L)
            conc_pm (float): 

    returns:
        b_run_n (float): baseline annual runoff load for
        nitrogen (lbs), as a new column in gdf
        b_run_p (float): baseline annual runoff load for
        phosphorus (lbs), as a new column in gdf
    '''
    # compute manure fraction
    # (number of months/year that manure is applied)
    m_frac = gdf['n_months']/12 # 12 months in a year

    # baseline runoff nitrogen load
    gdf['b_run_n'] = gdf['b_run_v'] * ((1 - m_frac) * gdf['conc_n'] + m_frac * gdf['conc_mn']) * (4047 * 0.3048/1000 * 2.2)
    
    # baseline runoff phosphorus load
    gdf['b_run_p'] = gdf['b_run_v'] * ((1 - m_frac) * gdf['conc_p'] + m_frac * gdf['conc_mp']) * (4047 * 0.3048/1000 * 2.2)

    # return
    return gdf

# sediment loss due to erosion
def calc_e(gdf):
    '''
    description:
    calculate sediment loss due to sheet and rill erosion (tons/year)

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            r_avg (float): RUSLE average rainfall factor
            k_avg (float): RUSLE average soil erodibility factor
            ls_avg (float): RUSLE average topographic factor
            c_avg (float): RUSLE average cropping management factor
            p_avg (float): RUSLE average erosion control practice factor
            area_ac (float): area of field (acres??)

    returns:
        erosion (float): sediment loss due to sheet and rill 
        erosion (tons/year), as a new column in gdf
    '''
    # sediment erosion
    gdf['erosion'] = gdf['r_avg'] * gdf['k_avg'] * gdf['ls_avg'] * gdf['c_avg'] * gdf['p_avg'] * gdf['area_ac']

    # return
    return gdf

# baseline runoff sediment load
def calc_base_run_sl(gdf):
    '''
    description:
    calculate baseline sediment load in runoff due to sheet and rill
    erosion (tons/year)

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            erosion (float): sediment loss due to erosion (tons/year), 
            see calc_e function
            area_ac (float): area of field (acres??)

    returns:
        del_ratio (float): sediment delivery ratio (unitless), as a new
        column in gdf
        b_run_sl (float): baseline sediment loss in runoff due to
        sheet and rill erosion (tons/year), as a new column in gdf
    '''
    # area cutoff
    area_cutoff = 200 # TODO acres?? - check units!

    # sediment delivery ratio
    gdf = gdf.reset_index(drop = True)
    for index, row in gdf.iterrows():
        # if less than area_cutoff
        if row['area_ac'] <= area_cutoff:
            gdf.loc[index, 'del_ratio'] = 0.42 * row['area_ac']**(-0.125)
            
        # else if greater than area_cutoff
        else:
            gdf.loc[index, 'del_ratio'] = (0.417662 * row['area_ac']**(-0.134958)) - 0.127097

    # sediment erosion
    gdf['b_run_sl'] = gdf['erosion'] * gdf['del_ratio']

    # return
    return gdf

# TODO baseline groundwater nutrient load (b_gw_nl)
# hold off on this for now until verify with esmc that it's needed


# %% ---- practice change functions ----
# 

# practice change runoff volume
def calc_prac_run_v(gdf):
    '''
    description:
    calculate practice change condition runoff volume (acre-feet)

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            q (float): runoff (inches/day), see calc_q function
            (this depends on calc_p and calc_s functions as well, where
            cn_value is for the practice change)
            area_ac (float): area of field (acres)
            rain_days (float): average number of rainy days per year
            rd_cor (float): rain day correction factor

    returns:
        p_run_v (float): runoff volume (acre-feet), as a new column in
        gdf
    '''
    # convert inches to feet
    q_ft = gdf['q']/12

    # TODO q will need to change with CN change for practice change

    # calculate p
    gdf['p_run_v'] = q_ft * gdf['area_ac'] * (gdf['rain_days'] * gdf['rd_cor'])

    # return
    return gdf

    # TODO need to finalize this function! for select BMPS

# practice change runoff sediment-bound nutrient load (reduction)
def calc_prac_sed_nl(gdf):
    '''
    description:
    calculate practice change condition sediment-bound nutrient load
    (lbs), can be used to calculate nutrient load for either nitrogen or 
    phosphorus and for either cropped land or grazed land/pastureland

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            b_run_n (float): baseline annual runoff load for nitrogen (lbs)
            b_run_p (float): baseline annual runoff load for phosphorus (lbs)
            erosion (float): sediment loss due to sheet and rill 
            erosion (tons/year), see erosion function
            area_ac (float): area of field (acres)
            eff_val_nitrogen (float): bmp efficiency for nitrogen
            eff_val_phophorus (float): bmp efficiency for phosphorus
            eff_val_sediment (float): bmp efficiency for sediment
            soil_conc (float): soil nutrient concentration for *either*
            nitrogen or phosphorus (decimal percent)

    returns:
        e_lbs (float): sediment loss due to sheet and rill erosion (lbs/year
        p_sed_n (float): practice change sediment-bound nitrogen load
        (lbs), as a new column in gdf
        p_sed_p (float): practice change sediment-bound phosphorus
        load (lbs), as a new column in gdf
    '''
    # TODO check if separate calc for pasture vs crop!

    # convert tons to lbs
    gdf['e_lbs'] = gdf['erosion'] * 2000

    # hard code soil concentrations (percent)
    soil_conc_n = 0.08
    soil_conc_p = 0.16

    # TODO can we update soil P and N concentrations by site?

    # calculate sediment-bound nutrient loads
    gdf = gdf.reset_index(drop = True)
    for index, row in gdf.iterrows():
        # sediment-bound nitrogen load
        # no efficiency value
        if np.isnan(row['eff_val_nitrogen']):
            gdf.loc[index, 'p_sed_n'] = np.nan

        # if has efficiency value
        else:
            gdf.loc[index, 'p_sed_n'] = row['e_lbs'] * row['del_ratio'] * (1 - row['eff_val_nitrogen']) * soil_conc_n
            
        # sediment-bound phosphorus load
        # no efficiency value
        if np.isnan(row['eff_val_phosphorus']):
            gdf.loc[index, 'p_sed_p'] = np.nan

        # if has efficiency value
        else:
            gdf.loc[index, 'p_sed_p'] = row['e_lbs'] * row['del_ratio'] * (1 - row['eff_val_phosphorus']) * soil_conc_p

    # return
    return gdf

# practice change runoff nutrient load
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
        p_run_n (float): practice change runoff nitrogen load (lbs),
        as a new column in gdf
        p_run_p (float): practice change runoff phosphorus load (lbs),
        as a new column in gdf
    '''
    # calculate practice change nutrient loads
    gdf = gdf.reset_index(drop = True)
    for index, row in gdf.iterrows():
        # practice change runoff nitrogen load
        # no efficiency value
        if np.isnan(row['eff_val_nitrogen']):
            gdf.loc[index, 'p_run_n'] = np.nan

        # if has efficiency value
        else:
            gdf.loc[index, 'p_run_n'] = row['b_run_n'] * row['eff_val_nitrogen'] + row['p_sed_n']

        # practice change runoff phosphorus load
        # no efficiency value
        if np.isnan(row['eff_val_phosphorus']):
            gdf.loc[index, 'p_run_p'] = np.nan

        # if has efficiency value
        else:
            gdf.loc[index, 'p_run_p'] = row['b_run_p'] * row['eff_val_phosphorus'] + row['p_sed_p']

    # return
    return gdf
