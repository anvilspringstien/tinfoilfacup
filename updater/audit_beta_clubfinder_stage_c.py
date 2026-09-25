#!/usr/bin/env python3
"""Read-only, full-file audit of the BETA Clubfinder -> Challenge Deck producer.

Run inside the checked-out repository; connector previews of the 4.6 MB file
are truncated. This is a *static index*, not a proof of call-graph reachability
or permission to change production.
"""
import argparse
import hashlib
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CLUB=ROOT/"beta/clubfinder-beta.html"
DECK=ROOT/"beta/challenges-beta.html"
REPORT=ROOT/"docs/refactor/2026-09-25-stage-c-clubfinder-producer-map.md"
START="/* TIN_FOIL_EMBEDDED_COMPETITION_BEGIN */"
STOP="/* TIN_FOIL_EMBEDDED_COMPETITION_END */"

# These seven definitions were present in the guarded, earlier full-source map.
CORE=[
    "openChallenges", "tinFoilChallengeStatsSnapshot",
    "tinFoilCampaignIdentityForSave", "tinFoilPersistCampaignIdentityBackup",
    "tinFoilRecoverCampaignIdentity", "tinFoilSavePigeonName",
    "tinFoilRestoreClubfinderReturnSnapshot",
]
SUPPORT=[
    "completedResultVenue", "tinFoilPigeonMilesForStats", "buildJourney",
    "journeyCertificate", "loadSavedJourney", "saveJourney",
    "tinFoilSavedPigeonName", "tinFoilPigeonNameInputHtml",
    "tinFoilPigeonNameBandHtml", "tinFoilSaveClubfinderReturnSnapshot",
]
KEYS=[
    "tffc.clubfinderCampaign.v1", "tffc.clubfinderCampaignIdentity.v1",
    "tffc.clubfinderReturnSnapshot.v1", "tffc.challengeOrigin",
    "tffc.challengeReturnIndex", "tffc.openStatsOnReturn",
    "tffc.challengeDeck.v1",
]
PROBE=[
    "completedResultVenue", "tinFoilPigeonMilesForStats",
    "TIN_FOIL_CHALLENGE_BRIDGE_KEY", "TIN_FOIL_CLUBFINDER_RETURN_SNAPSHOT_KEY",
    "TIN_FOIL_CAMPAIGN_IDENTITY_BACKUP_KEY",
    "localStorage.setItem", "sessionStorage.setItem",
    "challenges-beta.html", "pigeonName:", "selectedAt:", "originName:",
    "statsSnapshot:", "pigeonMiles:", "tiesPlayed:",
]
E="\u0060"

def q(value):
    return E+str(value).replace(E,"'")+E

def digest(data):
    return hashlib.sha256(data).hexdigest()

def line_no(text,index):
    return text.count("\n",0,index)+1

def mask_payload(text):
    if text.count(START)!=1 or text.count(STOP)!=1:
        raise ValueError("BETA embedded competition markers missing or duplicated")
    a=text.index(START);b=text.index(STOP,a)+len(STOP)
    removed=text[a:b]
    return (text[:a]+"/* offline competition payload excluded from code audit */"
            +"\n"*removed.count("\n")+text[b:])

def find_decl(text,name):
    pattern=r"(?m)^[ \t]*(?:async\s+)?function\s+"+re.escape(name)+r"\s*\("
    m=re.search(pattern,text)
    if m:return m.start(),m.end(),"function"
    # Mark non-declaration references honestly; don't treat these as a function.
    pattern=r"(?m)^[ \t]*(?:const|let|var)\s+"+re.escape(name)+r"\s*="
    m=re.search(pattern,text)
    if m:return m.start(),m.end(),"assigned value"
    m=re.search(r"\b"+re.escape(name)+r"\b",text)
    if m:return m.start(),m.end(),"reference only"
    return None,None,"not found"

def window(text,offset,limit=12000):
    """Evidence window until next unindented function declaration; not an AST."""
    if offset is None:return ""
    next_declaration=re.search(r"(?m)^(?:async\s+)?function\s+\w+\s*\(",
                               text[offset+1:])
    end=(offset+1+next_declaration.start()) if next_declaration else len(text)
    return text[offset:min(end,offset+limit)]

def context_lines(text,offset,limit=9):
    if offset is None:return ["Not found."]
    segment=text[offset:].splitlines()
    result=[]
    for row in segment[:limit]:
        row=row.rstrip()
        result.append(row[:240]+(" ..." if len(row)>240 else ""))
    return result

def key_inventory(text):
    out=[]
    for key in KEYS:
        positions=[line_no(text,m.start()) for m in re.finditer(re.escape(key),text)]
        out.append("| "+q(key)+" | "+str(len(positions))+" | "+
                   (", ".join(str(x) for x in positions[:6]) or "None")+" |")
    return out

def storage_inventory(text):
    result=[]
    # Alias declarations and direct storage calls. Dynamic expressions
    # cannot be resolved statically, so carry the literal expression too.
    aliases={}
    for m in re.finditer(r"\b(?:const|let|var)\s+(\w+)\s*=\s*(['\"])(.*?)\2",text):
        if len(m.group(3))<120:aliases[m.group(1)]=m.group(3)
    pattern=(r"\b(localStorage|sessionStorage)\s*\.\s*"
             r"(getItem|setItem|removeItem)\s*\(\s*"
             r"(?:(['\"])([^'\"\n]+)\3|([A-Za-z_$][\w$]*))")
    for m in re.finditer(pattern,text):
        expr=m.group(4) or m.group(5)
        val=aliases.get(expr,expr)
        if (val in KEYS or "CHALLENGE" in expr or "CAMPAIGN" in expr or
                "RETURN" in expr or "PIGEON" in expr):
            result.append("| "+str(line_no(text,m.start()))+" | "+
                          q(m.group(1)+"."+m.group(2))+" | "+q(expr)+
                          " | "+q(val)+" |")
    return result

def make_report():
    raw=CLUB.read_bytes()
    deck=DECK.read_bytes()
    source=mask_payload(raw.decode("utf-8"))
    deck_source=deck.decode("utf-8")
    scripts="\n".join(re.findall(r"<script\b[^>]*>(.*?)</script>",source,re.I|re.S))
    if len(scripts)<20000:
        raise ValueError("Could not inspect the complete BETA Clubfinder scripts")
    if "function applyClubfinderCampaignTruth()" not in deck_source:
        raise ValueError("Stage A Deck reader missing from checked-out source")
    if "function renderTrophyCabinet(" not in deck_source:
        raise ValueError("Stage B Deck renderer missing from checked-out source")
    decls=[]
    for name in CORE+SUPPORT:
        offset,_,kind=find_decl(source,name)
        if name in CORE and kind!="function":
            raise ValueError("Critical Clubfinder producer function missing: "+name)
        decls.append((name,offset,kind))
    lines=[
        "# Stage C — full-file BETA Clubfinder producer audit",
        "",
        "**Historical, source-scoped, read-only inventory.** Generated inside the "
        "repository with "+q("python3 updater/audit_beta_clubfinder_stage_c.py")+
        " from the **complete** BETA Clubfinder, with the large embedded "
        "competition-data literal masked while keeping source line numbers. "
        "No application file is changed by this audit. Static references and "
        "source windows are evidence pointers, **not** a complete JavaScript "
        "call graph.",
        "",
        "## Exact audited sources",
        "",
        "| File | Bytes | SHA-256 |",
        "|---|---:|---|",
        "| "+q("beta/clubfinder-beta.html")+" | "+f"{len(raw):,}"+" | "+q(digest(raw))+" |",
        "| "+q("beta/challenges-beta.html")+" | "+f"{len(deck):,}"+" | "+q(digest(deck))+" |",
        "",
        "The Deck side already contains the Stage A "
        +q("applyClubfinderCampaignTruth()")+" reader, Stage B "
        +q("renderTrophyCabinet()")+" helper and their regression tests.",
        "",
        "## Producer and downstream function declarations",
        "",
        "| Function or expression | First source line | Detected declaration | Source token occurrences |",
        "|---|---:|---|---:|",
    ]
    for name,offset,kind in decls:
        refs=len(re.findall(r"\b"+re.escape(name)+r"\b",scripts))
        lines.append("| "+q(name)+" | "+
                     (str(line_no(source,offset)) if offset is not None else "—")+
                     " | "+kind+" | "+str(refs)+" |")
    lines += [
        "",
        "The seven required rows form the existing BETA Clubfinder producer/"
        "saved-identity/return-snapshot boundary. Optional support names "
        "marked as references are not claimed to have a standalone function.",
        "",
        "## Shared browser-storage identifiers",
        "",
        "| Storage key | Source occurrences (excluding offline JSON) | First six source lines |",
        "|---|---:|---|",
        *key_inventory(source),
        "",
        "### Direct storage operations (filtered to relevant keys/aliases)",
        "",
        "| Source line | Operation | Source expression | Resolved literal if simple alias |",
        "|---|---|---|---|",
        *(storage_inventory(scripts) or ["| — | No direct relevant operations found; investigate helpers | — | — |"]),
        "",
        "## Critical producer evidence",
        "",
        "These are **bounded opening excerpts**, not whole function bodies; "
        "inspect the file itself before editing any function.",
    ]
    for name,offset,kind in decls[:7]:
        body=window(source,offset)
        lines += ["", "### "+q(name)+" — source line "+
                  (str(line_no(source,offset)) if offset is not None else "unknown"),
                  "", "~~~js", *context_lines(source,offset,14), "~~~", ""]
        if name=="openChallenges":
            lines += [
                "Within the first bounded source window (not a parser-grade AST):",
                "",
                "| Evidence string | Present in bounded window? |",
                "|---|---|",
            ]
            for probe in PROBE:
                lines.append("| "+q(probe)+" | "+
                             ("Yes" if probe in body else "Not within window")+
                             " |")
            lines += [""]
    lines += [
        "## Cross-page contract and safeguards",
        "",
        "- **Producer:** "+q("openChallenges(origin)")+
        " owns the direct Deck launch and v1 campaign bridge. The independent "
        "actual-Clubfinder VM regression verifies Call Sign, the full 19-character "
        "Pigeon Name, stable origin/selection timestamp and search number, "
        "canonical calculated mileage, a retained rendered-return snapshot "
        "and no additional counter allocation.",
        "- **Consumer:** the Deck's Stage A reader validates the existing "
        "Clubfinder source marker, normalises finite progress and falls back "
        "to the saved identity only when the current bridge lacks a name and "
        "the existing origin/selection rule permits it.",
        "- **Mileage trust:** "+q("completedResultVenue()")+
        " and "+q("tinFoilPigeonMilesForStats()")+
        " are existing calculation dependencies. Recalculate from resolved "
        "historical venues rather than trusting a stale cached counter; "
        "continue to include the Petts Wood BR2 8HQ override.",
        "- **Navigation:** preserve the snapshot restoration route and its "
        "exact previously rendered campaign. Legacy Stats-tab return belongs "
        "to the Deck and remains a regression requirement.",
        "- **Scope:** the audit does not refresh embedded competition JSON, "
        "change the simulator, alter v1 localStorage fields, modify production "
        "or enable the forthcoming BETA Clubfinder code change.",
        "",
        "## Next controlled step",
        "",
        "Inspect the bounded "+q("openChallenges")+" producer code and actual "
        "Clubfinder VM assertions together. Extract only duplicated **pure** "
        "bridge-field assembly if the full source proves it useful; retain "
        "function entry points and the original v1 shape. Make that change "
        "in a separate BETA Clubfinder PR behind the independently guarded "
        "Stage C workflow. Require the Clubfinder VM/mobile/Petts Wood/"
        "Holmesdale/Exmouth/Weston/Thame/conditional-draw tests plus the Deck "
        "bridge/Trophy suite and a protected-production/competition diff gate.",
        "",
    ]
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    content=make_report()
    if args.check:
        if not REPORT.exists() or REPORT.read_text(encoding="utf-8")!=content:
            raise SystemExit("FAIL: Stage C audited source or committed report has drifted")
        print("PASS: exact full-file Stage C dependency report reproduced")
    else:
        REPORT.parent.mkdir(parents=True,exist_ok=True)
        REPORT.write_text(content,encoding="utf-8")
        print("WROTE",REPORT.relative_to(ROOT))
    print("Audit is read-only for production, competition and BETA application files")

if __name__=="__main__":
    main()
