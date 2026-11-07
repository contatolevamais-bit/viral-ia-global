# VIRAL IA GLOBAL — versão 1.0 (custo zero)

Produz **três MP4 verticais 720×1280 por dia**, com narração sintética em português, telas de texto e áudio, usando exclusivamente ferramentas gratuitas. Produção original baseada numa biblioteca de 45 temas educativos. **Não acessa nem publica na conta Kwai**: o upload é manual após revisão.

## Passo a passo: GitHub

1. Entre em https://github.com/new e crie um repositório **público**, por exemplo `viral-ia-global`. NÃO carregue senhas, tokens ou dados pessoais; o conteúdo de repositórios públicos é visível a todos.
2. Baixe o ZIP do projeto, extraia e envie **todos os arquivos e pastas, inclusive `.github/workflows/gerar-videos.yml`**, para o repositório. Para preservar a pasta `.github`, é mais confiável usar Git no Windows ou enviar os arquivos manualmente pela interface do GitHub.
3. Vá em **Actions → VIRAL IA GLOBAL - gerar videos → Run workflow**. Na caixa `data`, coloque `2026-11-07` para o primeiro teste. Execute.
4. Quando a execução terminar, clique nela e baixe o artifact `viral-ia-videos-...` em **Artifacts**.
5. Extraia os vídeos MP4, assista cada um e revise roteiro, voz, ortografia e a exatidão científica. Use o arquivo `publicacoes.json` como rascunho para as legendas.
6. Abra o app Kwai e **publique manualmente** os vídeos aprovados. Confira se recursos de criação por IA precisam ser identificados na plataforma.
7. No dia seguinte, o agendamento executará a geração automaticamente, se o GitHub Actions estiver habilitado. Agendamentos podem sofrer atraso e não são garantia de pontualidade.

## Limites e cuidados

- Biblioteca de **45 temas = 15 dias a três por dia**, contando de 2026-11-07. A partir do 16º dia o fluxo **falha deliberadamente**, ao invés de duplicar temas. Adicione temas originais à lista `data/temas.json` e revise antes de continuar. Formato de cada entrada: `["título", "fato 1", "fato 2", "fato 3"]`.
- Renderização em nuvem usa minutos de GitHub Actions. Repositórios públicos em runners GitHub-hosted padrão têm condições gratuitas conforme regras vigentes; confirme limites, termos e alterações em https://docs.github.com/en/billing/.
- A estética usa gráficos procedurais e letreiros. É um **protótipo técnico**, não garantia de viralização ou monetização. Antes de escalar, melhorar animação, identidade visual e valor editorial. Vídeos excessivamente padronizados podem não ser elegíveis para monetização.
- As informações devem ser verificadas por editor humano, especialmente antes de alegações extraordinárias. Sem trilhas comerciais ou imagens de terceiros.
- O upload direto no Kwai não foi habilitado porque não identificamos uma integração oficial pública aplicável a esta conta. **Não automatize login, navegador ou CAPTCHA** de forma a burlar controles do serviço.
- O projeto não coleta estatísticas do Kwai automaticamente. Anote semanalmente seguidores, views, retenção e vídeos postados em sua própria planilha.

## Executar no Ubuntu ou WSL (Windows)

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg espeak-ng fonts-dejavu-core python3-pip
python3 -m pip install -r requirements.txt
python3 src/generate.py --date 2026-11-07 --count 3 --out output
```

Para verificar visualmente o render **sem o espeak-ng**: adicione `--silent-demo`; os arquivos resultantes não têm locução e NÃO devem ser publicados.

## Alterar agendamento

O workflow cron `20 10 * * *` é aproximadamente 07:20 de Fortaleza/Brasília (UTC-3). Se mudar o horário, use UTC e confira o fuso. Ajuste `PROJECT_START` se for começar em outra data: esse valor controla a sequência de temas (e precisa ser consistente entre dias).

## Próximas versões possíveis

- Renderização de ilustrações/infográficos novos por vídeo (sem copiar obras protegidas).
- Revisão editorial semiautomatizada e medição de retenção.
- Geração de versões traduzidas e publicação apenas pelas APIs oficialmente autorizadas de cada rede.
