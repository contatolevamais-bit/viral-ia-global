#!/usr/bin/env python3
"""VIRAL IA GLOBAL: renderizador local e GitHub Actions sem API paga.
Gera 3 vídeos verticais originais a partir de roteiros previamente revisados.
Nenhuma publicação automática nas redes sociais é realizada.
"""
import argparse
import datetime as dt
import json
import math
import os
import random
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 720, 1280
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def duration(file):
    p = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(file)], capture_output=True, text=True, check=True)
    return float(p.stdout.strip())


def lines(draw, text, font, limit):
    words = text.split(); result=[]; line=''
    for word in words:
        trial = f'{line} {word}'.strip()
        if draw.textbbox((0,0),trial,font=font)[2] > limit and line:
            result.append(line);line=word
        else:line=trial
    if line:result.append(line)
    return result


def render_card(path, title, statement, scene, number, seed):
    rng=random.Random(seed*31+scene*71)
    base=[(11,23,49),(15,32,54),(31,22,57),(14,47,55),(37,25,48)][scene]
    im=Image.new('RGB',(WIDTH,HEIGHT),base); d=ImageDraw.Draw(im)
    for n in range(85):
        x=rng.randint(0,WIDTH);y=rng.randint(0,HEIGHT)
        rad=rng.randint(1,3)
        d.ellipse((x-rad,y-rad,x+rad,y+rad), fill=(70+rng.randrange(55),96+rng.randrange(80),145+rng.randrange(80)))
    d.ellipse((75,160,645,730), outline=(63,181,191),width=3)
    d.ellipse((138,222,582,666), outline=(35,103,151),width=2)
    for k in range(9):
        a=(k/9)*math.pi*2+scene
        x=360+250*math.cos(a);y=447+250*math.sin(a)
        d.ellipse((x-6,y-6,x+6,y+6),fill=(111,231,213))
    d.rounded_rectangle((48,70,672,135),radius=22,fill=(18,69,82))
    label_font=ImageFont.truetype(BOLD,24)
    d.text((72,88),'VIRAL IA GLOBAL  •  CIÊNCIA',font=label_font,fill=(176,249,233))
    titlefont=ImageFont.truetype(BOLD,51)
    yy=770
    for line in lines(d,title,titlefont,605):
        d.text((56,yy),line,font=titlefont,fill=(255,255,255));yy+=65
    d.rounded_rectangle((51,yy+17,669,yy+22),radius=2,fill=(64,211,189))
    textfont=ImageFont.truetype(FONT,33)
    yy+=67
    for line in lines(d,statement,textfont,600):
        d.text((56,yy),line,font=textfont,fill=(222,230,245));yy+=49
    d.text((54,1206),f'CURIOSIDADE {number:02d}  •  CENA {scene+1}/5',font=ImageFont.truetype(BOLD,21),fill=(134,170,196))
    im.save(path)


def voice(text, path, silent=False):
    if silent:
        sec = max(4.0, len(text.split()) / 2.3)
        run([
            'ffmpeg', '-y',
            '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
            '-t', str(sec),
            '-c:a', 'aac',
            str(path)
        ])
        return

    temp_mp3 = str(Path(path).with_suffix('.mp3'))

    run([
        'python', '-m', 'edge_tts',
        '--voice', 'pt-BR-FranciscaNeural',
        '--text', text,
        '--write-media', temp_mp3
    ])

    run([
        'ffmpeg', '-y',
        '-i', temp_mp3,
        '-af', 'highpass=f=120,lowpass=f=8000,acompressor=threshold=-18dB:ratio=2.5:attack=20:release=150,loudnorm',
        '-ar', '44100',
        '-ac', '1',
        str(path)
    ])


def create_video(topic, index, output, silent=False):
    title, a,b,c=topic
    phrases=[f'Você sabe? {title}',a,b,c,'Gostou desta descoberta? Siga nosso perfil para mais ciência e curiosidades.']
    headlines=[title,'Primeira descoberta','O detalhe surpreendente','Agora faz sentido','Quer descobrir mais?']
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp); parts=[]
        for scene,phrase in enumerate(phrases):
            pic=tmp/f'scene_{scene}.png';aud=tmp/f'voice_{scene}.{ "m4a" if silent else "wav" }';vid=tmp/f'part_{scene}.mp4'
            render_card(pic,headlines[scene],phrase,scene,index,index)
            voice(phrase,aud,silent)
            sec=duration(aud)+0.4
            run(['ffmpeg','-y','-loop','1','-framerate','24','-i',str(pic),'-i',str(aud),'-t',f'{sec:.2f}', '-vf','format=yuv420p','-r','24','-c:v','libx264','-preset','ultrafast','-crf','28','-c:a','aac','-b:a','96k','-ar','44100','-shortest',str(vid)])
            parts.append(vid)
        playlist=tmp/'concat.txt';playlist.write_text(''.join(f"file '{p}'\n" for p in parts))
        run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(playlist),'-c','copy',str(output)])
    return title


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--date',default=dt.date.today().isoformat());ap.add_argument('--count',type=int,default=3);ap.add_argument('--silent-demo',action='store_true',help='Vídeo mudo de teste sem voz; não publicar');ap.add_argument('--out',default='output');args=ap.parse_args()
    subjects=json.loads((ROOT/'data'/'temas.json').read_text(encoding='utf-8'))
    first=dt.date.fromisoformat(os.environ.get('PROJECT_START','2026-11-07'))
    today=dt.date.fromisoformat(args.date)
    if today<first:raise SystemExit('Data anterior ao início configurado')
    offset=(today-first).days*3
    if offset>=len(subjects):raise SystemExit('BIBLIOTECA ESGOTADA: adicione novos temas originais a data/temas.json antes de gerar mais vídeos.')
    picked=subjects[offset:offset+args.count]
    if len(picked)<args.count:raise SystemExit('Não há temas novos suficientes para hoje. Renove a biblioteca.')
    dest=Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    meta=[]
    for i,topic in enumerate(picked):
        n=offset+i+1;path=dest/f'{args.date}_video_{i+1:02d}.mp4'
        print(f'Gerando {path} — {topic[0]}',flush=True)
        name=create_video(topic,n,path,args.silent_demo)
        meta.append({'arquivo':path.name,'titulo':name,'legenda':f'{name} 🔬 Qual dessas curiosidades você quer ver a seguir? #ciencia #curiosidades #descobertas','status':'REVISAR ANTES DE PUBLICAR','simulacao_sem_voz':args.silent_demo})
    (dest/'publicacoes.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    (dest/'LEIA_ANTES_DE_PUBLICAR.txt').write_text('Revise as informações, áudio, sincronização e direitos de todo material. Publicação no Kwai é manual. Se --silent-demo foi usado, NÃO publique: este modo não tem locução.\n',encoding='utf-8')
    print('Concluído. Saída:',dest)

if __name__=='__main__':main()
