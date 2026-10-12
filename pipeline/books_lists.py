"""Ground truth from each book's own printed lists, OCR page mapping, validation of Qwen's triage, and the index.

Ground truth = the book's List of Plates / List of Illustrations (or, where the book has none, the plate headings
printed in its text). Plate lists below were transcribed by reading IA's OCR and, where the OCR was garbled,
the list page image itself (noted per book). Figure lists are parsed from IA's OCR text automatically; where a
book's list is its own one-plate-per-leaf pages (the artists'-view books), the entries are transcribed per leaf
by hand instead (HAND_FIGS: fig = the leaf's n, '' when the plate has no leaf in the item) and the
book's list file is the dump of that table.

Each list entry carries `kind`, a judgement made from its printed title only:
    s = site plan (plan view of a work, a mound group, or a map of a valley/district showing works)
    o = other (views, sections alone, artifacts, skulls, state/country maps) - for the artists'-view books a
    town view, a drawing in its own right; the index carries it with view = true
    u = unsure from the title alone (e.g. "Mound No. 9, Miller group": plan or elevation?)
Unsure entries are left out of the strict metrics and reported separately.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
import books_ia as ia  # noqa: E402
from books import BOOKS, OUT, ROOT, SITE_TYPES, ink, site_pages_model, site_pages_qwen, stage_a, stage_b, stage_f, triage_path, _jsonl  # noqa: E402

# ---------------------------------------------------------------- plate lists (transcribed)
# plate | sub-number | title as printed | page printed in the list | kind

PLATES = {}

# Squier & Davis 1848, List of Plates pp. xxi-xxiii (leaves n28-n30). Column "Facing page".
# OCR garbled V, VI, VIII No. 3, XI page: read from the list page image (n28).
PLATES["ancientmonuments00squi"] = """
I||View of ancient works at Marietta||o
II||Map of a section of 12 miles of Scioto valley|3|s
III||Map of a section of 6 miles of Miami valley|4|s
III|2|Map of 6 miles of Paint creek valley|4|s
IV||Stone work near Bourneville, Ross co., Ohio|11|s
V||"Fort Hill," Highland county, Ohio|14|s
VI||Fortified Hill, Butler county, Ohio|16|s
VII||"Fort Ancient," Warren county, Ohio|18|s
VIII||Ancient work, Butler county, Ohio|21|s
VIII|2|Ancient work, Butler county, Ohio|22|s
VIII|3|Ancient work near Piqua, Miami co., Ohio|23|s
VIII|4|Ancient work near Dayton, Montgomery county, Ohio|23|s
IX||Fortified Hill near Granville, Licking co., Ohio|24|s
IX|2|Fortified Hill at the mouth of Great Miami river|25|s
IX|3|Ancient work near Lexington, Kentucky|26|s
X||Ancient work, Ross county, Ohio|26|s
XI||Ancient work, Butler county, Ohio|29|s
XI|2|Ancient work, Butler county, Ohio|29|s
XI|3|Ancient work, Butler county, Ohio|30|s
XII||Stone work on Duck river, Tennessee|31|s
XII|2|Ancient work, Preble county, Ohio|33|s
XII|3|Ancient work, Greene county, Ohio|33|s
XII|4|Ancient work, Ross county, Ohio|34|s
XIII||Ancient work, Bourbon county, Kentucky|35|s
XIII|2|Colerain works, Butler county, Ohio|35|s
XIV||Ancient work, Pickaway county, Ohio|36|s
XIV|2|Ancient work, Franklin county, Ohio|36|s
XIV|3|Ancient work, Fayette county, Kentucky|36|s
XIV|4|Ancient work, Fayette county, Kentucky|36|s
XV||Ancient work, Huron county, Ohio|37|s
XV|2|Ancient work, Ashtabula county, Ohio|38|s
XV|3|Ancient work, Cuyahoga county, Ohio|38|s
XV|4|Ancient work, Lorain county, Ohio|39|s
XV|5|Ancient work, Lorain county, Ohio|39|s
XV|6|Ancient work, Cuyahoga county, Ohio|40|s
XV|7|Ancient work, Cuyahoga county, Ohio|40|s
XV|8|Ancient work, Wood county, Ohio|40|s
XVI||High Bank works, Ross county, Ohio|50|s
XVII||Hopeton works, Ross county, Ohio|51|s
XVIII||Cedar Bank works, Ross county, Ohio|52|s
XIX||"Mound City," Ross county, Ohio|54|s
XX||Ancient work, Ross county, Ohio|56|s
XXI||Ancient work, Ross county, Ohio|57|s
XXI|2|Ancient work, Ross county, Ohio|57|s
XXI|3|Ancient work, Ross county, Ohio|58|s
XXI|4|Ancient work, Ross county, Ohio|59|s
XXII||"Junction Group," Ross county, Ohio|60|s
XXII|2|Blackwater Group, Ross county, Ohio|61|s
XXIII||Dunlap's works, Ross county, Ohio|63|s
XXIII|2|Ancient work, Athens county, Ohio|64|s
XXIV||Ancient work, Pike county, Ohio|66|s
XXV||Newark works, Licking county, Ohio|67|s
XXVI||Marietta works, Washington county, Ohio|73|s
XXVII||Portsmouth works, Scioto county, Ohio|77|s
XXVIII||Portsmouth works, Group A|78|s
XXVIII|2|Portsmouth works, Group B|80|s
XXVIII|3|Portsmouth works, Group C|81|s
XXIX||Ancient works, Montgomery county, Ohio|82|s
XXIX|2|Ancient works, Scioto county, Ohio|83|s
XXIX|3|Ancient works, Franklin county, Ohio|84|s
XXX||Ancient works, Butler county, Ohio|85|s
XXX|2|Ancient works, Butler county, Ohio|85|s
XXX|3|Ancient works, Ross county, Ohio|86|s
XXX|4|Stone work, Ross county, Ohio|87|s
XXXI||Graded Way, Pike county, Ohio|88|s
XXXI|2|Ancient work, Butler county, Ohio|90|s
XXXI|3|Ancient work, Butler county, Ohio|90|s
XXXI|4|Ancient work, Butler county, Ohio|90|s
XXXII||Ancient work, Butler county, Ohio|91|s
XXXII|2|Ancient work, Washington county, Ohio|92|s
XXXII|3|Ancient work, Ross county, Ohio|92|s
XXXII|4|Ancient work, Ross county, Ohio|92|s
XXXII|5|Ancient work, Ross county, Ohio|92|s
XXXII|6|Ancient work, Montgomery co., Kentucky||s
XXXIII||Ancient work, Montgomery co., Kentucky|93|s
XXXIII|2|Ancient work, Randolph county, Indiana|94|s
XXXIV||Ancient work, Clermont county, Ohio|94|s
XXXIV|2|Ancient work, Clermont county, Ohio|95|s
XXXIV|3|Ancient work, Greene county, Ohio|95|s
XXXIV|4|Ancient work, Greene county, Ohio|95|s
XXXV||Great Serpent, Adams county, Ohio|96|s
XXXVI||"The Cross," Pickaway county, Ohio|97|s
XXXVI|2|"The Alligator," Licking county, Ohio|98|s
XXXVI|3|Ancient work, Fairfield county, Ohio|100|s
XXXVI|4|Map of section of Newark valley|101|s
XXXVII||Ancient works, Wateree District, S. C.|105|s
XXXVIII||Ancient works on Etowah river, Alabama|108|s
XXXVIII|-|Ancient works on Tennessee river, Alabama|109|s
XXXVIII|2|Ancient works, Chickasaw surveys, Miss.|110|s
XXXVIII|3|Ancient works, Lafayette county, Miss.|111|s
XXXVIII|4|Ancient works, Prairie Jefferson, Louisiana|113|s
XXXIX||Ancient work, Madison parish, Louisiana|115|s
XXXIX|-|Ancient work, Bolivar county, Mississippi|116|s
XL||Ancient works, Dade county, Wisconsin|126|s
XLI||Ancient works, Dade county, Wisconsin|127|s
XLI|2|Ancient works, Dade county, Wisconsin|127|s
XLII||Ancient works, Dade county, Wisconsin|128|s
XLII|2|Ancient works, Richland county, Wisconsin|128|s
XLIII||Ancient works, Grant county, Wisconsin|129|s
XLIII|2-13|various localities|130|s
XLIV||Ancient work on Rock river, Wisconsin|131|s
XLIV|2-8|various localities|132|s
XLV||View of great mound at Marietta|138|o
XLVI||Pottery from the mounds|139|o
XLVII||Crania from the mounds|288|o
XLVIII||Crania from the mounds|288|o
"""

# Lapham 1855, List of Plates pp. ix-x (leaves n14-n15), read from the page images (OCR splits the columns).
# The PAGE column is the text page that describes the plate, not where the plate is bound.
PLATES["antiquitiesofwis00saph"] = """
I||Map of Wisconsin, showing the location of the Ancient Works.||o
II||Ancient Works near Racine|6|s
III||Ancient Works in the vicinity of Milwaukee|12|s
IV||Ancient Works near Forest Home Cemetery, Milwaukee|14|s
IV|2|Animal Mound on Sherman's Addition to Milwaukee|16|s
V||Ancient Works in the First Ward, Milwaukee|14|s
VI||Ancient Works in the Second Ward, Milwaukee|16|s
VII||Animal Mound, Beaubian Street, Milwaukee|16|s
VII|2|Animal Mound, Sherman's Addition, Milwaukee|17|s
VII|3|Animal mound on Block 120, Second Ward, Milwaukee|17|s
VII|4|Ancient Works on the School Section, Milwaukee|17|s
VIII||Ancient Works at Indian Prairie|17|s
IX||Ancient Excavations|18|u
IX|1|At Milwaukee|15|u
IX|2|At Indian Prairie|18|u
IX|3|At Indian Prairie|18|u
IX|4|At Indian Prairie|18|u
IX|5|At Theresa|58|u
IX|6|At Pewaukee|31|u
IX|7|At Fort Atkinson|36|u
X||Ancient Works, Township 11, Range 20, east|20|s
XI||Ancient Works, Township 12, Range 20, east|21|s
XII||Ancient Works near Sheboygan|21|s
XIII||Animal Mound near Burlington|24|s
XIII|2|Ancient Works at Burlington|24|s
XIV||Ancient Works near Muskego Lake|24|s
XIV|2|Group of Oblong Mounds at Crawfordsville|24|s
XV||Map of Ancient Works near Big Bend|25|s
XVI||Ancient Works at Crawfordsville|25|s
XVII||Animal Mound at Crawfordsville|25|s
XVII|2|Lizard Mound at Crawfordsville|25|s
XVII|3|The Frog, Big Bend|26|s
XVII|4|The Frog, Big Bend|26|s
XVIII||Ancient Works at Waukesha|26|s
XIX||The Turtle, Waukesha|26|s
XX||Bird Hill, Waukesha|27|s
XX|2|Lizard Mound, Waukesha|27|s
XXI||Ancient Works on Carroll College Hill, Waukesha|27|s
XXII||Birds, Waukesha|27|s
XXIII||Ancient Works on the School Section, Pewaukee|30|s
XXIV||Animal Mounds, Pewaukee|31|s
XXV||Ancient Works on the Pekatonica river|33|s
XXV|2|Oval Work at Fulton|33|s
XXVI||Ancient Works, Indian Hill, near Fulton|33|s
XXVII||Ancient Works on Lake Koshkonong|35|s
XXVIII||Ancient Works, Fort Atkinson|36|s
XXVIII|2|Ancient Works near Jefferson|36|s
XXIX||Ancient Works, Ripley Lake|37|s
XXX||Map of Ancient Works, Summit|38|s
XXXI||Ancient Works near Hartland|38|s
XXXI|2|Ancient Works at Merton|39|s
XXXI|3|The Cross at Merton|39|s
XXXII||Ancient Works, Madison|40|s
XXXIII||Ancient Works, Third Lake|40|s
XXXIV||Ancient Works at Aztalan|42|s
XXXV||Map of Ancient Works at Aztalan|42|s
XXXVI||Ancient Works, Pike Lake and Horicon|54|s
XXXVII||Ancient Works at Horicon|55|s
XXXVIII||Ancient Works and Diluvial Ridges at Mayville|56|s
XXXIX||Ancient Works near Mayville|56|s
XL||Ancient Works near Mayville|58|s
XLI||Ancient Works on Lake Winnebago|62|s
XLI|2|Ancient Works on Lake Winnebago|62|s
XLI|3|The Spread Eagle, Utica|63|s
XLII||Group of Mounds, Township 8, Range 4, east|63|s
XLII|2|One of the same enlarged|68|s
XLII|3|Mound, Township 9, Range 4, east|68|s
XLII|4|The Man, Township 9, Range 6, east|68|s
XLIII||Ancient Works at Moseley's, Township 9, Range 6|68|s
XLIV||Map of Ancient Works at Honey Creek Mills|69|s
XLIV|2|Ancient Works, Honey Creek Mills|69|s
XLV||The Buffalo, at Moseley's|69|s
XLV|2|Animal Mound, Honey Creek|69|s
XLV|3|Animal Mound, Honey Creek|69|s
XLV|4|The Bear, Honey Creek Mills|69|s
XLVI||Animal Mound at Mr. Durr's|70|s
XLVI|2|Deflected Ridges at Mr. Durr's|70|s
XLVI|3|Bird, at Honey Creek Mills|70|s
XLVI|4|Bird, Township 10, Range 7, east|70|s
XLVII||Ancient Works, Township 5, Range 7, east|70|s
XLVIII||Ancient Works, Township 5, Range 7, east|70|s
XLIX||Ancient Works on One Mile Creek, Adams County|72|s
L||Ancient Works, at Maus' Mill, Lemonwier river|73|s
LI||Ancient Works on the great dividing ridge between the Mississippi and Kickapoo rivers|77|s
LII||Ancient Works near Bartlett's Landing, Mississippi river|78|s
LIII||Human Skull, from a Mound at Racine|81|o
LIV||Ancient Works on the College grounds, Beloit|33|s
LV||Ancient Works on the east bank of Rock River, near Beloit|33|s
LV|2|Mound near the Wisconsin River.||s
"""

# Thomas 1894 (12th Annual Report BAE), Illustrations, Plates (leaf n18; same list again at n64). OCR is clean
# enough for the plate titles; XX and XXXI-XXXIV garbled, read from the n64 copy of the list.
PLATES["annualreportofbu1218901891smit"] = """
I||Plan of the Vilas and Flucke groups, Crawford county, Wisconsin|72|s
II||Plat of White's group, Vernon county, Wisconsin|82|s
III||Elephant mound and surroundings, Grant county, Wisconsin|94|s
IV||Plat of Rice lake group, Barron county, Wisconsin|96|s
V||Ancient works near New Albin, Allamakee county, Iowa|102|s
VI||Map of Cahokia group, Madison county, Illinois|134|s
VII||Map of the western part of Madison county, Illinois|136|s
VIII||Ancient works on Boulware's place, Clarke county, Missouri|168|s
IX||The De Soto mound, Jefferson county, and the Knapp mounds, Pulaski county, Arkansas|242|u
X||Plat of the Knapp mounds, Pulaski county, Arkansas|244|s
XI||Plat of the Carson mounds, Coahoma county, Mississippi|254|s
XII||Mound b, Carson group, Coahoma county, Mississippi|256|u
XIII||Mound d, Carson group, Coahoma county, Mississippi|258|u
XIV||Selsertown group, Adams county, Mississippi, and platform and mounds of the Selsertown group|264|s
XV||View of the large mound, Etowah group|294|o
XVI||Plan of the large mound, Etowah group|298|s
XVII||Figured copper plate from mound c, Etowah group (human figure)|304|o
XVIII||Figured copper plate from mound c, Etowah group (bird figure)|306|o
XIX||Pot from Hollywood mound, Georgia|318|o
XX||Map of mound distribution|In pocket|o
XXI||Observatory Circle, near Newark, Ohio|320|s
XXII||Fair Ground Circle, near Newark, Ohio|322|s
XXIII||High Bank Circle, near Chillicothe, Ohio|324|s
XXIV||Pipes from Hollywood mound, Georgia|328|o
XXV||Plat of the valley of the Little Tennessee river, Blount and Monroe counties, Tennessee|366|s
XXVI||Copy of Timberlake's map of Overhill Cherokee towns|368|u
XXVII||Plat of group near Charleston, Kanawha county, West Virginia|414|s
XXVIII||Plan and sections of the Staats mound, Knox county, Ohio|440|u
XXIX||Cemetery mound, Mount Vernon, Knox county, Ohio|444|u
XXX||Newark works, Licking county, Ohio|458|s
XXXI||Fair Ground Circle, Newark, Ohio|460|s
XXXII||Observatory Circle, Newark, Ohio|462|s
XXXIII||Octagon, Newark, Ohio|464|s
XXXIV||Square, Newark, Ohio|466|s
XXXV||Square of Hopeton works, Ross county, Ohio|472|s
XXXVI||Circle of Hopeton works, Ross county, Ohio|474|s
XXXVII||Circle of High Bank works, Ross county, Ohio|476|s
XXXVIII||Octagon of High Bank works, Ross county, Ohio|478|s
XXXIX||Square of Liberty township works, Ross county, Ohio|482|s
XL||Square of Baum works, Ross county, Ohio|484|s
XLI||Plat of the "Angel mounds," near Evansville, Indiana|558|s
XLII||Copy of Plate XI, "Brevis Narratio"|652|o
"""

# Whittlesey 1850: no list of plates; the Table of Contents (leaf n8) names every plate. Read from the page image.
PLATES["descriptionsofan00whit"] = """
I||Ancient Excavation, Big Bottom, Pike County|7|s
II||Ancient Work near Todd's Fork, Warren County|8|s
III|1|Work near Newtown|9|s
III|2|Mound near Newtown|10|s
III|3|Work near Columbus|10|s
IV||Ancient Works at Cincinnati|11|s
V|1|Ancient Works in Adams, Washington County|12|s
V|2|Work near Jacktown, Licking County|12|s
V|3|Stone Work, Perry County|13|s
V|4|Fortified Summit, three miles South of Newark, Licking County|14|s
VI|1|Work near Medina Centre, Medina County|15|s
VI|2|Fortified Position, Weymouth|16|s
VI|3|Earth-Work, South-East of Weymouth|16|s
VII|A|Work in North Field, Summit County|17|s
VII|1|Ancient Work in Jackson County|18|s
VII|2|Work between Jackson and Richmond|18|s
VII|3|Work in Ross County|18|s
"""

# Squier 1851 (Aboriginal Monuments of the State of New-York): no list of plates in the book. The volume's own
# contents (Smithsonian Contributions vol. 2, IA smithsoniancontr21851smit) says "fourteen plates"; the plate
# headings "PLATE I." ... "PLATE XIV. No. 2." are printed in the text and are parsed from the OCR (squier_ny_gt).
PLATES["b30449492"] = None


def parse_plates(ia_id):
    txt = PLATES.get(ia_id)
    if txt is None:
        return None
    out = []
    for line in txt.strip().splitlines():
        num, sub, title, page, kind = line.split("|")
        out.append(dict(plate=num, sub=sub, title=title, page=page, kind=kind))
    return out


def squier_ny_gt():
    """Plate headings printed in Squier 1851's text, e.g. 'PLATE III. No. 2.' -> entries (all earthwork plans)."""
    ia_id = "b30449492"
    ps = ia.pages(ia_id)
    T = ia.page_texts(ia_id)
    seen = []
    for p in ps:
        for m in re.finditer(r"PLATE\s+([IVXL]+)[.,]?\s*(?:Nos?\.\s*([\d\sand]+))?", T.get(p["leafNum"], "")):
            key = (m.group(1), (m.group(2) or "").strip())
            if key not in seen:
                seen.append(key)
    return [dict(plate=a, sub=b, title=f"Plate {a} {('No. ' + b) if b else ''}".strip(), page="", kind="s")
            for a, b in seen]


# ---------------------------------------------------------------- figure lists (parsed from OCR)

FIG_LISTS = {  # ia -> (ia whose OCR holds the cleanest copy of the list, first n, last n, style)
    "ancientmonuments00squi": ("ancientmonuments00squi", 32, 37, "plain"),
    "antiquitiesofwis00saph": ("antiquitiesofwis00saph", 16, 17, "plain"),
    # The Smithsonian scan's OCR splits the list into columns; the BPL copy of the same report
    # (annualreportofbu9091smit, leaves n65-n71) has it clean. Printed page numbers are the same in every copy.
    "annualreportofbu1218901891smit": ("annualreportofbu9091smit", 65, 71, "plain"),
    "b24849959": ("b24849959", 18, 23, "fowke"),
    "earthworkenglan01allcgoog": ("earthworkenglan01allcgoog", 16, 22, "plain"),
}
FIG_COUNT = {"ancientmonuments00squi": 207, "antiquitiesofwis00saph": 61, "annualreportofbu1218901891smit": 344,
             "b24849959": 303, "earthworkenglan01allcgoog": 224}

OTHER_RE = re.compile(
    r"\b(sections?|vertical|horizontal section|pipes?|vessels?|pots?|pottery|skulls?|crani|copper|shells?|axes?|"
    r"implements?|ornaments?|views?|elevation|burials?|graves?|beads?|gorgets?|sculptures?|sculptured|tubes?|bones?|"
    r"silver|medal|images?|cloth|weaving|tools?|knife|spear|bracelets?|altars?|hearth|fireplace|vaults?|bogus|"
    r"profiles?|restoration|engraved|tablets?|coins?|brooch|locket|spindles?|celts?|chisels?|arrow|perspective|"
    r"pendants?|terra cotta|heads?|toad|frog|bird|raven|eagle|serpent's head|stone heap|cast|casts|maize|lathing|"
    r"house|floor|hut|wigwam|dwelling|portrait|hieroglyphics|game|windfalls|beaver dam|septaria|stratified|"
    r"diagram|outline of mound|levels|natural|mica|antlers|plates? of|plate with|plate bearing|plate from|badge|"
    r"rattle|bell|hammer|specimens|sculpture of|duck-pond|weapon|urn|sword|brick|masonry|tower|keep|church)\b",
    re.I)
SITE_RE = re.compile(
    r"\b(plan|plat|map|works?|group|groups|inclosures?|enclosures?|forts?|fortified|camps?|circles?|squares?|"
    r"octagon|earthworks?|effig(y|ies)|serpent|embankments?|castles?|dykes?|ditch(es)?|entrenchments?|villages?|"
    r"towns?|settlement|parallels|graded way|mounds on|mounds near|mounds at|mound group|mounds,|rings?|burh|"
    r"motte|bury|beacon|barrows?|lynchets?|ramparts?|terraces?|fortification|hill-?fort|stronghold|redoubt|"
    r"moat|moated|walls|wark|wall)\b", re.I)
SINGLE_MOUND_RE = re.compile(r"^\s*(the\s+)?([\w'’]+\s+)?mound\b(?!s)", re.I)


SITEISH_RE = re.compile(r"mound|work|fort|circle|inclos|enclos|group|village|valley|effig|serpent|cross|camp|castle|"
                        r"earth|ring|dyke|ditch|moat|burial ground|graves|settlement|elephant|turtle|lizard|bird hill|"
                        r"man\b|elk|bear|buffalo|war club|row of|trefoil|tapir|opossum|gridiron|ellipse|lake", re.I)
OCR_FIX = [(r"mou[nu][d<][l]?|moun<l|mouu<l|motind|nu>uud|niouud|inouud|montKl|moiiiul|mounil", "mound"),
           (r"\buear\b", "near"), (r"iuclos", "inclos"), (r"\bPlau\b", "Plan"), (r"grouji", "group"),
           (r"[Ss]ectiou", "section"), (r"\biu\b", "in"), (r"\bou\b", "on"), (r"Mounils|Moun<ls", "Mounds")]


def kind_of(title, default="u"):
    t = title
    for a, b in OCR_FIX:
        t = re.sub(a, b, t)
    k = _kind(t.lower(), default)
    if k == "u" and not SITEISH_RE.search(t):
        k = "o"
    return k


def _kind(t, default):
    if re.search(r"plan of (the )?(burials?|altar|excavation|grave)", t):
        return "o"
    has_plan = re.search(r"\b(plan|plat|map)\b", t)
    if OTHER_RE.search(t) and not has_plan:
        return "o"
    if has_plan:
        return "s"
    if SINGLE_MOUND_RE.search(t):
        return "u"
    if SITE_RE.search(t):
        return "s"
    return default


def _clean(s):
    s = re.sub(r"[\s.\-_,:;'’•■=~—–—*]+$", "", s)
    s = re.sub(r"(\s*[.\-_•■=~]\s*){3,}", " ", s)
    return re.sub(r"\s+", " ", s).strip(" .,;:-—")


def parse_figures(ia_id):
    """Sequential parse: find 'k.' for k = 1..N in the list text; text up to the next entry is the title + page."""
    if ia_id not in FIG_LISTS:
        return []
    src, a, b, style = FIG_LISTS[ia_id]
    ps = ia.pages(src)
    T = ia.page_texts(src)
    text = "\n".join(T.get(ps[n]["leafNum"], "") for n in range(a, b + 1))
    N = FIG_COUNT[ia_id]
    if style == "fowke":
        pat = lambda k: re.compile(r"Figures?\s+%d\b(?:\s*(?:and|to)\s*(\d+))?\s*\.?\s*[—\-–]+" % k)
    else:
        pat = lambda k: re.compile(r"(?:(?<=\s)|^)%d\s*[.,:;]\s+(?=[A-Z\"“'‘*(])" % k, re.M)
    hits = []
    pos = 0
    for k in range(1, N + 1):
        m = pat(k).search(text, pos, pos + 1500)
        if not m and k >= 20:  # numbers lost for a stretch (columns split by OCR): look further ahead
            m = pat(k).search(text, pos)
        if m:
            hits.append((k, m.start(), m.end(), m.group(1) if style == "fowke" and m.lastindex else None))
            pos = m.end()
    out = []
    default = "s" if ia_id == "earthworkenglan01allcgoog" else "u"
    prev_title = ""
    for i, (k, s0, e0, k2) in enumerate(hits):
        end = hits[i + 1][1] if i + 1 < len(hits) else min(len(text), e0 + 200)
        # page = number ending the first line of the entry that ends in a number (an entry may wrap onto a
        # second line; if the next entry's number was lost to OCR, its text follows and must not be used)
        body_lines = text[e0:end].split("\n")
        page, title = None, None
        acc = ""
        for line in body_lines:
            m = re.search(r"(\d{1,3})(?:\s*[-—,]\s*(\d{1,3}))?[\s.,'’<\-]*$", line.strip())
            if m and (acc or line.strip()[:m.start()].strip()):
                page = int(m.group(1))
                title = _clean(acc + " " + line.strip()[:m.start()])
                break
            acc += " " + line.strip()
        if title is None:  # no line ends in a number: last number within the first two lines
            two = " ".join(l.strip() for l in body_lines[:2])
            m = re.search(r"(\d{1,3})(?:\s*[-—,]\s*(\d{1,3}))?[^\d]{0,8}$", two)
            page = int(m.group(1)) if m else None
            title = _clean(two[:m.start()] if m else two)
        if re.match(r"^(do|ditto)\b", title, re.I):  # "Do. do." = same as previous title
            title = prev_title + " [do.]"
        else:
            prev_title = title
        if page is not None and not (1 <= page <= 1000):
            page = None
        last = int(k2) if k2 else k
        for kk in range(k, last + 1):
            out.append(dict(fig=kk, title=title, page=page, kind=kind_of(title, default)))
    # pages must run in order: drop a page that is below the last good one or above the next few parsed ones
    good = None
    for i, f in enumerate(out):
        if f["page"] is None:
            continue
        nxt = [g["page"] for g in out[i + 1:i + 4] if g["page"] is not None]
        if (good is not None and f["page"] < good) or (nxt and f["page"] > max(nxt) + 2):
            f["page_ocr"], f["page"] = f["page"], None
        else:
            good = f["page"]
    ov = KIND_OVERRIDES.get(ia_id, {})
    for f in out:
        if f["fig"] in ov:
            f["kind"], f["kind_by"] = ov[f["fig"]], "hand"
    return out


def _ov(spec):
    d = {}
    for part in spec.split():
        figs, k = part.split(":")
        for x in figs.split(","):
            a, _, b = x.partition("-")
            for i in range(int(a), int(b or a) + 1):
                d[i] = k
    return d


# Hand corrections to the title rules, judged from the printed title (and, where noted in summary.md, the page).
KIND_OVERRIDES = {
    # 19 and 20 are perspective views (checked on the pages n183, n193), not plans.
    "ancientmonuments00squi": _ov("3,9,15,23,58,59,61,66,67,207:u 12,57,60:s 27,51,92,98,101,104,105,107,118,121,"
                                  "140,150-152,195-206,53,70,19,20:o"),
    "antiquitiesofwis00saph": _ov("1,5,6,9,10,13,17,18,19,21,22,23,24,26,27,28,29:s 25,30,35:u 3,4,8,11,15,20,53,58:o"),
    "annualreportofbu1218901891smit": _ov(
        "3,4,6,8,14,16,18,20,21,22,23,44,45,54,66,70,74,84,86,88,93,96,107,119,135,149,154,161,165,270,275,276,293,"
        "303,317,326,334,339:s 24,53,67,110,136,162,177,183,207,208,223,234,288,322,325,327:u "
        "100,109,152,153,157,191,206,212,222,232,255,273,281,301,337,340,343,344:o"),
    "b24849959": _ov("1,10,19,20,23,24,35,42,44,48,73,78,80,81,82,85,86,88,98,234:s 4,64-66,99,100,112,235:u "
                     "89-92,95,105,110,118,121,125,127,129,130-138,159-188,199,200,212,236-266,279,280:o"),
    "earthworkenglan01allcgoog": _ov("1,2,168,218:s 82:o"),
}


# ---------------------------------------------------------------- hand transcriptions (the view books)

# Per-leaf transcription of the artists'-view books' own plates: one line per plate (a double-page or a
# 4-page spread is one line; a leaf carrying two entries gets two lines, the o row before the s row):
# fig|title|page|kind|kind_by. fig = the leaf's own n ('' = the plate has no leaf in the item - fold-out-only
# or unengraved; the index skips it, validate counts it as nopage). kind: o = town view - a drawing in its own
# right (GOAL.md point 5); s = bird's-eye plan (Merian: "im Grund"); u = excluded from the drawings (regional
# maps, natural features, a coin sheet, faded blank fold-out versos, a town's coat of arms). kind_by: hand =
# read from the plate pages (213 for civitates; 217's image-checked readings for Merian), A = the stage A page
# type (a view leaf that is not a plan). data/books/lists/<ia>.json is this table's dump (cmd_ocrmap
# regenerates it, ensure_ascii=False for these books: the printed titles keep their own diacritics). One place
# for the knowledge, the file is the dump.
HAND_FIGS = {"civitatesorbiste00brau": """
4|CIVITATIS ORBIS TERRARVM||o|A
29|LONDINVM FELICIAE REGN||o|A
30|SSIMI AN TROPOLIS||o|A
33|LISBOO CASCALE Lusitaniae opp.||o|A
34|OLISIPO, SIVE VT PERVE TVSTA LAPIDVM INSCRIPTIO NES HABENT, VLYSIPPO, VVLGO LISBONA FLORENTIS SIMVM PORTVGALLIAE EMPORIVM.||o|A
37|MALAGA||o|A
38|SEVILLA CADIZ MACE||o|A
41|TOLETVM VALLISOLETVM||o|A
42|ALLISOLETVM||o|A
45|Ormus.||o|A
46|Granada||o|A
49|BARCELONA||o|A
50|Cum Privilegio [other plate: inland view; 'Depingit G. Gorizius 1587']||o|hand
53|Burgos + S. Sebastian||o|hand
54|BVRGOS celebris et antiqua Hispaniae civitas, quae Auca, Brautum, Masburgi, Li conitiurgis, nomina habet [other plate: SANCT. SEBASTIANVM vulgo Donostien ad mare Oceanum insigne regni Guipuzcoa oppidum]||o|hand
57|VTELLA, vulgari nomine Paris, urbs||o|A
58|LVTETIA PARISIORVM||s|hand
61|MONS PESSULVVS. MONTPELLIER||o|A
62|TVRO. TOVRS.||o|A
65|ROTOMAGVS. VVIGO. KORN. NOR. MAGNÆ METROPOLIS||o|A
66|ROAN||o|A
69|LE ROSNE||o|A
70|Lyon Qui de la France||o|A
73|LEO||o|A
74|DIV M. LIEGE||o|A
77|MAGDEBURG||o|A
78|AQVISGRA NVM, VRBS PRÆ CLARISSIMA. PRIMVM, INTER QVATVOR IMPE RII CIVITATES, LOCVM OBTINET.||o|A
81|MONTES, HANNO NIAE METROPOLIS.||o|A
82|ATREBATVM, EPISCO PALIS ET METROPOLITI CA ARTESIA CIVITAS||o|A
85|BRVXELLA||s|hand
86|BRVXELLA, vrbs aulico rum frequentia, fontium copia, magnificentia principalis aulæ, Castræ domus, ac plurium aliarum splendore, nobilissima.||o|hand
89|GANDANVM||o|A
90|GANDANVM||s|hand
93|BRVGA, vulgo Brügge-Teuto: niae Flandriae urbs omnium pulcherrima||o|A
94|ORICARVM AMENTA.||o|A
97|ANVERP. PARS FLANDRIAE||o|hand
98|ANVERPIA||s|hand
101|TSHERTO LOE MAC||o|A
102|GENBOSCH EN. ELEN.||o|A
105|TRAIECTVM CLARA ET VETVS EST EPISCOPALIS CIVITAS||o|A
106|RAETVM||o|A
109|AMSTELEDAVM||s|hand
110|AMSTELEDAVM||o|A
113|GROENINGA. BROVERSAVIA.||o|A
114|INGA. GORICVM, NO BILE HOLLANDI Æ. OPPIDVM.||o|A
117|MONASTERIVM, Wesalia Inferior.||o|A
118|OSNABRUGVM E L. GANS SAXONIAE OPP.||o|A
121|LUNEBVRGVM, NOBILIS SAXONIAE VRBS, SALINIS CELEBERRIMA. BREMA.||o|A
122|BRVNOPOLIS VVLGO BRVNSVICVM, BRAVNSCHWICH. VR.BS MAXIMA, V NIVERSA. Saxonis Metropolis. ALDENBVREGVM HOLSATIA.||o|A
125|LVBECA VRBIS IMPERIALIS DALICARVM, ET INCLYTÆ||o|A
126|HAMBURGA, CIVITATVM WANSEATICA SOCIETATIS CAPVT||o|A
129|WEIMAR IENA GOTHA||o|A
130|WEIMARIA NOBILE THV RINGIAE OPP. ILLVST. SAX ONIA. DVCVM SAED. E.||o|A
133|M A R C A S S||o|A
134|MARTPVRGVM VRBS HASSIAE METROPOLIS, VNIVERSITATE CLARA. CASSVLA, communiter Castel, florentissimum langerae Hassiae oppidum||o|A
137|WITTENBURGA, WISMARIA||o|A
138|CIVITAS FRANCFORDIENSIS ROSTOCHIVM||o|A
141|DRES LEI||o|A
142|Alte Drefzden. BZIGK||o|A
145|PRA GA E G||o|A
146|G A. R A.||o|A
149|MAGDEBURGVM||o|A
150|ARGVM.||o|A
153|VRBIS SALISBV RG GEN. SIS GENVINA DE. SCRIPTIO||o|A
154|LINDOLIA, oppidum superij insulare, undique aqua acromi lacis circumfusum||o|A
157|DECEM ET TRIA LOCA CON||o|hand
158|FEDERATORVM HELVETIAE||o|hand
161|ARGENTORATVM.||o|A
162|Strasburg||o|A
165|WORMATIA||o|A
166|IDELBERGA. PIRA.||o|A
169|CIVITAS FRANCO||o|A
170|TRANCORDELLE||o|A
173|TREVERIS COBOL ROTEN||o|A
174|TYPVS AC SITVS ANTIQVISSIMÆ ET PRÆCIPVÆ MEDIOMATRI CVM CIVITATIS TREVIRENSIS||o|A
177|MOGVN TIA, Germaniæ Metropolis, ad Rheni ripas Vrbis cele||o|A
178|SITTEN||o|A
181|De Ponte et insula||o|A
182|COLONIA AGRIPPEA||o|A
185|AVGVSTVS||o|A
186|HABET DELINE||o|hand
187|AVGVSTA, verso of the fold-out||u|hand
189|MONACVM, NOMINATIS SIMA BAVARIAE CIVITAS. FRISINGENSIS Episcopalis civitatis icon. RATISPONA antiquissima Bavaria urbs, Danubij ripis adiacens.||o|A
190|OENIPONS. NOR.DLINGA. STRAVBINGA.||o|A
193|VIENNA AVSTRIAE [other plate: 'Danubius flu.' panorama; 'BVDA, vulgo...' cartouche]|2|o|hand
194|VIENNA AVSTRIAE|3|o|hand
197|Armes de ceste Ville de Milan||u|hand
198|MEDIOLANVM||o|hand
199|MEDIOLANVM, verso of the fold-out||u|hand
201|VENETIA||o|hand
202|VENETIA, verso of the fold-out||o|hand
205|FLORENTIA urbs est suffragio Heracius, alias Flacurios dicta, quod sita sit ad fluvium Arno fluminis [other plate: Genoa harbour; 'La sfortina']||o|hand
206|VA. FLORENTIA [other plate: 'GENVEA Ligurum...'; Cum Privilegio]||o|hand
209|ROMA||o|hand
210|CVM PRIVILEGIO||o|A
213|ANCONA||o|A
214|ANCONA||o|hand
217|NEAPOLIS||o|hand
218|NEAPOLIS||o|hand
221|PARMA||o|A
222|SENA. ERM. ANVM.||o|A
225|MESSANA||o|hand
226|MESSANÆ urbs est Siciliæ maxima, firu, opulentia, & tu...||o|A
229|CALARIS RHODVS||o|A
230|MALTA. FAMAVGVSTA.||o|A
233|BYZANTIUM Nunc Constantinopolis||o|A
234|ISTANBOLIS||o|A
237|Descriptio antiquae urbis Hierosolymorum, qua amplitudine et splendore tempore Christi Salvatoris nosteri||s|hand
238|Nova urbis Hierosolymitanae descriptio, quia forma. Q. sita naturo fecile se conficiendam praestat.||s|hand
241|MOMBAZA||o|A
242|Cum Privilegio||o|A
245|CALECHV MVM INDI ORMVVS.||o|A
246|EBERRI PORIVM.||o|A
249|ARUS, QVÆ OLIM BABYLON||o|A
250|CIVITAS MAXIMA VRBS||o|A
253|TINGIS, LVSTITANIS, TANGIARA. SEPTA. ARZILLA||o|A
254|TZAFFIN. SALA.||o|A
257|GOA fortissima Indiae urbs in Christo fiantorum||o|A
258|AZAAMVRVM.||o|A
261|MEXICO.||o|A
262|CUSCO, REGNI PERU IN NOVO ORBE CAPVT.||o|A
""",
             "topographiahelve00zeil": """
16|Tafel des Teutschlands|10|u|hand
24|der Endgnoschaffte|15|u|hand
|Elgaw und Murrz|16|o|hand
32|Zurich im Grund|17|s|hand
36|Tigurvm (Zurich im Prospect)|17|o|hand
42|Forsteck. FORSTECK.|19|o|hand
|Eglisaw, Grüningen, Griffensee und Regensperg|20|o|hand
52|Stein am Rhein|21|o|hand
58|Winterhur, Undelfingen und Kyburg|22|o|hand
|Willisaw und Wedeschwyl|23|o|hand
66|Bern die HauptStatt in Nüchternland|24|s|hand
|Thron|26|o|hand
80|Araw. Arberg. Arburg.|27|o|hand
72|Lentzburg. LENTZBURGV. + Brugg im Argaw. BRVG ARGOLIA.|27|o|hand
72|Habsburg. HASSBURGŰ.|27|o|hand
86|Burgdorff. BURGDORF.|28|o|hand
90|Lausanne|79|o|hand
94|THUNA. Thun.|31|o|hand
98|S. Peter. Bibiscum. [Beven]|31|o|hand
104|Abbildung des Gletschers im Grindelwalde in der Herrschafft Bern (GLATSCHER)|32|u|hand
110|Mürten. Neus. Nion. Aventicum. Vifffisburg.|34|o|hand
116|LVCERN.|36|o|hand
120|Abbildung der 4. Waldstätten See.|36|u|hand
124|SEMPACH. SEMPACHIUM.|37|o|hand
124|SURSEE.|37|s|hand
128|Ragus et Ecclesia Collegiata MUNSTER in Argovia (Der Flecken und Stift Münster im Argaw)|37|o|hand
134|Altorff Haupt flecken des Lands URY|38|o|hand
134|Flüelen|38|s|hand
138|SVITIA. Schwytz|39|o|hand
142|Prospect des Haubt Closters Schwytz|39|o|hand
146|Einsiedelen. INSVLA EREMI|39|o|hand
152|Das Landt Unterwalden|41|u|hand
|Engelberg|41|o|hand
160|TVGIVM. Zug.|43|o|hand
166|GLARONA. Glaris.|44|o|hand
172|Basel im Grund|46|s|hand
176|BASILEA im Prospect (2. Kupffer)|46|o|hand
180|Die Brück (Prospectvs Cathedrals, Pontis Rheni)|47|o|hand
184|CAMPVS DIVI PETRI (S. Peters Platz daselbst)|47|o|hand
190|Münchenstein|48|o|hand
194|Viechtstall [Lichtstall]|49|o|hand
198|WALLENBURG|49|o|hand
204|PIERRE PERTUISE|50|o|hand
208|Romamostier.|50|o|hand
214|Freÿburg in Üechtlandt. FRYBURGUM NUITONIA.|52|o|hand
218|SOLOTURVM|53|s|hand
224|Schaffhausen|54|o|hand
228|Eigentliche Bildnüß des Großen Wasserbruchs oder Falls des Rheins im Lauffen|55|u|hand
|Nünkirchen|55|s|hand
236|APPENZELL. + HERISSAW.|56|o|hand
240|Baden im Argov|57|o|hand
246|Klingnaw, Leuggern, Der mittlere Lauffen oder Fall des Rheins, Monast. Wettingen|58|o|hand
250|Heidnische Münzen vnd Silbergeschirr (Monetarum)|58|u|hand
254|Forvm Tyberii. Zurzach.|58|o|hand
258|BRENGGARTEN.|59|o|hand
|Lowerk und Wellenk|60|o|hand
268|Die Statt Dissenhofen... in grund gelegt im Jahr 1648|60|s|hand
272|FRAWENFELD. + MELLINGEN.|60|o|hand
276|RAP PERSWYL. Rapperswyl.|61|o|hand
|Pfeffers (2. Kupffer, 2 Ansichten)|63|o|hand
288|MULHUSIA ALSATIAE. Müllhausen.|65|s|hand
294|BIENNA. Biel.|66|o|hand
298|S. GALLEN.|67|s|hand
308|GENEVE. GENEVA. im Grund|70|s|hand
312|GENEUE. Genff im Prospect|71|o|hand
316|NEOCOMVM. Steinenburg am See. (2. Ansichten, 2 Kupffer)|72|o|hand
328|Weyerhauß. WEYERHAUS. (Castelen, Etiszwenyl)|77|o|hand
334|Chur. CURIA RHETIA.|79|o|hand
|Plürs|83|o|hand
348|Fontes Rheni anterioris et Posterioris (Ursprung des hinteren und Vorderen Rheins)|84|u|hand
350|S. Luzissteig in Vünken sambt Alter Demolierten vnd Neuen Schantzen|85|o|hand
356|Leugg|87|o|hand
362|PRYG. NATERS.|88|o|hand
|Bisp/ oder Bispach|88|o|hand
368|S. Mauritus in Valessia. S. Mairise in Walls|89|o|hand
374|SEDUNVM. Sitten|90|o|hand
378|Breiten Landenberg im Zürrcher Gebiet. BRAITEN LANDEIBERG in Territorio Tigurino|90|o|hand
|Chastillard und Blonay|90|o|hand
|Sandeck und Mauwister|90|o|hand
384|WERDENSTEIN. Kloster S. Urban|90|o|hand
"""}


def parse_hand_figures(ia_id):
    """The per-leaf hand table: one entry per plate leaf, keyed by the leaf's own n (fig); page stays a string.
    fig '' = the plate has no leaf in the item (fold-out-only or unengraved): fig is None - validate counts
    those entries as nopage, and list_pages/index skip them."""
    txt = HAND_FIGS.get(ia_id)
    if txt is None:
        return []
    out = []
    for line in txt.strip().splitlines():
        fig, title, page, kind, kind_by = line.split("|")
        out.append(dict(fig=None if fig == "" else int(fig), title=title,
                        page=None if page == "" else page, kind=kind, kind_by=kind_by))
    return out


def figure_list(ia_id):
    """The book's figure list: parsed from its list page's OCR, or the per-leaf hand table where there is none."""
    return parse_figures(ia_id) or parse_hand_figures(ia_id)


# ---------------------------------------------------------------- page numbers -> leaves

def pagenum_map(ia_id):
    """printed page number -> n. IA's own pageNum where present, filled across gaps only where consistent."""
    ps = ia.pages(ia_id)
    known = [(p["n"], int(p["pageNum"])) for p in ps if str(p.get("pageNum", "")).isdigit()]
    m = {}
    for n, pg in known:
        m.setdefault(pg, n)
    for (n0, p0), (n1, p1) in zip(known, known[1:]):
        if n1 - n0 == p1 - p0 and n1 - n0 > 1:
            for j in range(1, n1 - n0):
                m.setdefault(p0 + j, n0 + j)
    return m


# ---------------------------------------------------------------- plate leaves (ground-truth mapping)

STOPWORDS = set("the and of to in is which was that with this from were are for by on at as".split())
ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


def roman(s):
    s = s.upper().strip(" .,")
    if not s or any(c not in ROMAN for c in s):
        return None
    v = 0
    for a, b in zip(s, s[1:] + " "):
        v += -ROMAN[a] if b != " " and ROMAN[a] < ROMAN.get(b, 0) else ROMAN[a]
    return v


def _title_tokens(t):
    t = re.sub(r"[^a-z ]+", " ", (t or "").lower())
    return [w for w in t.split() if len(w) > 2 and w not in ("the", "and", "near", "county", "ohio", "plan", "plat",
                                                             "map", "ancient", "works", "work")]


def ocr_numerals(text):
    """Plate numerals printed in a plate's own header and picked up by IA's OCR: 'PL. XXXI', 'PLATE XXV'."""
    out = set()
    for m in re.finditer(r"\b(?:PL|Pl|PLATE|Plate)\s*[.,]?\s*([IVXLivxl]{1,8})\b", text or ""):
        v = roman(m.group(1))
        if v:
            out.add(v)
    return out


def numerals_in(numbers):
    """Roman plate numerals Qwen read on a page ('PLATE XXV', 'XVI.', 'Pl. XXI')."""
    out = set()
    for s in numbers or []:
        s = str(s)
        for _ in range(4):  # engraved numerals are letter-spaced: "X I." -> "XI"
            s = re.sub(r"\b([IVXL])\s+(?=[IVXL]{1,3}\b)", r"\1", s)
        if re.search(r"\bfig", s, re.I) or re.search(r"\bface\b|\bp\.\s*\d", s, re.I):
            continue
        for tok in re.findall(r"\b([IVXLC]{1,8})\b\.?", s.replace("PLATE", " ").replace("Plate", " ")
                              .replace("PL.", " ").replace("Pl.", " ")):
            v = roman(tok)
            if v:
                out.add(v)
    return out


def map_plates(ia_id, plates, A):
    """Plate numeral -> n. Anchors: leaves where Qwen read the numeral, kept only if they increase with the leaf
    order. Between anchors, unnumbered inked leaves are assigned in order when their count matches the plates
    expected there. Returns {numeral_value: (n, method)}."""
    ps = ia.pages(ia_id)
    vals = []
    for p in plates:
        v = roman(p["plate"])
        if v and v not in vals:
            vals.append(v)
    T = ia.page_texts(ia_id)
    cand = []
    for p in ps:
        # IA's pageNum is not used here: in Lapham it numbers the plate leaves straight on from the text.
        if not os.path.exists(triage_path(ia_id, p["n"])):
            continue
        # no running text: plates OCR to garbage, text pages (even with a figure) have >= 45 of these words
        sw = sum(1 for w in re.findall(r"[a-z]+", T.get(p["leafNum"], "")) if w in STOPWORDS)
        if ink(ia_id, p["n"]) > 0.004 and sw < 20:
            cand.append(p["n"])
    # Anchor evidence per (leaf, plate): Qwen read the numeral (1), IA's OCR of the plate header has it (1),
    # Qwen's caption matches the list title (1.5 x similarity). The plate order must increase with the leaf
    # order, so the best-scoring increasing chain wins (a misread "XXXII" on the Octagon plate loses to its
    # caption "OCTAGON, NEWARK" matching Plate XXXIII). Ties go to the larger scan (unfolded fold-out).
    titles = defaultdict(list)
    for p in plates:
        titles[roman(p["plate"])].append(p["title"])
    area = {p["n"]: p["width"] * p["height"] for p in ps}
    amax = max(area.values())
    score, src = {}, {}
    for n in cand:
        out = A.get(n, {}).get("out", {}) if n in A else {}
        q = numerals_in(out.get("numbers"))
        o = ocr_numerals(T.get(ps[n]["leafNum"], ""))
        cap = set(_title_tokens(out.get("caption") or ""))
        for v in vals:
            sc, how = 0.0, []
            if v in q:
                sc += 1; how.append("qwen")
            if v in o:
                sc += 1; how.append("ocr")
            if cap:
                sim = max((len(cap & set(_title_tokens(t))) / max(1, len(set(_title_tokens(t)) | cap))
                           for t in titles[v]), default=0)
                if sim >= 0.5:
                    sc += 1.5 * sim; how.append("title")
            if sc > 0:
                score[(n, v)] = sc + 0.01 * area[n] / amax
                src[(n, v)] = "+".join(how)
    anchors = sorted(score)
    dp, prev = [], []
    for i, (n, v) in enumerate(anchors):
        best_j, best_s = None, 0.0
        for j in range(i):
            if anchors[j][0] < n and anchors[j][1] < v and dp[j] > best_s:
                best_j, best_s = j, dp[j]
        dp.append(best_s + score[(n, v)])
        prev.append(best_j)
    chain = []
    if dp:
        i = max(range(len(dp)), key=lambda k: dp[k])
        while i is not None:
            chain.append(anchors[i])
            i = prev[i]
    chain.reverse()
    res = {v: (n, src[(n, v)]) for n, v in chain}
    bounds = [(-1, 0)] + chain + [(10 ** 9, 10 ** 9)]
    for (n0, v0), (n1, v1) in zip(bounds, bounds[1:]):
        want = [v for v in vals if v0 < v < v1]
        have = [n for n in cand if n0 < n < n1 and n not in {x for x, _ in chain}]
        if want and len(want) == len(have):
            for v, n in zip(want, have):
                res[v] = (n, "order")
    return res, cand


# ---------------------------------------------------------------- validation

def plate_key(p):
    return roman(p["plate"])


def validate_book(key):
    b = BOOKS[key]
    ia_id = b["ia"]
    A = stage_a(ia_id)
    if not A:
        return None
    ps = ia.pages(ia_id)
    rep = {"book": key, "ia": ia_id, "pages": len(ps), "triaged_A": len(A)}
    flagged_a = {n for n, r in A.items() if r["out"].get("page_type") in SITE_TYPES}
    F = stage_f(ia_id)
    flagged = site_pages_qwen(ia_id)
    rep["flagged_site_pages_stageA"] = len(flagged_a)
    rep["stageF_pages"] = len(F)
    rep["flagged_site_pages"] = len(flagged)
    plates = parse_plates(ia_id) if ia_id != "b30449492" else squier_ny_gt()
    plate_leaves = set()
    if plates:
        by_num = defaultdict(list)
        for p in plates:
            by_num[plate_key(p)].append(p)
        kinds = {v: ("s" if any(e["kind"] == "s" for e in es) else "u" if any(e["kind"] == "u" for e in es) else "o")
                 for v, es in by_num.items()}
        pm, cand = map_plates(ia_id, plates, A)
        plate_leaves = {n for n, _ in pm.values()}
        site = [v for v, k in kinds.items() if k == "s"]
        other = [v for v, k in kinds.items() if k == "o"]
        mapped_site = [v for v in site if v in pm]
        det = [v for v in mapped_site if pm[v][0] in flagged]
        read = [v for v in mapped_site if v in numerals_in(A.get(pm[v][0], {}).get("out", {}).get("numbers"))]
        fp_other = [v for v in other if v in pm and pm[v][0] in flagged]
        rep["plates"] = {
            "listed": len(by_num), "site": len(site), "other": len(other), "unsure": len(kinds) - len(site) - len(other),
            "site_mapped_to_leaf": len(mapped_site),
            "mapped_by": dict(sorted(Counter(m for _, m in pm.values()).items())),
            "recall_site_plan_type": round(len(det) / len(mapped_site), 3) if mapped_site else None,
            "qwen_read_numeral_on_site_plates": round(len(read) / len(mapped_site), 3) if mapped_site else None,
            "other_plates_flagged_as_site": f"{len(fp_other)}/{len([v for v in other if v in pm])}",
            "missed": [dict(plate=v, n=pm[v][0], qwen=A.get(pm[v][0], {}).get("out")) for v in mapped_site
                       if v not in det],
            "unmapped_site": [v for v in site if v not in pm],
            "map": {str(v): pm[v] for v in sorted(pm)},
        }
    figs = figure_list(ia_id)
    if figs:
        pmap = {} if ia_id in HAND_FIGS else pagenum_map(ia_id)
        gt_site, gt_unsure, gt_other, nopage = set(), set(), set(), 0
        for f in figs:
            n = f["fig"] if ia_id in HAND_FIGS else (pmap.get(f["page"]) if f["page"] else None)
            if n is None:
                nopage += 1
                continue
            f["n"] = n
            {"s": gt_site, "u": gt_unsure, "o": gt_other}[f["kind"]].add(n)
        gt_only_other = gt_other - gt_site - gt_unsure

        def pr(flg):
            fl = flg - plate_leaves
            return {"recall": round(len(gt_site & flg) / len(gt_site), 3) if gt_site else None,
                    "precision_strict": round(len(fl & gt_site) / len(fl), 3) if fl else None,
                    "precision_lenient": round(len(fl & (gt_site | gt_unsure)) / len(fl), 3) if fl else None,
                    "flagged": len(fl)}
        stage_a_only = pr(flagged_a)
        fl = flagged - plate_leaves
        hit = gt_site & flagged
        hit1 = {n for n in gt_site if {n - 1, n, n + 1} & flagged}
        rep["figures"] = {
            "listed": len(figs), "expected": FIG_COUNT.get(ia_id),
            "parsed_with_page_on_a_leaf": len(figs) - nopage,
            "site": sum(f["kind"] == "s" for f in figs), "unsure": sum(f["kind"] == "u" for f in figs),
            "other": sum(f["kind"] == "o" for f in figs),
            "gt_site_pages": len(gt_site),
            "recall_pages": round(len(hit) / len(gt_site), 3) if gt_site else None,
            "recall_pages_pm1": round(len(hit1) / len(gt_site), 3) if gt_site else None,
            "flagged_nonplate_pages": len(fl),
            "precision_strict": round(len(fl & gt_site) / len(fl), 3) if fl else None,
            "precision_lenient": round(len(fl & (gt_site | gt_unsure)) / len(fl), 3) if fl else None,
            "flagged_on_other_only_pages": sorted(fl & gt_only_other),
            "flagged_not_in_list": sorted(fl - gt_site - gt_unsure - gt_other),
            "missed_pages": sorted(gt_site - flagged),
            "stage_A_only": stage_a_only,
        }
    return rep


def cmd_validate(args):
    reps = [r for r in (validate_book(k) for k in (args or BOOKS)) if r]
    p = os.path.join(OUT, "validation.json")
    old = {}
    if os.path.exists(p):
        old = {r["book"]: r for r in json.load(open(p))}
    for r in reps:
        old[r["book"]] = r
    json.dump(list(old.values()), open(p, "w"), indent=1)
    for r in reps:
        print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items()
                                                                  if kk not in ("map", "missed")})
                          for k, v in r.items()}, indent=1)[:3000])


# ---------------------------------------------------------------- list -> leaves, index

def list_pages(key):
    """{n: [list entries]} for site-plan (kind s) and unsure (kind u) entries, mapped to leaves; for the view
    books (HAND_FIGS) the town views (kind o) count too, mapped by their own leaf n."""
    ia_id = BOOKS[key]["ia"]
    A = stage_a(ia_id)
    out = defaultdict(list)
    plates = parse_plates(ia_id) if ia_id != "b30449492" else (squier_ny_gt() if ia_id == "b30449492" else None)
    if ia_id in ("ArcheologicalAtlasOfOhio",):
        plates = None
    if plates:
        pm, _ = map_plates(ia_id, plates, A)
        for p in plates:
            v = roman(p["plate"])
            if v in pm and p["kind"] in "su":
                out[pm[v][0]].append(dict(p, type="plate", map_method=pm[v][1]))
    pmap = {} if ia_id in HAND_FIGS else pagenum_map(ia_id)
    for f in figure_list(ia_id):
        n = f["fig"] if ia_id in HAND_FIGS else (pmap.get(f["page"]) if f["page"] else None)
        if n is not None and f["kind"] in ("so" if ia_id in HAND_FIGS else "su"):
            out[n].append(dict(f, type="figure"))
    return out


def cmd_ocrmap(args):
    for key in args or BOOKS:
        ia_id = BOOKS[key]["ia"]
        plates = parse_plates(ia_id) if ia_id != "b30449492" else squier_ny_gt()
        figs = figure_list(ia_id)
        if not plates and not figs:
            # No list source for this book (PLATES, FIG_LISTS and HAND_FIGS all absent, e.g. mills): never write
            # its list file - a hand transcription might live there and a re-derive would clobber it.
            p = os.path.join(OUT, "lists", f"{ia_id}.json")
            kept = f"; keeping the existing {os.path.relpath(p, ROOT)}" if os.path.exists(p) else ""
            print(f"{key}: no list yet (no OCR list source){kept}")
            continue
        os.makedirs(os.path.join(OUT, "lists"), exist_ok=True)
        # The hand books' list file is the dump of their table: raw UTF-8 (the printed titles keep their own
        # diacritics). The OCR-parsed books keep the default ascii escapes - byte identity with their committed
        # files is an invariant (216).
        json.dump({"plates": plates, "figures": figs}, open(os.path.join(OUT, "lists", f"{ia_id}.json"), "w"),
                  indent=0, ensure_ascii=(ia_id not in HAND_FIGS))
        lp = list_pages(key) if stage_a(ia_id) else {}
        m = [{"n": n, "site_plan": any(e["kind"] == "s" for e in es), "entries": es} for n, es in sorted(lp.items())]
        json.dump(m, open(os.path.join(OUT, "lists", f"{ia_id}.map.json"), "w"), indent=0,
                  ensure_ascii=(ia_id not in HAND_FIGS))
        print(key, "plates", len(plates or []), "figures", len(figs),
              "fig kinds", {k: sum(f["kind"] == k for f in figs) for k in "suo"}, "list leaves", len(m))


def _sub_of(label):
    m = re.search(r"(?:No|N°|Nº|Fig)\.?\s*(\d+|[A-Z])\b", label or "", re.I)
    return m.group(1) if m else None


def north_angle(pl, size):
    """Degrees clockwise from page-up to the arrow's north end, from Qwen's two end points (0-1000 per axis)."""
    import math
    t, b = pl.get("north_tip"), pl.get("south_end")
    if not size or not (isinstance(t, list) and isinstance(b, list) and len(t) == 2 and len(b) == 2):
        return None
    try:
        dx = (float(t[0]) - float(b[0])) * size[0] / 1000
        dy = (float(t[1]) - float(b[1])) * size[1] / 1000
    except (TypeError, ValueError):
        return None
    if abs(dx) + abs(dy) < 1:
        return None
    return round(math.degrees(math.atan2(dx, -dy)), 1)


def box01(b):
    if not isinstance(b, (list, tuple)) or len(b) != 4:
        return None
    try:
        x0, y0, x1, y1 = [max(0.0, min(1.0, float(v) / 1000)) for v in b]
    except (TypeError, ValueError):
        return None
    if x1 <= x0 or y1 <= y0:
        return None
    return [round(x0, 4), round(y0, 4), round(x1, 4), round(y1, 4)]


CAP_RE = re.compile(r"F\s*[Ii1l]\s*[Gg]\s*[.,]?\s*(\d{1,3})\s*[a-zA-Z]?\s*[.,:]?\s*[-—–~]+\s*([^\n]{3,90}?)"
                    r"(?:\.\s*$|\.\s|$)", re.M)


def ocr_captions(ia_id, txt):
    """Printed figure captions ("FIG. 109.—ARDOCH, PERTHSHIRE.") found in one leaf's IA OCR text: [(fig, title)].
    Kept only when short (<= 8 words: a caption, not running text) and the number is within the book's figure count."""
    out = []
    for m in CAP_RE.finditer(txt or ""):
        fig, title = int(m.group(1)), re.sub(r"\s+", " ", m.group(2)).strip(" ,;:")
        if 0 < fig <= FIG_COUNT.get(ia_id, 999) and 1 <= len(title.split()) <= 8 and not title.startswith('"'):
            out.append((fig, title))
    return out


def cmd_index(args):
    from books import BOOKS as BK
    rows = []
    for key in args or BK:
        b = BK[key]
        ia_id = b["ia"]
        A, B = stage_a(ia_id), stage_b(ia_id)
        if not A:
            continue
        view_book = ia_id in HAND_FIGS
        ps = ia.pages(ia_id)
        lp = list_pages(key)
        if view_book:
            # The view book's IA hOCR is misaligned (213's pitfall): never read it - the titles come from the
            # hand list.
            T = {}
        else:
            try:
                T = ia.page_texts(ia_id)
            except Exception as e:  # Mills has no hOCR page index on IA (404)
                print(key, "no per-page OCR:", e)
                T = {}
        pages = {}
        for n, how in site_pages_model(ia_id).items():
            pages.setdefault(n, set()).add(how)
        # a fold-out scanned folded (halves) next to the same plate scanned unfolded: keep the unfolded one
        mapped = {n for n, es in lp.items() if any(e["type"] == "plate" for e in es)}
        area = {p["n"]: p["width"] * p["height"] for p in ps}
        partial = {}
        for n in list(pages):
            if n in mapped or A.get(n, {}).get("out", {}).get("page_type") != "plate_site_plan":
                continue
            near = [m for m in mapped if abs(m - n) <= 4 and area[m] >= 1.3 * area[n]]
            if near:
                partial[n] = min(near, key=lambda m: abs(m - n))
                del pages[n]
        if partial:
            print(key, "folded halves dropped (leaf -> unfolded leaf):", partial)
        for n, es in lp.items():
            if any(e["kind"] == "s" for e in es):
                pages.setdefault(n, set()).add("list")
            elif any(e["kind"] == "o" for e in es):
                pages.setdefault(n, set()).add("list_view")
            elif n in pages:
                pages[n].add("list_unsure")
        for n in sorted(pages):
            p = ps[n]
            es = lp.get(n, [])
            a = A.get(n, {}).get("out", {})
            plans = (B.get(n, {}).get("out") or {}).get("plans") or [{}]
            if not isinstance(plans, list):
                plans = [{}]
            blanks = [dict(kind=x.get("kind"), box=box01(x.get("box")))
                      for x in ((B.get(n, {}).get("out") or {}).get("blank_boxes") or []) if isinstance(x, dict)]
            blanks = [x for x in blanks if x["box"]]
            plate_es = [e for e in es if e["type"] == "plate"]
            fig_es = [e for e in es if e["type"] == "figure" and (e["kind"] == "s" or (view_book and e["kind"] == "o"))]
            # No stage B (no per-plan reading): one row per site entry the book's list puts on this leaf.
            site_es = [e for e in plate_es if e["kind"] == "s"] or fig_es
            per_entry = not B.get(n) and len(site_es) > 1
            if per_entry:
                plans = [{} for _ in site_es]
            caps = ocr_captions(ia_id, T.get(p["leafNum"]))
            qtitle = a.get("caption") or " / ".join(t for t in (a.get("titles") or []) if t) or None
            for k, pl in enumerate(plans):
                pl = pl if isinstance(pl, dict) else {}
                sub = _sub_of(pl.get("label"))
                entry = site_es[k] if per_entry else None
                if per_entry:
                    pass
                elif plate_es:
                    entry = next((e for e in plate_es if e["sub"] and sub and e["sub"] == sub), None)
                    if entry is None and k == 0:
                        entry = next((e for e in plate_es if not e["sub"] or e["sub"] in ("1",)), plate_es[0])
                elif fig_es:
                    entry = next((e for e in fig_es if sub and str(e["fig"]) == sub), None)
                    if entry is None and len(fig_es) == 1 and len(plans) == 1:
                        entry = fig_es[0]
                rows.append({
                    "id": f"{ia_id}_n{n:04d}_{k + 1}",
                    "book": key, "ia_id": ia_id, "cite": b["cite"],
                    "leaf_n": n, "leaf_jp2": p["leafNum"], "page_printed": p.get("pageNum"),
                    "page_type": a.get("page_type") or ("plate_site_plan" if plate_es else "figure_site_plan"),
                    **({"view": (entry["kind"] == "o") if entry else True} if view_book else {}),
                    "found_by": sorted(pages[n]),
                    "plate": entry["plate"] if entry and entry["type"] == "plate" else
                    (plate_es[0]["plate"] if plate_es else None),
                    "sub": entry["sub"] if entry and entry["type"] == "plate" else None,
                    "fig": entry["fig"] if entry and entry["type"] == "figure" else
                    (caps[0][0] if len(caps) == 1 and len(plans) == 1 and not plate_es else None),
                    "title": entry["title"] if entry else (pl.get("title") or qtitle or
                                                           (" / ".join(c[1] for c in caps) if caps else None)),
                    "title_source": ("book's list of plates, transcribed" if entry["type"] == "plate" else
                                     ("book's figure list, hand-transcribed" if view_book else
                                      "book's list of figures, IA OCR (OCR errors kept)")) if entry else
                    ("page, read by Qwen" if pl.get("title") or qtitle else
                     ("caption on the page, IA OCR (OCR errors kept)" if caps else None)),
                    "captions_ocr": [f"Fig. {c[0]}. {c[1]}" for c in caps],
                    "title_on_page": pl.get("title") or None,
                    "label_on_page": pl.get("label") or None,
                    "numbers_on_page": a.get("numbers") or a.get("page_numbers"),
                    "site_names": pl.get("site_names") or [],
                    "place": pl.get("place") or None,
                    "scale_bar": pl.get("scale_bar"), "scale_text": pl.get("scale_text") or None,
                    "north_arrow": pl.get("north_arrow"),
                    "north_angle_deg": north_angle(pl, B.get(n, {}).get("img_size")),
                    "north_angle_note": "Qwen-read arrow end points; a hint only (see summary.md: wrong by 95-180 deg"
                                        " on 2 of 6 fitted plates)",
                    "map_box": box01(pl.get("map_box")),
                    "blank_boxes": blanks if k == 0 else [],
                    "boxes_convention": "fractions of page width/height, [x0, y0, x1, y1], origin top-left",
                    "plans_on_page": len(plans) if B.get(n) else None,
                    "stage_b": bool(B.get(n)),
                    "full_url": ia.full_url(ia_id, n),
                    "full_local": f"data/raw/books/{ia_id}/full/n{n:04d}.jpg",
                    "full_size": [p["width"], p["height"]],
                })
    with open(os.path.join(OUT, "index.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    from collections import Counter
    print(len(rows), "rows;", dict(Counter(r["book"] for r in rows)))
