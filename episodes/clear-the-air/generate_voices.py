#!/usr/bin/env python3
"""Resume-safe Fish synthesis using the show's existing models. No embedded API key."""
import argparse,importlib.util,json,os,pathlib,re,time
import requests
HERE=pathlib.Path(__file__).resolve().parent
KEYS={'NARRATOR':'narrator','JASON':'jason-wilcox','BRUNO':'bruno-fernandes',
      'CARRICK':'michael-carrick','GARY':'gary-neville'}
TAGS={'NARRATOR':'[serious, low documentary voice] ',
      'JASON':'[calm, brisk, matter of fact] ',
      'BRUNO':'[indignant, frustrated] ',
      'CARRICK':'[calm, low, deadpan, unimpressed] ',
      'GARY':'[firm, officious] '}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--only',default='');ap.add_argument('--check',action='store_true')
    a=ap.parse_args()
    key=os.environ.get('FISH_API_KEY')
    if a.check:
        print('Fish credential configured' if key else 'BLOCKED: FISH_API_KEY is not configured')
        return 0 if key else 2
    if not key: raise SystemExit('Set FISH_API_KEY in the execution environment; no speech has been generated.')
    mp=HERE/'voices/fish_models.json';models=json.loads(mp.read_text())
    only=set(filter(None,a.only.split(',')))
    lines=re.findall(r'^\[(L\d+)\]\s+([A-Z]+):\s*(.+)$',(HERE/'script.md').read_text(),re.M)
    wanted=[x for x in lines if not only or x[0] in only]
    if any(sp=='GARY' for _,sp,_ in wanted) and 'gary-neville' not in models:
        with (HERE/'voices/gary-source.mp3').open('rb') as f:
            r=requests.post('https://api.fish.audio/model',headers={'Authorization':'Bearer '+key},
                data={'type':'tts','title':'AOS Gary Neville (parody)','train_mode':'fast','visibility':'private',
                      'description':'Private fictional satire character; source is the supplied Clony recording.',
                      'enhance_audio_quality':'true'},
                files=[('voices',('gary-source.mp3',f,'audio/mpeg'))],timeout=(30,180))
        r.raise_for_status();j=r.json()
        models['gary-neville']={'id':j['_id'],'state':j.get('state'),'source':'voices/gary-source.mp3'}
        mp.write_text(json.dumps(models,indent=2)+'\n')
        if j.get('state')!='trained':
            raise SystemExit('Gary model created and its ID saved. Training is pending; do not recreate the model.')
    for _,sp,_ in wanted:
        if sp=='GARY':
            j=requests.get('https://api.fish.audio/model/'+models['gary-neville']['id'],
                           headers={'Authorization':'Bearer '+key},timeout=30)
            j.raise_for_status()
            if j.json().get('state')!='trained':raise SystemExit('Gary voice model is still training; retry later.')
            break
    spec=importlib.util.spec_from_file_location('aos_fish',HERE/'voices/fish_tts.py')
    fish=importlib.util.module_from_spec(spec);spec.loader.exec_module(fish)
    out=HERE/'voiceovers';out.mkdir(exist_ok=True)
    manifest={}
    mf=out/'manifest.json'
    if mf.exists():manifest=json.loads(mf.read_text())
    for lid,sp,text in wanted:
        dest=out/f'{lid}.wav'
        if dest.exists():continue
        ref=models[KEYS[sp]]['id']
        fish.tts(key,ref,TAGS[sp]+text,dest,'s2.1-pro')
        manifest[lid]={'character':KEYS[sp],'model_id':ref,'text':text,'file':dest.name,'reviewed':False}
        mf.write_text(json.dumps(manifest,indent=2)+'\n')
        print(lid,KEYS[sp],'generated; awaiting listening review',flush=True)
    print('Synthesis complete. Listen to takes, align real speech, and review the timeline before rendering.')

if __name__=='__main__':raise SystemExit(main())
