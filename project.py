"""Compute foreground/background contrast in the sRGB color space."""
import re

TITLE = "Palette Pair Proof"
DESCRIPTION = "Audit named text and background pairs, then find passing alternatives in the same palette."
PROMPT = "Explain the weakest text color pair using the observed ratios. Prefer a passing in-palette replacement when available. This is a color check, not a full accessibility assessment."


def luminance(value):
    if not isinstance(value, str) or not re.fullmatch(r"#[a-fA-F0-9]{6}", value):
        raise ValueError("Specify every color as a six-digit sRGB hex value.")
    channels = [int(value[i:i+2], 16)/255 for i in (1,3,5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v+0.055)/1.055)**2.4 for v in channels]
    return sum(v*k for v,k in zip(linear,(0.2126,0.7152,0.0722)))


def ratio(a,b):
    return (max(a,b)+0.05)/(min(a,b)+0.05)


def analyze(data):
    colors, pairs = data["palette"], data["pairs"]
    if not isinstance(colors, dict) or not colors or not isinstance(pairs,list) or not pairs:
        raise ValueError("Provide a named palette and at least one text pair.")
    values = {key:luminance(color) for key,color in colors.items()}
    rows, samples = [], []
    for pair in pairs:
        name, fg, bg = pair["label"], pair["foreground"], pair["background"]
        target = pair.get("target",4.5)
        if fg not in values or bg not in values or not isinstance(name,str) or not name:
            raise ValueError("Each named pair must reference two palette entries.")
        if type(target) not in (float,int) or not 1 <= target <= 21:
            raise ValueError("Choose a ratio target between 1 and 21.")
        observed = ratio(values[fg],values[bg])
        alternatives = [c for c,v in values.items() if ratio(v,values[bg]) >= target]
        replacement = min(alternatives, key=lambda c:(abs(values[c]-values[fg]),c)) if alternatives else None
        rows.append({"Text role":name,"Pair":f"{fg} / {bg}","Ratio":round(observed,3),"Target":target,
                     "Result":"Pass" if observed>=target else "Below target",
                     "Try foreground":"—" if observed>=target else replacement or "No palette match"})
        samples.append({"label":name,"foreground":colors[fg],"background":colors[bg]})
    return {"summary": "Pairs are evaluated before rounding. Suggested alternatives preserve the background and minimize the luminance change.",
            "metrics":{"Text roles":len(rows),"Passing":sum(r["Result"]=="Pass" for r in rows),
                       "Below target":sum(r["Result"]!="Pass" for r in rows)}, "rows":rows,"swatches":samples}
