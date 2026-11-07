        draw.text((56, y), row, font=body_font, fill=(222, 230, 245))
        y += 42
    draw.text((54, 1206), f'CURIOSIDADE {number:02d}  •  CENA {scene+1}/5',
              font=font(BOLD, 21), fill=(134, 170, 196))
    picture.save(path)


def create_voice(narration, destination, silent=False):
    if silent:
        seconds = max(4.0, len(narration.split()) / 2.3)
        run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono',
             '-t', str(seconds), '-c:a', 'pcm_s16le', str(destination)])
        return
    mp3_file = destination.with_suffix('.mp3')
    run([sys.executable, '-m', 'edge_tts', '--voice',
         'pt-BR-FranciscaNeural', '--text', narration,
         '--write-media', str(mp3_file)])
    run(['ffmpeg', '-y', '-i', str(mp3_file), '-vn',
         '-af', 'highpass=f=90,lowpass=f=11000,acompressor=threshold=-18dB:ratio=2:attack=20:release=150,loudnorm=I=-16:TP=-1.5:LRA=11',
         '-ar', '44100', '-ac', '1', '-c:a', 'pcm_s16le', str(destination)])


def make_video(topic, number, output, silent=False):
    if not isinstance(topic, list) or len(topic) != 4:
        raise ValueError('Cada tema precisa de título e exatamente três frases.')
    title, first, second, third = topic
    narration = [f'Você sabia? {title}', first, second, third,
                 'Quer mais descobertas? Siga nosso perfil para ver a próxima.']
    headings = [title, 'Primeira descoberta', 'O detalhe surpreendente',
                'Entenda o fenômeno', 'Quer descobrir mais?']
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        parts = []
        for scene, phrase in enumerate(narration):
            still = folder / f'scene_{scene}.png'
            audio = folder / f'voice_{scene}.wav'
            clip = folder / f'part_{scene}.mp4'
            render_scene(still, headings[scene], phrase, scene, number)
            create_voice(phrase, audio, silent)
            seconds = audio_duration(audio) + 0.4
            effect = "scale=720:1280,zoompan=z='min(zoom+0.0008,1.08)':d=1:s=720x1280:fps=30,format=yuv420p"
            run(['ffmpeg', '-y', '-loop', '1', '-framerate', '30',
                 '-i', str(still), '-i', str(audio), '-t', f'{seconds:.2f}',
                 '-vf', effect, '-r', '30', '-c:v', 'libx264',
                 '-preset', 'ultrafast', '-crf', '25', '-c:a', 'aac',
                 '-b:a', '160k', '-ar', '44100', '-shortest', str(clip)])
            parts.append(clip)
        playlist = folder / 'concat.txt'
        playlist.write_text(''.join(f"file '{part.as_posix()}'\n" for part in parts),
                            encoding='utf-8')
        run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(playlist),
             '-c', 'copy', str(output)])
    return title


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default=dt.date.today().isoformat())
    parser.add_argument('--count', type=int, default=3)
    parser.add_argument('--out', default='output')
    parser.add_argument('--silent-demo', action='store_true',
                        help='Apenas teste técnico sem voz; não publicar')
    arguments = parser.parse_args()
    if not 1 <= arguments.count <= 3:
        parser.error('--count deve ser entre 1 e 3')
    themes = json.loads((ROOT / 'data' / 'temas.json').read_text(encoding='utf-8'))
    start = dt.date.fromisoformat(os.environ.get('PROJECT_START', '2026-11-07'))
    day = dt.date.fromisoformat(arguments.date)
    if day < start:
        raise SystemExit('A data solicitada é anterior ao início do projeto.')
    offset = (day - start).days * 3
    selected = themes[offset:offset + arguments.count]
    if len(selected) != arguments.count:
        raise SystemExit('Biblioteca esgotada: adicione novos temas a data/temas.json.')
    folder = Path(arguments.out)
    folder.mkdir(parents=True, exist_ok=True)
    metadata = []
    for index, topic in enumerate(selected, 1):
        destination = folder / f'{arguments.date}_video_{index:02d}.mp4'
        print(f'Gerando: {topic[0]}', flush=True)
        title = make_video(topic, offset + index, destination, arguments.silent_demo)
        metadata.append({
            'arquivo': destination.name,
            'titulo': title,
            'legenda': f'{title} 🔬 Você já sabia? #ciencia #curiosidades #descobertas',
            'status': 'REVISAR ANTES DE PUBLICAR',
            'simulacao_sem_voz': arguments.silent_demo
        })
    (folder / 'publicacoes.json').write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    (folder / 'LEIA_ANTES_DE_PUBLICAR.txt').write_text(
        'Revise fatos, narração, sincronização e direitos. Postagem no Kwai é manual. '
        'Se gerou com --silent-demo, NÃO publique: o vídeo está sem narração.\n',
        encoding='utf-8')
    print(f'Concluído: {len(metadata)} vídeos em {folder}', flush=True)


if __name__ == '__main__':
    main()
