# Run from anywhere:  python3 itch/make_cover.py   (needs Pillow)
# Cover 630x500: the centre of the ChatGPT banner (title and slogan) with two of the game's people
# (assets/cast: a pizzaiola and a waitress with a pizza) drawn 3x in the bottom corners, over the cut-off pizza and chair at the edges.
from PIL import Image, ImageDraw, ImageFilter
import os
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')+'/'
cv=Image.open(R+'itch/banner-main.png').crop((580,0,1420,667)).resize((630,500),Image.LANCZOS).convert('RGBA')
def cell(path,w,h,c,r): return Image.open(R+path).crop((c*w,r*h,c*w+w,r*h+h))
def put(sp,k,x,y):
    sp=sp.resize((sp.width*k,sp.height*k),Image.NEAREST)
    bb=sp.getbbox();sh=Image.new('RGBA',cv.size,(0,0,0,0));d=ImageDraw.Draw(sh)
    fx0,fx1=x+bb[0],x+bb[2];fy=y+bb[3]
    d.ellipse((fx0-6,fy-12,fx1+6,fy+8),fill=(20,8,2,130));sh=sh.filter(ImageFilter.GaussianBlur(4))
    cv.alpha_composite(sh);cv.alpha_composite(sp,(x,y))
cook=cell('assets/cast/cooks/02/idle.png',32,58,0,0)
waiter=cell('assets/cast/waiters/02/service.png',32,58,0,1)   # facing down, carrying
put(cook,3,4,500-174+8)
put(waiter,3,630-96+2,500-174+8)
cv.convert('RGB').save(R+'itch/cover-main.png',optimize=True)
