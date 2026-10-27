import io, tempfile, subprocess
from pathlib import Path
import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import imageio_ffmpeg

ROOT=Path(__file__).parent
OUT=ROOT/"output"
OUT.mkdir(exist_ok=True)
st.set_page_config(page_title="Realty Galaxy Studio",page_icon="🌌",layout="wide")

st.markdown(r"""
<style>
.stApp{background:radial-gradient(ellipse at 15% 15%,#51449b88,transparent 35%),radial-gradient(ellipse at 85% 25%,#1689a855,transparent 34%),linear-gradient(125deg,#050713,#10132d 48%,#080b1b);background-size:160% 160%;animation:drift 26s ease-in-out infinite alternate;color:#fff}
@keyframes drift{from{background-position:0% 0%}to{background-position:100% 100%}}
.stApp:before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.7;background-image:radial-gradient(2px 2px at 8% 17%,white 95%,transparent),radial-gradient(1px 1px at 23% 77%,white 95%,transparent),radial-gradient(2px 2px at 42% 32%,white 95%,transparent),radial-gradient(1px 1px at 64% 81%,white 95%,transparent),radial-gradient(2px 2px at 79% 12%,white 95%,transparent),radial-gradient(1px 1px at 92% 61%,white 95%,transparent);background-size:370px 300px;animation:stars 34s linear infinite}
@keyframes stars{from{transform:translate(0,0)}to{transform:translate(-55px,38px)}}
.stApp,.stApp *{cursor:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 32 32'%3E%3Cpath d='M16 1L19 12L30 16L19 19L16 31L12 19L1 16L12 12Z' fill='white' stroke='%23b8c9ff'/%3E%3C/svg%3E") 16 16,auto}
.block-container{position:relative;z-index:1;max-width:1380px;padding-top:1.2rem}
.hero{padding:28px;border:1px solid #ffffff66;border-radius:24px;background:linear-gradient(120deg,#ffffff22,#ffffff08);box-shadow:0 0 28px #ffffff20;backdrop-filter:blur(16px);margin-bottom:20px}
.hero h1{font-size:2.3rem;color:white;margin:0 0 8px}.hero p{color:#e5eaff;margin:0}
div[data-testid="stForm"],div[data-testid="stExpander"],div[data-testid="stMetric"],div[data-testid="stFileUploader"]{border:1px solid #ffffff70!important;border-radius:15px!important;background:#ffffff0d!important;box-shadow:0 0 15px #ffffff12}
.stButton button,.stDownloadButton button{border:1px solid #ffffffaa!important;border-radius:14px!important;background:linear-gradient(100deg,#ffffff30,#ffffff0d)!important;color:white!important;box-shadow:0 0 15px #ffffff25;transition:.2s}
.stButton button:hover,.stDownloadButton button:hover{transform:translateY(-2px);box-shadow:0 0 25px #ffffff55}
[data-testid="stSidebar"]{background:#070a1deF;border-right:1px solid #ffffff30}
hr{border-color:#ffffff35}
</style>
""",unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🌌 Realty Galaxy Studio</h1><p>Universe motion • white sparkles • 12 themes • editable scenes • MP4 export</p></div>',unsafe_allow_html=True)

TEMPLATES=["Galaxy Universe","Luxury Gold","Dreamy Pastel","Cyber Neon","Minimal White","Cinematic Noir","Nature Zen","Rose Gold","Ocean Blue","Retro Film","Royal Purple","Sunset Warm"]
PALETTES={
"Galaxy Universe":((11,14,42),(147,131,255),(255,255,255)),"Luxury Gold":((24,22,27),(232,190,105),(255,255,255)),
"Dreamy Pastel":((242,224,244),(190,127,190),(48,42,66)),"Cyber Neon":((8,12,28),(0,244,255),(255,255,255)),
"Minimal White":((245,247,252),(93,111,151),(32,38,56)),"Cinematic Noir":((12,15,25),(230,230,245),(255,255,255)),
"Nature Zen":((27,52,42),(167,207,139),(255,255,255)),"Rose Gold":((52,30,43),(239,166,169),(255,255,255)),
"Ocean Blue":((10,40,65),(89,202,232),(255,255,255)),"Retro Film":((69,48,36),(232,176,106),(255,244,220)),
"Royal Purple":((36,20,66),(199,158,255),(255,255,255)),"Sunset Warm":((91,42,40),(255,178,117),(255,255,255))}
def font(sz,bold=False):
    path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:return ImageFont.truetype(path,sz)
    except:return ImageFont.load_default()
def crop(im,size):
    w,h=size; im=im.convert("RGB"); scale=max(w/im.width,h/im.height)
    im=im.resize((int(im.width*scale),int(im.height*scale)),Image.Resampling.LANCZOS)
    return im.crop(((im.width-w)//2,(im.height-h)//2,(im.width+w)//2,(im.height+h)//2))
def wrap(draw,text,f,maxw):
    lines=[]; line=""
    for word in str(text).split():
        test=(line+" "+word).strip()
        if draw.textbbox((0,0),test,font=f)[2]<=maxw:line=test
        else:
            if line:lines.append(line)
            line=word
    if line:lines.append(line)
    return lines
def scene(photo,title,subtitle,theme,index,total,size,tag,filter_name,brightness):
    base,accent,fg=PALETTES[theme]; im=crop(photo,size) if photo else Image.new("RGB",size,base)
    if filter_name=="Vintage":im=ImageEnhance.Color(im).enhance(.65);im=ImageEnhance.Contrast(im).enhance(1.1)
    elif filter_name=="Vivid":im=ImageEnhance.Color(im).enhance(1.35)
    elif filter_name=="Soft":im=ImageEnhance.Color(im).enhance(.8);im=im.filter(ImageFilter.GaussianBlur(1))
    im=ImageEnhance.Brightness(im).enhance(brightness).convert("RGBA")
    tint=Image.new("RGBA",size,(*base,48));im=Image.alpha_composite(im,tint)
    d=ImageDraw.Draw(im);w,h=size
    d.rounded_rectangle((28,int(h*.58),w-28,h-20),radius=24,fill=(*base,220),outline=(*accent,235),width=2)
    if theme=="Galaxy Universe":
        for x,y,r in [(80,90,3),(250,180,2),(w-100,100,3),(w-180,300,2),(w//2,70,2),(150,h//2,2)]:
            d.ellipse((x-r,y-r,x+r,y+r),fill="white");d.line((x-8,y,x+8,y),fill="white");d.line((x,y-8,x,y+8),fill="white")
    d.rounded_rectangle((45,30,305,72),radius=18,fill=(*accent,245))
    d.text((61,41),"✦ REALTY ASSISTANT",font=font(17,True),fill=base)
    d.text((w-125,38),f"{index+1:02d}/{total:02d}",font=font(17,True),fill=fg)
    y=int(h*.64)
    for line in wrap(d,title,font(42 if w>800 else 30,True),w-100)[:2]:
        d.text((48,y),line,font=font(42 if w>800 else 30,True),fill=fg);y+=50 if w>800 else 38
    for line in wrap(d,subtitle,font(23 if w>800 else 18),w-100)[:2]:
        d.text((50,y+4),line,font=font(23 if w>800 else 18),fill=fg);y+=30
    if tag.strip():
        d.rounded_rectangle((w-360,100,w-42,145),radius=17,fill=(*accent,240))
        d.text((w-345,112),tag[:30],font=font(16,True),fill=base)
    d.rounded_rectangle((48,h-36,w-48,h-29),radius=4,fill=(255,255,255,90))
    d.rounded_rectangle((48,h-36,48+int((w-96)*(index+1)/total),h-29),radius=4,fill=(*accent,255))
    return im.convert("RGB")
def render_video(images,titles,captions,tags,theme,out,seconds,music,filter_name,brightness,ratio):
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    size=(1280,720) if ratio=="16:9" else ((720,1280) if ratio=="9:16" else (1080,1080))
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp);paths=[]
        for i in range(len(images)):
            p=tmp/f"s{i}.jpg";scene(images[i],titles[i],captions[i],theme,i,len(images),size,tags[i],filter_name,brightness).save(p,quality=93);paths.append(p)
        concat=tmp/"list.txt"
        with open(concat,"w") as f:
            for p in paths:f.write(f"file '{p.as_posix()}'\nduration {seconds}\n")
            f.write(f"file '{paths[-1].as_posix()}'\n")
        cmd=[ff,"-y","-f","concat","-safe","0","-i",str(concat),"-vf","format=yuv420p","-r","25","-c:v","libx264","-preset","fast","-crf","22","-movflags","+faststart"]
        if music:
            mp=tmp/"music";mp.write_bytes(music);cmd+=["-stream_loop","-1","-i",str(mp),"-shortest","-c:a","aac","-b:a","160k"]
        else:cmd+=["-an"]
        cmd += [str(out)]
        res=subprocess.run(cmd,capture_output=True,text=True)
        if res.returncode:raise RuntimeError(res.stderr[-1600:])
    return out

with st.sidebar:
    st.markdown("## ✨ Galaxy controls")
    theme=st.selectbox("Video template",TEMPLATES)
    ratio=st.selectbox("Video ratio",["16:9","9:16","1:1"],help="16:9 YouTube • 9:16 Reels/Shorts • 1:1 square")
    seconds=st.slider("Seconds per scene",2,8,4)
    filter_name=st.selectbox("Photo filter",["Natural","Vivid","Vintage","Soft"])
    brightness=st.slider("Brightness",0.6,1.4,1.0,0.05)
    st.caption("The animated universe background, moving starfield and white sparkle cursor decorate the app.")

a,b=st.columns(2,gap="large")
with a:
    st.markdown("### 🏡 Property details")
    with st.form("property"):
        name=st.text_input("Property name","Modern 2-BHK Apartment")
        location=st.text_input("Location","Kalka, Himachal Pradesh")
        price=st.text_input("Price","₹45 lakh")
        kind=st.selectbox("Property type",["Apartment","Independent House","Villa","Studio","Plot","Commercial"])
        beds=st.selectbox("Bedrooms",["Studio","1 BHK","2 BHK","3 BHK","4+ BHK","Not applicable"],index=2)
        feature_text=st.text_area("Features (one per line)","Bright living room\nModular kitchen\nBalcony with a view\nCovered parking")
        cta=st.text_input("Contact / CTA","Book your site visit today")
        submitted=st.form_submit_button("🌠 Create / update video",use_container_width=True)
    photos=st.file_uploader("Upload up to 8 property photos",type=["jpg","jpeg","png","webp"],accept_multiple_files=True)
    music=st.file_uploader("Optional licensed music",type=["mp3","wav","m4a"])
with b:
    st.markdown("### 🎬 Scene editor")
    st.caption("Edit the text shown on each scene before exporting. Your edits are used in the generated video.")
    feats=[x.strip() for x in feature_text.splitlines() if x.strip()]
    defaults_t=[name,f"{kind} in {location}","Thoughtful details",price or "Enquire for pricing","Make it yours"]
    defaults_c=[f"{location} • {beds}","A closer look at the property"," • ".join(feats[:3]) if feats else "Explore the space",
                " • ".join(feats[3:6]) if len(feats)>3 else f"{beds} • {kind}",cta]
    defaults_b=["NEW LISTING","LOCATION","FEATURES","PRICE","ENQUIRE NOW"]
    if "titles" not in st.session_state:st.session_state.titles=defaults_t
    if "captions" not in st.session_state:st.session_state.captions=defaults_c
    if "tags" not in st.session_state:st.session_state.tags=defaults_b
    if len(st.session_state.titles)!=5:
        st.session_state.titles=defaults_t[:];st.session_state.captions=defaults_c[:];st.session_state.tags=defaults_b[:]
    with st.expander("✏️ Edit all 5 scenes",expanded=True):
        for i in range(5):
            st.markdown(f"**Scene {i+1}**")
            st.session_state.titles[i]=st.text_input("Headline",st.session_state.titles[i],key=f"headline{i}")
            st.session_state.captions[i]=st.text_input("Caption",st.session_state.captions[i],key=f"caption{i}")
            st.session_state.tags[i]=st.text_input("Small badge",st.session_state.tags[i],key=f"tag{i}")

if submitted:
    errors=[]
    if not name.strip():errors.append("Enter a property name.")
    if not location.strip():errors.append("Enter a location.")
    if not cta.strip():errors.append("Enter a contact / CTA.")
    if len(photos or [])>8:errors.append("Upload no more than 8 photos.")
    if errors:
        for e in errors:st.error(e)
    else:
        imgs=[]
        for f in photos or []:
            try:imgs.append(Image.open(io.BytesIO(f.getvalue())).convert("RGB"))
            except Exception:pass
        if not imgs:
            for i in range(5):
                bg=PALETTES[theme][0];im=Image.new("RGB",(1280,720),bg);d=ImageDraw.Draw(im)
                d.ellipse((850,-120,1450,480),fill=PALETTES[theme][1])
                d.rounded_rectangle((60,100,1220,620),radius=30,outline="white",width=3)
                d.text((100,240),"PROPERTY VIDEO PREVIEW",font=font(42,True),fill="white")
                d.text((105,315),"Upload real listing photos for a personalised video",font=font(23),fill="white")
                imgs.append(im)
        while len(imgs)<5:imgs.append(imgs[-1].copy())
        out=OUT/"property_promo_video.mp4"
        try:
            with st.spinner("✨ Rendering your video..."):
                render_video(imgs[:5],st.session_state.titles,st.session_state.captions,st.session_state.tags,
                             theme,out,seconds,music.getvalue() if music else None,filter_name,brightness,ratio)
            st.success("Video ready! Preview and download below.")
            st.video(str(out))
            st.download_button("⬇️ Download edited MP4",out.read_bytes(),file_name=f"{name.replace(' ','_')}_promo.mp4",mime="video/mp4",use_container_width=True)
            x,y,z=st.columns(3);x.metric("Scenes",5);y.metric("Template",theme);z.metric("Ratio",ratio)
        except Exception as e:st.error(f"Video export failed: {e}")
st.markdown("---")
x,y,z=st.columns(3)
x.markdown("**🌌 12 different themes**");x.caption("Galaxy, luxury, pastel, neon, minimal, nature, retro and more.")
y.markdown("**✏️ Editing tools**");y.caption("Edit scene headlines, captions, badges, filters, brightness and video ratio.")
z.markdown("**🎵 Soundtrack**");z.caption("Add licensed music and export a share-ready MP4.")
st.caption("CapCut-inspired lightweight editor; not a full multi-track timeline editor. Uses rule-based captions, not an external AI API. Use only property photos and music you have permission to use.")
