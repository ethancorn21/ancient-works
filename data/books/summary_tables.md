| book | IA id | pages | stage A | stage F | stage B | index rows | site-plan pages | by Qwen | by list only |
|---|---|---|---|---|---|---|---|---|---|
| squier_davis_1848 | ancientmonuments00squi | 452 | 452 | 125 | 65 | 145 | 68 | 67 | 1 |
| lapham_1855 | antiquitiesofwis00saph | 230 | 230 | 38 | 68 | 115 | 68 | 65 | 3 |
| thomas_1894 | annualreportofbu1218901891smit | 896 | 896 | 302 | 196 | 197 | 193 | 187 | 6 |
| fowke_1902 | b24849959 | 788 | 788 | 216 | 75 | 88 | 75 | 71 | 4 |
| squier_1851 | b30449492 | 222 | 222 | 41 | 34 | 55 | 33 | 33 | 0 |
| whittlesey_1850 | descriptionsofan00whit | 54 | 54 | 0 | 7 | 18 | 7 | 7 | 0 |
| allcroft_1908 | earthworkenglan01allcgoog | 743 | 743 | 211 | 205 | 235 | 205 | 200 | 5 |
| mills_1914 | ArcheologicalAtlasOfOhio | 206 | 206 | 13 | 26 | 37 | 26 | 26 | 0 |

| book | site plates listed | mapped to a leaf | Qwen typed site plan | Qwen read the numeral | other plates called site plan |
|---|---|---|---|---|---|
| squier_davis_1848 | 43 | 43 | 1.0 | 1.0 | 0/4 |
| lapham_1855 | 52 | 51 | 0.98 | 0.98 | 0/2 |
| whittlesey_1850 | 7 | 7 | 1.0 | 1.0 | 0/0 |
| squier_1851 | 14 | 14 | 1.0 | 1.0 | 0/0 |
| thomas_1894 | 29 | 29 | 1.0 | 0.759 | 0/6 |

| book | figures parsed / listed | site-plan pages in list | recall A | recall A+Clef | recall A+Clef (+-1 leaf) | precision A (strict/lenient) | precision A+Clef (strict/lenient) |
|---|---|---|---|---|---|---|---|
| squier_davis_1848 | 196/207 | 15 | 0.733 | 0.933 | 0.933 | 0.647/0.882 | 0.583/0.833 |
| lapham_1855 | 50/61 | 14 | 0.643 | 0.857 | 0.857 | 0.692/0.692 | 0.857/0.929 |
| thomas_1894 | 325/344 | 113 | 0.938 | 0.947 | 0.973 | 0.658/0.733 | 0.677/0.759 |
| fowke_1902 | 298/303 | 69 | 0.971 | 0.942 | 0.986 | 0.957/0.971 | 0.915/0.944 |
| allcroft_1908 | 162/224 | 139 | 0.964 | 0.964 | 0.993 | 0.67/0.67 | 0.67/0.67 |

index rows by page type: {'plate_site_plan': 331, 'figure_site_plan': 515, 'other_illustration': 38, 'text_only': 6}
rows with a map box: 850 / 890 ; with scale text: 508 ; with a north arrow end-point pair: 589
matches: {'no_candidate': 517, 'ambiguous': 161, 'matched': 135, 'generic': 73, 'doubtful': 2, 'rejected_by_eye': 2}
