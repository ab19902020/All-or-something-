"""Simple prop inserts, in the existing engine's raster drawing convention."""
import math
import numpy as np
from PIL import Image,ImageDraw
from studio.film import graphics as G
from studio.film.engine import OW,OH,RS

def spray(s,t):
    im=Image.new('RGB',(1920,1080),(62,48,44));d=ImageDraw.Draw(im)
    ink=(22,20,23)
    d.rectangle((0,740,1920,1080),fill=(100,60,39))
    # Complete drawn hand around the can: no detached or floating prop.
    d.polygon([(1040,1080),(1030,710),(1100,635),(1180,655),(1220,745),(1280,1080)],fill=(237,163,108),outline=ink,width=8)
    d.rounded_rectangle((915,420,1135,850),radius=28,fill=(37,108,187),outline=ink,width=10)
    d.rectangle((930,380,1120,445),fill=(199,206,215),outline=ink,width=8)
    d.rounded_rectangle((995,350,1100,390),radius=10,fill=(36,39,46),outline=ink,width=8)
    d.ellipse((1040,575,1190,660),fill=(244,173,118),outline=ink,width=8)
    d.text((960,500),'AIR',font=G.font(G.BEBAS,68),fill='white')
    phase=min(abs(t-10.80),abs(t-11.30))
    if phase<.23:
        layer=Image.new('RGBA',im.size);p=ImageDraw.Draw(layer)
        for i in range(8):
            x=1020-i*43;y=350-i*7
            r=20+i*10
            p.ellipse((x-r,y-r,x+r,y+r),fill=(231,240,248,int(100*(1-phase/.23))))
        im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
    return np.asarray(im.resize((OW,OH),Image.Resampling.LANCZOS)).astype(np.float32)/255.

def overlay(img,t,s):
    im=Image.fromarray(np.clip(img*255,0,255).astype('uint8'));d=ImageDraw.Draw(im)
    def label(txt,y,size=28,color=(255,255,255)):
        f=G.font(G.INTER,size*RS)
        box=d.textbbox((0,0),txt,font=f);x=(OW-(box[2]-box[0]))/2
        d.text((x,y*RS),txt,font=f,fill=color,stroke_width=max(1,int(2*RS)),stroke_fill=(15,15,18))
    if t<2.1: label('CARRINGTON',180,34)
    if 20.6<t<22.7:
        label('GARY NEVILLE',780,32)
        label('SELF-APPOINTED INSPECTOR',825,23)
    if 27.2<=t<28.2:
        # The centre pose has no separate pointing arm: his eyeline supplies his nomination.
        label('WHO IS IN CHARGE?',780,30)
    if t>=28.2: label('SPECIAL MEASURES',805,42,(255,210,75))
    label('ALL OR SOMETHING • FICTIONAL PARODY',995,17)
    return np.asarray(im).astype(np.float32)/255.
