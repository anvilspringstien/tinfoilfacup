#!/usr/bin/env python3
"""Tin Foil FA Cup synthetic system-ingestion health suite.

Fictional clubs only.  The suite exercises shared ingestion/state machinery
without reading or writing production competition.json.
"""
import copy
from round_state_engine import classify_observation
from reconcile_next_round_advancement import resolve, merge_evidence

PASS=[]

def req(ok,msg):
    if not ok: raise AssertionError(msg)

def scenario(name,fn):
    try:
        fn(); PASS.append(name); print(f"{name:.<38} PASS")
    except Exception as exc:
        print(f"{name:.<38} FAIL")
        raise AssertionError(f"{name}: {exc}") from exc

def fixture(home,away,date="2026-09-26",rnd="Third Round Qualifying"):
    return {"home":home,"away":away,"date":date,"round":rnd,"kickoff":"15:00"}

def obs(home,away,hs,aw,date="2026-09-26",status="FT",winner=""):
    return {"home":home,"away":away,"home_score":hs,"away_score":aw,"date":date,"status":status,"winner":winner}

def advancement_state(home,away,next_home,next_away):
    return {
      "source_round":"Fourth Round Qualifying",
      "fixtures":{"next":fixture(next_home,next_away,"2026-10-10","Fourth Round Qualifying")},
      "replays":{"r":fixture(home,away,"2026-09-29","Third Round Qualifying Replay")},
      "results":{},"result_history":{}
    }

def golden_path():
    f=fixture("Anvil Rovers","Hammer Town")
    r=classify_observation(f,obs("Anvil Rovers","Hammer Town",2,0),[])
    req(r["kind"]=="result","decisive result not ingested")
    req(r["result"]["winner"]=="Anvil Rovers","wrong custodian")
    req(r["result"]["round"]=="Third Round Qualifying","round drift")

def draw_replay():
    f=fixture("Tin Foil United","Pie Athletic")
    first=classify_observation(f,obs("Tin Foil United","Pie Athletic",1,1),[])
    req(first["result"]["decision"]=="draw-replay","draw did not create replay ancestry")
    replay=obs("Pie Athletic","Tin Foil United",0,2,"2026-09-29")
    second=classify_observation(f,replay,[first["result"]])
    req(second["result"]["round"].endswith(" Replay"),"later observation not classified as replay")
    req(second["result"]["winner"]=="Tin Foil United","replay winner wrong")

def next_round_proof():
    data=advancement_state("Barry Athletic","Pigeon Vale","Barry Athletic","Primark Town")
    resolved,retained,ambiguous=resolve(data)
    req(len(resolved)==1 and resolved[0]["winner"]=="Barry Athletic","unique advancement not inferred")
    req(resolved[0]["home_score"] is None and resolved[0]["away_score"] is None,"score fabricated")
    req(not retained and not ambiguous,"unique proof not clean")
    req(merge_evidence(data,resolved[0]),"advancement evidence not persisted")
    real=obs("Barry Athletic","Pigeon Vale",3,0,"2026-09-29")
    classified=classify_observation(data["replays"]["r"],real,data["result_history"]["Barry Athletic"])
    req(classified["result"]["winner"]=="Barry Athletic","later real score did not supersede evidence")
    req(classified["result"]["home_score"]==3,"real score lost")

def missing_proof_fails_closed():
    data=advancement_state("Barry Athletic","Pigeon Vale","Other Town","Primark Town")
    resolved,retained,ambiguous=resolve(data)
    req(not resolved and len(retained)==1 and not ambiguous,"missing proof advanced a club")

def ambiguous_proof_fails_closed():
    data=advancement_state("Rocking Horse FC","Unicorn Town","Rocking Horse FC","Unicorn Town")
    resolved,retained,ambiguous=resolve(data)
    req(not resolved and len(ambiguous)==1,"ambiguous proof did not fail closed")

def contradiction_fails_closed():
    f=fixture("Primark Town","Cheap Coat Wanderers")
    first=classify_observation(f,obs("Primark Town","Cheap Coat Wanderers",2,0),[])
    try:
        classify_observation(f,obs("Primark Town","Cheap Coat Wanderers",0,2),[first["result"]])
    except ValueError:
        return
    raise AssertionError("contradictory same-date result was accepted")

def postponement_reschedule():
    f=fixture("Shingles Athletic","Jab United")
    postponed=obs("Shingles Athletic","Jab United",None,None,status="POSTPONED")
    event=classify_observation(f,postponed,[])
    req(event["kind"]=="event" and event["event"]["winner"]=="","postponement became result")
    later=obs("Shingles Athletic","Jab United",1,0,"2026-09-28")
    result=classify_observation(f,later,[event["event"]])
    req(result["result"]["winner"]=="Shingles Athletic","rescheduled result did not resolve")

def penalties():
    f=fixture("Bovril City","Caliper County")
    first=classify_observation(f,obs("Bovril City","Caliper County",2,2),[])
    replay=obs("Caliper County","Bovril City",1,1,"2026-09-29",winner="Bovril City")
    result=classify_observation(f,replay,[first["result"]])
    req(result["result"]["winner"]=="Bovril City","penalty winner lost")
    req(result["result"]["decision"]=="penalties","penalty decision lost")
    req(result["result"]["round"].endswith(" Replay"),"penalty replay ancestry lost")

def voided_replay_order():
    f=fixture("Pigeon Vale","Mileage Preservation Society")
    voided={"home":"Pigeon Vale","away":"Mileage Preservation Society","home_score":None,"away_score":None,
            "winner":"","status":"VOID","decision":"voided-replay-ordered","date":"2026-09-26","round":"Third Round Qualifying"}
    replay=obs("Mileage Preservation Society","Pigeon Vale",0,1,"2026-09-29")
    result=classify_observation(f,replay,[voided])
    req(result["result"]["round"].endswith(" Replay"),"voided tie lost replay ancestry")
    req(result["result"]["winner"]=="Pigeon Vale","replayed voided tie winner wrong")
    req(voided["date"]=="2026-09-26","original journey event mutated")

def alias_identity():
    f=fixture("Anvil Rovers FC","Hammer Town AFC")
    r=classify_observation(f,obs("Anvil Rovers","Hammer Town",4,1),[])
    req(r["result"]["winner"]=="Anvil Rovers","FC/AFC alias identity failed")

def round_transition():
    data=advancement_state("Wembley Nightmare","Turnstile Borough","Wembley Nightmare","Final Frontier")
    resolved,_,_=resolve(data)
    req(len(resolved)==1,"round transition did not consume previous replay")
    merge_evidence(data,resolved[0])
    again,_,_=resolve(data)
    req(len(again)==1,"idempotent inference disappeared")
    req(not merge_evidence(data,again[0]),"repeat ingestion duplicated history")
    hist=data["result_history"]["Wembley Nightmare"]
    req(len([x for x in hist if x.get("decision")=="next-round-fixture"])==1,"duplicate advancement evidence")

def main():
    tests=[
      ("Golden Path / Anvil Rovers",golden_path),
      ("Draw + Replay",draw_replay),
      ("Missing Result / Draw Proof",next_round_proof),
      ("Missing Evidence Fails Closed",missing_proof_fails_closed),
      ("Ambiguous Advancement",ambiguous_proof_fails_closed),
      ("Contradictory Sources",contradiction_fails_closed),
      ("Postponement / Reschedule",postponement_reschedule),
      ("Penalty Winner",penalties),
      ("Voided Result + Replay",voided_replay_order),
      ("Club Alias Resolution",alias_identity),
      ("Round Transition / Idempotency",round_transition),
    ]
    print("TIN FOIL FA CUP — SYNTHETIC SYSTEM INGESTION HEALTH\n")
    for name,fn in tests: scenario(name,fn)
    print(f"\nSYSTEM INGESTION HEALTH: {len(PASS)} / {len(tests)}")
    print("All scenarios use fictional data; production competition.json untouched.")

if __name__=="__main__": main()
