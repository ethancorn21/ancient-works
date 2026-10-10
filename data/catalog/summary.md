# Site catalog: summary

Built 2026-10-10 11:33 from Wikidata (CC0) by `pipeline/catalog.py build`; this page by `pipeline/catalog.py summary`. One line per site in `sites.jsonl`; each entry's facts come from its Wikidata item, https://www.wikidata.org/wiki/<qid> (synthetic groups carry a `source` note instead). US entries were also selected through English Wikipedia's 'Mounds in the United States' category tree (selection only; see `found_via`).

Entries: **12603** (from 16228 candidate items before cleaning, grouping and de-duplication).

## Counts by region and kind

| kind | us | england | wales | netherlands | france | all |
|---|---|---|---|---|---|---|
| barrow | 21 | 5204 | 1617 | 426 | 179 | 7447 |
| causewayed_enclosure |  | 8 | 1 |  |  | 9 |
| earthwork | 9 | 227 | 20 | 11 |  | 267 |
| effigy_mound | 9 |  |  |  |  | 9 |
| enclosure |  | 46 | 202 | 6 | 27 | 281 |
| henge |  | 48 | 4 |  |  | 52 |
| hillfort |  | 1207 | 802 |  | 191 | 2200 |
| linear_earthwork |  | 92 | 114 |  |  | 206 |
| military_earthwork | 13 |  |  |  |  | 13 |
| motte |  | 687 | 263 | 46 | 153 | 1149 |
| mound_site | 284 | 4 |  |  |  | 288 |
| platform_mound | 1 |  |  |  |  | 1 |
| roman_fort |  | 206 | 54 | 22 | 17 | 299 |
| terp |  |  |  | 382 |  | 382 |
| **total** | 337 | 7729 | 3077 | 893 | 567 | 12603 |

`kind` comes from the item's Wikidata class (P31) where one matched. US entries found only by name or category get a kind from the words in their name/description (`kind_basis` says which); `mound_site` = 'mound(s)' in the name without a class, `earthwork` = generic.

Kind basis: us: category 63, class 35, part-of link 1, words 238; england: class 7578, members 64, part-of link 56, words 31; wales: class 3076, words 1; netherlands: class 890, part-of link 3; france: class 509, part-of link 8, words 50

Groups: 197 entries list members (460 member items folded in); 64 of them are synthetic groups (no Wikidata item of their own, built from members whose labels share a 'one of a group of ...' or 'forming part of a ...' phrase, within 2 km of each other).

## Top 50 per region by notability

Notability = number of Wikipedia language editions with an article (`wiki_links`; Commons and the bot-generated Cebuano/Waray editions not counted), then raw Wikidata sitelinks. It measures how much has been written, not size or preservation. Ties are common past the first few dozen in England and France, where most items have no article at all; order within a tie is by raw sitelinks, then name, and means nothing.

### us (337 entries; 11 without any Wikipedia article)

| # | name | kind | admin area | wikis | sitelinks | members | qid | 3DEP |
|---|---|---|---|---|---|---|---|---|
| 1 | Cahokia | mound_site | Illinois | 49 | 54 | 1 | Q333661 | 1 m |
| 2 | Poverty Point | mound_site | Louisiana | 24 | 26 |  | Q964745 | 1 m |
| 3 | Serpent Mound | effigy_mound | Ohio | 17 | 19 |  | Q968802 | 1 m |
| 4 | Hopewell Culture National Historical Park | mound_site | Ohio | 10 | 12 |  | Q4315010 | 1 m |
| 5 | Hopewell Ceremonial Earthworks | mound_site | Ohio | 9 | 10 |  | Q10525989 | 3.44 m |
| 6 | Watson Brake | mound_site | Louisiana | 8 | 10 |  | Q2552689 | 1 m |
| 7 | Etowah Indian Mounds | mound_site | Georgia | 8 | 9 |  | Q4533107 | 1 m |
| 8 | Moundville Archaeological Site | mound_site | Alabama | 8 | 9 |  | Q1320821 | 1 m |
| 9 | Spiro Mounds | mound_site | Oklahoma | 8 | 9 |  | Q2044290 | 1 m |
| 10 | Effigy Mounds National Monument | effigy_mound | Iowa | 7 | 10 |  | Q1296201 | 1 m |
| 11 | Ocmulgee Mounds National Historical Park | mound_site | Georgia | 6 | 8 |  | Q1517500 | 1 m |
| 12 | Aztalan State Park | earthwork | Wisconsin | 5 | 7 |  | Q4832928 | 1 m |
| 13 | Grave Creek Mound | barrow | West Virginia | 5 | 7 |  | Q5597781 | 1 m |
| 14 | Rock Eagle Effigy Mound | effigy_mound | Georgia | 5 | 6 |  | Q1153892 | 1 m |
| 15 | Fort Ancient | mound_site | Ohio | 4 | 6 |  | Q5470727 | 1 m |
| 16 | Bottle Creek Indian Mounds | mound_site | Alabama | 4 | 5 |  | Q4949038 | 1 m |
| 17 | Newark Earthworks | earthwork | Ohio | 4 | 5 |  | Q7016678 | 3.44 m |
| 18 | Indian Mound Cemetery | mound_site | West Virginia | 4 | 4 |  | Q6020961 | 1 m |
| 19 | Kolomoki Mounds State Park | mound_site | Georgia | 3 | 5 | 1 | Q4228402 | 1 m |
| 20 | Mounds State Park | mound_site | Indiana | 3 | 5 |  | Q1950269 | 1 m |
| 21 | Winterville Site | mound_site | Mississippi | 3 | 5 |  | Q4470180 | 1 m |
| 22 | Adena Mound | mound_site | Ohio | 3 | 4 |  | Q4682185 | 1 m |
| 23 | Angel Mounds | mound_site | Indiana | 3 | 4 |  | Q4530064 | 1 m |
| 24 | Emerald Mound Site | mound_site | Mississippi | 3 | 4 |  | Q5370466 | 3.44 m |
| 25 | Fort Bayard | military_earthwork |  | 3 | 4 |  | Q3077774 | 1 m |
| 26 | Pinson Mounds | mound_site | Tennessee | 3 | 4 |  | Q4363053 | 1 m |
| 27 | Wickliffe Mounds | mound_site | Kentucky | 3 | 4 |  | Q1269580 | 1 m |
| 28 | Fort Washington | military_earthwork | Massachusetts | 2 | 4 |  | Q5472257 | 1 m |
| 29 | Indian Mounds Park | mound_site | Minnesota | 2 | 4 |  | Q3150092 | 1 m |
| 30 | Miamisburg Mound | barrow | Ohio | 2 | 4 |  | Q34827561 | 1 m |
| 31 | Safety Harbor Site | mound_site | Florida | 2 | 4 |  | Q7398614 | 1 m |
| 32 | Town Creek Indian Mound | mound_site | North Carolina | 2 | 4 |  | Q4452751 | 3.44 m |
| 33 | Tremper Mound and Works | mound_site | Ohio | 2 | 4 |  | Q7838197 | 1 m |
| 34 | Alligator Effigy Mound | effigy_mound | Ohio | 2 | 3 |  | Q4732645 | 3.44 m |
| 35 | Battle Mound Site | mound_site | Arkansas | 2 | 3 |  | Q4870073 | 1 m |
| 36 | Bynum Mound and Village Site | mound_site | Mississippi | 2 | 3 |  | Q5004170 | 3.44 m |
| 37 | Caddo Mounds State Historic Site | mound_site | Texas | 2 | 3 |  | Q5016312 | 10.31 m |
| 38 | Crystal River Archaeological State Park | barrow | Florida | 2 | 3 |  | Q3485388 | 1 m |
| 39 | Dunns Pond Mound | mound_site | Ohio | 2 | 3 |  | Q5315620 | 1 m |
| 40 | Fort DeRussy | military_earthwork | Washington County | 2 | 3 |  | Q5471024 | 1 m |
| 41 | Fort Foote | military_earthwork | Maryland | 2 | 3 |  | Q14691922 | 1 m |
| 42 | Fort Hill State Memorial | earthwork | Ohio | 2 | 3 |  | Q16210178 | 1 m |
| 43 | Fort Totten | military_earthwork |  | 2 | 3 |  | Q18150335 | 1 m |
| 44 | Kincaid Mounds State Historic Site | mound_site | Illinois | 2 | 3 |  | Q4220862 | 1 m |
| 45 | LSU Campus Mounds | mound_site | Louisiana | 2 | 3 |  | Q6460005 | 1 m |
| 46 | Lake Ridge Island Mounds | mound_site | Ohio | 2 | 3 |  | Q6477523 | 1 m |
| 47 | Marietta Earthworks | mound_site | Ohio | 2 | 3 |  | Q6763227 | 1 m |
| 48 | Menard-Hodges Site | mound_site | Arkansas | 2 | 3 |  | Q4290309 | 1 m |
| 49 | Mound Cemetery Mound | mound_site | Ohio | 2 | 3 |  | Q14716731 | 1 m |
| 50 | Nacoochee Mound | platform_mound | Georgia | 2 | 3 |  | Q4312576 | 1 m |

### england (7729 entries; 7042 without any Wikipedia article)

| # | name | kind | admin area | wikis | sitelinks | members | qid |
|---|---|---|---|---|---|---|---|
| 1 | Stonehenge | henge | Salisbury, Wiltshire | 116 | 135 |  | Q39671 |
| 2 | Avebury | henge | Wiltshire | 41 | 44 |  | Q661855 |
| 3 | Sutton Hoo | earthwork | Suffolk Coastal, Suffolk | 39 | 39 | 1 | Q503256 |
| 4 | Silbury Hill | barrow | Wiltshire | 26 | 28 |  | Q225896 |
| 5 | Lincoln Castle | motte | Lincoln, Lincolnshire | 22 | 24 |  | Q727760 |
| 6 | York Castle | motte | City of York, City of York | 22 | 24 |  | Q80637 |
| 7 | Maiden Castle | hillfort | West Dorset, Dorset | 22 | 23 |  | Q1232816 |
| 8 | Camulodunum | roman_fort | Colchester, Essex | 19 | 20 |  | Q630604 |
| 9 | Warkworth Castle | motte | Northumberland | 17 | 19 |  | Q922422 |
| 10 | Old Sarum | hillfort | Wiltshire | 17 | 18 |  | Q782719 |
| 11 | Fotheringhay Castle | motte | North Northamptonshire | 16 | 18 |  | Q1439593 |
| 12 | Norwich Castle | motte | Norwich, Norfolk | 16 | 18 |  | Q1672292 |
| 13 | Sandal Castle | motte | Wakefield, West Yorkshire | 15 | 17 |  | Q1760652 |
| 14 | Dunster Castle | motte | Somerset West and Taunton, Somerset | 14 | 16 |  | Q2969173 |
| 15 | Arbeia | roman_fort | South Tyneside, Tyne and Wear | 13 | 15 |  | Q1131391 |
| 16 | Barnard Castle | motte | County Durham, County Durham | 13 | 15 |  | Q4185811 |
| 17 | Viroconium Cornoviorum | roman_fort | Shropshire | 13 | 15 |  | Q1361580 |
| 18 | Hardknott Roman Fort | roman_fort | Copeland, Cumberland | 13 | 14 |  | Q1584994 |
| 19 | Castlerigg stone circle | barrow | Allerdale, Cumberland | 12 | 14 |  | Q1850757 |
| 20 | Castra Deva Victrix | roman_fort | Cheshire West and Chester, Cheshire West and Chester | 12 | 13 |  | Q2450247 |
| 21 | Pontefract Castle | motte | Wakefield, West Yorkshire | 11 | 13 |  | Q1949590 |
| 22 | Calleva Atrebatum | hillfort | Basingstoke and Deane, Hampshire | 11 | 12 |  | Q1027253 |
| 23 | West Kennet Long Barrow | barrow | Wiltshire | 11 | 12 |  | Q541312 |
| 24 | Strutt's Park Roman fort | roman_fort | City of Derby, City of Derby | 11 | 11 |  | Q1241270 |
| 25 | Castrum Segedunum | roman_fort | North Tyneside, Tyne and Wear | 10 | 12 |  | Q637958 |
| 26 | Richborough Roman Fort | roman_fort | Dover, Kent | 10 | 11 |  | Q1309736 |
| 27 | Berkhamsted Castle | motte | Dacorum, Hertfordshire | 9 | 11 |  | Q4892150 |
| 28 | Dudley Castle | motte | Dudley, West Midlands | 9 | 11 |  | Q5311832 |
| 29 | Okehampton Castle | motte | West Devon, Devon | 9 | 11 |  | Q1419982 |
| 30 | Little Solsbury Hill | hillfort | Wansdyke, Bath and North East Somerset | 9 | 10 |  | Q548780 |
| 31 | Bramber Castle | motte | Horsham, West Sussex | 8 | 10 |  | Q897538 |
| 32 | Cadbury Castle | hillfort | South Somerset, Somerset | 8 | 10 |  | Q1025082 |
| 33 | Leicester Castle | motte | City of Leicester, City of Leicester | 8 | 10 |  | Q6519156 |
| 34 | Athelney | hillfort | Sedgemoor, Somerset | 8 | 9 |  | Q3496233 |
| 35 | Mamucium | roman_fort | Manchester, Greater Manchester | 8 | 9 | 1 | Q3285089 |
| 36 | Coria | roman_fort | Northumberland | 7 | 9 |  | Q3819299 |
| 37 | Ewyas Harold Castle | motte | Herefordshire | 7 | 9 |  | Q5419097 |
| 38 | Oakham Castle | motte | Rutland, Rutland | 7 | 9 |  | Q2968294 |
| 39 | Pickering Castle | motte | Ryedale, North Yorkshire | 7 | 9 |  | Q7190805 |
| 40 | Totnes Castle | motte | South Hams, Devon | 7 | 9 |  | Q2445840 |
| 41 | Windmill Hill | earthwork | Wiltshire | 7 | 9 |  | Q4348373 |
| 42 | Castrum Anderitum | roman_fort | Wealden, East Sussex | 7 | 8 |  | Q943660 |
| 43 | Lanyon Quoit | barrow | Cornwall | 7 | 8 |  | Q1725167 |
| 44 | Glevum | roman_fort | Gloucester, Gloucestershire | 7 | 7 |  | Q360974 |
| 45 | Bedford Castle | motte | Bedford, Bedford | 6 | 8 |  | Q4879112 |
| 46 | Danebury Hill Camp | hillfort | Test Valley, Hampshire | 6 | 8 |  | Q677333 |
| 47 | Trematon Castle | motte | Cornwall | 6 | 8 |  | Q7838051 |
| 48 | Arbor Low | henge | Derbyshire Dales, Derbyshire | 6 | 7 |  | Q630312 |
| 49 | Barbury Castle | hillfort | Swindon | 6 | 7 |  | Q807881 |
| 50 | Binchester Roman Fort | roman_fort | County Durham, County Durham | 6 | 7 |  | Q4913955 |

### wales (3077 entries; 2325 without any Wikipedia article)

| # | name | kind | admin area | wikis | sitelinks | members | qid |
|---|---|---|---|---|---|---|---|
| 1 | Offa's Dyke | earthwork | Powys | 30 | 31 |  | Q1127343 |
| 2 | Isca Augusta | roman_fort | Newport | 14 | 15 |  | Q929778 |
| 3 | Castrum Segontium | roman_fort | Gwynedd | 12 | 13 |  | Q1309657 |
| 4 | Llansteffan Castle | hillfort | Carmarthenshire | 11 | 13 |  | Q1936320 |
| 5 | Wat's Dyke | earthwork | Powys | 10 | 11 | 1 | Q696088 |
| 6 | Castell Dinas Brân | hillfort | Denbighshire | 9 | 11 |  | Q1226281 |
| 7 | Llandovery Castle | motte | Carmarthenshire | 9 | 11 |  | Q1493071 |
| 8 | Pennard Castle | motte | Swansea | 9 | 11 |  | Q4185855 |
| 9 | Eliseg's Pillar | barrow | Denbighshire | 9 | 10 |  | Q3090852 |
| 10 | Dinas Emrys | hillfort | Gwynedd | 8 | 10 |  | Q354820 |
| 11 | Blestium | roman_fort | Monmouthshire | 8 | 9 |  | Q572453 |
| 12 | Burry Holms | hillfort | Swansea | 7 | 9 |  | Q248118 |
| 13 | Sycharth Castle | motte | Powys | 7 | 9 |  | Q7659623 |
| 14 | Tinkinswood | barrow | The Vale of Glamorgan | 7 | 8 |  | Q1859561 |
| 15 | Castell Henllys | hillfort | Pembrokeshire | 6 | 8 |  | Q3399096 |
| 16 | Morlais Castle | hillfort | Merthyr Tydfil County Borough | 6 | 8 |  | Q6912480 |
| 17 | Wiston Castle | motte | Pembrokeshire | 6 | 8 |  | Q8027762 |
| 18 | Barclodiad y Gawres | barrow | Gwynedd | 6 | 7 |  | Q807965 |
| 19 | Aberdyfi Castle | motte | Ceredigion | 5 | 7 |  | Q4667053 |
| 20 | Dolforwyn Castle | hillfort | Powys | 5 | 7 |  | Q1235495 |
| 21 | Twtil, Castle Motte | motte | Denbighshire | 5 | 7 |  | Q7859519 |
| 22 | Canovium | roman_fort | Conwy County Borough | 5 | 6 |  | Q5033467 |
| 23 | Crug Hywel | hillfort | Powys | 5 | 6 |  | Q851344 |
| 24 | Foel Drygarn | hillfort | Pembrokeshire | 5 | 6 |  | Q20594728 |
| 25 | St Lythans Chambered Tomb | barrow | The Vale of Glamorgan | 5 | 6 |  | Q7594075 |
| 26 | Burrium | roman_fort | Monmouthshire | 5 | 5 |  | Q602000 |
| 27 | Caer Gybi | roman_fort | Gwynedd | 4 | 6 |  | Q5016868 |
| 28 | Colwyn Castle | motte | Powys | 4 | 6 |  | Q5150338 |
| 29 | Mold Castle | motte | Flintshire | 4 | 6 |  | Q6895734 |
| 30 | Nidum | roman_fort | Neath Port Talbot | 4 | 5 |  | Q10962522 |
| 31 | Pen y Clawdd Castle | motte | Monmouthshire | 4 | 5 |  | Q7162124 |
| 32 | Penycloddiau | hillfort | Denbighshire | 4 | 5 |  | Q7165400 |
| 33 | Prestatyn Castle | motte | Denbighshire | 4 | 5 |  | Q7241757 |
| 34 | St Clears Castle | motte | Carmarthenshire | 4 | 5 |  | Q13130290 |
| 35 | Tre'r Ceiri | hillfort | Gwynedd | 4 | 5 |  | Q1088007 |
| 36 | Y Gaer Roman Fort | hillfort | Powys | 4 | 5 |  | Q8046130 |
| 37 | Pen y Gaer | hillfort | Conwy County Borough | 4 | 4 |  | Q3374625 |
| 38 | Caer Castell | motte | Cardiff | 3 | 5 |  | Q13126473 |
| 39 | Caerau Hillfort | hillfort | Cardiff | 3 | 5 |  | Q5016882 |
| 40 | Hen Domen | motte | Powys | 3 | 5 |  | Q5712905 |
| 41 | Owain Glyndŵr's Mount | motte | Denbighshire | 3 | 5 |  | Q13126900 |
| 42 | Painscastle Castle | motte | Powys | 3 | 5 |  | Q24659303 |
| 43 | Tinboeth Castle | hillfort | Powys | 3 | 5 |  | Q7808013 |
| 44 | Tredegar Fort | hillfort | Newport | 3 | 5 |  | Q20584714 |
| 45 | Caer Bach | hillfort | Conwy County Borough | 3 | 4 |  | Q13126465 |
| 46 | Caer Drewyn | hillfort | Denbighshire | 3 | 4 |  | Q13126471 |
| 47 | Caer y Twr | hillfort | Isle of Anglesey | 3 | 4 |  | Q5016875 |
| 48 | Caerleon Castle | motte | Newport | 3 | 4 |  | Q15790795 |
| 49 | Cardiff Roman Fort | roman_fort |  | 3 | 4 |  | Q5038461 |
| 50 | Carreghofa Castle | motte | Powys | 3 | 4 |  | Q15097770 |

### netherlands (893 entries; 760 without any Wikipedia article)

| # | name | kind | admin area | wikis | sitelinks | members | qid |
|---|---|---|---|---|---|---|---|
| 1 | Lower German Limes | earthwork |  | 16 | 17 |  | Q1265889 |
| 2 | Warffum | terp | Het Hogeland, Groningen | 14 | 15 |  | Q1942428 |
| 3 | Oostum | terp | Winsum, Groningen | 8 | 9 |  | Q2598567 |
| 4 | Traiectum | roman_fort | Utrecht, Utrecht | 8 | 9 |  | Q2199749 |
| 5 | Aalsum | terp | Zuidhorn, Groningen | 7 | 8 |  | Q3902030 |
| 6 | Flevum | roman_fort | Velsen, North Holland | 6 | 6 |  | Q615397 |
| 7 | Laurium | roman_fort |  | 5 | 6 |  | Q2089258 |
| 8 | Municipium Ulpia Noviomagus Batavorum | roman_fort | Nijmegen, Gelderland | 5 | 6 |  | Q1309708 |
| 9 | Vorstengraf Oss | barrow | Oss, North Brabant | 5 | 6 |  | Q2207902 |
| 10 | Bethlehem | terp | Het Hogeland, Groningen | 5 | 5 |  | Q2523914 |
| 11 | Castra Herculis | roman_fort |  | 4 | 5 |  | Q515850 |
| 12 | Fletio | roman_fort | Utrecht, Utrecht | 4 | 5 | 3 | Q2072212 |
| 13 | Oldorp | terp | Eemsmond, Groningen | 4 | 5 |  | Q931301 |
| 14 | Terpensmole | terp | Súdwest-Fryslân, Friesland | 4 | 5 |  | Q4687217 |
| 15 | Duno | enclosure | Renkum, Gelderland | 3 | 4 |  | Q17454361 |
| 16 | Emmeloord | terp | Noordoostpolder, Flevoland | 3 | 4 |  | Q4604102 |
| 17 | Motte Montferland | motte | Montferland, Gelderland | 3 | 4 |  | Q2845894 |
| 18 | Terpzigt | terp | Menameradiel, Friesland | 3 | 4 |  | Q1919205 |
| 19 | Carvium | roman_fort |  | 3 | 3 |  | Q1046167 |
| 20 | Castrum Carvo | roman_fort | Neder-Betuwe, Gelderland | 3 | 3 |  | Q1046175 |
| 21 | Castrum Levefanum | roman_fort |  | 3 | 3 |  | Q1309559 |
| 22 | Castrum Mannaricium | roman_fort | Buren, Gelderland | 3 | 3 |  | Q1309550 |
| 23 | Teerd | terp | Dongeradeel, Friesland | 3 | 3 |  | Q13138282 |
| 24 | Burcht van Voorne | motte | Voorne aan Zee, South Holland | 2 | 3 |  | Q2765622 |
| 25 | D7 | barrow | Aa en Hunze, Drenthe | 2 | 3 |  | Q2209037 |
| 26 | D8 | barrow | Aa en Hunze, Drenthe | 2 | 3 |  | Q11714040 |
| 27 | De Thombe | motte | Maastricht, Limburg | 2 | 3 |  | Q2359601 |
| 28 | Dolmen of Mander | barrow | Tubbergen, Overijssel | 2 | 3 |  | Q13729209 |
| 29 | Eelswerd | terp | Eemsmond, Groningen | 2 | 3 |  | Q1926527 |
| 30 | Elens | terp | De Marne, Groningen | 2 | 3 |  | Q2132755 |
| 31 | Enghenbergje | barrow | Soest, Utrecht | 2 | 3 |  | Q13135468 |
| 32 | Heveskesklooster | terp | Eemsdelta, Groningen | 2 | 3 |  | Q3276052 |
| 33 | Kops Plateau | roman_fort | Nijmegen, Gelderland | 2 | 3 |  | Q3921197 |
| 34 | Oldenklooster | terp | Eemsdelta, Groningen | 2 | 3 |  | Q2454252 |
| 35 | Ranum | terp | Winsum, Groningen | 2 | 3 |  | Q1871445 |
| 36 | Selwerd | terp | Zuidhorn, Groningen | 2 | 3 |  | Q1965019 |
| 37 | Terptsjerke | terp | Boarnsterhim, Friesland | 2 | 3 |  | Q2350852 |
| 38 | Vorstengraf De Hamert | barrow | Bergen, Limburg | 2 | 3 |  | Q2531222 |
| 39 | Wierhuizen | terp | Appingedam, Groningen | 2 | 3 |  | Q3209584 |
| 40 | Zwarte Berg | barrow | Bladel, North Brabant | 2 | 3 |  | Q2409112 |
| 41 | Frytum | terp | Zuidhorn, Groningen | 2 | 2 |  | Q13426818 |
| 42 | Lekkerterp | terp | Heerenveen, Friesland | 2 | 2 |  | Q13136776 |
| 43 | Valcum | terp | Winsum, Groningen | 2 | 2 |  | Q3240092 |
| 44 | Walsweer | terp | Het Hogeland, Groningen | 2 | 2 |  | Q15943789 |
| 45 | Vasserheide | barrow |  | 1 | 3 |  | Q7476251 |
| 46 | Aldenhaag | motte | Buren, Gelderland | 1 | 2 |  | Q23650779 |
| 47 | Appelse walburg | enclosure | Nijkerk, Gelderland | 1 | 2 |  | Q42328240 |
| 48 | Blijdestein | motte | Nissewaard, South Holland | 1 | 2 |  | Q18812970 |
| 49 | Bolleberg | motte | Echt-Susteren, Limburg | 1 | 2 |  | Q17365920 |
| 50 | Burial mount Grootebroek | barrow | Stede Broec, North Holland | 1 | 2 |  | Q17453732 |

### france (567 entries; 276 without any Wikipedia article)

| # | name | kind | admin area | wikis | sitelinks | members | qid |
|---|---|---|---|---|---|---|---|
| 1 | Carnac stones | enclosure | Morbihan | 34 | 37 | 1 | Q833850 |
| 2 | Alesia | hillfort | Côte-d’Or | 30 | 33 |  | Q835966 |
| 3 | Bibracte | hillfort | Saône-et-Loire | 30 | 30 |  | Q650053 |
| 4 | Avaricum | hillfort | Cher | 14 | 15 |  | Q281826 |
| 5 | Vix grave | barrow | Côte-d’Or | 12 | 13 |  | Q1483632 |
| 6 | Argentoratum | roman_fort | Bas-Rhin | 10 | 11 |  | Q2361353 |
| 7 | Oppidum d'Ensérune | hillfort | Hérault | 10 | 11 |  | Q77221 |
| 8 | Tumulus of Bougon | barrow | Deux-Sèvres | 9 | 10 |  | Q1310277 |
| 9 | Entremont | hillfort | Bouches-du-Rhône | 8 | 9 |  | Q281494 |
| 10 | Uxellodunum | hillfort |  | 8 | 9 |  | Q1290232 |
| 11 | Cenabum | hillfort |  | 7 | 8 |  | Q2710144 |
| 12 | Durocortorum | hillfort | Marne | 7 | 8 |  | Q4896307 |
| 13 | Pech Maho | hillfort | Aude | 7 | 8 |  | Q3373902 |
| 14 | Saint-Michel tumulus | barrow | Morbihan | 7 | 8 |  | Q1419562 |
| 15 | Argentomagus | hillfort | Indre | 6 | 7 |  | Q2860982 |
| 16 | Dissignac tumulus | barrow | Loire-Atlantique | 6 | 7 |  | Q2459723 |
| 17 | Ambrussum | hillfort | Hérault | 5 | 6 |  | Q1458146 |
| 18 | Araghju | enclosure | Corse-du-Sud | 5 | 6 |  | Q2859432 |
| 19 | Vertillum | hillfort | Côte-d’Or | 5 | 6 |  | Q7922962 |
| 20 | Bibrax | hillfort |  | 4 | 5 |  | Q856700 |
| 21 | Camp d'Attila | hillfort | Marne | 4 | 5 |  | Q18749222 |
| 22 | Castra Argentovaria | roman_fort | Haut-Rhin | 4 | 5 |  | Q2654537 |
| 23 | Hotié de Viviane | barrow | Ille-et-Vilaine | 4 | 5 |  | Q1590832 |
| 24 | tumulus d'Er Grah | barrow | Morbihan | 4 | 5 |  | Q1347902 |
| 25 | Château de Labrit | motte | Landes | 3 | 4 |  | Q2969604 |
| 26 | Cromlech des Bonnettes | barrow | Pas-de-Calais | 3 | 4 |  | Q19520988 |
| 27 | Montlaurès | hillfort | Aude | 3 | 4 |  | Q3322814 |
| 28 | Motte castrale de Doué-la-Fontaine | motte | Maine-et-Loire | 3 | 4 |  | Q3325341 |
| 29 | Oppidum of Corent | hillfort | Puy-de-Dôme | 3 | 4 |  | Q3354365 |
| 30 | Pierre Turquaise | barrow | Seine-et-Oise | 3 | 4 |  | Q1799018 |
| 31 | Vellaunodunum | hillfort |  | 3 | 3 |  | Q673209 |
| 32 | Alignement du Camp de la Justice | enclosure | Saône-et-Loire | 2 | 3 |  | Q22965925 |
| 33 | Alignements du Bosc | barrow | Lot-et-Garonne | 2 | 3 |  | Q21007917 |
| 34 | Andone Castrum | enclosure | Charente | 2 | 3 |  | Q2941535 |
| 35 | Britzgyberg oppidum | hillfort | Haut-Rhin | 2 | 3 |  | Q14627810 |
| 36 | Camp celtique de la Bure | roman_fort | Vosges | 2 | 3 |  | Q2935231 |
| 37 | Camp gaulois de la pointe de Kervédan | hillfort | Morbihan | 2 | 3 |  | Q22991880 |
| 38 | Château du Kochersberg | motte | Bas-Rhin | 2 | 3 |  | Q1012697 |
| 39 | Dolmen de Toulvern | barrow | Morbihan | 2 | 3 |  | Q108861902 |
| 40 | Gondole | hillfort | Puy-de-Dôme | 2 | 3 |  | Q775166 |
| 41 | Jardin aux Moines | barrow | Morbihan | 2 | 3 |  | Q1494595 |
| 42 | Jastres-nord | hillfort | Ardèche | 2 | 3 |  | Q603603 |
| 43 | Kastell Lostmarc'h | hillfort | Finistère | 2 | 3 |  | Q22925755 |
| 44 | Kernourz dolmen | barrow | Morbihan | 2 | 3 |  | Q1235878 |
| 45 | Le Reclus dolmen | barrow | Marne | 2 | 3 |  | Q21469684 |
| 46 | Les Mousseaux tumulus | barrow | Loire-Atlantique | 2 | 3 |  | Q1258182 |
| 47 | Mané-er-Hroëk tumulus | barrow | Morbihan | 2 | 3 |  | Q1891971 |
| 48 | Motte de la Jacquille | motte | Charente | 2 | 3 |  | Q3325352 |
| 49 | Moustoir tumulus | barrow | Morbihan | 2 | 3 |  | Q19603941 |
| 50 | Oppidum d'Altimurium | hillfort | Hérault | 2 | 3 |  | Q3354357 |

## Data quality (honest notes)

Dropped during cleaning: missing 50, no_coord 216, out_of_region 0, junk_class 7, summit_only 5, hop_not_site 165, uk_other_part 2505, not_site_like 35, culture_category_only 59, megalith 14. Examples:

- junk_class: Q1075868 Chokoloskee; Q6433153 Koshkonong Mounds; Q355841 Adena culture; Q6560597 list of Adena culture sites; Q15693968 Bruinsburg; Q576386 Mound City
- summit_only: Q20594866 Craig y Castell; Q24638115 White Caterthun; Q22910051 Nottingham Hill; Q24654443 Brown Caterthun; Q131830814 Churn Hill
- hop_not_site: Q2600886 Oxford Castle; Q26441946 Ana Cross; Q3003309 Bewcastle Cross; Q140139594 cult site at Richborough fort; Q17777886 Dunnottar Castle, Stables; Q56661813 Antonine Wall and fort, Castlecary
- uk_other_part: Q56661444 Trenabie Farm,standing stones, mound and bank 300m W of; Q56661591 cairns and standing stones 1200m SSE of Kensaleyre Church; Q56662229 mound 150m S of Dronley House; Q56662337 Kinnells Mill,cairn; Q56662674 Mote Hill, palisaded settlement and cairn; Q56663413 burial mound 50m E of Glenskinno
- not_site_like: Q3034172 Kerroc'h dolmen; Q51076105 Allée couverte de Run-Aour; Q125024736 dolmen de l'Île Longue; Q20170739 Cam Louis menhir; Q21254112 menhir de Cohardais; Q1891983 dolmen de Mané-Kerioned
- culture_category_only: Q14690049 Baker Site; Q19461261 Damariscotta Shell Midden Historic District; Q5371016 Emeryville Shellmound; Q5447668 Fig Island; Q5522536 Gardiner Pond Shell Midden; Q1519323 Indian Knoll
- megalith: Q22927271 Dolmen à galerie avec la base de son tumulus; Q30740203 allée couverte du Tertre de l'église; Q90146372 dolmen de Puech Camp 1; Q11350706 Caixa del Camp de l'Obra; Q20817227 Dolmen del Camp de la Coma; Q16031898 dolmen du Camp Gran I

Merged: 190 items folded into their part-of group (all linked items within 4 km); 267 items into 64 synthetic groups; 3 items named relative to a neighbour ('Bowl barrow 100m south of X') folded in as members of X; 173 near-duplicates (< 300 m apart, distinctive name words overlap, no conflicting register numbers or designators) merged into one entry, the lost item listed in `merged_from`. Sample merged pairs (kept <= merged):

- Q17648223 Earthworks on Brent Tor <= Q31115407 Brent Tor
- Q110408488 Winterbourne Poor Lot Barrows <= Q17676907 Twenty-one barrows forming part of a round barrow cemetery at Winterbourne Poor Lot
- Q24659214 Leigh Drummers; The Castle <= Q31115910 The Castle, Leigh
- Q17662820 Saxon barrow, church and cemeteries in the old churchyard at Taplow Court <= Q31117370 Taplow
- Q17676747 Billings Ring large univallate hillfort <= Q31113102 Billings Ring
- Q5050206 Castle Old Fort <= Q17664073 Hillfort known as The Castle Fort at Castlebank Plantation
- Q24661534 Langton Castle <= Q24661532 Langton Motte
- Q4185811 Barnard Castle <= Q17644043 Barnard Castle: ringwork, shell keep castle, chapel and dovecote
- Q17643525 Brandon Dean camp <= Q31111603 Brandon HIll
- Q31111864 Pace Hill <= Q31111639 Pace Hill

### Famous sites: present or missing

| region | site | catalog entry | lat, lon |
|---|---|---|---|
| us | Serpent Mound | Serpent Mound [Q968802, effigy_mound] via qid | 39.02586, -83.43044 |
| us | Cahokia | Cahokia [Q333661, mound_site] via qid | 38.65389, -90.06444 |
| us | Monks Mound (Cahokia) | member of Cahokia [Q280444, mound_site] via qid (member) | 38.66070, -90.06200 |
| us | Poverty Point | Poverty Point [Q964745, mound_site] via qid | 32.63670, -91.41140 |
| us | Newark Earthworks | Newark Earthworks [Q7016678, earthwork] via qid | 40.04217, -82.43011 |
| us | Fort Ancient | Fort Ancient [Q5470727, mound_site] via qid | 39.40778, -84.09025 |
| us | Fort Hill (Ohio) | Fort Hill State Memorial [Q16210178, earthwork] via name | 39.11310, -83.40630 |
| us | High Bank Works | **MISSING** |  |
| us | Hopeton Earthworks | **MISSING** |  |
| us | Marietta Earthworks | Marietta Earthworks [Q6763227, mound_site] via qid | 39.42000, -81.45190 |
| us | Mound City Group | **MISSING** |  |
| us | Hopewell Mound Group | **MISSING** |  |
| us | Seip Earthworks | Seip Earthworks [Q123916810, earthwork] via qid | 39.23680, -83.22020 |
| us | Grave Creek Mound | Grave Creek Mound [Q5597781, barrow] via qid | 39.91694, -80.74444 |
| us | Miamisburg Mound | Miamisburg Mound [Q34827561, barrow] via qid | 39.62722, -84.28111 |
| us | Etowah | Etowah Indian Mounds [Q4533107, mound_site] via qid | 34.12801, -84.80706 |
| us | Moundville | Moundville Archaeological Site [Q1320821, mound_site] via qid | 33.00467, -87.63107 |
| us | Ocmulgee | Ocmulgee Mounds National Historical Park [Q1517500, mound_site] via qid | 32.84110, -83.60507 |
| us | Kincaid Mounds | Kincaid Mounds State Historic Site [Q4220862, mound_site] via qid | 37.08056, -88.49167 |
| us | Spiro Mounds | Spiro Mounds [Q2044290, mound_site] via qid | 35.31194, -94.56861 |
| us | Pinson Mounds | Pinson Mounds [Q4363053, mound_site] via qid | 35.49778, -88.68250 |
| us | Angel Mounds | Angel Mounds [Q4530064, mound_site] via qid | 37.94179, -87.45546 |
| us | Aztalan | Aztalan State Park [Q4832928, earthwork] via qid | 43.06560, -88.86290 |
| us | Effigy Mounds NM | Effigy Mounds National Monument [Q1296201, effigy_mound] via qid | 43.08860, -91.18560 |
| us | Toltec Mounds | Plum Bayou Mounds Archeological State Park [Q7814641, mound_site] via name | 34.64690, -92.06530 |
| us | Winterville Mounds | Winterville Site [Q4470180, mound_site] via name | 33.48580, -91.06110 |
| us | Emerald Mound | Emerald Mound Site (+1 more name matches) [Q5370466, mound_site] via name | 31.63611, -91.24723 |
| us | Crystal River | Crystal River Archaeological State Park [Q3485388, barrow] via name | 28.91694, -82.60917 |
| us | Watson Brake | Watson Brake [Q2552689, mound_site] via name | 32.36840, -92.13140 |
| england | Maiden Castle (Dorset) | Maiden Castle [Q1232816, hillfort] via qid | 50.69500, -2.47000 |
| england | Avebury | Avebury [Q661855, henge] via qid | 51.42861, -1.85417 |
| england | Silbury Hill | Silbury Hill [Q225896, barrow] via qid | 51.41556, -1.85750 |
| england | Stonehenge | Stonehenge [Q39671, henge] via qid | 51.17889, -1.82611 |
| england | West Kennet Long Barrow | West Kennet Long Barrow (+5 more name matches) [Q541312, barrow] via name | 51.40860, -1.85104 |
| england | Sutton Hoo | Sutton Hoo [Q503256, earthwork] via qid | 52.08972, 1.33889 |
| england | Danebury | Danebury Hill Camp (+1 more name matches) [Q677333, hillfort] via name | 51.13680, -1.53970 |
| england | Uffington Castle | Uffington Castle (+1 more name matches) [Q2473790, hillfort] via name | 51.57500, -1.56928 |
| england | Old Sarum | Old Sarum [Q782719, hillfort] via qid | 51.09333, -1.80472 |
| england | Thornborough Henges | Thornborough Henges [Q2428964, henge] via qid | 54.20900, -1.56315 |
| england | Offa's Dyke (spans England and Wales) | Offa's Dyke [Q1127343, earthwork] via qid | 52.34400, -3.04900 |
| england | Windmill Hill (Avebury) | Windmill Hill [Q4348373, earthwork] via qid | 51.44153, -1.87622 |
| netherlands | Hunneschans | Duno (+2 more name matches) [Q17454361, enclosure] via name | 51.97167, 5.81211 |
| netherlands | Ezinge (wierde) | Wierde van Ezinge [Q17599084, terp] via name | 53.31102, 6.43910 |
| france | Bougon tumuli | Tumulus of Bougon [Q1310277, barrow] via name | 46.37400, -0.06750 |
| france | Tumulus Saint-Michel | Saint-Michel tumulus [Q1419562, barrow] via name | 47.58806, -3.07361 |
| france | Gergovie | petit camp de César de la bataille de Gergovie (+1 more name matches) [Q58578274, enclosure] via name | 45.72110, 3.11510 |
| france | Alesia | Alesia [Q835966, hillfort] via name | 47.53917, 4.50056 |
| france | Bibracte | Bibracte [Q650053, hillfort] via name | 46.92440, 4.03500 |

### Known problems

- **US typing is thin.** Only 35 of 337 US entries carry an earthwork class in Wikidata; 238 were found by words in the name/description and 63 only through a 'Mounds in <state>' Wikipedia category. Cahokia, Poverty Point, Moundville are typed just 'archaeological site'. Their `kind` is a guess from words (`kind_basis`).
- **US recall gaps.** Hopeton Earthworks (Q5899962) has an 'unknown value' coordinate, so it is dropped. No Wikidata item was found under the labels 'High Bank Works', 'High Banks Works', 'Hopewell Mound Group' or 'Mound City Group' (Hopewell Culture NHP's point stands in for Mound City). Aztalan, Seip Earthworks and Windmill Hill (Avebury) are in only because they are in a hand list of seed QIDs (`SEEDS` in catalog.py). Expect other well-known US works to be missing the same way.
- **Kept but not ancient:** 13 forts typed 'fort' + 'earthworks' (Fort Bayard, Fort Washington, Fort DeRussy, Fort Foote, Fort Totten, Battle of Island Mound State Historic Site...) are tagged `military_earthwork` and left out of the triage. Some parks, museums and multi-site listings are entries (Hopewell Culture NHP, Indian Mounds Park; Kolomoki's museum is listed as a member of Kolomoki); multi-site listings whose parts lie > 4 km apart are flagged `unit`.
- **Overlapping entries.** Marietta Earthworks, Conus Mound and Mound Cemetery are three entries within 57 m of each other (different names, so not merged). Same name is not same site: Story Mound (Hamilton Co., NRHP 75001436) and Story Mound State Memorial (Ross Co., 73001529) are 148 km apart; Emerald Mound (Mississippi) and Emerald Mound and Village Site (Illinois) are different sites. (I picked the wrong Story Mound as a triage positive by name; the hand check caught it.)
- **England:** 7042 of 7729 entries have no Wikipedia article and 3775 are named by distance from a landmark (Historic England list-entry style), so the notability order means little past the top hundred or so. Offa's Dyke is filed under Wales (its Wikidata admin area is Powys) although it runs through both.
- **Netherlands:** 576 of 893 entries have generic register names ('Terrein waarin grafheuvel', 'Wierde', 'Terp'); use the admin area and Rijksmonument number. Some villages are typed as terps and absorbed their wierde item in the de-duplication (Aalsum, Ranum, Oldorp).
- **France is thin (567 entries):** Merimee earthworks are mostly typed only 'archaeological site'; the French word route ('camp', 'enceinte', 'motte'...) adds some noise. 27 have no departement in Wikidata.
- **Not included:** Denmark (22,068 items typed as barrows in Wikidata; not trivial in size and no Danish DEM source in the pipeline) and Flanders (68 Belgian barrows; no DEM source). UK items not placed in England or Wales (2,502; the sampled ones are Scottish) are dropped by design.

### Coordinates

Stated precision of the coordinate (Wikidata `precision`; it says how many decimals were entered, not how right the point is):

| region | fine | medium | coarse | missing |
|---|---|---|---|---|
| us | 203 | 90 | 43 | 1 |
| england | 7618 | 39 | 5 | 67 |
| wales | 3060 | 3 | 13 | 1 |
| netherlands | 129 | 760 | 4 | 0 |
| france | 534 | 1 | 32 | 0 |

Items with several coordinates more than 200 m apart: 43 (e.g. Durocortorum 58978 m; Persimmon Mound 6119 m; Tremper Mound and Works 1972 m; Eaker Site 1927 m; Multi-period site on Brean Down 1816 m; Caersws Roman Forts 1606 m).

Points shared by 3 or more distinct entries (to 4 decimals): 1 (e.g. 3 at 45.8085,3.0747: Plateau des Côtes de Clermont / plateau des Côtes de Clermont).

**Measured by eye on the top 150 US entries** (800 m relief crops, middle third): 64 show an earthwork near the point, 64 do not, 22 unclear. 'Do not' mixes points that miss the work (Etowah, Fort Ancient, Ocmulgee: the work is in the picture but not near the point), works destroyed or plowed out (Adena Mound, Troyville, Monte Sano), works too low or small to see at this scale (effigy mounds), and a few junk entries. Treat a Wikidata point as unchecked until its crop has been looked at.

## US LiDAR coverage (3DEP)

Checked 337 of 337 US entries (`catalog_cover.py`): one `identify` call for the finest 3DEP source under the point, plus a 200 x 200 px, 1 m `aw.fetch_dem` export. Data came back for 337. The export resamples whatever exists to 1 m, so 'data came back' is not LiDAR; the finest source is: 1 m 326, ~3 m (1/9 arc-sec) 10, 10 m or coarser 1.

Cross-check, 1-3 m detail in the exported DEM (std of DEM minus a 1.5 px blur): median 3.87 cm at 326 points with a 1 m source, 3.82 cm at 10 with ~3 m, 0.67 cm at 1 with 10 m. It also rises with rough ground and buildings, so it separates 10 m data from LiDAR only roughly and does not tell 3 m from 1 m.

## Relief-crop triage

Validation run 2026-10-10 11:14: 35 crops at known-site points (the 6 built sites + famous standing works) and 35 at random points 3-8 km from any US entry on 1 m LiDAR. Every crop: 800 m square, 1.0 m/px, one renderer, fixed clip 0.8 m. Models see only the picture. Per-image scores: `triage_scores.jsonl`.

Three ways of scoring: **all** = against the a-priori truth (site point vs random point); **hand-checked** = dropping crops where, by eye, no earthwork is in the middle third of a site crop (13 of 35: point off the work, work off-centre, or plowed out); **truth by eye** = keeping those crops as negatives (the case triage is meant to catch). Hand checks: Claude looking at the crops before any model output, not a field check.

| scoring | pos / neg | Clef AUC (question v1) | Clef AUC (v2) | Clef v2 recall / false-pos (in-sample best threshold) | Qwen recall / false-pos |
|---|---|---|---|---|---|
| all | 35 / 35 | 0.662 | 0.751 | 0.657 / 0.171 at p >= 0.0654 | 0.629 / 0.057 |
| hand_checked | 22 / 35 | 0.735 | 0.836 | 0.773 / 0.171 at p >= 0.0654 | 0.818 / 0.057 |
| truth_by_eye | 22 / 48 | 0.724 | 0.812 | 0.864 / 0.333 at p >= 0.0579 | 0.818 / 0.125 |

Clef question v1 is the lead's whole-image question, asked first. v2 (earthwork *near the centre*, with what does not count) was written after seeing v1's results on this set, so its numbers here are optimistic; the in-sample thresholds are optimistic for both. Clef's probabilities are small (highest on this set: v1 0.38, v2 0.55), so only the ranking means anything. Qwen labels come from one run on these 70 crops (prompt v1, two servers, temperature 0) made before the lead stopped all Qwen use; no Qwen calls were made after that, and the top-150 batch has no Qwen labels.

Qwen confusion matrix, truth by eye:

| truth \ Qwen | earthwork_visible | unsure | nothing | modern_only |
|---|---|---|---|---|
| positive | 18 | 0 | 1 | 3 |
| negative | 6 | 3 | 23 | 16 |

Batch: the top 150 US entries by notability (forts typed 'fort' + 'earthworks' left out), Clef scores only, in `triage.jsonl`.

Batch check by eye (Claude, before looking at the scores): of 150 crops, 64 show an earthwork in the middle third, 64 do not, 22 unclear. Clef on this held-out set: question v1 AUC 0.77, v2 AUC 0.857; at the thresholds picked on the validation set, v1 recall 0.375 / false-pos 0.109, v2 recall 0.797 / false-pos 0.266. Clef v2 at p >= 0.0579: of 68 crops it passes, 51 show a work by eye; of 60 it flags, 47 show none. Entries in this batch that later catalog fixes dropped or re-tagged: Battle of Island Mound State Historic Site (military_earthwork), Berry Brothers Bolt Works (dropped), Civil War Earthworks at Tallahatchie Crossing (military_earthwork).

