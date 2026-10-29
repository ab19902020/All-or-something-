from studio.film import audio as A
from film.timeline import TL

def main():
    dlg,amb,fx,mus=A.Bus(),A.Bus(),A.Bus(),A.Bus()
    A.dialogue(dlg,room_s=.25,room_db=-26)
    A.bed(amb,'ambience/room-tone-hvac',0.,30.,-53,fin=.05)
    for t in (10.75,11.25):
        A.ev(fx,'cloth/cloth-c',t,-43,highpass=1500)
    A.ev(fx,'creaks/creak-short',19.7,-38,semis=-4)
    A.ev(fx,'foley/cup-down',19.85,-38)
    A.ev(fx,'foley/pen-click-a',27.2,-46)
    A.ev(fx,'foley/pen-click-b',28.28,-44)
    A.master(dlg,[amb,fx],[mus])
