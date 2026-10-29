import re
from studio.film import ep

SPEAKER = {'NARRATOR':'narrator','JASON':'jason','BRUNO':'bruno','CARRICK':'carrick','GARY':'gary'}
IDS = [f'L{i:03d}' for i in range(1,12)]
MAXGAP = .22
GAPS = {}
TEMPO = 1.0
EXTRA = {'ofsted':'AA F S T EH D','carrington':'K AE R IH NG T AH N'}

def script():
    return [(lid,SPEAKER[sp],txt) for lid,sp,txt in re.findall(
        r'^\[(L\d+)\]\s+([A-Z]+):\s*(.+)$',(ep.DIR/'script.md').read_text(),re.M)]

def lines():
    return [(lid,who,text,str(ep.DIR/'voiceovers'/f'{lid}.wav'),None,1) for lid,who,text in script()]
