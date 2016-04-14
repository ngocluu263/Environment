---------------------------------------------------------------
Equations *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  * 
---------------------------------------------------------------

Legend:

  pk         Title    Total
------------------------------------------------


  1-12		General Equations (IPCC, Chave, Brown)  12 Total
------------------------------------------------
	Location: allometric.json
	
		not specific to any region or country


   13-355   India Volumetric Equations    343 Total
----------------------------------------------
    Location: india_volumetric.json
    Source:    Ministry of Enviroment & Forests. Annexure I of "Carbon Stocks in India's Forests." 		Forest Survey of India: Dehradun.
    Uploaded Dev: Installed 343 object(s) from 1 fixture(s)

    356-1408   India Biomass Equations   1053 Total
------------------------------------------------
	Location: india_biomass.json
	Source:    Ministry of Enviroment & Forests. Annexure I of "Carbon Stocks in India's Forests." 		Forest Survey of India: Dehradun.
	Uploaded Dev: Installed 1053 object(s) from 1 fixture(s)


How to get total: Last number minus first number + 1

-----------------------------------------------------------------
Regions *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *
-----------------------------------------------------------------


    1-14 		India Regions
--------------------------------------------
	Location: allometric.json


    15 		Indonesia Region
--------------------------------------------
	Location: allometric.json

	16-49	Indonesia Provinces		34 Total
---------------------------------------------
	Location: allometric.json


-----------------------------------------------------------------
Countries *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *
-----------------------------------------------------------------


    1,2 	India, Indonesia
--------------------------------------------

	Location: allometric.json


-----------------------------------------------------------------
Species *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *
-----------------------------------------------------------------


  Wood Density Values
---------------------------------------------
		Source:http://www.worldagroforestry.org/regions/southeast_asia/resources/db/wd
		
		Location: table.txt, parsed into india_species.json
		
		Unknown species/no data: Abies densa; Abies smithiana; Acacia lenticularis; Acacia species; Acer species; Albizia species; Amoora species; Amoora wallichii; Aporosa lindleyana; Bauhinia retusa; Bauhinia species; Bombax insigne; Callicarpa arborea; Castanopsis species; Cinnamomum species; Cleistanthus collinus; Diospyros species; Dolichandrone falcata; Eucalyptus species; Eugenia species; Ficus species; Gardenia gum; Gardenia lucida; Grewia tiliaefolia; Jonesia asoca; Lagerstroemia flosreginae; Lyonia ovalifolia; Macaranga species; Machilus species; Michelia species; Myristica malabarica; Odina wodier; Olea dioica; Pieris ovalifolia; Pinus excelsa; Quercus floribunda; Quercus semecarpifolia; Quercus species; Quercus tribuloides; Saccopetalum tomentosum; Saraca asoca; Stephegyne parviflora; Stereospermum colais; Symplocos theaefolia; Terminalia belerica; Zizyphus jujuba; Zizyphus mauritiana; Zizyphus xylopyrus; Macaranga peltata; Salvadora oleoides;
		Grewia species; Memecylon angustifolium; Miliusa tomentosum; Myrica esculenta; Myrica integrifolia; Myrica nagi; Myrica sapida; Protium caudatum; Rhododendron species; Terminalia species;


 
    1-151	India Species Volumetric   150 Total
 --------------------------------------------
 	Note: Deleted 32, mistake species 
 	Location: json/uploaded/india_species_v_uploaded.json
 	Source: 	Ministry of Enviroment & Forests. Annexure I of "Carbon Stocks in India's Forests." 				Forest 	Survey of India: Dehradun.
 	Uploaded Dev: Installed 149 object(s) from 1 fixture(s)

    151-172  India Species Biomass 22 Total
-----------------------------------------------
	Location: json/uploaded/india_species_b_uploaded.json
	Source: 	Ministry of Enviroment & Forests. Annexure I of "Carbon Stocks in India's Forests." 				Forest 	Survey of India: Dehradun.
 	Uploaded Dev: Installed 22 object(s) from 1 fixture(s)
---------------------------------------------------------------
CHANGE LOG *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  * 
---------------------------------------------------------------

    Name Changes
-------------------------------------------------

 --------------------------- -----------------------
| Before                    | After                 |
 --------------------------- -----------------------
| Acacia leucophlaea        | Acacia leucophloea
| Pinus pectula             | Pinus patula 
| Acacia mearnsu            | Acacia mearnsii
| Xylia xylocarpus		    | Xylia xylocarpa
| Prosopis guliflora	    | Prosopis juliflora
| Prosopis ceneraria        | Prosopis cineraria
| Palaquim ellipticum       | Palaquium ellipticum
| Mallotus philippinensis   | Mallotus philippensis
| Lagerstroemia spaciosa    | Lagerstroemia speciosa
| Lagerstroemia inicrocarpa | Lagerstroemia microcarpa
| Amoora wallichi			| Amoora wallichii
| Eucalyptus globules		| Eucalyptus globulus


    Added Names
------------------------------------------
	Note:  Some names were added as a result of being more common
 --------------------------- -----------------------
| Before                    | New                 |
 --------------------------- -----------------------
Flacourtia ramontchi ++ Flacourtia indica (volume done)
Jonesia asoca ++ Saraca asoca (volume done)
Madhuca latifolia ++ Madhuca longifolia (volume done)
Castanopsis tribuloides ++ Quercus tribuloides (volume done)
Terminalia tomentosa ++ Terminalia elliptica (volume done)
Bauhinia variegata ++ Phanera variegata (volume done)
Myrica nagi ++ Myrica esculenta, Myrica integrifolia  (volume done)

Equation Changes
--------------------------------------
Diospyros Melanoxylon  Removed variable D from middle term
