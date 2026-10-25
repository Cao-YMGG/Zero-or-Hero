import json, sys
from datetime import date
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2]))
from zoh.strategy import opex_week
rows=json.load(open(str(__import__('pathlib').Path(__file__).resolve().parents[2])+'/journal/research/opendrive.json'))
def st(p):
    if not p: return "-"
    s=sorted(p); a=lambda x: sum(x)/len(x) if x else float('nan')
    return f"{a(p):+.0%} / {a(s[:-1]):+.0%} / {a(s[:-2]):+.0%} (n={len(p)}, win {sum(x>0 for x in p)/len(p):.0%})"
def d(r): return date.fromisoformat(r['day'])
MODES=("take3","hold","trail","half3_hold","half3_trail")
def rule(sym_thr, weekdays, filt=True):
    def f(r):
        if r['kind']!='call' or r['sym'] not in sym_thr: return False
        if r['move10'] < sym_thr[r['sym']]: return False
        if filt:
            if d(r).weekday() not in weekdays or r['macro'] or opex_week(d(r)): return False
        return True
    return f
groups={
 "spy_open_drive (SPY>=0.5%, Mon-Thu, no release/opex)": rule({"SPY":0.005},(0,1,2,3)),
 "spy_open_drive_wide (SPY>=0.3%)": rule({"SPY":0.003},(0,1,2,3)),
 "SPY 0.3-0.5% only": lambda r: rule({"SPY":0.003},(0,1,2,3))(r) and r['move10']<0.005,
 "stock_open_drive (NVDA/TSLA>=0.8%, Mon/Wed)": rule({"NVDA":0.008,"TSLA":0.008},(0,2)),
 "NVDA/TSLA>=0.8% any weekday, filters": rule({"NVDA":0.008,"TSLA":0.008},(0,1,2,3,4)),
 "SPY+NVDA+TSLA calls >=0.5% no filters": rule({"SPY":0.005,"NVDA":0.005,"TSLA":0.005},None,False),
}
for name,f in groups.items():
    print("##",name)
    for per,cut in (("3m","2026-07-16"),("1y","2025-10-16"),("all","")):
        sel=[r for r in rows if f(r) and r['day']>=cut and r.get('exits_10')]
        if not sel: continue
        print(" ",per, " | ".join(f"{m} {st([r['exits_10'][m] for r in sel])}" for m in MODES))
# weekday effect for SPY calls >=0.3 no weekday filter
print("## weekday, SPY calls >=0.3%, no release/opex, take3 and half3_trail")
for wd in range(5):
    sel=[r for r in rows if r['sym']=='SPY' and r['kind']=='call' and r['move10']>=0.003 and not r['macro'] and not opex_week(d(r)) and d(r).weekday()==wd]
    print(" ", "MTWTF"[wd], "take3", st([r['exits_10']['take3'] for r in sel]), "| half3_trail", st([r['exits_10']['half3_trail'] for r in sel]))
