import sys
from PIL import Image, ImageDraw
ks=sys.argv[2:]; W=300
ims=[Image.open(f'img/{k}.jpg') for k in ks]
for i in ims: i.thumbnail((W,400))
cols=min(6,len(ims)); rows=(len(ims)+cols-1)//cols
c=Image.new('RGB',(cols*(W+8),rows*420),'#666'); d=ImageDraw.Draw(c)
for n,(k,i) in enumerate(zip(ks,ims)):
    x,y=(n%cols)*(W+8),(n//cols)*420; c.paste(i,(x,y)); d.text((x+4,y+404),k,fill='white')
c.save(sys.argv[1],quality=85)
