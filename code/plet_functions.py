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

# %% ---- load libraries ----
import numpy as np


# %% ---- general functions ----
# precipitation
def calc_p(gdf):
    '''
    description:
    calculate rainfall per event (p) in units of inches, where "event"
    is equal to a day (24-hr) period (source: STEPL "Land&Rain" tab)

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            aa_rain (float): average annual rainfall (inches)
            r_cor (float): rainfall correction factor
            rain_days (float): average number of rainy days per year
            rd_cor (float): rain day correction factor

    returns:
        p (float): rainfall per event (inches/event), as a new column in gdf
    '''
    # calculate
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
            cn_value (int): curve number for specific land cover/land use and
            it's associated condition (e.g., good or poor)

    returns:
        s (float): potential maximum water retention after runoff 
        begins (inches), as a new column in gpf
    '''
    # calculate
    gdf['s'] = (1000 / gdf['cn_value']) - 10

    # return
    return gdf

# runoff
def calc_q(gdf):
    '''
    description:
    calculate runoff depth (inches/event)

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            p (float): rainfall per event (inches/event), see calc_p function
            s (float): potential maximum water retention after runoff 
            begins (inches), see calc_s function

    returns:
        q (float): runoff depth (inches/event), as a new column in gdf
    '''
    # calculate
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
        animal_aeu (float): animal equivalent units which is equal to
        animal_den / 1000, as a new column in gdg
        animal_inten (str): animal intensity (low, medium, high), a new
        column in the gdf
    '''
    # if animal type is beef cattle
    if(animal_type == 'beef_cattle'):
        # define standard beef cattle weight (lbs)
        animal_wt = 1000

        # calculate animal density
        gdf['animal_den'] = (gdf['n_animals'] * animal_wt) / gdf['area_ac']

        # calculate animal equivalent units
        gdf['animal_aeu'] =  gdf['animal_den'] / 1000

        # calculate animal intensity
        gdf = gdf.reset_index(drop = True)
        for index, row in gdf.iterrows():
            if ((row['animal_aeu'] > 0) | (row['animal_aeu'] <= 1.5)):
                gdf.loc[index, 'animal_inten'] = 'low'
            
            elif ((row['animal_aeu'] > 1.5) | (row['animal_aeu'] < 2.5)):
                gdf.loc[index, 'animal_inten'] = 'medium'

            elif (row['animal_aeu'] >= 2.5):
                gdf.loc[index, 'animal_inten'] = 'high'

            else:
                gdf.loc[index, 'animal_inten'] = np.nan
                print("intensity is zero or outside of defined range")

    # if not beef cattle
    else:
        # calculate animal density
        gdf['animal_den'] = np.nan

        # calculate animal equivalent units
        gdf['animal_aeu'] =  np.nan

        # calculate animal intensity
        gdf['animal_inten'] = np.nan
        print("only beef cattle is allowed at this time")

    # return
    return gdf


# %% ---- baseline functions ----
# baseline runoff volume
def calc_base_run_v(gdf):
    '''
    description:
    calculate baseline condition runoff volume (acre-feet)

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            q (float): runoff depth (inches/event), see calc_q function
            (this depends on calc_p and calc_s functions as well)
            area_ac (float): area of field (acres)
            rain_days (float): average number of rainy days per year
            rd_cor (float): rain day correction factor

    returns:
        b_run_v (float): baseline annual runoff volume (acre-feet), 
        as a new column in gdf
    '''
    # convert inches to feet
    q_ft = gdf['q']/12

    # calculate
    gdf['b_run_v'] = q_ft * gdf['area_ac'] * (gdf['rain_days'] * gdf['rd_cor'])

    # return
    return gdf

# baseline irrigation runoff volume (b_irr_v)
# hold off on this for now until verify with esmc that it's needed

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
            b_run_v (float): baseline annual runoff volume (acre-feet),
            see calc_base_run_v function
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
    calculate baseline annual sediment load in runoff due to sheet
    and rill erosion (tons)

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            erosion (float): sediment loss due to erosion (tons), 
            see calc_e function
            area_ac (float): area of field

    returns:
        del_ratio (float): sediment delivery ratio (unitless), as a new
        column in gdf
        b_run_s (float): baseline annual sediment loss in runoff due to
        sheet and rill erosion (tons), as a new column in gdf
    '''
    # area cutoff
    area_cutoff = 200
    # area cutoff is in units of acres but delivery ratio emperical
    # relationship requires area to be in sq mi
    # (source: STEPL spreadsheet "Sediment" tab)

    # sediment delivery ratio
    gdf = gdf.reset_index(drop = True)
    for index, row in gdf.iterrows():
        # if less than area_cutoff
        if row['area_ac'] <= area_cutoff:
            # convert acres to sq mi
            area_mi = row['area_ac']/640

            # calculate delivery ratio
            gdf.loc[index, 'del_ratio'] = 0.42 * area_mi**(-0.125)
            
        # else if greater than area_cutoff
        else:
            # convert acres to sq mi
            area_mi = row['area_ac']/640

            # calculate delivery ratio
            gdf.loc[index, 'del_ratio'] = (0.417662 * area_mi**(-0.134958)) - 0.127097

    # sediment erosion
    gdf['b_run_s'] = gdf['erosion'] * gdf['del_ratio']

    # return
    return gdf

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
            p (float): rainfall per event (inches/event), see calc_p function
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
    infil_ft = infil / 12
    
    # baseline groundwater infiltraiton volume
    gdf['b_in_v'] = infil_ft * gdf['area_ac'] * (gdf['rain_days'] * gdf['rd_cor'])

    # return
    return gdf

# baseline groundwater nutrient load (b_gw_nl)
# hold off on this for now until verify with esmc that it's needed


# %% ---- practice change functions ----
# practice change runoff volume
def calc_prac_run_v(gdf):
    '''
    description:
    calculate practice change condition runoff volume (acre-feet)

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            q (float): runoff depth (inches/event), see calc_q function
            (this depends on calc_p and calc_s functions as well, where
            cn_value is for the practice change)
            area_ac (float): area of field (acres)
            rain_days (float): average number of rainy days per year
            rd_cor (float): rain day correction factor

    returns:
        p_cn_value (float): practice change curve number value, as a new
        column in gdf
        p_run_v (float): practice change annual runoff volume (acre-feet),
        as a new column in gdf
    '''
    # calculate practice change runoff volume
    gdf = gdf.reset_index(drop = True)
    for index, row in gdf.iterrows():
        # cover crop bmp list
        cc_bmp_list = ['cov_crop_1', 'cov_crop_2', 'cov_crop_3']

        # if bmp provides water quantity benefits
        if row['eff_val_quantity'] == 1:

            # if cover crop bmp
            if row['bmp_name'] in cc_bmp_list:

                # recalculate cn
                gdf.loc[index, 'p_cn_value'] = row['cn_value'] - 3
                # p_cn_value = row['cn_value'] - 3
                # source: see table 9-1 in usda nrcs handbook chapter 9
                # (2004) on crop residue cover for poor and good soil
                # conditions
                # assumption: not all cover crop bmps have sediment bmp
                # efficiency values so using usda nrcs handbook information
                # instead of the efficiency values as described below for
                # non-cover crop bmps

                # recalculate s
                # gdf.loc[index, 'p_s'] = (1000 / gdf.loc[index, 'p_cn_value']) - 10
                p_s = (1000 / gdf.loc[index, 'p_cn_value']) - 10

                # recalculate q
                # gdf.loc[index, 'p_q'] = (row['p']**2) / (row['p'] + row['p_s'])
                p_q = (row['p']**2) / (row['p'] + p_s)

                # convert inches to feet
                # q_ft = row['p_q'] / 12
                p_q_ft = p_q / 12

                # calculate
                gdf.loc[index, 'p_run_v'] = p_q_ft * row['area_ac'] * (row['rain_days'] * row['rd_cor'])
            
            # if not cover crop bmp
            else:
                 # apply bmp percent applied
                eff_val_sed_adj = row['eff_val_sediment'] * (row['bmp_ac']/row['area_ac'])

                # recalculate cn
                gdf.loc[index, 'p_cn_value'] = row['cn_value'] - row['cn_value'] * eff_val_sed_adj
                # p_cn_value = row['cn_value'] - row['cn_value'] * row['eff_val_sediment']
                # assumption: assuming that sediment load reductions are
                # due to decreases in runoff volume so that they are 
                # directly proportional and can bue used to scale the 
                # new cn values for practice changes

                # recalculate s
                # gdf.loc[index, 'p_s'] = (1000 / gdf.loc[index, 'p_cn_value']) - 10
                p_s = (1000 / gdf.loc[index, 'p_cn_value']) - 10

                # recalculate q
                # gdf.loc[index, 'p_q'] = (row['p']**2) / (row['p'] + row['p_s'])
                p_q = (row['p']**2) / (row['p'] + p_s)

                # convert inches to feet
                # q_ft = row['p_q'] / 12
                p_q_ft = p_q / 12

                # calculate
                gdf.loc[index, 'p_run_v'] = p_q_ft * row['area_ac'] * (row['rain_days'] * row['rd_cor'])
        
        # if bmp provides no water quantity benefits
        else:
            # practice change cn and runoff volume equals baseline
            gdf.loc[index, 'p_cn_value'] = row['cn_value']
            gdf.loc[index, 'p_run_v'] = row['b_run_v']

    # return
    return gdf

# practice change runoff sediment-bound nutrient load (reduction)
def calc_prac_sed_nl(gdf):
    '''
    description:
    calculate practice change condition sediment-bound nutrient load
    (lbs), can be used to calculate nutrient load for either
    sediment-bound nitrogen or phosphorus and for either cropped land
    or grazed land/pastureland

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            del_ratio (float): sediment delivery ratio (unitless),
            see calc_base_run_sl function (this also depends on the 
            calc_c function)
            erosion (float): sediment loss due to sheet and rill 
            erosion (tons/year), see calc_e function
            eff_val_nitrogen (float): bmp efficiency for nitrogen
            eff_val_phophorus (float): bmp efficiency for phosphorus
            soil_conc_n (float): soil nitrogen concentration (percent)
            soil_conc_p (float): soil phosphorus concentration (percent)

    returns:
        e_lbs (float): sediment loss due to sheet and rill erosion (lbs/year
        p_sed_n (float): practice change sediment-bound nitrogen load
        (lbs), as a new column in gdf
        p_sed_p (float): practice change sediment-bound phosphorus
        load (lbs), as a new column in gdf
    '''
    # convert tons to lbs
    gdf['e_lbs'] = gdf['erosion'] * 2000

    # hard code soil concentrations (percent)
    soil_conc_n = 0.08
    soil_conc_p = 0.0308
    # TODO check whether need to divide by 100 here

    # TODO add soil p and n concentrations provided by the user here

    # calculate sediment-bound nutrient loads
    gdf = gdf.reset_index(drop = True)
    for index, row in gdf.iterrows():
        # sediment-bound nitrogen load
        # no efficiency value
        if np.isnan(row['eff_val_nitrogen']):
            gdf.loc[index, 'p_sed_n'] = np.nan

        # if has efficiency value
        else:
            # apply bmp percent applied
            eff_val_n_adj = row['eff_val_nitrogen'] * (row['bmp_ac']/row['area_ac'])

            # calculate
            gdf.loc[index, 'p_sed_n'] = row['e_lbs'] * row['del_ratio'] * (1 - eff_val_n_adj) * soil_conc_n
            
        # sediment-bound phosphorus load
        # no efficiency value
        if np.isnan(row['eff_val_phosphorus']):
            gdf.loc[index, 'p_sed_p'] = np.nan

        # if has efficiency value
        else:
            # apply bmp percent applied
            eff_val_p_adj = row['eff_val_phosphorus'] * (row['bmp_ac']/row['area_ac'])

            # calculate
            gdf.loc[index, 'p_sed_p'] = row['e_lbs'] * row['del_ratio'] * (1 - eff_val_p_adj) * soil_conc_p

    # return
    return gdf

# practice change runoff nutrient load
def calc_prac_run_nl(gdf):
    '''
    description:
    calculate practice change condition runoff nutrient load (lbs),
    will calculate nutrient load for nitrogen or phosphorus
    for either cropped land or grazed land/pastureland

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            b_run_n (float): baseline annual runoff load for nitrogen (lbs),
            see calc_base_run_nl function
            b_run_p (float): baseline annual runoff load for phosphorus (lbs),
            see calc_base_run_nl function
            eff_val_nitrogen (float): bmp efficiency for nitrogen
            eff_val_phophorus (float): bmp efficiency for phosphorus
            eff_val_sediment (float): bmp efficiency for sediment
            p_sed_n (float): practice change sediment-bound nitrogen
            load (lbs), see calc_prac_sed_nl function
            p_sed_p (float): practice change sediment-bound phosphorus
            load (lbs), see calc_prac_sed_nl function

    returns:
        p_run_n (float): practice change annual runoff nitrogen load
        (lbs), as a new column in gdf
        p_run_p (float): practice change annual runoff phosphorus load
        (lbs), as a new column in gdf
    '''
    # calculate practice change nutrient loads
    gdf = gdf.reset_index(drop = True)
    for index, row in gdf.iterrows():
        # if cropland
        if row['user_lu'] == 'cropland':
            # practice change runoff nitrogen load
            # if no efficiency value then return baseline condition
            if np.isnan(row['eff_val_nitrogen']):
                gdf.loc[index, 'p_run_n'] = row['b_run_n']

            # if has efficiency value
            else:
                # apply bmp percent applied
                eff_val_n_adj = row['eff_val_nitrogen'] * (row['bmp_ac']/row['area_ac'])
                
                # calculate
                gdf.loc[index, 'p_run_n'] = row['b_run_n'] * eff_val_n_adj

            # practice change runoff phosphorus load
            # if no efficiency value then return baseline condition
            if np.isnan(row['eff_val_phosphorus']):
                gdf.loc[index, 'p_run_p'] = row['b_run_p']

            # if has efficiency value
            else:
                # apply bmp percent applied
                eff_val_p_adj = row['eff_val_phosphorus'] * (row['bmp_ac']/row['area_ac'])
                
                # calculate
                gdf.loc[index, 'p_run_p'] = row['b_run_p'] * eff_val_p_adj

        # if pastureland
        elif row['user_lu'] == 'pastureland':
            # practice change runoff nitrogen load
            # if no efficiency value then return baseline condition
            if np.isnan(row['eff_val_nitrogen']):
                gdf.loc[index, 'p_run_n'] =  row['b_run_n']

            # if has efficiency value
            else:
                # apply bmp percent applied
                eff_val_n_adj = row['eff_val_nitrogen'] * (row['bmp_ac']/row['area_ac'])
                
                # calculate
                gdf.loc[index, 'p_run_n'] = row['b_run_n'] * eff_val_n_adj + row['p_sed_n']

            # practice change runoff phosphorus load
            # if no efficiency value then return baseline condition
            if np.isnan(row['eff_val_phosphorus']):
                gdf.loc[index, 'p_run_p'] =  row['b_run_p']

            # if has efficiency value
            else:
                # apply bmp percent applied
                eff_val_p_adj = row['eff_val_phosphorus'] * (row['bmp_ac']/row['area_ac'])
                
                # calculate
                gdf.loc[index, 'p_run_p'] = row['b_run_p'] * eff_val_p_adj + row['p_sed_p']

        else:
            # result cannot be determined for other land use types
            gdf.loc[index, 'p_run_n'] = np.nan
            gdf.loc[index, 'p_run_p'] = np.nan
            print("please choose either cropland or pastureland for practice change runoff nutrient load calculations")

    # return
    return gdf

# practice change runoff sediment load
def calc_prac_run_sl(gdf):
    '''
    description:
    calculate practice change condition runoff sediment load (tons)

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            del_ratio (float): sediment delivery ratio (unitless),
            see calc_base_run_sl function (this also depends on the 
            calc_c function)
            erosion (float): annual sediment loss due to sheet and rill 
            erosion (tons), see calc_e function
            eff_val_sediment (float): bmp efficiency for sediment
    returns:
        p_run_s (float): practice change annual runoff sediment load
        (tons), as a new column in gdf
    '''
    # calculate practice change nutrient loads
    gdf = gdf.reset_index(drop = True)
    for index, row in gdf.iterrows():
        # practice change runoff sediment load
        # if no efficiency value then return baseline condition
        if np.isnan(row['eff_val_sediment']):
            gdf.loc[index, 'p_run_s'] = row['b_run_s']

        # if has efficiency value
        else:
            # apply bmp percent applied
            eff_val_s_adj = row['eff_val_sediment'] * (row['bmp_ac']/row['area_ac'])
                
            # calculate
            gdf.loc[index, 'p_run_s'] = row['erosion'] * row['del_ratio'] * (1 -eff_val_s_adj)

    # return
    return gdf

# practice change groundwater nutrient load (p_gw_nl)
# hold off on this for now until verify that we can calculate it
# efficiency valus are for surface water bmp impacts and there might
# not be a way to estimate practice change impact on gw loads

# %% ---- calculate change function ----
# percent change function
def calc_perc_change(gdf):
    '''
    description:
    calculate the annual percent change from the baseline to practice
    change conditions for all variables (runoff, nitrogen loads, phosphorus
    loads, and sediment loads), ranges from 0% to 100%

    parameters:
        gdf (geopandas geodataframe): PLET module geopandas dataframe
        that must have the following columns:
            b_run_v (float): baseline annual runoff volume (acre-feet)
            b_run_n (float): baseline annual runoff nitrogen load (lbs)
            b_run_p (float): baseline annual runoff phosphorus load (lbs)
            b_run_s (float): baseline annual sediment loss in runoff due to
            sheet and rill erosion (tons)
            p_run_v (float): practice change annual runoff volume (acre-feet)
            p_run_n (float): practice change annual runoff nitrogen load (lbs)
            p_run_p (float): practice change annual runoff phosphorus load (lbs)
            p_run_s (float): practice change annual sediment loss in
            runoff due to sheet and rill erosion (tons)
    returns:
        pc_v (float): percent change in runoff volume (%),
        as a new column in gdf
        pc_n (float): percent change in nitrogen load (%),
        as a new column in gdf
        pc_p (float): percent change in phosphorus load (%),
        as a new column in gdf
        pc_s (float): percent change in sediment load (%),
        as a new column in gdf
    '''
    # calcuate percent changes for all variables
    gdf = gdf.reset_index(drop = True)
    for index, row in gdf.iterrows():
        # calculate percent change in runoff
        # if baseline is greater than zero
        if (row['b_run_v'] > 0):
            gdf.loc[index, 'pc_v'] = round(((row['b_run_v'] - row['p_run_v']) / row['b_run_v']) * 100, 1)

        # if baseline is equal to or less than zero
        else:
            gdf.loc[index, 'pc_v'] = np.nan
            print("baseline runoff volume is either equal to or less than zero or is not defined, so percent change cannot be calculated. nan will be returned.")

        # calculate percent change in nitrogen load
        # if baseline is greater than zero
        if (row['b_run_n'] > 0):
            gdf.loc[index, 'pc_n'] = round(((row['b_run_n'] - row['p_run_n']) / row['b_run_n']) * 100, 1)

        # if baseline is equal to or less than zero
        else:
            gdf.loc[index, 'pc_n'] = np.nan
            print("baseline nitrogen load is either equal to or less than zero or is not defined, so percent change cannot be calculated. nan will be returned.")

        # calculate percent change in phosphorus load
        # if baseline is greater than zero
        if (row['b_run_p'] > 0):
            gdf.loc[index, 'pc_p'] = round(((row['b_run_p'] - row['p_run_p']) / row['b_run_p']) * 100, 1)

        # if baseline is equal to or less than zero
        else:
            gdf.loc[index, 'pc_p'] = np.nan
            print("baseline phosphorus load is either equal to or less than zero or is not defined, so percent change cannot be calculated. nan will be returned.")

        # calculate percent change in sediment load
        # if baseline is greater than zero
        if (row['b_run_s'] > 0):
            gdf.loc[index, 'pc_s'] = round(((row['b_run_s'] - row['p_run_s']) / row['b_run_s']) * 100, 1)

        # if baseline is equal to or less than zero
        else:
            gdf.loc[index, 'pc_s'] = np.nan
            print("baseline sediment load is either equal to or less than zero or is not defined, so percent change cannot be calculated. nan will be returned.")

    # return
    return gdf