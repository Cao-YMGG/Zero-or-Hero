import json, sys
from datetime import date
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2]))
from zoh.strategy import opex_week
def st(p):
    if not p: return "-"
    s=sorted(p); a=lambda x: sum(x)/len(x) if x else float('nan')
    return f"{a(p):+.0%}/{a(s[:-1]):+.0%}/{a(s[:-2]):+.0%} n={len(p)}"
sc=json.load(open(str(__import__('pathlib').Path(__file__).resolve().parents[2])+'/journal/research/scanners.json'))
ex=json.load(open(str(__import__('pathlib').Path(__file__).resolve().parents[2])+'/journal/research/exits.json'))
def show(name, rows, lab, rule):
    print("##", name, lab, rule)
    for per,cut in (("3m","2026-07-16"),("all","")):
        line=[]
        for wd in range(5):
            p=[r['picks'][lab]['exits_10'][rule] for r in rows if lab in r['picks'] and r['day']>=cut and date.fromisoformat(r['day']).weekday()==wd]
            line.append("MTWTF"[wd]+" "+st(p))
        sameday=[r['picks'][lab]['exits_10'][rule] for r in rows if lab in r['picks'] and r['day']>=cut and r.get('expiry')==r['day']]
        nextexp=[r['picks'][lab]['exits_10'][rule] for r in rows if lab in r['picks'] and r['day']>=cut and r.get('expiry')!=r['day']]
        print(" ",per," | ".join(line), "|| same-day expiry", st(sameday), "| later expiry", st(nextexp))
leader=[r for r in sc if r['study']=='leader' and r.get('entry_min')==15]
show("leader_follow 15min 1.5%", leader, "d0.20", "trail2x")
reb=[r for r in ex if r['study']=='rebound']
print(reb[0].get('day'), list(reb[0]['picks'].keys()))
lab=list(reb[0]['picks'].keys())[0]
for lab in reb[0]['picks']:
    show("rebound (exits.json)", reb, lab, "trail2x")
