#!/usr/bin/env python3
"""
Extract vocabulary words from GreatSchools scraped markdown data.
"""

import json
from datetime import datetime

# Data extracted from scraped markdown

grade_6_words = [
    "adjacent", "accumulate", "adapt", "adequate", "analyze", "anticipate", "appropriate", "artifact",
    "benefit", "calculate", "catastrophe", "chronological", "citizen", "civilization", "compose",
    "conclusion", "congruent", "consequence", "construct", "continuous", "contrast", "contribute",
    "declare", "democracy", "dimension", "drastic", "elaborate", "encourage", "equation", "evaluate",
    "exaggerate", "exhaust", "expression", "extend", "extensive", "factor", "ferocious", "frequent",
    "frequency", "genuine", "government", "history", "hypothesis", "insists", "irrigate", "lofty",
    "manipulate", "massive", "narrate", "obedient", "oblivious", "origin", "peculiar", "persuade",
    "prediction", "priority", "quote", "realistic", "recount", "reinforce", "repetition", "retrieve",
    "similar", "solution", "strategy", "substitute", "suspense", "tentative", "thesis", "transfer",
    "unanimous", "unique", "variable", "viewpoint", "violate"
]

grade_7_words = [
    "abdicate", "abrasive", "abruptly", "acknowledge", "acquire", "addict", "adequate", "admonish",
    "affiliation", "agitate", "allege", "allocate", "alternative", "amendment", "antagonize",
    "attribute", "authentic", "bamboozle", "belligerent", "bewilder", "bias", "boycott", "cause",
    "characterize", "chronological", "compel", "competent", "component", "conclusive", "concur",
    "condemn", "condor", "confront", "connotation", "consecutive", "consult", "contrast", "copious",
    "correspond", "dawdle", "deceitful", "demeanor", "derogatory", "devastate", "devious", "devour",
    "diversity", "eligible", "emphasize", "estimate", "evaluate", "exonerated", "exposition",
    "exuberant", "famished", "formidable", "impartial", "indifferent", "industrious", "inevitable",
    "infuriate", "inhabitants", "initiate", "intimidate", "irate", "irrelevant", "legendary",
    "liaison", "libel", "ludicrous", "mandatory", "mitigate", "naive", "narrate", "necessity",
    "negligent", "obnoxious", "omit", "opposition", "oppress", "perceive", "persuasive", "prediction",
    "prominent", "prospective", "punctual", "quote", "relinquish", "resolve", "rudimentary", "signify",
    "sovereign", "suspense", "talisman", "tentative", "toxic", "treason", "viewpoint"
]

grade_8_words = [
    "abhor", "abrasive", "alternative", "ambiguous", "amiss", "anarchy", "anonymous", "anthology",
    "apathy", "apprehend", "assimilate", "assumption", "audacious", "authority", "avid", "ban",
    "belligerent", "bisect", "bizarre", "boycott", "capable", "cause", "characterize", "chronological",
    "commence", "compels", "concise", "conclude", "confiscate", "conjecture", "conscientious",
    "consecutive", "consistent", "construct", "contrast", "corroborate", "depict", "derive",
    "despicable", "despondent", "elapse", "embark", "encompass", "endeavor", "evidence", "evoke",
    "feasible", "focus", "formula", "generation", "gruesome", "imminent", "impel", "imperative",
    "inspire", "integrate", "interrogate", "merge", "modify", "mutiny", "narrate", "novice",
    "obsolete", "opposition", "perish", "perspective", "persuasive", "plagiarize", "precise",
    "prediction", "prevalent", "procedure", "profound", "proprietor", "prudent", "pseudonym",
    "quote", "rebel", "rebuff", "rebuke", "recur", "resilient", "response", "reverberate",
    "significant", "similar", "simulate", "simultaneous", "source", "specific", "spontaneous",
    "surmise", "theory", "tirade", "universal", "validate", "variable"
]

grade_9_words = [
    "absolve", "alleviate", "alternative", "ambivalent", "analyze", "animosity", "approximate",
    "arbitrary", "attribute", "beneficial", "comprehensive", "connotation", "contrast", "credible",
    "cursory", "cynic", "dearth", "deficient", "demonstrate", "depict", "derive", "detract",
    "devastate", "digress", "dilemma", "diligent", "dissent", "distort", "diversion", "elation",
    "elicit", "elude", "escalate", "evaluate", "exacerbate", "excerpt", "exemplify", "explicit",
    "exposition", "falter", "feasible", "feign", "fluctuate", "formulate", "generate", "gist",
    "hypothetical", "impartial", "implausible", "implication", "imply", "incentive", "incoherent",
    "indolent", "infamous", "infuriate", "innovation", "intercede", "interpret", "intimidate",
    "isolate", "jeopardize", "lucrative", "mandatory", "mediate", "mortify", "niche", "obscure",
    "obsolete", "pacify", "perception", "perspective", "pertinent", "ponder", "prevalent",
    "proponent", "punitive", "rapport", "rationale", "reconcile", "redundant", "respective",
    "retaliate", "sabotage", "scrutiny", "simulate", "squander", "succumb", "tangible", "technique",
    "traumatic", "turmoil", "valid", "verify", "viable", "vulnerable"
]

grade_10_words = [
    "abstract", "admonish", "advocate", "alternative", "ambiguous", "analogy", "anarchy", "assiduous",
    "assimilate", "augment", "authentic", "belligerent", "bolster", "bureaucratic", "circumvent",
    "coalition", "cohesive", "collaborate", "comply", "concurrent", "connotation", "constituent",
    "contingent", "criteria", "demeanor", "deplore", "derogatory", "disparity", "disseminate",
    "dissident", "distraught", "docile", "divert", "dormant", "egocentric", "elusive", "emulate",
    "equitable", "eradicate", "estrange", "exacerbate", "expedite", "fabricate", "facilitate",
    "fortuitous", "fraudulent", "heinous", "hypothetical", "illicit", "imminent", "impetuous",
    "incongruous", "indigenous", "indiscriminate", "inherent", "jurisdiction", "lax", "meticulous",
    "negligent", "nonchalant", "oblivious", "obscure", "omnipotent", "opportune", "oppose", "panacea",
    "perfunctory", "preposterous", "precarious", "precipitate", "preclude", "proficient", "propensity",
    "qualitative", "quantitative", "recalcitrant", "redeem", "rejuvenate", "relegate", "relinquish",
    "repugnant", "resilient", "retrospect", "sanction", "spontaneous", "static", "stringent",
    "subordinate", "subsidize", "tenuous", "travesty", "tumult", "unilateral", "validate", "vindicate",
    "zealot"
]

grade_11_words = [
    "aberration", "abstract", "accolade", "accommodate", "aesthetic", "affinity", "altercation",
    "ameliorate", "amicable", "anarchy", "anomaly", "despot", "appall", "archaic", "arduous",
    "articulate", "astute", "authoritarian", "aversion", "biased", "brevity", "cajole", "callous",
    "capitulate", "catalyst", "catharsis", "caustic", "censure", "chastise", "clamor", "coalesce",
    "cognizant", "commiserate", "composure", "conciliatory", "contract", "copious", "cordial",
    "dearth", "debilitate", "decadence", "deference", "delineate", "deprecate", "devious", "didactic",
    "disparage", "dissonance", "duplicity", "edifice", "effervescent", "egregious", "elusive",
    "equivocal", "erroneous", "exemplary", "expedient", "extraneous", "formidable", "frivolous",
    "grueling", "haphazard", "heretic", "hindrance", "hypocrisy", "iconoclast", "incessant",
    "incidental", "incite", "incorrigible", "indoctrinate", "insurgent", "intangible", "judicious",
    "lavish", "listless", "meager", "meander", "negligent", "obliterate", "ponderous", "preclude",
    "prerequisite", "proximity", "rectify", "rescind", "resolution", "rigorous", "scrutinize",
    "substantiate", "surmise", "tirade", "turbulence", "unimpeachable", "unobtrusive", "usurp",
    "vacillate", "whimsical"
]

grade_12_words = [
    "anachronistic", "abbreviate", "abdicate", "abstinence", "adulation", "adversity", "aesthetic",
    "amicable", "anecdote", "anonymous", "antagonist", "arid", "assiduous", "asylum", "benevolent",
    "camaraderie", "censure", "circuitous", "clairvoyant", "collaborate", "compassion", "compromise",
    "condescending", "conditional", "conformist", "congregation", "convergence", "deleterious",
    "demagogue", "digression", "diligent", "discredit", "disdain", "divergent", "empathy", "emulate",
    "enervating", "enhance", "ephemeral", "evanescent", "exasperation", "exemplary", "extenuating",
    "florid", "fortuitous", "frugal", "hackneyed", "haughty", "hedonist", "hypothesis", "impetuous",
    "impute", "incompatible", "inconsequential", "inevitable", "integrity", "intrepid", "intuitive",
    "jubilation", "lobbyist", "longevity", "mundane", "nonchalant", "novice", "opulent", "orator",
    "ostentatious", "parched", "perfidious", "precocious", "pretentious", "procrastinate", "prosaic",
    "prosperity", "provocative", "prudent", "querulous", "rancorous", "reclusive", "reconciliation",
    "renovation", "resilient", "restrained", "reverence", "sagacity", "scrutinize", "spontaneity",
    "spurious", "submissive", "substantiate", "superficial", "superfluous", "suppress", "surreptitious",
    "tactful", "tenacious", "transient", "venerable", "vindicate", "wary", "zealot"
]

# Create JSON files
grades = {
    6: ("https://www.greatschools.org/gk/articles/academic-vocabulary-words-for-sixth-graders/", grade_6_words),
    7: ("https://www.greatschools.org/gk/articles/academic-vocabulary-words-for-seventh-graders/", grade_7_words),
    8: ("https://www.greatschools.org/gk/articles/academic-vocabulary-words-for-eighth-graders/", grade_8_words),
    9: ("https://www.greatschools.org/gk/articles/9th-grade-vocabulary-words/", grade_9_words),
    10: ("https://www.greatschools.org/gk/articles/10th-grade-vocabulary-words/", grade_10_words),
    11: ("https://www.greatschools.org/gk/articles/11th-grade-vocabulary-words/", grade_11_words),
    12: ("https://www.greatschools.org/gk/articles/12th-grade-vocabulary-words/", grade_12_words)
}

for grade, (url, words) in grades.items():
    data = {
        "source": "GreatSchools",
        "grade": grade,
        "url": url,
        "scraped_date": datetime.now().strftime("%Y-%m-%d"),
        "word_count": len(words),
        "words": words
    }

    output_path = f"../raw/greatschools-grade-{grade}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✓ Grade {grade}: {len(words)} words → {output_path}")

total = sum(len(words) for _, words in grades.values())
print(f"\n✓ Created 7 files with {total} total words from GreatSchools")
