# README for `2024-esmc-plet`

## 1. Project Information

**Client Name:** Ecosystem Services Market Consortium (ESMC)

**Project Period:** May 2024 - May 2025

**Project Number:** 100-WTR-T43877 (task 3)

**EAM Staff Project Manager:** Brian Pickard (brian.pickard@tetratech.com)

**EAM Project Staff:** Sheila Saia (sheila.saia@tetratech.com), Maddie Keefer (maddie.keefer@tetratech.com), Hannah Ferriby (hannah.ferriby@tetratech.com)

**EAM Repo Maintainer/Key Contact:** Sheila Saia (sheila.saia@tetratech.com)

**Project Description (1-3 sentences):** Tetra Tech is collaborating with ESMC's EcoHarvest MMRV technical and operational teams to develop an ESMC-specific version of the U.S. Environmental Protection Agency (USEPA) Pollutant Load Estimation Tool (PLET), henceforth referred to as the PLET module. The PLET module will be used to quantify impacts of water quality and water quantity best management practices. Specifically, ESMC will use the PLET module to automate the impact quantification scope 3 producer programs on cropped and grazed lands.

**O-Drive Project URL:** Projects\ESMC\2024_contract\

**Project Tags:** INSERT_TAGS (URL_WITH_EAM_TAGS_LIST)

**Coding Programs Used:** Python


## 2. Repository File Structure Description

INSERT DETAILS ABOUT THE FILE STRUCTURE, INCLUDING A DESCRIPTION OF FILES, PRESCRIBED ORDER OF ANALYSIS, ETC.

[fill in]

## 3. Description of Data Sources and Versions

INSERT DETAILS ABOUT THE SOURCES OF DATA USED, INCLUDING THEIR VERSIONS AND RELEVANT CITATIONS AND WEB URLS.

[fill in]

## 4. Description of Libraries/Packages Used and Versions

INSERT DETAILS ABOUT THE CODING LIBRARIES/PACKAGES USED, INCLUDING THEIR VERSIONS AND RELEVANT CITATIONS AND WEB URLS.

[fill in]

## 5. Additional Information

INSERT ANY ADDITIONAL INFORMATION. FEEL FREE TO RENAME THIS SECTION OR ADD MORE SECTIONS, AS NEEDED.

[fill in]


# Table of Contents

1. [Third-Party Services](#1-third-party-services)

2. [Architecture Overview](#2-architecture-overview)

3. [Documentation Overview](#3-documentation-overview)

4. [Contact Information](#4-contact-information)

## 1. Third-Party Services

[fill in]

## 2. Arcitecture Overview

An overview of the PLET Module is shown in Figure 1 and explained below.

![Figure 1. Schematic of the PLET module architecture hosted within the ESMC Eco-Harvest MMRV. See the text below for more details on each number label in this plot.](/docs/images/plet_mod_architecture.png)
**Figure 1.** Schematic of the PLET module architecture hosted within the ESMC Eco-Harvest MMRV. See the text below for more details on each number label in this plot.

Description of proposed PLET module components shown in Figure 1:

1.	Eco-Harvest MMRV application/server
2.	PLET Module application hosted by ESMC
3.	Retrieval of baseline and practice change impact calculation results
4.	Database is a PostGIS instance hosted by ESMC
5.	Retrieval of data for baseline and practice change impact calculations
6.	Retrieval of baseline and practice change impact calculations
7.	Analysis server calculates baseline and practice change impacts
8.	Retrieval and update of external dataset are updated on an annual (or less frequent) basis, depending on the data provider
9.	External data provided via API (e.g., PRISM) or direct download (e.g., NLCD)
10.	Retrieval of internal (user) data for baseline and practice change impact calculations
11.	Internal (user) data provided by the Eco-Harvest MMRV

## 3. Documentation Overview

Instructions explaining how to perform a variety of tasks can be found in the following documents in the `docs` directory [here](/docs/).

- [ANALYSIS.md](ANALYSIS.md) explains the various PLET module analysis scripts and how to set up the analysis server.
- [CITATION.md](CITATION.md) explains how to cite and give attribution to PLET and the PLET module source code.
- [DEVELOPER.md](DEVELOPER.md) explains the structure of the repository, how to setup the API webs service and how to perform common development tasks.
- [DATA_UPDATES.md](DATA_UPDATES.md) explains how to update PLET module datasets. This will be done once per year for more datasets and as updates are released by the corresponding dataset provider (approx every 5 years) for other datasets. 
- [CONTRIBUTING.md](CONTRIBUTING.md) explains how to submit a PLET module issue.

## 4. Contact Information

If you have any questions, feedback, or suggestions please submit issues [through GitHub](https://github.com/eam-group/2024-esmc-plet/issues).