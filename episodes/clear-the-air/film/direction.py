"""Documentary coverage; compose faces inside the centre portrait crop.
Seating: Carrick left, Wilcox centre, Bruno right. Neville enters at the right doorway.
Close singles are centred for portrait delivery; eyelines retain the seating in every cut.
"""
from studio.film.shots import single,group,world,insert,finish,shot_at as _shot_at
from film.timeline import TL

PLATES={'B':'club/boardroom'}
TABLE=[(598,440),(1068,440),(1500,735),(1500,780),(85,780),(85,712)]
OCCL={'B':{'table':[TABLE]}}
DRAW={'carrick':'michael-carrick:track','jason':'jason-wilcox:pockets',
      'bruno':'bruno-fernandes:full','gary':'gary-neville:inspector'}
ALSO=['michael-carrick:point','gary-neville:write','bruno-fernandes:point']
EYES={'carrick':{'jason':(.55,0,.08),'bruno':(.8,0,.15),'gary':(.8,-.1,.15)},
      'jason':{'carrick':(-.6,0,-.1),'bruno':(.6,0,.1),'gary':(.8,-.1,.1)},
      'bruno':{'jason':(-.55,0,-.08),'carrick':(-.8,0,-.15),'gary':(.4,-.1,.08)},
      'gary':{'jason':(-.55,0,-.1),'carrick':(-.8,0,-.15),'bruno':(-.3,0,-.04)}}
EYES_FIRST=True

def close(t,who,ed=105,draw=None,layers=()):
    bgx={'carrick':1330,'jason':470,'bruno':700,'gary':1470}[who]
    return single(t,who,draw or DRAW[who],('B',bgx,282,3.2,2.0),
                  ('B','table',833,440,3.9,0),ed=ed,eye=(960,420),
                  table=3.9,push=(1.,1.025),drift=.25,layers=list(layers))

def trio(t,point=False):
    actors=[('carrick','michael-carrick:point' if point else DRAW['carrick'],(770,430),36,False),
            ('jason',DRAW['jason'],(960,430),36,False),
            ('bruno','bruno-fernandes:point' if point else DRAW['bruno'],(1150,430),36,False)]
    return group(t,actors,[(t,(960,540,1.)),(t+2,(960,540,1.015))],
                 bg=('B',833,330,1.4,1.),fg=('B','table',833,440,2.9,0),table_y=660,drift=.15,
                 layers=[('props','point_labels')] if point else [])

SHOTS=finish([
 trio(0),close(2.3,'jason'),close(5.3,'bruno',112),close(8.1,'carrick',110),
 insert(10.7,'spray'),close(12.,'bruno',118),close(14.2,'jason',108),
 close(17.4,'carrick',115),close(19.7,'gary',100),close(20.5,'gary',110),
 close(22.8,'jason',112),close(25.1,'gary',115),trio(27.2,True),
 close(28.2,'gary',115,draw='gary-neville:write')],TL['total'])
TITLE=()
CAPTIONS=[(.15,2.1,'place','CARRINGTON','A meeting to clear the air.'),
          (20.7,22.6,'name','GARY NEVILLE','Self-appointed standards inspector. Fictional parody.')]
WHIPS=[]
def shot_at(t): return _shot_at(SHOTS,t)
