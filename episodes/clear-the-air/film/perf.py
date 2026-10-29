import json
from studio.film import ep
from studio.film.perf import Performance
from film.timeline import TL
from film.direction import SHOTS
L=json.loads(ep.path('lines.json').read_text())
WHO=['carrick','jason','bruno','gary']
META={'L002':('diplomatic','bruno',['blame','fresh']),
 'L003':('indignant','carrick',['tactics','shit']),
 'L004':('deadpan','bruno',['defending']),
 'L005':('angry','jason',['jason','hell']),
 'L006':('innocent','bruno',['clearing','agenda']),
 'L007':('deadpan','cam',['fucking','freshener']),
 'L008':('confident','jason',['ofsted','inspection']),
 'L009':('confused','gary',['not','ofsted']),
 'L010':('firm','jason',['charge']),
 'L011':('flat','down',['special','measures'])}
BASE={'carrick':(-.15,-.1),'jason':(.15,.15),'bruno':(-.5,-.2),'gary':(-.3,-.1)}
GAZE={w:[(19.75,20.6,'gary')] for w in WHO if w!='gary'}
GAZE['carrick']=[(17.45,19.7,'cam'),(19.75,20.6,'gary'),(27.2,28.2,'jason')]
GAZE['jason'] += [(27.2,28.2,'bruno')]
GAZE['bruno'] += [(27.2,28.2,'carrick')]
GAZE['gary']=[(28.2,30.,'down')]
EXPR={'bruno':[(10.8,12.1,.8,-.4,.08)],'carrick':[(10.9,12.,.35,-.1,.12)]}
PERF=Performance(TL,L,WHO,{w:w for w in WHO},META,
 lambda lid:ep.path('lines',f'{lid}.wav'),base=BASE,gaze=GAZE,expr=EXPR,
 rest_target={'carrick':'jason','jason':'bruno','bruno':'jason','gary':'jason'},
 noblink={'carrick':[(17.4,19.7)],'gary':[(28.2,30.)]},cuts=[s['t'] for s in SHOTS])
