# Diminui o olho escuro grande ("olho de panda") da comemoração do Timtim para o tamanho do olho dele.
# Uso: python3 game/tools/conserta-olho-comemora.py <entrada.webp> <saida.png> [escala=0.74]  (precisa de opencv-python-headless)
import cv2, numpy as np, json, sys
A='/home/user/timtim/game/assets/anim/'
SRC=sys.argv[1]; OUT=sys.argv[2]; K=float(sys.argv[3]) if len(sys.argv)>3 else 0.74
m=json.load(open(A+'timtim-comemora.json')); im=cv2.imread(SRC, cv2.IMREAD_UNCHANGED)
fw=im.shape[1]//m['cols']; res=im.copy(); log=[]
for i in range(m['n']):
    fr=im[:, i*fw:(i+1)*fw].copy(); g=cv2.cvtColor(fr[:,:,:3],cv2.COLOR_BGR2GRAY)
    dark=((g<70)&(fr[:,:,3]>200)).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(dark,8)
    best=None
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if not (50<=a<=220 and w<=24 and h<=20 and 45<=x<=135): continue
        blob=(lab==k).astype(np.uint8); ring=cv2.dilate(blob,np.ones((7,7),np.uint8))-blob
        if g[ring>0].mean()<140: continue
        if best is None or y<st[best,1]: best=k
    if best is None: log.append((i,'-')); continue
    blob=(lab==best).astype(np.uint8)
    # olho inteiro: o escuro mais a borda acinzentada em volta
    soft=((g<150)&(fr[:,:,3]>200)).astype(np.uint8)
    grow=cv2.dilate(blob,np.ones((5,5),np.uint8))&soft | blob
    ys,xs=np.nonzero(blob); cx,cy=xs.mean(),ys.mean()
    ax=(xs.max()-xs.min()+1)/2*K; ay=(ys.max()-ys.min()+1)/2*K
    # brilho original (o ponto mais claro dentro do olho) para manter o lado da luz
    hl=cv2.inRange(g,170,255)&cv2.dilate(blob,np.ones((3,3),np.uint8)); hy,hx=np.nonzero(hl)
    hdx,hdy=((hx.mean()-cx)/max(1,ax/K),(hy.mean()-cy)/max(1,ay/K)) if len(hx) else (-0.3,-0.35)
    mask=cv2.dilate(grow,np.ones((3,3),np.uint8))*255
    bgr=cv2.inpaint(fr[:,:,:3],mask,4,cv2.INPAINT_TELEA)
    # olho novo desenhado em 4x e reduzido (borda macia)
    S=4; H,W=g.shape
    big=cv2.resize(bgr,(W*S,H*S),interpolation=cv2.INTER_CUBIC)
    lay=np.zeros((H*S,W*S),np.float32); eye=np.zeros((H*S,W*S,3),np.float32)
    c=(int(cx*S),int(cy*S)); ax_=(int(ax*S),int(ay*S))
    cv2.ellipse(lay,c,ax_,0,0,360,1.0,-1,cv2.LINE_AA)
    eye[:]=(22,24,30)
    # leve tom castanho no centro
    cv2.ellipse(eye,c,(int(ax*S*0.7),int(ay*S*0.7)),0,0,360,(28,34,48),-1,cv2.LINE_AA)
    lay=cv2.GaussianBlur(lay,(0,0),S*0.6)
    out=big*(1-lay[...,None])+eye*lay[...,None]
    hc=(int((cx+hdx*ax*0.45)*S),int((cy+hdy*ay*0.45)*S)); r=max(2,int(min(ax,ay)*0.30*S))
    hlay=np.zeros((H*S,W*S),np.float32); cv2.circle(hlay,hc,r,1.0,-1,cv2.LINE_AA); hlay=cv2.GaussianBlur(hlay,(0,0),S*0.4)*0.95
    out=out*(1-hlay[...,None])+255*hlay[...,None]
    small=cv2.resize(out.astype(np.uint8),(W,H),interpolation=cv2.INTER_AREA)
    keep=fr[:,:,3]>0
    fr[:,:,:3]=np.where(keep[...,None],small,fr[:,:,:3])
    res[:, i*fw:(i+1)*fw]=fr; log.append((i,int(cx),int(cy),round(ax,1),round(ay,1)))
cv2.imwrite(OUT,res,[cv2.IMWRITE_WEBP_QUALITY,100] if OUT.endswith('.webp') else [])
print(log)
