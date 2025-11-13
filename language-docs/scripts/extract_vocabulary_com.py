#!/usr/bin/env python3
"""
Extract vocabulary words from Vocabulary.com scraped markdown data.
"""

import json
import re
from datetime import datetime

# Data from scraped markdown - Grade 6
grade_6_words = [
    "abundant", "authentic", "dedicate", "efficient", "forfeit", "intention", "loathe", "makeshift",
    "meager", "perceive", "prominent", "rigorous", "stealthy", "unanimous", "verify", "accumulate",
    "beneficial", "complexity", "diverge", "evade", "fatigue", "haste", "interpret", "mischievous",
    "persevere", "pulverize", "refrain", "reminisce", "solitude", "treacherous", "bewilder", "boycott",
    "condemn", "deteriorate", "emit", "feeble", "hoarse", "intervene", "momentum", "persistent",
    "ration", "reluctant", "scarce", "subsequent", "trudge", "acquire", "adapt", "consecutive",
    "determined", "elaborate", "excel", "hypothesis", "intricate", "mournful", "optimistic", "reassure",
    "sabotage", "serene", "sufficient", "waver", "adequate", "contemplate", "devastate", "evaluate",
    "factor", "immature", "interject", "linger", "nurture", "precision", "rebellion", "repetition",
    "shrill", "symbol", "unique", "apparent", "chronological", "commotion", "controversy", "diminish",
    "flammable", "frigid", "impair", "prediction", "prejudice", "represent", "stern", "sympathetic",
    "unruly", "variable", "appease", "arrogant", "cultivate", "distinguish", "exempt", "frustration",
    "inevitable", "lurch", "overwhelm", "reckless", "recoil", "resolve", "spacious", "tentative",
    "urgent", "circumstance", "commence", "current", "desperate", "extensive", "glum", "grimace",
    "inferior", "parched", "plummet", "priority", "recount", "recurring", "rummage", "stable",
    "terrain", "transmit", "viewpoint", "visibility", "wither"
]

# Grade 7
grade_7_words = [
    "abolish", "coherent", "comprise", "domestic", "earnest", "explicit", "impede", "instinctive",
    "nostalgic", "prevail", "relevant", "somber", "stagnant", "turmoil", "zeal", "agile", "chronic",
    "dwindle", "eccentric", "flounder", "impose", "lax", "lull", "meticulous", "oblige", "plagiarize",
    "remnant", "sophisticated", "sustain", "versatile", "askew", "contemporary", "crude", "defiant",
    "fluctuate", "haphazard", "inconceivable", "jeer", "lenient", "obliterate", "predicament",
    "resilience", "sprawl", "tarnish", "vigilant", "astride", "clamor", "converge", "delegate",
    "elated", "forsake", "incorporate", "jostle", "lapse", "liable", "oblivious", "rural", "taut",
    "veer", "vulnerable", "benevolent", "blunt", "censorship", "contract", "diligent", "embellish",
    "endure", "fugitive", "inexplicable", "intrigue", "obscure", "prod", "torrent", "tranquil",
    "warily", "blemish", "colossal", "conscious", "discipline", "gingerly", "infringe", "judicial",
    "jut", "mediocre", "ominous", "protrude", "sheepish", "stricken", "stupendous", "whim",
    "compatible", "convey", "disdain", "entail", "grueling", "ingenious", "juvenile", "melancholy",
    "oppress", "rebellious", "scorn", "smug", "subside", "tumultuous", "wispy", "calamity", "casual",
    "chortle", "cower", "curt", "dormant", "dubious", "falter", "idle", "keen", "lament", "ornate",
    "perpetual", "recede", "relentless", "sociable", "sullen", "unfurl", "waft", "writhe"
]

# Grade 8
grade_8_words = [
    "abate", "assimilate", "concede", "dissipate", "erratic", "flourish", "impulsive", "longevity",
    "malleable", "obstruct", "render", "rueful", "subordinate", "tarry", "transgression", "adamant",
    "audacious", "concise", "elusive", "exasperate", "foolhardy", "gnarled", "implore", "impudent",
    "mandatory", "pensive", "reprieve", "shrewd", "succinct", "tedious", "belligerent", "benign",
    "ecstatic", "emaciated", "exploit", "formidable", "haughty", "initiative", "monotonous",
    "pervasive", "resent", "succumb", "sully", "teem", "usurp", "accustom", "affluent", "conspicuous",
    "eddy", "exuberant", "furtive", "havoc", "innate", "petulant", "profound", "respite", "squalor",
    "telltale", "threadbare", "undulate", "aloof", "amiable", "dainty", "ebb", "exult", "gait",
    "headlong", "insolent", "motivate", "muse", "revelation", "stifle", "synopsis", "wallow", "wane",
    "billow", "bleak", "concession", "deft", "feasible", "gaudy", "gaunt", "inundate", "oblique",
    "obsolete", "roil", "strenuous", "systematic", "temperate", "tendril", "anecdote", "brusque",
    "dejected", "emphatic", "feign", "impassive", "implicit", "quaver", "quibble", "ruddy", "strew",
    "tangible", "taper", "terse", "wily", "apathy", "apt", "candid", "chastise", "desolate",
    "endeavor", "fleeting", "glean", "glower", "incessant", "listless", "loll", "obstinate",
    "painstaking", "qualm", "reverence", "sheer", "smolder", "throng", "wry"
]

# Grade 9
grade_9_words = [
    "abhor", "ambiguous", "appalled", "besiege", "comprehensive", "conviction", "demeanor", "diligent",
    "elude", "exacerbate", "fortitude", "implication", "insidious", "nonchalant", "oblivion",
    "proficient", "rectify", "retort", "speculative", "sporadic", "alleviate", "annihilate", "archaic",
    "blatant", "concur", "cordial", "defunct", "diplomatic", "emulate", "exemplify", "heterogeneous",
    "homogeneous", "irksome", "multifarious", "omnipotent", "prerequisite", "redemption", "reverberate",
    "surpass", "undermine", "aesthetic", "altercation", "aspire", "callous", "concurrent", "covert",
    "defile", "disconcerting", "ensue", "fallibility", "incredulous", "indigenous", "irrevocable",
    "notorious", "omniscient", "persecute", "refute", "rotund", "stratagem", "vexation", "afflict",
    "anomaly", "avid", "cognizant", "consolation", "credible", "denounce", "discordant", "enumerate",
    "forlorn", "immaculate", "jocular", "jubilance", "nefarious", "politic", "proponent", "relinquish",
    "sage", "tremulous", "vindictive", "abyss", "antagonism", "befuddled", "compensate", "conspire",
    "creed", "derogatory", "disparity", "equitable", "harrowing", "impediment", "industrious",
    "infamous", "malign", "perturb", "reciprocal", "repentant", "salutation", "surreal", "vitality",
    "allocate", "apathetic", "begrudge", "composite", "contempt", "cynical", "detract", "eloquent",
    "erroneous", "giddy", "implausible", "inquisitive", "lavish", "myopic", "plausible",
    "reconciliation", "retaliate", "solace", "transcend", "vivacious"
]

# Grade 10
grade_10_words = [
    "acquiesce", "ardent", "bravado", "complacent", "conscientious", "cynicism", "docile", "err",
    "frivolous", "frugal", "inept", "meander", "mnemonic", "ostentatious", "palpable", "pervade",
    "repudiate", "slovenly", "supersede", "vanquish", "aggregate", "arduous", "cacophony", "conceive",
    "contemptuous", "dilapidated", "effervescent", "erudite", "fervent", "incongruous", "iniquity",
    "lucrative", "myriad", "ostracize", "pertinent", "quandary", "rescind", "surmise", "tactful",
    "vehement", "adulterate", "ascertain", "cajole", "condescend", "copious", "corroborate", "dictum",
    "egalitarian", "exaltation", "fortuitous", "imperious", "insinuate", "mutinous", "prevailing",
    "punctilious", "rapport", "scrutinize", "taciturn", "ungainly", "vilify", "amenable", "barrage",
    "candor", "conflagration", "deleterious", "elucidate", "exemplary", "gesticulate", "impervious",
    "insipid", "lucid", "magnanimous", "misgiving", "penitent", "prudent", "reprehensible", "umbrage",
    "uncouth", "unilateral", "vindicate", "antipathy", "boisterous", "cantankerous", "conformity",
    "covet", "discern", "endear", "expedite", "fawning", "hegemony", "intermittent", "morbid",
    "odious", "permeate", "prodigious", "reprimand", "sojourn", "tractable", "unobtrusive", "whimsical",
    "apprehensive", "buttress", "cleave", "congenial", "crestfallen", "dissent", "enigmatic",
    "facilitate", "genial", "indignant", "languid", "mitigate", "opulent", "pious", "procure",
    "reproach", "stoic", "trepidation", "unscrupulous", "zealot"
]

# Grade 11
grade_11_words = [
    "accost", "ambivalent", "austere", "brevity", "censure", "compulsory", "didactic", "digress",
    "elicit", "faction", "flagrant", "flippant", "inflection", "laudable", "mortification",
    "plaintive", "prerogative", "rancor", "satiate", "superfluous", "acrid", "ameliorate",
    "auspicious", "brazen", "circumspect", "dearth", "disparage", "dogmatic", "empirical",
    "fastidious", "goad", "guile", "indoctrinate", "intimate", "nebulous", "portend", "pretext",
    "rapacious", "scintillating", "tenet", "anachronistic", "ardor", "asunder", "bequeath",
    "credulous", "demure", "discourse", "duplicity", "enmity", "felicity", "implacable", "inordinate",
    "interdict", "jaunty", "pall", "precarious", "profane", "rapt", "scruple", "usurpation",
    "admonish", "approbation", "avarice", "buffet", "consign", "deplorable", "dote", "ebullience",
    "expostulate", "germane", "gilded", "impertinence", "inclement", "livid", "pallor", "precept",
    "propensity", "relegate", "spurn", "vex", "acrimonious", "affable", "belie", "cadence", "contend",
    "derision", "disseminate", "edict", "extraneous", "hiatus", "imbue", "invective", "languorous",
    "lurid", "partisan", "precipitate", "provincial", "sagacious", "stolid", "visage", "allay",
    "asinine", "bemused", "castigate", "contrive", "despotic", "doggedly", "egregious", "exude",
    "forbear", "ignominious", "indolent", "irascible", "morose", "pecuniary", "predilection",
    "pugnacious", "reproof", "stupor", "viscous"
]

# Grade 12
grade_12_words = [
    "abject", "avail", "capitulate", "cursory", "deference", "discrete", "ephemeral", "errant",
    "expedient", "gratuitous", "inimical", "levity", "peremptory", "poignant", "purport", "reticent",
    "sinewy", "sublime", "tenuous", "venerable", "arbitrary", "banal", "capricious", "conjecture",
    "decorous", "embroil", "edification", "esoteric", "fitful", "garish", "hackneyed", "obsequious",
    "perfunctory", "prevaricate", "sagacity", "sordid", "strident", "supercilious", "torpor",
    "vestige", "alacrity", "bearing", "circuitous", "conciliatory", "consternation", "diffident",
    "enjoin", "estimable", "forbearance", "iconoclast", "lassitude", "obstreperous", "pique",
    "profligate", "quotidian", "rancorous", "specious", "supplication", "trite", "vicarious",
    "assiduous", "bode", "circumvent", "cogent", "deign", "disingenuous", "euphemism", "fractious",
    "impute", "inured", "obeisance", "officious", "pedantic", "propriety", "recalcitrant", "sanguine",
    "scrupulous", "surreptitious", "vicissitude", "willful", "assuage", "brandish", "contingent",
    "contrite", "disabuse", "dissemble", "epithet", "exhort", "inculcate", "mollify", "ornery",
    "posterity", "prosaic", "redolent", "repose", "sedulous", "spurious", "tacit", "vacillate",
    "wanton", "austerity", "canvass", "commensurate", "countenance", "demur", "deprecate", "dissolute",
    "equivocal", "exigent", "garrulous", "inextricable", "nascent", "precocious", "presentiment",
    "prostrate", "sidle", "solicitous", "temerity", "upbraid", "vapid"
]

# Create JSON files
grades = {
    6: ("https://www.vocabulary.com/lists/adtf2rj2/125-words-every-6th-grader-should-know", grade_6_words),
    7: ("https://www.vocabulary.com/lists/kc6rvcj7/125-words-every-7th-grader-should-know", grade_7_words),
    8: ("https://www.vocabulary.com/lists/r3qovfdy/125-words-every-8th-grader-should-know", grade_8_words),
    9: ("https://www.vocabulary.com/lists/hnahnhvy/120-words-every-9th-grader-should-know", grade_9_words),
    10: ("https://www.vocabulary.com/lists/gw5mfvr5/120-words-every-10th-grader-should-know", grade_10_words),
    11: ("https://www.vocabulary.com/lists/5vykmkps/120-challenging-words-for-11-graders", grade_11_words),
    12: ("https://www.vocabulary.com/lists/xr7k6hak/120-words-every-12th-grader-should-know", grade_12_words)
}

for grade, (url, words) in grades.items():
    data = {
        "source": "Vocabulary.com",
        "grade": grade,
        "url": url,
        "scraped_date": datetime.now().strftime("%Y-%m-%d"),
        "word_count": len(words),
        "words": words
    }

    output_path = f"../raw/vocabulary-com-grade-{grade}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✓ Grade {grade}: {len(words)} words → {output_path}")

total = sum(len(words) for _, words in grades.values())
print(f"\n✓ Created 7 files with {total} total words from Vocabulary.com")
