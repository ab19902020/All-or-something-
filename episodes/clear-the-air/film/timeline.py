"""Authored slots. Natural takes must fit; never silently truncate or accelerate dialogue."""
import json
from studio.film import ep

SLOTS = {
 'L001':(.10,2.30),'L002':(2.40,5.30),'L003':(5.40,8.10),
 'L004':(8.20,10.70),'L005':(12.10,14.20),'L006':(14.30,17.40),
 'L007':(17.50,19.70),'L008':(20.60,22.80),'L009':(22.90,25.10),
 'L010':(25.20,27.20),'L011':(28.30,29.90)}
L = json.loads(ep.path('lines.json').read_text())
bad = [f'{lid}: {L[lid]["dur"]:.2f}s > {b-a:.2f}s slot' for lid,(a,b) in SLOTS.items()
       if L[lid]['dur'] > b-a+.01]
if bad:
    raise ValueError('Re-perform the overlong lines; do not cut words: '+ '; '.join(bad))
TL = {'total':30.0,'lines':{lid:dict(start=a,end=a+L[lid]['dur'],speaker=L[lid]['speaker'])
                           for lid,(a,b) in SLOTS.items()},
      'marks':dict(spray=10.7,spray2=11.2,door=19.7,point=27.2,verdict=28.2,end=30.0)}
