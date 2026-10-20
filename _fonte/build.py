"""Gera o site da Trypace (várias páginas estáticas) a partir dos dados abaixo.

Uso: python3 _fonte/build.py .   (rodar dentro da pasta do site)
Para mudar preço, modelo ou foto, edite MODELOS e rode de novo.
Estilo em _fonte/trypace.css, comportamento em _fonte/trypace.js.
"""
import json, html, hashlib, os, re, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__)) + '/'
OUT = os.path.abspath(sys.argv[1]) + '/'
SITE = 'https://trypace.com.br/'          # CONFIRMAR: domínio
HANDLE = 'trypace'                         # CONFIRMAR: @ do Instagram
IG_DM = f'https://ig.me/m/{HANDLE}'
IG_PROFILE = f'https://www.instagram.com/{HANDLE}/'
DATA_PRECOS = '19/10/2026'

# Valor de avaliação do usado (R$) para o simulador de upgrade, em ótimo estado.
# Vazio = o site diz "avaliado no direct". CONFIRMAR: preencher quando a loja tiver a tabela.
TROCA = {}

# ---------- Fotos de corrida (Unsplash, licença Unsplash) ----------
U = 'https://images.unsplash.com/'
F = {
    'pista': ('photo-1744060204728-f68e434a3edf', 'Corredor em velocidade numa pista de atletismo ao pôr do sol'),
    'trilha': ('photo-1697663837192-797d28e564d8', 'Homem correndo numa trilha no meio da mata'),
    'pulso': ('photo-1773399452188-a42e29543bf2', 'Relógio esportivo no pulso durante o treino'),
    'corredora': ('photo-1509010636466-2292663e132f', 'Mulher correndo na rua com relógio esportivo'),
    'prova': ('photo-1759674861540-afed9f86f94a', 'Corredores durante uma prova de rua'),
    'confere': ('photo-1759488885839-557b23c54d34', 'Corredor conferindo o relógio durante o longão'),
    'punho': ('photo-1728281189472-7070f13b0b29', 'Relógio esportivo no pulso de um corredor'),
    'mata': ('photo-1729280924877-4750c0dba51e', 'Corredor de camiseta azul no meio da mata'),
    'cidade': ('photo-1758506971986-b0d0edebd8d5', 'Corredor numa avenida da cidade'),
    'rua': ('photo-1766970096320-c62c49517226', 'Corredor numa rua da cidade'),
    'asfalto': ('photo-1763489471289-175a87ce5b3a', 'Largada de prova no asfalto'),
    'trio': ('photo-1552674605-db6ffd4facb5', 'Grupo de corredores treinando antes do sol nascer'),
    'tatuagem': ('photo-1755682235609-dc8c9d98772d', 'Pulso com relógio esportivo depois do treino'),
    'fonte': ('photo-1727094141271-9bea5bc8c757', 'Corredor numa praça da cidade'),
}
ORDEM_FOTOS = list(F)
LEGENDA = {'pista': 'Tiro na pista', 'trilha': 'Trilha fechada', 'pulso': 'Zona 2 no pulso', 'corredora': 'Rodagem de manhã', 'prova': 'Dia de prova', 'confere': 'Conferindo o pace', 'punho': 'Pace na hora', 'mata': 'Longão na mata', 'cidade': 'Tiro na avenida', 'rua': 'Rua livre', 'asfalto': 'Largada', 'trio': 'Treino em grupo', 'tatuagem': 'Body Battery em dia', 'fonte': 'Rodagem leve'}

def u(k, w, h=None):
    s = f'{U}{F[k][0]}?auto=format&fit=crop&q=70&w={w}' + (f'&h={h}' if h else '')
    return s.replace('&', '&amp;')

def img(k, ratio, sizes, widths=(480, 800, 1200), lazy=True, cls='', alt=None):
    w0 = widths[1] if len(widths) > 1 else widths[0]
    srcset = ', '.join(f'{u(k, w, round(w*ratio))} {w}w' for w in widths)
    a = html.escape(alt if alt is not None else F[k][1])
    return (f'<img{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} src="{u(k, w0, round(w0*ratio))}" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w0}" height="{round(w0*ratio)}" alt="{a}"'
            + (' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high" decoding="async"') + '>')

def picture_hero(k, primeiro=False):
    mob = ', '.join(f'{u(k, w, round(w*1.6))} {w}w' for w in (480, 720, 960))
    return (f'<picture><source media="(max-width: 640px)" srcset="{mob}" sizes="100vw">'
            + img(k, .56, '100vw', (960, 1440, 1920, 2560), lazy=not primeiro) + '</picture>')

# ---------- Fotos de produto (Wikimedia Commons) ----------
def wiki(nome, w):
    h = hashlib.md5(nome.encode()).hexdigest()
    return f'https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{nome}/{w}px-{nome}'

FOTOS_PROD = {
    'fr55': ('Forerunner_55_Garmin_Filipinas_shopD.jpg', 'Valenzuela400', 'CC BY-SA 4.0'),
    'fr165': ('Garmin_Forerunner_165.jpg', 'Ed Crystal', 'CC0'),
    'fr245': ('Garmin_fitness_watch_.jpg', 'GautamSudhanshu', 'CC BY-SA 4.0'),
    'fr255': ('GarminForerunner255MusicWhitestone.jpg', 'Tomek7000', 'CC BY-SA 4.0'),
    'fr265': ('Forerunner_265.jpg', '3r1ccc', 'CC0'),
    'fr945': ('Forerunner_945_Music.jpg', 'TheKleptomaniac', 'CC BY-SA 4.0'),
    'fr955': ('Garmin_955_Solar.jpg', 'Oatberry', 'CC BY-SA 4.0'),
    'fr965': ('Garmin_Forerunner_965.jpeg', 'SUNSmania41', 'CC BY-SA 4.0'),
}

DESENHO = ('<svg viewBox="0 0 200 260" aria-hidden="true"><rect x="62" y="0" width="76" height="260" rx="14" fill="#2C2C2E"/>'
           '<circle cx="100" cy="130" r="78" fill="#48484A"/><circle cx="100" cy="130" r="71" fill="#1C1C1E"/><circle cx="100" cy="130" r="61" fill="#000"/>'
           '<path d="M100 76A54 54 0 1 1 49 112" stroke="#B8FF00" stroke-width="5" fill="none" stroke-linecap="round"/>'
           '<text x="100" y="134" text-anchor="middle" font-family="Montserrat,sans-serif" font-weight="700" font-size="28" fill="#fff">5:12</text>'
           '<text x="100" y="154" text-anchor="middle" font-family="Montserrat,sans-serif" font-weight="600" font-size="11" fill="#A3A3A3">PACE /KM</text>'
           '<rect x="175" y="102" width="8" height="20" rx="3" fill="#636366"/><rect x="175" y="140" width="8" height="20" rx="3" fill="#636366"/><rect x="17" y="110" width="8" height="20" rx="3" fill="#636366"/></svg>')

# ---------- Estoque: aba "Listas" da planilha (coluna "Nosso preço") ----------
# perfil: inicio, evolucao, performance, triathlon. nivel: 0 a 3 (profundidade dos dados de treino).
MODELOS = [
    dict(id='fr265', nome='Forerunner 265', marca='Garmin', preco=2000, perfil='evolucao performance', foto='fr265', etiqueta='Mais procurado',
         resumo='AMOLED · GPS multibanda · música', frase='Sabe quando forçar. E quando descansar.',
         desc='Tela AMOLED, prontidão de treino e GPS multibanda. O relógio mais pedido da casa.',
         tela='AMOLED 1,3"', amoled=True, multibanda=True, musica=True, mapas=False, tri=True, pay=True, gpsH=20, bat='13 dias', peso='47 g', nivel=3,
         rec=('Prontidão de treino', 'Uma nota de 0 a 100 toda manhã, juntando sono, VFC e carga recente. Você sabe se hoje é dia de tiro ou de rodagem leve.'),
         motivos=['Prontidão de treino todo dia', 'Tela AMOLED e GPS multibanda', 'O mais procurado da loja']),
    dict(id='fr55', nome='Forerunner 55', marca='Garmin', preco=850, perfil='inicio', foto='fr55', etiqueta='Menor preço',
         resumo='GPS · treino sugerido', frase='O primeiro passo certo.',
         desc='O primeiro relógio de corrida certo. Simples, leve e com treino sugerido todo dia.',
         tela='MIP 1,04"', amoled=False, multibanda=False, musica=False, mapas=False, tri=False, pay=False, gpsH=20, bat='2 semanas', peso='37 g', nivel=0,
         rec=('Treino sugerido', 'Todo dia o relógio sugere o treino certo pro seu nível, com ritmo e duração. É como ter uma planilha no pulso.'),
         motivos=['GPS e treino sugerido todo dia', 'Até 2 semanas de bateria', 'O menor preço da loja']),
    dict(id='fr255', nome='Forerunner 255', marca='Garmin', preco=1500, perfil='performance triathlon', foto='fr255',
         resumo='GPS multibanda · modo triathlon', frase='Multibanda e triathlon. Sem pesar no bolso.',
         desc='GPS multibanda, status de VFC e modo triathlon. O melhor custo por quilômetro.',
         tela='MIP 1,3"', amoled=False, multibanda=True, musica=False, mapas=False, tri=True, pay=False, gpsH=30, bat='14 dias', peso='49 g', nivel=2,
         rec=('Status de VFC', 'A variabilidade da frequência cardíaca medida enquanto você dorme mostra se o corpo está absorvendo bem o treino.'),
         motivos=['GPS multibanda no dia da prova', '30 h de bateria com GPS', 'Modo triathlon completo']),
    dict(id='fr165', nome='Forerunner 165', marca='Garmin', preco=1450, perfil='inicio evolucao', foto='fr165',
         resumo='AMOLED · Body Battery', frase='Tela AMOLED. Recuperação no pulso.',
         desc='Tela AMOLED colorida e as métricas de recuperação dos modelos mais caros.',
         tela='AMOLED 1,2"', amoled=True, multibanda=False, musica=False, mapas=False, tri=False, pay=False, gpsH=19, bat='11 dias', peso='39 g', nivel=1,
         rec=('Body Battery e VFC', 'O Body Battery mostra quanta energia você tem pro dia. A VFC noturna acompanha como você está se recuperando.'),
         motivos=['Tela AMOLED muito nítida', 'Body Battery e VFC noturna', 'Leve no pulso']),
    dict(id='fr955', nome='Forerunner 955', marca='Garmin', preco=2500, perfil='performance triathlon', foto='fr955',
         resumo='Mapas · multibanda · touch', frase='Mapas no pulso. Bateria pro longão.',
         desc='Mapas, GPS multibanda, tela touch e plano de treino adaptativo para provas longas.',
         tela='MIP 1,3" touch', amoled=False, multibanda=True, musica=True, mapas=True, tri=True, pay=True, gpsH=42, bat='15 dias', peso='52 g', nivel=3,
         rec=('Prontidão de treino', 'Junta sono, VFC, carga e tempo de recuperação numa nota diária. É a métrica que fez a fama da linha 955.'),
         motivos=['Mapas e navegação no pulso', '42 h de bateria com GPS', 'Prontidão de treino e multibanda']),
    dict(id='fr965', nome='Forerunner 965', marca='Garmin', preco=3000, perfil='performance triathlon', foto='fr965', etiqueta='Topo de linha',
         resumo='AMOLED · mapas · titânio', frase='O mais completo. Em titânio.',
         desc='O Forerunner mais completo: AMOLED, mapas, multibanda e acabamento em titânio.',
         tela='AMOLED 1,4" touch', amoled=True, multibanda=True, musica=True, mapas=True, tri=True, pay=True, gpsH=31, bat='23 dias', peso='53 g', nivel=3,
         rec=('Prontidão de treino', 'Todas as métricas de treino da Garmin numa tela AMOLED grande: prontidão, carga aguda, VFC e tempo de recuperação.'),
         motivos=['AMOLED grande com mapas', 'Acabamento em titânio', 'Todas as métricas de treino']),
    dict(id='fr245', nome='Forerunner 245', marca='Garmin', preco=900, perfil='inicio evolucao', foto='fr245',
         resumo='Status de treino · dinâmicas', frase='Status de treino pelo preço de um básico.',
         desc='Status de treino e dinâmicas de corrida pelo preço de um básico.',
         tela='MIP 1,2"', amoled=False, multibanda=False, musica=False, mapas=False, tri=False, pay=False, gpsH=24, bat='7 dias', peso='38,5 g', nivel=1,
         rec=('Status de treino', 'Mostra se o treino está sendo produtivo, mantendo ou exagerando, com VO2 máx e carga de treino.'),
         motivos=['VO2 máx e status de treino', 'Planos do Garmin Coach', 'Ótimo custo-benefício']),
    dict(id='fr245m', nome='Forerunner 245 Music', marca='Garmin', preco=1200, perfil='evolucao', foto='fr245',
         resumo='Música · Garmin Pay', frase='Música no pulso. Celular em casa.',
         desc='Tudo do 245 com músicas no relógio. Dá para treinar sem levar o celular.',
         tela='MIP 1,2"', amoled=False, multibanda=False, musica=True, mapas=False, tri=False, pay=True, gpsH=24, bat='6 dias', peso='38,5 g', nivel=1,
         rec=('Status de treino', 'VO2 máx, carga e status de treino pra saber se a planilha está funcionando.'),
         motivos=['Música offline no relógio', 'VO2 máx e status de treino', 'Garmin Pay no pulso']),
    dict(id='fr255m', nome='Forerunner 255 Music', marca='Garmin', preco=1800, perfil='performance triathlon', foto='fr255',
         resumo='Multibanda · música', frase='O 255 completo. Com trilha sonora.',
         desc='O 255 completo, com música offline para os longões.',
         tela='MIP 1,3"', amoled=False, multibanda=True, musica=True, mapas=False, tri=True, pay=True, gpsH=30, bat='14 dias', peso='49 g', nivel=2,
         rec=('Status de VFC', 'VFC noturna, prontidão e carga de treino pra montar a semana sem chute.'),
         motivos=['Multibanda e música offline', '30 h de bateria com GPS', 'Modo triathlon e Garmin Pay']),
    dict(id='fr945', nome='Forerunner 945', marca='Garmin', preco=2000, perfil='triathlon', foto='fr945',
         resumo='Mapas · música · Garmin Pay', frase='Mapas, música e bateria de ultra.',
         desc='Mapas, música e bateria para ultra. Topo de linha com preço de intermediário.',
         tela='MIP 1,2"', amoled=False, multibanda=False, musica=True, mapas=True, tri=True, pay=True, gpsH=36, bat='2 semanas', peso='50 g', nivel=2,
         rec=('Status de treino', 'Carga de treino, foco de carga e Body Battery: o painel completo que os triatletas usam há anos.'),
         motivos=['36 h de bateria com GPS', 'Mapas e música', 'Multiesporte completo']),
    dict(id='pace3', nome='COROS Pace 3', marca='COROS', preco=1600, perfil='evolucao performance', foto=None,
         resumo='Dupla frequência · muito leve', frase='Leve como nada. Bateria que não acaba.',
         desc='Leve, GPS de dupla frequência e bateria que dura semanas.',
         tela='MIP 1,2"', amoled=False, multibanda=True, musica=True, mapas=False, tri=True, pay=False, gpsH=38, bat='24 dias', peso='39 g', nivel=2,
         rec=('Plataforma EvoLab', 'O EvoLab da COROS estima seu nível de corrida, fadiga e carga de treino a partir de cada atividade.'),
         motivos=['Muito leve no pulso', '38 h de bateria com GPS', 'GPS de dupla frequência']),
]

def slug(m):
    base = m['nome'] if m['marca'] == 'Garmin' else m['nome']
    s = base.lower().replace(' ', '-')
    return re.sub(r'[^a-z0-9-]', '', s) + '.html'

BAT_DIAS = {'fr55': 14, 'fr165': 11, 'fr245': 7, 'fr245m': 6, 'fr255': 14, 'fr255m': 14, 'fr265': 13, 'fr945': 14, 'fr955': 15, 'fr965': 23, 'pace3': 24}
for i, m in enumerate(MODELOS):
    m['batDias'] = BAT_DIAS[m['id']]
    m['pesoG'] = float(m['peso'].split(' ')[0].replace(',', '.'))
    m['url'] = slug(m)
    m['ordem'] = i
    m['nome_completo'] = m['nome'] if m['marca'] != 'Garmin' else f"Garmin {m['nome']}"
por_id = {m['id']: m for m in MODELOS}

def brl(v):
    return 'R$ ' + f'{v:,}'.replace(',', '.')

def ic(path, w=1.8):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>'

ICON_IG = ic('<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r="1" fill="currentColor" stroke="none"/>')
ICON_SACOLA = ic('<path d="M5 8h14l-1.2 12H6.2z"/><path d="M9 8V6.5a3 3 0 016 0V8"/>')
ICON_MENU = ic('<path d="M4 9h16M4 15h16"/>', 1.8)
ICON_X = ic('<path d="M6 6l12 12M18 6L6 18"/>', 2.2)
ICON_ESQ = ic('<path d="M15 5l-7 7 7 7"/>', 2.4)
ICON_DIR = ic('<path d="M9 5l7 7-7 7"/>', 2.4)
ICON_PAUSA = '<svg viewBox="0 0 14 14" aria-hidden="true"><rect x="3" y="2" width="2.6" height="10" rx=".8" fill="currentColor"/><rect x="8.4" y="2" width="2.6" height="10" rx=".8" fill="currentColor"/></svg>'
ICON_PLAY = '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M4 2.2v9.6a.6.6 0 00.9.5l7.6-4.8a.6.6 0 000-1L4.9 1.7a.6.6 0 00-.9.5z" fill="currentColor"/></svg>'

def foto_prod(m, w=500, sizes='340px', lazy=True, cls=''):
    f = FOTOS_PROD.get(m['foto']) if m['foto'] else None
    if not f:
        return f'<span class="desenho">{DESENHO}</span>'
    c = f' class="{cls}"' if cls else ''
    return (f'<img{c} src="{wiki(f[0], w)}" srcset="{wiki(f[0], 330)} 330w, {wiki(f[0], 500)} 500w, {wiki(f[0], 960)} 960w" '
            f'sizes="{sizes}" width="{w}" height="{w}" alt="{m["marca"]} {m["nome"]}"'
            + (' loading="lazy" decoding="async"' if lazy else ' decoding="async"') + '>')

def card(m, k=0):
    etq = m.get('etiqueta') or 'Seminovo'
    return f"""      <article class="card" data-rv style="--i:{min(k, 4)}">
        <div class="palco">{foto_prod(m)}<span class="etq">{etq}</span></div>
        <div class="corpo"><span class="estado">Seminovo revisado</span><h3><a href="{m['url']}">{m['nome']}</a></h3><p class="resumo">{m['resumo']}</p>
          <div class="pe"><span class="preco">{brl(m['preco'])}</span><button class="btn btn-lima btn-p" type="button" data-add="{m['id']}" aria-label="Comprar {m['nome']}">Comprar</button></div></div>
      </article>"""

SETAS = f'<div class="wrap setas"><button type="button" data-voltar aria-label="Anterior">{ICON_ESQ}</button><button type="button" data-avancar aria-label="Próximo">{ICON_DIR}</button></div>'

def fileira(id_, titulo, sub, itens, extra=''):
    return f"""  <div class="fileira" id="{id_}">
    <div class="wrap"><h2 class="titulo-fileira" data-rv>{titulo} <span>{sub}</span></h2></div>
    <div class="rolagem" data-rolagem>
{chr(10).join(card(m, k) for k, m in enumerate(itens))}
    </div>
    {SETAS}{extra}
  </div>"""

CATEGORIAS = [
    ('mais', 'Mais procurados.', 'Os favoritos de quem corre.', ['fr265', 'fr55', 'fr255', 'fr165', 'fr955', 'fr965']),
    ('inicio', 'Para começar.', 'GPS, ritmo e treino guiado sem complicação.', None),
    ('evolucao', 'Para evoluir.', 'Métricas de recuperação e status de treino.', None),
    ('performance', 'Performance.', 'GPS multibanda para quem treina com objetivo.', None),
    ('triathlon', 'Triathlon e ultra.', 'Mapas e bateria para provas longas.', None),
]
def itens_cat(k, ids):
    return [por_id[i] for i in ids] if ids else sorted([m for m in MODELOS if k in m['perfil'].split()], key=lambda m: m['preco'])

# ---------- Textos que se repetem ----------
VANT = [
    ('<circle cx="12" cy="12" r="7"/><path d="M12 8.5V12l2.3 1.6"/><path d="M9 2.8h6M9 21.2h6"/>', 'Revisão completa', 'Teste de GPS em rua, sensor óptico, bateria, tela e botões antes de cada venda.'),
    ('<path d="M12 3l7.5 3v5.5c0 4.6-3.2 8.3-7.5 9.5-4.3-1.2-7.5-4.9-7.5-9.5V6z"/><path d="M8.8 12.2l2.2 2.2 4.3-4.6"/>', 'Garantia de 90 dias', 'Defeito de funcionamento a gente resolve com reparo, troca ou devolução.'),
    ('<rect x="5.5" y="3.5" width="13" height="17" rx="2"/><path d="M8.5 8.5h7M8.5 12h7M8.5 15.5h4"/>', 'Procedência conferida', 'Número de série verificado e relógio desvinculado da conta do dono anterior.'),
    ('<path d="M4 8h13l-3.5-3.5M20 16H7l3.5 3.5"/>', 'Seu usado na troca', 'Seu Garmin atual entra como parte do pagamento do próximo.'),
    ('<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/>', 'Compra pelo direct', 'Monte a sacola aqui. O site prepara a mensagem e você fecha com uma pessoa de verdade.'),
    ('<path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0113 0c0 5.4-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.4"/>', 'Retire em Joinville', 'Ou receba em casa. A gente combina o envio pelo direct.'),
]
def vantagens():
    cards = '\n'.join(f'      <div class="vantagem" data-rv style="--i:{min(k,4)}"><span class="ic">{ic(p, 2)}</span><h3>{t}</h3><p>{d}</p></div>' for k, (p, t, d) in enumerate(VANT))
    return f"""<section class="secao gelo" id="diferenca" aria-labelledby="t-dif">
  <!-- CONFIRMAR: cada card abaixo precisa ser verdade para a loja -->
  <div class="fileira">
    <div class="wrap"><h2 class="titulo-fileira" id="t-dif" data-rv>Por que a Trypace. <span>Seminovo com cuidado de loja.</span></h2></div>
    <div class="rolagem" data-rolagem>
{cards}
    </div>
    {SETAS}
  </div>
</section>"""

def como_funciona(id_='como'):
    return f"""<section class="secao escuro" id="{id_}" aria-labelledby="t-{id_}">
  <div class="wrap">
    <h2 class="titulo-fileira" id="t-{id_}" data-rv style="font-size:clamp(32px,4vw,48px)">Compra sem cadastro. <span>Fecha no direct.</span></h2>
    <div class="passos">
      <div class="passo-c" data-rv style="--i:0"><span class="n">1</span><h3>Escolha o relógio e coloque na sacola.</h3><p>Sem cadastro e sem pagar nada no site.</p></div>
      <div class="passo-c" data-rv style="--i:1"><span class="n">2</span><h3>Toque em Finalizar no Instagram.</h3><p>O site copia o pedido e abre o nosso direct com tudo pronto.</p></div>
      <div class="passo-c" data-rv style="--i:2"><span class="n">3</span><h3>A gente confirma a unidade.</h3><p>Fotos reais do relógio, forma de pagamento e entrega combinadas com uma pessoa.</p></div>
    </div>
  </div>
</section>"""

def linha_escolha(fundo=''):
    ops = [('inicio', 'Começando agora'), ('evolucao', 'Corro com frequência'), ('performance', 'Treino pra prova'), ('triathlon', 'Triathlon ou ultra')]
    botoes = ''.join(f'<a class="opcao" href="escolha.html?perfil={k}">{t}</a>' for k, t in ops)
    return f"""<section class="secao {fundo}" aria-labelledby="t-escolha">
  <div class="wrap dupla">
    <div class="texto" data-rv>
      <p class="selo" style="color:var(--lima-texto)">Escolha o Garmin por mim</p>
      <h2 id="t-escolha">Na dúvida? A gente escolhe com você.</h2>
      <p class="lead">Responda 4 perguntas sobre seu treino, o que importa pra você e quanto quer investir. No fim, mostramos o relógio certo do nosso estoque.</p>
      <a class="btn btn-escuro" href="escolha.html" style="margin-top:8px">Começar</a>
    </div>
    <div class="painel" data-rv style="--i:1">
      <span class="passo">Pergunta 1 de 4</span>
      <strong>Como está sua corrida hoje?</strong>
      <div class="opcoes">{botoes}</div>
    </div>
  </div>
</section>"""

def linha_upgrade(para=None):
    m = por_id[para] if para else por_id['fr265']
    return f"""<section class="faixa-foto" aria-labelledby="t-upg">
  <div class="fundo" data-px>{img('punho', .62, '100vw', (960, 1440, 1920), cls='px')}</div>
  <div class="wrap dupla">
    <div class="texto" data-rv>
      <p class="selo">Upgrade de Garmin</p>
      <h2 id="t-upg">Dê seu relógio. Suba de nível.</h2>
      <p class="lead">Seu Garmin atual entra como parte do pagamento. Você paga só a diferença pelo modelo novo.</p>
      <div class="botoes" style="justify-content:flex-start;margin-top:10px"><a class="btn btn-lima" href="upgrade.html{('?para=' + para) if para else ''}#simular">Simular meu upgrade</a><a class="btn btn-borda" href="upgrade.html#como-upgrade">Como funciona</a></div>
    </div>
    <div class="conta-troca" data-rv style="--i:1">
      <div class="l"><span>{m['nome']}</span><span>{brl(m['preco'])}</span></div>
      <div class="l"><span>Seu Garmin de hoje</span><span>avaliado no direct</span></div>
      <div class="l total"><strong>Você paga</strong><b>só a diferença</b></div>
    </div>
  </div>
</section>"""

FAQ = [
    ('Os relógios são originais?', 'Sim. Trabalhamos só com relógios originais Garmin e COROS. Conferimos o número de série de cada unidade e garantimos que ele foi desvinculado da conta do dono anterior.'),
    ('Como funciona a compra pelo Instagram?', 'Você monta a sacola aqui no site e toca em Finalizar pedido. O site copia a mensagem com os modelos e o total e abre o nosso direct. Lá a gente confirma a unidade com fotos e combina pagamento e entrega.'),
    ('Garmin seminovo vale a pena?', 'Vale. Os Forerunner recebem atualizações por anos e são feitos para aguentar suor e chuva. Um seminovo revisado tem as mesmas funções do novo (VO2 máx, carga de treino, VFC, Garmin Coach) por um preço bem menor.'),
    ('Qual Garmin escolher para começar a correr?', 'Para quem está começando, o Forerunner 55 cobre tudo: GPS, ritmo, frequência cardíaca e treinos sugeridos. Se quiser tela colorida e métricas de recuperação, o Forerunner 165 é o passo seguinte. Na dúvida, use o Escolha o Garmin por mim.'),
    ('Qual a diferença entre o Forerunner 255 e o 265?', 'Os dois têm GPS multibanda e modo triathlon. O 265 tem tela AMOLED, prontidão de treino e música em todas as versões. O 255 tem tela de baixo consumo e bateria maior com GPS ligado.'),
    ('Tem garantia?', 'Sim. Todos os relógios saem com 90 dias de garantia Trypace contra defeitos de funcionamento.'),
    ('Vocês aceitam meu relógio usado na troca?', 'Aceitamos. Simule na página de Upgrade ou mande no direct o modelo e fotos do seu relógio atual. A gente avalia e desconta do valor.'),
    ('Entregam fora de Joinville?', 'Em Joinville e região dá para retirar em mãos. Para outras cidades, combinamos o envio pelo direct.'),
]

# ---------- Peças da página ----------
logo = open(AQUI + 'trypace-logo-horizontal.svg').read()
logo = re.sub(r'<metadata>.*?</metadata>', '', logo, flags=re.S)
logo = re.sub(r'<title>.*?</title>', '', logo, flags=re.S)
VB = re.search(r'viewBox="([^"]+)"', logo).group(1)
LOGO_PATHS = re.search(r'<svg[^>]*>(.*)</svg>', logo, flags=re.S).group(1).strip().replace('fill="#F5F5F5"', 'fill="currentColor"')

def versao(nome):
    return hashlib.md5(open(AQUI + nome, 'rb').read()).hexdigest()[:8]

import subprocess, datetime
os.makedirs(OUT + 'assets/js', exist_ok=True)
if os.path.exists(OUT + 'assets/css/trypace.css'):
    os.remove(OUT + 'assets/css/trypace.css')
# Minifica com lightningcss e terser quando instalados (npx); senão usa os arquivos como estão.
def minificar(cmd, entrada):
    try:
        r = subprocess.run(cmd, input=entrada, capture_output=True, text=True, timeout=120)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
    except Exception:
        pass
    return entrada
NPM = os.environ.get('TRYPACE_NPM_BIN', '')
css_fonte = open(AQUI + 'trypace.css').read().replace('url(../fonts/', 'url(assets/fonts/')
def minificar_css(css):
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.css', delete=False) as t:
        t.write(css)
    try:
        return minificar([NPM + 'lightningcss', '--minify', '--targets', '>= 0.5%', t.name], css)
    finally:
        os.unlink(t.name)
CSS_MIN = minificar_css(css_fonte) if NPM else css_fonte
js_fonte = open(AQUI + 'trypace.js').read()
JS_MIN = minificar([NPM + 'terser', '--compress', '--mangle'], js_fonte) if NPM else js_fonte
open(OUT + 'assets/js/trypace.js', 'w').write(JS_MIN)
shutil.copyfile(AQUI + 'lenis.min.js', OUT + 'assets/js/lenis.min.js')
V_JS, V_LENIS = hashlib.md5(JS_MIN.encode()).hexdigest()[:8], versao('lenis.min.js')
HOJE = datetime.date.today()

CREDITOS = ', '.join(
    f'<a href="https://commons.wikimedia.org/wiki/File:{n}" target="_blank" rel="noopener">{n.rsplit(".", 1)[0].replace("_", " ").strip()}</a> ({a}, {l})'
    for n, a, l in FOTOS_PROD.values())

NAV_ITENS = [('loja.html', 'Loja'), ('loja.html#inicio', 'Para começar'), ('loja.html#performance', 'Performance'), ('loja.html#triathlon', 'Triathlon'),
             ('escolha.html', 'Escolha por mim'), ('comparar.html', 'Comparar'), ('upgrade.html', 'Upgrade')]

def produtos_js():
    out = []
    for m in MODELOS:
        f = FOTOS_PROD.get(m['foto']) if m['foto'] else None
        out.append(dict(id=m['id'], nome=m['nome'], marca=m['marca'], preco=m['preco'], url=m['url'],
                        foto=wiki(f[0], 330) if f else None, fotoG=wiki(f[0], 960) if f else None,
                        perfil=m['perfil'].split(), amoled=m['amoled'], musica=m['musica'], gpsH=m['gpsH'], nivel=m['nivel'],
                        porque=m['desc'], motivos=m['motivos'], tela=m['tela'], bat=m['bat'], batDias=m['batDias'], peso=m['peso'], pesoG=m['pesoG'],
                        multibanda=m['multibanda'], mapas=m['mapas'], pay=m['pay'], tri=m['tri'], rec=m['rec'][0], resumo=m['resumo']))
    return out

def pagina(arquivo, titulo, desc, corpo, atual='', jsonld=None, preload='', og_img=None, tipo='', indexar=True):
    canon = SITE + ('' if arquivo == 'index.html' else arquivo)
    nav = '\n'.join(f'      <li><a href="{h}"{" aria-current=" + chr(34) + "page" + chr(34) if h == atual else ""}>{t}</a></li>' for h, t in NAV_ITENS)
    tp = json.dumps({'p': produtos_js(), 'ig': IG_DM, 'troca': TROCA, 'desenho': DESENHO}, ensure_ascii=False).replace('</', '<\\/')
    ld = f'<script type="application/ld+json">\n{json.dumps(jsonld, ensure_ascii=False, indent=1).replace("</", "<\\/")}\n</script>' if jsonld else ''
    og = og_img or SITE + 'assets/img/og-trypace.jpg'
    og_dim = '' if og_img else '<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
    og_type = 'product' if tipo == 'produto' else 'website'
    t = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{titulo}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="{'index, follow, max-image-preview:large, max-snippet:-1' if indexar else 'noindex, follow'}">
<meta name="theme-color" content="#161617">
<meta name="geo.region" content="BR-SC">
<meta name="geo.placename" content="Joinville">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Trypace">
<meta property="og:title" content="{html.escape(titulo)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og}">
{og_dim}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(titulo)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{og}">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<link rel="preconnect" href="https://images.unsplash.com">
<link rel="preconnect" href="https://upload.wikimedia.org">
<link rel="preload" href="assets/fonts/montserrat-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/js/trypace.js?v={V_JS}" as="script">
<link rel="alternate" type="text/plain" href="llms.txt" title="Resumo da Trypace para agentes de IA">
<link rel="alternate" type="application/json" href="catalogo.json" title="Catálogo da Trypace em JSON">
{preload}<style>{CSS_MIN}</style>
<script>document.documentElement.classList.add('js')</script>
{ld}
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><symbol id="logo" viewBox="{VB}">{LOGO_PATHS}</symbol></defs></svg>
<a class="sr" href="#conteudo">Pular para o conteúdo</a>

<nav class="nav" aria-label="Principal">
  <div class="wrap">
    <a class="logo" href="index.html" aria-label="Trypace, página inicial"><svg role="img" aria-label="Trypace" width="125" height="20"><use href="#logo"/></svg></a>
    <ul id="menu">
{nav}
    </ul>
    <div class="acoes">
      <a class="icone" href="{IG_PROFILE}" target="_blank" rel="noopener" aria-label="Instagram da Trypace">{ICON_IG}</a>
      <button class="icone" type="button" id="abrir-sacola" aria-label="Abrir sacola">{ICON_SACOLA}<span class="contador" data-zero>0</span></button>
      <button class="icone menu-btn" type="button" aria-label="Menu" aria-controls="menu" aria-expanded="false">{ICON_MENU}</button>
    </div>
  </div>
</nav>

<main id="conteudo">
{corpo}
</main>

<footer>
  <div class="wrap">
    <div class="notas">
      <p>Preços de seminovo, conferidos em {DATA_PRECOS}. A disponibilidade e a cor de cada unidade são confirmadas no direct. Fotos de produto ilustrativas.</p>
      <p>Garmin e Forerunner são marcas registradas da Garmin Ltd. ou de suas subsidiárias. COROS é marca da COROS Wearables Inc. A Trypace é uma loja independente e não é representante oficial dessas marcas.</p>
      <p>Fotos de produto do Wikimedia Commons: {CREDITOS}. Fotos de corrida: Unsplash.</p>
    </div>
    <div class="colunas">
      <div><h3>Loja</h3><ul><li><a href="loja.html#mais">Mais procurados</a></li><li><a href="loja.html#inicio">Para começar</a></li><li><a href="loja.html#evolucao">Para evoluir</a></li><li><a href="loja.html#performance">Performance</a></li><li><a href="loja.html#triathlon">Triathlon e ultra</a></li></ul></div>
      <div><h3>Ajuda pra escolher</h3><ul><li><a href="escolha.html">Escolha o Garmin por mim</a></li><li><a href="comparar.html">Comparar relógios</a></li><li><a href="index.html#duvidas">Dúvidas</a></li></ul></div>
      <div><h3>Upgrade</h3><ul><li><a href="upgrade.html#simular">Simular meu upgrade</a></li><li><a href="upgrade.html#como-upgrade">Como funciona</a></li></ul></div>
      <div><h3>Atendimento</h3><ul><li><a href="{IG_PROFILE}" target="_blank" rel="noopener">Instagram @{HANDLE}</a></li><li>Joinville, SC</li><!-- CONFIRMAR: CNPJ ou nome do responsável --></ul></div>
    </div>
    <div class="final"><p>© <span id="ano">2026</span> Trypace. Mais performance em cada passo.</p><svg role="img" aria-label="Trypace" width="100" height="16"><use href="#logo"/></svg></div>
  </div>
</footer>

<dialog class="sacola" id="sacola" aria-labelledby="s-tit" data-lenis-prevent>
  <header><h2 id="s-tit">Sacola</h2><button class="fechar" type="button" data-fechar aria-label="Fechar sacola">{ICON_X}</button></header>
  <ul class="itens" id="itens"></ul>
  <div class="vazio" id="vazio"><p>Sua sacola está vazia.</p><a class="btn btn-escuro" href="loja.html">Ver relógios</a></div>
  <form class="fechamento" id="fechamento">
    <div class="total"><span>Total</span><span id="total">R$ 0</span></div>
    <div class="campos">
      <label for="f-nome">Seu nome<input id="f-nome" name="nome" autocomplete="given-name"></label>
      <label for="f-cidade">Cidade<input id="f-cidade" name="cidade" autocomplete="address-level2"></label>
    </div>
    <button class="btn btn-lima btn-g" type="submit">{ICON_IG} Finalizar pedido no Instagram</button>
    <small>Ao finalizar, copiamos a mensagem do pedido e abrimos o direct da Trypace. Lá é só colar e enviar.</small>
  </form>
</dialog>

<div class="toast" id="toast" role="status" aria-live="polite"></div>

<script>window.TP={tp};</script>
<script src="assets/js/lenis.min.js?v={V_LENIS}" defer></script>
<script src="assets/js/trypace.js?v={V_JS}" defer></script>
</body>
</html>
"""
    open(OUT + arquivo, 'w').write(t)
    return arquivo

def migalhas_ld(itens):
    lista = [('Início', '')] + itens
    return {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u_} for i, (n, u_) in enumerate(lista)]}

LOJA_LD = {'@type': 'Store', '@id': SITE + '#loja', 'name': 'Trypace', 'url': SITE,
           'description': 'Loja de relógios esportivos Garmin seminovos e revisados em Joinville, SC.',
           'slogan': 'Mais performance em cada passo', 'logo': SITE + 'assets/img/icon-512.png', 'image': SITE + 'assets/img/og-trypace.jpg',
           'address': {'@type': 'PostalAddress', 'addressLocality': 'Joinville', 'addressRegion': 'SC', 'addressCountry': 'BR'},
           'areaServed': ['Joinville', 'Santa Catarina', 'Brasil'], 'currenciesAccepted': 'BRL', 'sameAs': [IG_PROFILE],
           'priceRange': f"{brl(min(m['preco'] for m in MODELOS))} a {brl(max(m['preco'] for m in MODELOS))}",
           'contactPoint': {'@type': 'ContactPoint', 'contactType': 'sales', 'url': IG_DM, 'availableLanguage': 'pt-BR'},
           'knowsAbout': ['Garmin Forerunner', 'relógios de corrida', 'relógios esportivos seminovos']}

def oferta(m):
    return {'@type': 'Offer', 'price': m['preco'], 'priceCurrency': 'BRL', 'itemCondition': 'https://schema.org/UsedCondition',
            'availability': 'https://schema.org/InStock', 'url': SITE + m['url'], 'seller': {'@id': SITE + '#loja'},
            'priceValidUntil': (HOJE + datetime.timedelta(days=60)).isoformat(),
            'areaServed': {'@type': 'Country', 'name': 'BR'}}

def specs(m):
    return [('Condição', 'Seminovo revisado'), ('Tela', m['tela']), ('Bateria no modo relógio', m['bat']), ('Bateria com GPS', f"{m['gpsH']} h"), ('GPS', 'Multibanda' if m['multibanda'] else 'Simples'),
            ('Métrica de recuperação', m['rec'][0]), ('Música offline', sim(m['musica'])), ('Mapas', sim(m['mapas'])), ('Multiesporte', sim(m['tri'])),
            ('Pagamento por aproximação', sim(m['pay'])), ('Resistência à água', '5 ATM'), ('Peso', m['peso'])]

def sim(v): return 'Sim' if v else 'Não'

def produto_ld(m):
    d = {'@type': 'Product', '@id': SITE + m['url'] + '#produto', 'name': m['nome_completo'], 'brand': {'@type': 'Brand', 'name': m['marca']}, 'sku': m['id'],
         'mpn': m['nome'], 'model': m['nome'], 'category': 'Relógios esportivos > Relógios de corrida com GPS', 'itemCondition': 'https://schema.org/UsedCondition',
         'description': m['desc'], 'url': SITE + m['url'], 'offers': oferta(m),
         'weight': {'@type': 'QuantitativeValue', 'value': m['pesoG'], 'unitCode': 'GRM'},
         'additionalProperty': [{'@type': 'PropertyValue', 'name': a, 'value': b} for a, b in specs(m)]}
    if m['foto']:
        d['image'] = wiki(FOTOS_PROD[m['foto']][0], 960)
    return d

PAGINAS = []

# ---------- Início ----------
SLIDES = [('pista', 'fr265', 'Mais procurado'), ('trilha', 'fr955', 'Trilha e ultra'), ('prova', 'fr255', 'Dia de prova')]
slides = []
for k, (foto, pid, selo) in enumerate(SLIDES):
    m = por_id[pid]
    tag = 'h2'
    slides.append(f"""  <article class="slide{' ativo' if k == 0 else ''}" aria-roledescription="slide" aria-label="{k+1} de {len(SLIDES)}">
    {picture_hero(foto, primeiro=k == 0)}
    <div class="texto"><p class="selo">{selo}</p><{tag}>{m['nome']}</{tag}><p class="sub">{m['frase']}</p><p class="preco-bloco">Seminovo a partir de {brl(m['preco'])}</p>
      <div class="botoes"><a class="btn btn-lima" href="{m['url']}">Saiba mais</a><button class="btn btn-borda" type="button" data-add="{m['id']}">Comprar</button></div></div>
  </article>""")
segs = ''.join(f'<button type="button" aria-label="Destaque {k+1}"><span></span></button>' for k in range(len(SLIDES)))
preload_hero = (f'<link rel="preload" as="image" media="(max-width: 640px)" imagesrcset="{", ".join(f"{u(SLIDES[0][0], w, round(w*1.6))} {w}w" for w in (480, 720, 960))}" imagesizes="100vw" fetchpriority="high">\n'
                f'<link rel="preload" as="image" media="(min-width: 641px)" imagesrcset="{", ".join(f"{u(SLIDES[0][0], w, round(w*.56))} {w}w" for w in (960, 1440, 1920, 2560))}" imagesizes="100vw" fetchpriority="high">\n')

def bloco_foto(foto, pid, selo=None):
    m = por_id[pid]
    return f"""  <article class="bloco" data-rv="cheio">
    <div class="fundo">{img(foto, 1.1, '(max-width: 833px) 100vw, 50vw', (480, 800, 1100))}</div>
    <div class="texto">{f'<p class="selo">{selo}</p>' if selo else ''}<h2>{m['nome']}</h2><p class="sub">{m['frase']}</p><p class="preco-bloco">Seminovo a partir de {brl(m['preco'])}</p>
      <div class="botoes"><a class="btn btn-lima" href="{m['url']}">Saiba mais</a><button class="btn btn-borda" type="button" data-add="{m['id']}">Comprar</button></div></div>
  </article>"""

def bloco_claro(pid):
    m = por_id[pid]
    return f"""  <article class="bloco claro" data-rv="cheio">
    <div class="texto"><p class="selo" style="color:var(--lima-texto)">{m.get('etiqueta') or 'Seminovo'}</p><h2>{m['nome']}</h2><p class="sub">{m['frase']}</p><p class="preco-bloco">Seminovo a partir de {brl(m['preco'])}</p>
      <div class="botoes"><a class="btn btn-escuro" href="{m['url']}">Saiba mais</a><button class="btn btn-claro" type="button" data-add="{m['id']}">Comprar</button></div></div>
    <div class="produto">{foto_prod(m, 500, '(max-width: 833px) 80vw, 380px')}</div>
  </article>"""

FOTOS_FILEIRA = [('confere', 'Longão', 'Conferindo o pace'), ('trio', 'Treino em grupo', 'Antes do sol nascer'), ('cidade', 'Rua', 'Tiro na avenida'),
                 ('pulso', 'Academia', 'Zona 2 no pulso'), ('asfalto', 'Prova', 'Largada'), ('tatuagem', 'Recuperação', 'Body Battery em dia'), ('fonte', 'Cidade', 'Rodagem leve')]
fotos_fileira = '\n'.join(f'      <figure class="foto-card" data-rv style="--i:{min(k,4)}">{img(f, 1.25, "(max-width: 640px) 82vw, 400px", (400, 800))}<figcaption>{cat}<b>{leg}</b></figcaption></figure>'
                          for k, (f, cat, leg) in enumerate(FOTOS_FILEIRA))
faq_html = '\n'.join(f'      <details><summary>{q}</summary><div class="resp"><p>{a}</p></div></details>' for q, a in FAQ)

inicio = f"""<h1 class="sr">Trypace: Garmin Forerunner seminovo e revisado em Joinville, SC</h1>
<p class="faixa">Escolha aqui e finalize pelo direct do Instagram. <a href="#como">Veja como funciona</a></p>

<section class="vitrine" aria-roledescription="carrossel" aria-label="Destaques">
{chr(10).join(slides)}
  <div class="controles">
    <div class="segmentos">{segs}</div>
    <button class="pausa" type="button" aria-label="Pausar destaques" data-play='{ICON_PLAY}'>{ICON_PAUSA}</button>
  </div>
</section>

<div class="grade">
{bloco_foto('rua', 'fr165')}
{bloco_foto('corredora', 'fr55', 'Menor preço')}
{bloco_claro('fr965')}
{bloco_foto('mata', 'fr945')}
</div>

<section class="secao gelo" id="loja" aria-labelledby="t-loja">
  <div class="wrap cab-secao" data-rv>
    <h2 id="t-loja">Loja. <span>O jeito mais fácil de escolher seu próximo Garmin.</span></h2>
    <div class="ajuda"><p>Em dúvida entre dois modelos?<br><a class="link" href="escolha.html">Escolha o Garmin por mim</a></p><p>Já tem um Garmin?<br><a class="link" href="upgrade.html">Use como parte do pagamento</a></p></div>
  </div>
  <div style="margin-top:44px">
{fileira('mais', 'Mais procurados.', 'Os favoritos de quem corre.', itens_cat('mais', CATEGORIAS[0][3]))}
  </div>
  <div class="wrap" style="margin-top:18px"><a class="btn btn-claro" href="loja.html">Ver a loja completa</a></div>
</section>

{linha_escolha()}

{linha_upgrade()}

<section class="secao escuro" aria-labelledby="t-fotos">
  <div class="fileira">
    <div class="wrap"><h2 class="titulo-fileira" id="t-fotos" data-rv style="font-size:clamp(32px,4vw,48px)">Na rua, na trilha, na prova. <span>Quem corre com Garmin.</span></h2></div>
    <div class="rolagem" data-rolagem>
{fotos_fileira}
    </div>
    {SETAS}
  </div>
</section>

{vantagens()}

{como_funciona()}

<section class="secao" id="duvidas" aria-labelledby="t-faq">
  <div class="wrap centro">
    <h2 id="t-faq" class="titulo-fileira" data-rv style="font-size:clamp(32px,4vw,48px)">Perguntas frequentes.</h2>
    <div class="faq" style="text-align:left" data-rv>
{faq_html}
    </div>
  </div>
</section>"""

PAGINAS.append(pagina('index.html', 'Trypace | Garmin Forerunner seminovo em Joinville',
    'Loja de Garmin Forerunner seminovo em Joinville/SC. Do FR 55 ao FR 965, revisados e com garantia. Monte sua sacola e finalize pelo direct do Instagram.',
    inicio, jsonld={'@context': 'https://schema.org', '@graph': [
        LOJA_LD,
        {'@type': 'WebSite', '@id': SITE + '#site', 'url': SITE, 'name': 'Trypace', 'inLanguage': 'pt-BR', 'publisher': {'@id': SITE + '#loja'}},
        {'@type': 'ItemList', 'name': 'Relógios esportivos seminovos em estoque', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'url': SITE + m['url'], 'name': m['nome_completo']} for i, m in enumerate(MODELOS)]},
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]},
    ]}, preload=preload_hero))

# ---------- Loja ----------
ATALHOS = [('mais', 'Mais procurados', 'fr265'), ('inicio', 'Para começar', 'fr55'), ('evolucao', 'Para evoluir', 'fr165'),
           ('performance', 'Performance', 'fr255'), ('triathlon', 'Triathlon e ultra', 'fr955')]
atalhos = '\n'.join(f'  <a href="#{k}"><span class="q"><img src="{wiki(FOTOS_PROD[f][0], 250)}" alt="" width="104" height="104" loading="lazy"></span><span>{n}</span></a>' for k, n, f in ATALHOS)
atalhos += f'\n  <a href="escolha.html"><span class="q">{DESENHO}</span><span>Escolha por mim</span></a>'
atalhos += f'\n  <a href="upgrade.html"><span class="q"><img src="{u("punho", 208, 208)}" alt="" width="104" height="104" loading="lazy"></span><span>Upgrade</span></a>'

loja = f"""<section class="secao gelo" style="padding-top:0" aria-labelledby="t-loja">
  <header class="wrap loja-cab cab-secao" data-rv>
    <h1 id="t-loja">Loja. <span>O jeito mais fácil de escolher seu próximo Garmin.</span></h1>
    <div class="ajuda"><p>Não sabe qual escolher?<br><a class="link" href="escolha.html">Escolha o Garmin por mim</a></p><p>Em dúvida entre modelos?<br><a class="link" href="comparar.html">Compare lado a lado</a></p><p>Já tem um Garmin?<br><a class="link" href="upgrade.html">Use como parte do pagamento</a></p></div>
  </header>
  <nav class="atalhos" aria-label="Categorias" data-rv style="--i:1">
{atalhos}
  </nav>
{chr(10).join(fileira(k, t, s, itens_cat(k, ids)) for k, t, s, ids in CATEGORIAS)}
</section>

{linha_escolha()}

{vantagens()}

{como_funciona()}"""

PAGINAS.append(pagina('loja.html', 'Loja Trypace | Garmin Forerunner seminovo por categoria',
    'Todos os Garmin Forerunner seminovos da Trypace por categoria: para começar, para evoluir, performance e triathlon. Preços de R$ 850 a R$ 3.000.',
    loja, atual='loja.html', jsonld={'@context': 'https://schema.org', '@graph': [LOJA_LD, migalhas_ld([('Loja', 'loja.html')]), {
        '@type': 'ItemList', 'name': 'Loja Trypace', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'item': produto_ld(m)} for i, m in enumerate(MODELOS)]}]}))

# ---------- Página de cada relógio ----------
def destaques(m):
    marca_app = 'Garmin Connect' if m['marca'] == 'Garmin' else 'COROS'
    d = []
    if m['amoled']:
        d.append(('Tela', 'AMOLED que dá pra ler no sol.', 'Cores vivas e brilho forte. Você confere pace e frequência sem quebrar o ritmo.', [(m['tela'].split(' ')[1], 'tela'), ('AMOLED', 'sempre visível')]))
    else:
        d.append(('Tela', 'Sempre ligada, mesmo no sol do meio-dia.', 'Tela de baixo consumo, feita pra leitura em plena luz. É ela que segura a bateria por tanto tempo.', [(m['tela'].split(' ')[1], 'tela'), (m['bat'], 'de bateria')]))
    d.append(('Recuperação', m['rec'][0] + '.', m['rec'][1], []))
    if m['multibanda']:
        d.append(('Precisão', 'GPS multibanda entre prédios e árvores.', 'Distância e pace certos no centro da cidade, na beira-mar ou na trilha fechada.', [('Multibanda', 'GPS'), (f"{m['gpsH']} h", 'com GPS ligado')]))
    else:
        d.append(('GPS', 'Pace e distância sem levar o celular.', f'GPS no pulso, ritmo em tempo real e o mapa de cada treino no app {marca_app}.', [('GPS', 'integrado'), (f"{m['gpsH']} h", 'com GPS ligado')]))
    extras = []
    if m['mapas']: extras.append('mapas')
    if m['musica']: extras.append('música offline')
    if m['pay']: extras.append('pagamento por aproximação')
    if m['tri']: extras.append('modo triathlon')
    texto_b = f"No dia a dia, até {m['bat']} longe da tomada. Com GPS ligado, até {m['gpsH']} h de treino." + (f" E ainda tem {', '.join(extras[:-1]) + ' e ' + extras[-1] if len(extras) > 1 else extras[0]}." if extras else '')
    d.append(('Bateria', f"Até {m['bat']} com uma carga.", texto_b, [(m['bat'], 'modo relógio'), (f"{m['gpsH']} h", 'com GPS')]))
    return d

CAT_NOME = {'inicio': 'Para começar', 'evolucao': 'Para evoluir', 'performance': 'Performance', 'triathlon': 'Triathlon e ultra'}
PARA_QUEM = {'inicio': 'quem está começando a correr', 'evolucao': 'quem já corre com frequência e quer evoluir', 'performance': 'quem treina com planilha para provas', 'triathlon': 'triatletas e quem faz provas longas'}

def faq_modelo(m):
    pq = m['perfil'].split()
    quem = PARA_QUEM[pq[0]] + (f" e {PARA_QUEM[pq[1]]}" if len(pq) > 1 else '')
    viz = [v for v in vizinhos(m) if v is not m][0]
    def resumo_tec(x):
        return f"tela {x['tela']}, GPS {'multibanda' if x['multibanda'] else 'simples'} e até {x['gpsH']} h de bateria com GPS"
    extras = [t for t, ok in (('música offline', m['musica']), ('mapas', m['mapas']), ('pagamento por aproximação', m['pay']), ('modo triathlon', m['tri'])) if ok]
    tem = ('Tem ' + (', '.join(extras[:-1]) + ' e ' + extras[-1] if len(extras) > 1 else extras[0]) + '.') if extras else 'É um relógio focado em corrida, sem música, mapas ou pagamento por aproximação.'
    return [
        (f"Para quem o {m['nome']} é indicado?", f"Para {quem}. {m['desc']}"),
        (f"Quanto dura a bateria do {m['nome']}?", f"Até {m['bat']} no modo relógio e até {m['gpsH']} h com GPS ligado, segundo a fabricante. Em cada seminovo, a saúde da bateria da unidade é informada no direct antes da compra."),
        (f"O {m['nome']} tem música, mapas ou pagamento por aproximação?", tem),
        (f"Qual a diferença entre o {m['nome']} e o {viz['nome']}?", f"O {m['nome']} custa {brl(m['preco'])} seminovo e tem {resumo_tec(m)}. O {viz['nome']} custa {brl(viz['preco'])} e tem {resumo_tec(viz)}. Para ver lado a lado, use a página Comparar."),
        (f"O {m['nome']} seminovo tem garantia?", 'Sim. Todos os relógios da Trypace saem revisados e com 90 dias de garantia contra defeitos de funcionamento.'),
        (f"Como comprar o {m['nome']} na Trypace?", f"Toque em Adicionar à sacola e depois em Finalizar no Instagram, ou em Comprar agora pelo direct. A mensagem vai pronta para o direct da Trypace, onde a gente confirma a unidade com fotos e combina pagamento e entrega."),
    ]

def vizinhos(m):
    lista = sorted(MODELOS, key=lambda x: (x['preco'], x['ordem']))
    i = lista.index(m)
    if i == 0: return lista[0:3]
    if i == len(lista) - 1: return lista[-3:]
    return lista[i-1:i+2]

for n, m in enumerate(MODELOS):
    rot = ORDEM_FOTOS[(n * 5) % len(ORDEM_FOTOS):] + ORDEM_FOTOS[:(n * 5) % len(ORDEM_FOTOS)]
    f_gal, f_faixa, f_mos, f_dest, f_row, f_caixa = rot[0:3], rot[3], rot[4:7], rot[7:11], rot[11:14] + rot[0:3], rot[1]
    f = FOTOS_PROD.get(m['foto']) if m['foto'] else None
    if f:
        principal = f'<img class="on" src="{wiki(f[0], 960)}" srcset="{wiki(f[0], 500)} 500w, {wiki(f[0], 960)} 960w" sizes="(max-width: 900px) 100vw, 680px" width="960" height="960" alt="{m["marca"]} {m["nome"]}" fetchpriority="high">'
        mini0 = f'<img src="{wiki(f[0], 250)}" alt="" width="125" height="125">'
    else:
        principal = f'<span class="desenho">{DESENHO}</span><img class="on" src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" alt="">'
        mini0 = f'<span style="display:grid;place-items:center;height:100%">{DESENHO.replace("<svg ", "<svg width=" + chr(34) + "44%" + chr(34) + " ")}</span>'
    principal += ''.join(f'<img src="{u(k, 960, 960)}" alt="{html.escape(F[k][1])}" width="960" height="960" loading="lazy">' for k in f_gal)
    minis = f'<button type="button" aria-current="true" aria-label="Foto 1">{mini0}</button>' + ''.join(
        f'<button type="button" aria-current="false" aria-label="Foto {j+2}"><img src="{u(k, 250, 250)}" alt="" width="125" height="125" loading="lazy"></button>' for j, k in enumerate(f_gal))
    dests = '\n'.join(f"""      <div class="destaque">
        <div class="d-foto" data-rv="foto">{img(k, .8, '(max-width: 833px) 100vw, 570px', (480, 800, 1200))}</div>
        <div class="d-texto" data-rv style="--i:1"><span class="etq-d">{e}</span><h3>{t}</h3><p>{tx}</p>{('<div class="numeros">' + ''.join(f'<div><b>{a}</b><span>{b}</span></div>' for a, b in nums) + '</div>') if nums else ''}</div>
      </div>""" for k, (e, t, tx, nums) in zip(f_dest, destaques(m)))
    galeria_row = '\n'.join(f'      <figure class="foto-card" data-rv style="--i:{min(j,4)}">{img(k, 1.25, "(max-width: 640px) 82vw, 400px", (400, 800))}<figcaption>{m["nome"]}<b>{LEGENDA[k]}</b></figcaption></figure>' for j, k in enumerate(f_row))
    comp = ''
    for v in vizinhos(m):
        fv = FOTOS_PROD.get(v['foto']) if v['foto'] else None
        mini = f'<img src="{wiki(fv[0], 500)}" alt="{v["marca"]} {v["nome"]}" width="500" height="375" loading="lazy">' if fv else DESENHO
        tagc = 'div' if v is m else 'a'
        href = '' if v is m else f' href="{v["url"]}"'
        comp += f"""      <{tagc} class="col{' atual' if v is m else ''}"{href} data-rv>
        <div class="mini">{mini}</div>
        <h3>{v['nome']}</h3><span class="p">{brl(v['preco'])}</span>
        <dl><dt>Tela</dt><dd>{v['tela']}</dd><dt>GPS</dt><dd>{'Multibanda' if v['multibanda'] else 'Simples'}</dd><dt>Bateria com GPS</dt><dd>{v['gpsH']} h</dd><dt>Recuperação</dt><dd>{v['rec'][0]}</dd><dt>Música</dt><dd>{sim(v['musica'])}</dd><dt>Mapas</dt><dd>{sim(v['mapas'])}</dd></dl>
        {'<span class="link" style="margin-top:6px">Ver este</span>' if v is not m else '<span class="cinza" style="font-size:14px;margin-top:6px">Você está aqui</span>'}
      </{tagc}>
"""
    specs_html = ''.join(f'<div data-rv style="--i:{k % 4}"><dt>{a}</dt><dd>{b}</dd></div>' for k, (a, b) in enumerate(specs(m)))
    msg = html.escape(f'Faala, Trypace! Vi o {m["nome"]} ({brl(m["preco"])}) no site. Ainda tem disponível? Pode me mandar fotos da unidade?', quote=True)
    corpo = f"""<div class="barra-prod">
  <div class="wrap"><strong>{m['nome']}</strong><nav aria-label="Seções do produto"><a href="#visao">Visão geral</a><a href="#specs">Especificações</a><a href="comparar.html?a={m['id']}">Comparar</a><button class="btn btn-lima btn-p" type="button" data-add="{m['id']}">Comprar</button></nav></div>
</div>

<section class="wrap compra" aria-labelledby="t-prod">
  <nav class="migalhas" aria-label="Você está em" data-rv><ol><li><a href="index.html">Início</a></li><li><a href="loja.html">Loja</a></li><li><a href="loja.html#{m['perfil'].split()[0]}">{CAT_NOME[m['perfil'].split()[0]]}</a></li><li aria-current="page">{m['nome']}</li></ol></nav>
  <p class="marca" data-rv>{m['marca']} · Seminovo revisado</p>
  <h1 id="t-prod" data-rv style="--i:1">{m['nome']} <span class="cinza">seminovo</span></h1>
  <p class="apartir" data-rv style="--i:2">{brl(m['preco'])} · <a class="link" href="upgrade.html?para={m['id']}#simular">ou dê seu Garmin na troca</a></p>
  <div class="compra-grid">
    <div class="galeria" data-rv="foto">
      <div class="principal">{principal}</div>
      <div class="miniaturas">{minis}</div>
    </div>
    <div class="lado">
      <div data-rv><h2>{m['frase']}</h2><p class="cinza" style="margin-top:8px">{m['desc']}</p></div>
      <div data-rv style="--i:1"><h2>Destaques. <span>O que vem no pulso.</span></h2>
        <ul class="lista-check">{''.join(f'<li>{x}</li>' for x in m['motivos'])}</ul></div>
      <div class="caixa-compra" data-rv style="--i:2">
        <div class="linha-total"><span>Seminovo revisado</span><b>{brl(m['preco'])}</b></div>
        <button class="btn btn-lima btn-g" type="button" data-add="{m['id']}">Adicionar à sacola</button>
        <button class="btn btn-escuro btn-g" type="button" data-msg="{msg}">{ICON_IG} Comprar agora pelo direct</button>
        <a class="btn btn-claro btn-g" href="upgrade.html?para={m['id']}#simular">Tenho um Garmin para dar na troca</a>
        <small>Você finaliza pelo direct do Instagram, sem cadastro e sem pagar no site. A gente manda fotos reais da unidade antes.</small>
      </div>
      <!-- CONFIRMAR: garantia e nota -->
      <div class="selos" data-rv style="--i:3"><span>Revisado</span><span>Garantia 90 dias</span><span>Série conferida</span></div>
    </div>
  </div>
</section>

<section class="faixa-foto baixo" id="visao" aria-labelledby="t-visao">
  <div class="fundo" data-px>{img(f_faixa, .56, '100vw', (960, 1440, 1920), cls='px')}</div>
  <div class="wrap"><h2 id="t-visao" data-rv>{m['frase']}</h2><p class="lead" data-rv style="--i:1">{m['rec'][1]}</p></div>
</section>

<div class="mosaico">
  <figure data-rv="foto">{img(f_mos[0], .9, '(max-width: 700px) 100vw, 66vw', (640, 1000, 1400))}</figure>
  <figure data-rv="foto" style="--i:1">{img(f_mos[1], .8, '(max-width: 700px) 100vw, 33vw', (480, 800))}</figure>
  <figure data-rv="foto" style="--i:2">{img(f_mos[2], .8, '(max-width: 700px) 100vw, 33vw', (480, 800))}</figure>
</div>

<section class="secao" aria-labelledby="t-por-que">
  <div class="wrap">
    <h2 id="t-por-que" class="titulo-fileira centro" data-rv style="font-size:clamp(36px,4.6vw,56px)">Por que o {m['nome'].replace('Forerunner ', '')}.</h2>
    <div class="destaques">
{dests}
    </div>
  </div>
</section>

<section class="secao escuro" aria-labelledby="t-gal">
  <div class="fileira">
    <div class="wrap"><h2 class="titulo-fileira" id="t-gal" data-rv style="font-size:clamp(32px,4vw,48px)">Galeria. <span>Feito pra rua, trilha e prova.</span></h2></div>
    <div class="rolagem" data-rolagem>
{galeria_row}
    </div>
    {SETAS}
  </div>
</section>

<section class="secao" aria-labelledby="t-unidade">
  <div class="wrap">
    <h2 id="t-unidade" class="titulo-fileira" data-rv style="font-size:clamp(32px,4vw,48px)">Esta unidade. <span>Conferida antes de sair.</span></h2>
    <div class="duas-col" style="margin-top:36px">
      <!-- CONFIRMAR: itens da revisão -->
      <div class="cartao" data-rv>
        <h2>Revisão Trypace.</h2>
        <p class="cinza">Tudo o que a gente testa antes de anunciar. O laudo da sua unidade vai junto no direct.</p>
        <div class="linhas"><div><span>GPS testado na rua</span><b>Ok</b></div><div><span>Sensor óptico de frequência</span><b>Ok</b></div><div><span>Saúde da bateria</span><b>Informada no direct</b></div><div><span>Tela, vidro e botões</span><b>Ok</b></div><div><span>Número de série</span><b>Conferido</b></div><div><span>Conta do dono anterior</span><b>Desvinculada</b></div></div>
      </div>
      <div style="display:grid;gap:12px">
        <!-- CONFIRMAR: o que vai na caixa -->
        <div class="cartao" data-rv style="--i:1"><h2>Na caixa.</h2><ul class="lista-check" style="margin:0"><li>{m['nome_completo']}</li><li>Cabo de carga</li><li>Pulseira</li><li>Garantia Trypace de 90 dias</li></ul></div>
        <div class="cartao-foto" data-rv="foto" style="--i:2">{img(f_caixa, .6, '(max-width: 833px) 100vw, 590px', (480, 800, 1200))}</div>
      </div>
    </div>
  </div>
</section>

<section class="secao gelo" id="comparar" aria-labelledby="t-comp">
  <div class="wrap">
    <h2 id="t-comp" class="titulo-fileira centro" data-rv style="font-size:clamp(32px,4vw,48px)">Compare com os vizinhos.</h2>
    <div class="comparar">
{comp}    </div>
    <div class="centro" style="margin-top:32px" data-rv><a class="btn btn-escuro" href="comparar.html?a={m['id']}">Comparar com outro relógio</a></div>
  </div>
</section>

<section class="secao" id="specs" aria-labelledby="t-specs">
  <div class="wrap">
    <h2 id="t-specs" class="titulo-fileira" data-rv style="font-size:clamp(32px,4vw,48px)">Especificações.</h2>
    <dl class="specs">{specs_html}</dl>
  </div>
</section>

<section class="secao gelo" id="perguntas" aria-labelledby="t-perg">
  <div class="wrap">
    <h2 id="t-perg" class="titulo-fileira centro" data-rv style="font-size:clamp(32px,4vw,48px)">Perguntas sobre o {m['nome'].replace('Forerunner ', 'Forerunner ')}.</h2>
    <div class="faq" data-rv>
{chr(10).join(f'      <details><summary>{q}</summary><div class="resp"><p>{a}</p></div></details>' for q, a in faq_modelo(m))}
    </div>
  </div>
</section>

{linha_upgrade(m['id'])}

{linha_escolha()}"""
    titulo = f"{m['nome_completo']} seminovo | {brl(m['preco'])} | Trypace"
    desc = f"{m['nome_completo']} seminovo revisado por {brl(m['preco'])} em Joinville. {m['desc']} Finalize pelo direct do Instagram."
    og = wiki(f[0], 960) if f else None
    pre = f'<link rel="preload" as="image" imagesrcset="{wiki(f[0], 500)} 500w, {wiki(f[0], 960)} 960w" imagesizes="(max-width: 900px) 100vw, 680px" fetchpriority="high">\n' if f else ''
    PAGINAS.append(pagina(m['url'], titulo, desc, corpo, atual='', preload=pre, og_img=og, jsonld={'@context': 'https://schema.org', '@graph': [
        LOJA_LD, produto_ld(m),
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq_modelo(m)]},
        migalhas_ld([('Loja', 'loja.html'), (m['nome'], m['url'])])]}, tipo='produto'))

# ---------- Escolha o Garmin por mim ----------
escolha = f"""<div class="quiz" id="quiz">
  <div class="topo"><span data-num>Pergunta 1 de 4</span><button class="voltar" type="button" hidden>Voltar</button></div>
  <div class="barra" aria-hidden="true"><i></i></div>
  <div class="palco-q">
    <div class="perguntas">
      <h1 class="titulo-q">Escolha o Garmin por mim</h1>
      <h2 class="pergunta-q">Como está sua corrida hoje?</h2>
      <p class="ajuda-q">Sem resposta errada. É pra gente entender seu momento.</p>
      <div class="respostas">{''.join(f'<button class="resposta" type="button" data-v="{v}"><b>{t}</b><span>{d}</span></button>' for v, t, d in [('inicio', 'Começando agora', 'Corro pouco ou quero começar'), ('evolucao', 'Corro com frequência', '5 a 10 km algumas vezes por semana'), ('performance', 'Treino pra prova', 'Meia, maratona, planilha'), ('triathlon', 'Triathlon ou ultra', 'Nado, pedal ou provas longas')])}</div>
      <noscript><p style="margin-top:24px">Pra usar o Escolha por mim, ative o JavaScript. Ou <a href="{IG_DM}">fale com a gente no direct</a> e veja a <a href="loja.html">loja completa</a>.</p></noscript>
    </div>
    <div class="resultado" hidden>
      <p class="selo" style="color:var(--lima-texto)">Nossa escolha pra você</p>
      <h2 data-r-nome style="font-size:clamp(44px,6vw,64px);font-weight:700;margin-top:6px"></h2>
      <p data-r-porque style="font-size:21px;font-weight:500;margin-top:10px;max-width:46ch"></p>
      <div class="rec">
        <div class="r-foto" data-r-foto></div>
        <div class="r-info">
          <strong style="font-size:17px">Por que esse</strong>
          <ul class="lista-check" data-r-motivos style="margin:0"></ul>
          <div class="linha-total"><span>Seminovo revisado</span><b data-r-preco></b></div>
          <a class="btn btn-lima btn-g" data-r-ver href="loja.html">Ver o relógio</a>
          <button class="btn btn-escuro btn-g" type="button" data-r-add data-add="">Adicionar à sacola</button>
        </div>
      </div>
      <p style="margin-top:32px;font-weight:700">Também combinam com você</p>
      <div class="alternativas" data-r-alt></div>
      <div class="botoes" style="justify-content:flex-start;margin-top:28px"><button class="btn btn-claro" type="button" data-refazer>Refazer</button><button class="btn btn-escuro" type="button" data-r-direct data-msg="">{ICON_IG} Tirar dúvida no direct</button></div>
    </div>
  </div>
</div>

{linha_upgrade()}"""
PAGINAS.append(pagina('escolha.html', 'Escolha o Garmin por mim | Trypace',
    'Responda 4 perguntas sobre seu treino e descubra qual Garmin Forerunner seminovo combina com você. Do Forerunner 55 ao 965.', escolha, atual='escolha.html', jsonld={'@context': 'https://schema.org', '@graph': [LOJA_LD, migalhas_ld([('Escolha o Garmin por mim', 'escolha.html')])]}))

# ---------- Upgrade de Garmin ----------
ATUAIS = [('fr45', 'Forerunner 45'), ('fr55', 'Forerunner 55'), ('fr165', 'Forerunner 165'), ('fr235', 'Forerunner 235'), ('fr245', 'Forerunner 245'),
          ('fr255', 'Forerunner 255'), ('fr265', 'Forerunner 265'), ('fr735', 'Forerunner 735XT'), ('fr935', 'Forerunner 935'), ('fr945', 'Forerunner 945'),
          ('venu', 'Venu ou vívoactive'), ('fenix', 'Fenix ou Epix'), ('instinct', 'Instinct'), ('outro', 'Outro modelo')]
chips_atual = ''.join(f'<button class="chip" type="button" data-atual="{k}" aria-pressed="false">{n}</button>' for k, n in ATUAIS)
chips_estado = ''.join(f'<button class="chip" type="button" data-estado="{k}" aria-pressed="false">{n}</button>' for k, n in [('otimo', 'Ótimo'), ('bom', 'Bom'), ('marcas', 'Com marcas')])
destinos = ''.join(f'<button class="destino" type="button" data-destino="{m["id"]}" aria-pressed="false"><span>{m["nome"]}</span><span>{brl(m["preco"])}</span></button>'
                   for m in sorted(MODELOS, key=lambda x: x['preco']))
SALTOS = [('fr245', 'fr265', 'Tela AMOLED, GPS multibanda e prontidão de treino todo dia.'),
          ('fr55', 'fr165', 'Tela AMOLED, VFC noturna e Body Battery num relógio bem mais bonito.'),
          ('fr945', 'fr965', 'Tela AMOLED com mapas, multibanda e as métricas de treino mais novas.'),
          ('fr245', 'fr255', 'GPS multibanda, modo triathlon e o dobro de bateria com GPS.')]
saltos = '\n'.join(f'    <a class="salto" href="{por_id[b]["url"]}" data-rv style="--i:{k}"><span class="de">Do {por_id[a]["nome"]}</span><b>Para o {por_id[b]["nome"].replace("Forerunner ", "")}</b><p>{t}</p><span class="link">Ver o {por_id[b]["nome"].replace("Forerunner ", "")}</span></a>'
                   for k, (a, b, t) in enumerate(SALTOS))
upgrade = f"""<section class="faixa-foto" style="min-height:min(720px,88svh);align-items:flex-start;text-align:center" aria-labelledby="t-up">
  <div class="fundo" data-px>{img('punho', .56, '100vw', (960, 1440, 1920, 2560), lazy=False, cls='px')}</div>
  <div class="wrap" style="display:grid;justify-items:center;gap:8px;padding-top:80px">
    <p class="selo" data-rv>Upgrade de Garmin</p>
    <h1 id="t-up" data-rv style="--i:1;font-size:clamp(44px,6vw,64px);font-weight:700;max-width:18ch">Seu Garmin vale desconto no próximo.</h1>
    <p class="lead" data-rv style="--i:2;margin-inline:auto">Traga o relógio que você usa hoje. Ele entra como parte do pagamento de um modelo mais novo.</p>
    <div class="botoes" data-rv style="--i:3"><a class="btn btn-lima" href="#simular">Simular meu upgrade</a><a class="btn btn-borda" href="#como-upgrade">Como funciona</a></div>
  </div>
</section>

<section class="secao gelo" id="simular" aria-labelledby="t-sim">
  <div class="wrap">
    <h2 id="t-sim" class="titulo-fileira" data-rv style="font-size:clamp(32px,4vw,48px)">Simule seu upgrade. <span>Leva 20 segundos.</span></h2>
    <div class="simulador" id="simulador">
      <div class="sim-col" data-rv>
        <h3>1. Qual Garmin você tem hoje?</h3>
        <div class="chips">{chips_atual}</div>
        <h3>2. Como ele está?</h3>
        <div class="chips tres">{chips_estado}</div>
      </div>
      <div class="sim-res" data-rv style="--i:1">
        <h3 style="font-size:19px;font-weight:700">3. Para qual você quer ir?</h3>
        <div class="destinos" data-lenis-prevent>{destinos}</div>
        <div class="sim-conta">
          <div class="l"><span>Novo relógio</span><span data-novo>R$ 0</span></div>
          <div class="l"><span data-seu>Seu relógio</span><span data-cred>Avaliado no direct</span></div>
          <div class="l grande"><strong data-dif-rot>Você paga a diferença</strong><b data-dif>Sob consulta</b></div>
        </div>
        <button class="btn btn-lima btn-g" type="button" data-pedir data-msg="">{ICON_IG} Pedir avaliação no direct</button>
        <small>A mensagem vai pronta com o seu relógio e o que você quer. A gente responde com o valor do seu usado e quanto fica a diferença.</small>
      </div>
    </div>
  </div>
</section>

<section class="secao" aria-labelledby="t-saltos">
  <div class="wrap">
    <h2 id="t-saltos" class="titulo-fileira" data-rv style="font-size:clamp(32px,4vw,48px)">O que muda no seu pulso. <span>Os saltos mais comuns.</span></h2>
    <div class="saltos">
{saltos}
    </div>
  </div>
</section>

<section class="secao escuro" id="como-upgrade" aria-labelledby="t-como-up">
  <div class="wrap">
    <h2 class="titulo-fileira" id="t-como-up" data-rv style="font-size:clamp(32px,4vw,48px)">Como funciona.</h2>
    <div class="passos">
      <div class="passo-c" data-rv style="--i:0"><span class="n">1</span><h3>Simule aqui</h3><p>Escolha o relógio que você tem e o que você quer.</p></div>
      <div class="passo-c" data-rv style="--i:1"><span class="n">2</span><h3>Mande no direct</h3><p>A mensagem vai pronta. Junte fotos do relógio e da tela de bateria.</p></div>
      <div class="passo-c" data-rv style="--i:2"><span class="n">3</span><h3>A gente avalia</h3><p>Respondemos com o valor do seu usado e quanto fica a diferença.</p></div>
      <div class="passo-c" data-rv style="--i:3"><span class="n">4</span><h3>Troca feita</h3><p>Você entrega o antigo e sai com o novo, pagando só a diferença.</p></div>
    </div>
  </div>
</section>

<!-- CONFIRMAR: regras de aceite do usado -->
<section class="secao gelo" aria-labelledby="t-aceita">
  <div class="wrap dupla" style="align-items:start">
    <div class="texto" data-rv><h2 id="t-aceita">O que a gente aceita.</h2><p class="lead">Garmin funcionando, com carregador. Outras marcas a gente avalia caso a caso no direct.</p></div>
    <div class="aceita" data-rv style="--i:1"><div>Forerunner, todas as linhas</div><div>Venu e vívoactive</div><div>Fenix, Epix e Instinct</div><div>Outras marcas sob consulta</div></div>
  </div>
</section>

{linha_escolha()}"""
PAGINAS.append(pagina('upgrade.html', 'Upgrade de Garmin: seu usado vale desconto | Trypace',
    'Troque seu Garmin usado por um Forerunner mais novo e pague só a diferença. Simule o upgrade e receba a avaliação pelo direct da Trypace em Joinville.',
    upgrade, atual='upgrade.html', jsonld={'@context': 'https://schema.org', '@graph': [LOJA_LD, migalhas_ld([('Upgrade de Garmin', 'upgrade.html')]),
        {'@type': 'Service', 'name': 'Upgrade de Garmin (troca com usado na entrada)', 'provider': {'@id': SITE + '#loja'}, 'areaServed': 'BR',
         'description': 'Seu Garmin usado entra como parte do pagamento de um modelo mais novo. A avaliação é feita pelo direct do Instagram.'}]}))

# ---------- Comparar ----------
CMP_PADRAO = ['fr265', 'fr255', 'fr955']
COR_CMP = ['#B8FF00', '#FFFFFF', '#8E8E93']
NIVEL = ['Básico', 'Intermediário', 'Avançado', 'Completo']
def card_cmp(p):
    f = FOTOS_PROD.get(p['foto']) if p['foto'] else None
    foto = f'<img src="{wiki(f[0], 960)}" alt="{p["marca"]} {p["nome"]}" width="600" height="450" loading="lazy">' if f else DESENHO
    return (f'<div class="palco">{foto}</div><div class="corpo"><h2>{p["nome"]}</h2><p class="resumo">{p["resumo"]}</p><div class="pe"><b>{brl(p["preco"])}</b>'
            f'<span style="display:flex;gap:8px"><a class="btn btn-claro btn-p" href="{p["url"]}">Ver</a><button class="btn btn-lima btn-p" type="button" data-add="{p["id"]}">Comprar</button></span></div></div>')
ASP_NOMES = [('batDia', 'Bateria no dia a dia', lambda p: p['bat']), ('batGps', 'Bateria com GPS', lambda p: f"{p['gpsH']} h"),
             ('gps', 'Precisão do GPS', lambda p: 'Multibanda' if p['multibanda'] else 'Simples'), ('tela', 'Tela', lambda p: p['tela']),
             ('dados', 'Dados de treino', lambda p: NIVEL[p['nivel']]), ('extras', 'Recursos extras', lambda p: f"{sum([p['musica'], p['mapas'], p['pay'], p['tri']])} de 4"),
             ('leve', 'Leveza', lambda p: p['peso'])]
def barras_cmp():
    out = ''
    for k, t, val in ASP_NOMES:
        linhas = ''
        for j in range(3):
            fundo = COR_CMP[j] + (';background-image:repeating-linear-gradient(90deg,#8E8E93 0 10px,#6E6E73 10px 14px)' if j == 2 else '')
            linhas += f'<div class="barra-l" data-l="{j}"><div class="trilha-b"><i style="background:{fundo}"></i></div><span class="v">{val(por_id[CMP_PADRAO[j]])}</span></div>'
        out += f'<div class="aspecto" data-asp="{k}"><h3>{t}</h3><div class="linhas-b">{linhas}</div></div>'
    return out
def tabela_cmp():
    es = [por_id[i] for i in CMP_PADRAO]
    LIN = [('Preço', lambda p: brl(p['preco']), lambda p: -p['preco']), ('Tela', lambda p: p['tela'], lambda p: 1 if p['amoled'] else 0),
           ('Bateria no modo relógio', lambda p: p['bat'], lambda p: p['batDias']), ('Bateria com GPS', lambda p: f"{p['gpsH']} h", lambda p: p['gpsH']),
           ('GPS', lambda p: 'Multibanda' if p['multibanda'] else 'Simples', lambda p: 1 if p['multibanda'] else 0), ('Métrica de recuperação', lambda p: p['rec'][0], None),
           ('Dados de treino', lambda p: NIVEL[p['nivel']], lambda p: p['nivel']), ('Música offline', lambda p: sim(p['musica']), lambda p: 1 if p['musica'] else 0),
           ('Mapas', lambda p: sim(p['mapas']), lambda p: 1 if p['mapas'] else 0), ('Multiesporte', lambda p: sim(p['tri']), lambda p: 1 if p['tri'] else 0),
           ('Pagamento por aproximação', lambda p: sim(p['pay']), lambda p: 1 if p['pay'] else 0), ('Peso', lambda p: p['peso'], lambda p: -p['pesoG']),
           ('Resistência à água', lambda p: '5 ATM', None)]
    h = '<thead><tr><th scope="col"><span class="sr">Item</span></th>' + ''.join(f'<th scope="col"><span class="cab-cor"><span class="cor c{k}" style="width:12px;height:12px;border-radius:3px;display:inline-block"></span>{p["nome"]}</span></th>' for k, p in enumerate(es)) + '</tr></thead><tbody>'
    for nome, f, nota in LIN:
        vs = [nota(p) for p in es] if nota else []
        mx = max(vs) if vs else None
        unico = vs.count(mx) < len(es) if vs else False
        h += f'<tr><th scope="row">{nome}</th>' + ''.join(f'<td{" class=" + chr(34) + "best" + chr(34) if nota and unico and vs[j] == mx else ""}>{f(p)}</td>' for j, p in enumerate(es)) + '</tr>'
    return h + '</tbody>'

def opcoes_sel(sel, vazio=False):
    o = '<option value="">Nenhum</option>' if vazio else ''
    return o + ''.join(f'<option value="{m["id"]}"{" selected" if m["id"] == sel else ""}>{m["nome"]} · {brl(m["preco"])}</option>' for m in sorted(MODELOS, key=lambda x: x['preco']))
slots = ''
for k, (sel, vazio) in enumerate(zip(CMP_PADRAO, [False, False, True])):
    slots += f"""      <div class="slot" data-slot="{k}" data-rv style="--i:{k}">
        <div class="slot-sel"><span class="cor c{k}" aria-hidden="true"></span><label class="sr" for="s{k}">Relógio {k+1}</label><select id="s{k}" data-sel="{k}">{opcoes_sel(sel, vazio)}</select></div>
        <div class="slot-card" data-card="{k}" data-id="{sel}">{card_cmp(por_id[sel])}</div>
      </div>
"""
tabela_estatica = ''.join(f'<tr><th scope="row">{m["nome"]}</th><td>{brl(m["preco"])}</td><td>{m["tela"]}</td><td>{m["bat"]}</td><td>{m["gpsH"]} h</td><td>{"Multibanda" if m["multibanda"] else "Simples"}</td><td>{m["peso"]}</td></tr>' for m in sorted(MODELOS, key=lambda x: x['preco']))
comparar = f"""<section class="secao gelo" style="padding-top:64px" aria-labelledby="t-cmp">
  <div class="wrap">
    <div class="cab-secao" data-rv><h1 id="t-cmp" style="font-size:clamp(44px,6vw,64px);font-weight:700;max-width:16ch">Compare. <span class="cinza">Até 3 relógios lado a lado.</span></h1>
      <div class="ajuda"><p>Ainda sem ideia de qual?<br><a class="link" href="escolha.html">Escolha o Garmin por mim</a></p></div></div>
    <div class="slots" id="comparador">
{slots}    </div>
  </div>
</section>

<section class="secao escuro" id="graficos" aria-labelledby="t-graf">
  <div class="wrap">
    <h2 id="t-graf" class="titulo-fileira" data-rv style="font-size:clamp(32px,4vw,48px)">Desempenho em cada aspecto. <span>Quanto maior, melhor.</span></h2>
    <div class="legenda" data-legenda data-rv style="--i:1">{''.join(f'<span><i class="{"tracejado" if k == 2 else ""}" style="background:{COR_CMP[k]}"></i>{por_id[i]["nome"]}</span>' for k, i in enumerate(CMP_PADRAO))}</div>
    <div class="graf-grid">
      <figure class="radar" data-rv style="--i:1"><svg viewBox="0 0 460 440" role="img" aria-label="Gráfico de radar com a nota de cada relógio por aspecto" data-radar></svg><figcaption>Visão geral, nota de 0 a 10 em cada aspecto.</figcaption></figure>
      <div class="barras" data-barras data-rv style="--i:2">{barras_cmp()}</div>
    </div>
    <p class="nota-graf" data-rv>Notas calculadas pela Trypace a partir das especificações de fábrica de cada modelo: bateria em dias e em horas de GPS, tipo de GPS e de tela, profundidade das métricas de treino, recursos extras e peso.</p>
  </div>
</section>

<section class="secao" aria-labelledby="t-ficha">
  <div class="wrap">
    <h2 id="t-ficha" class="titulo-fileira" data-rv style="font-size:clamp(32px,4vw,48px)">Ficha lado a lado. <span>O melhor de cada linha em destaque.</span></h2>
    <div class="tabela-wrap" data-rv style="--i:1"><table class="cmp-tabela" data-tabela>{tabela_cmp()}</table></div>
    <noscript><table class="cmp-tabela"><thead><tr><th>Modelo</th><th>Preço</th><th>Tela</th><th>Bateria</th><th>GPS ligado</th><th>GPS</th><th>Peso</th></tr></thead><tbody>{tabela_estatica}</tbody></table></noscript>
  </div>
</section>

{linha_escolha('gelo')}"""
PAGINAS.append(pagina('comparar.html', 'Comparar Garmin Forerunner lado a lado | Trypace',
    'Compare até 3 Garmin Forerunner seminovos lado a lado: bateria, GPS, tela, métricas de treino, peso e preço, com tabela e gráficos.',
    comparar, atual='comparar.html', jsonld={'@context': 'https://schema.org', '@graph': [LOJA_LD, migalhas_ld([('Comparar relógios', 'comparar.html')])]}))

# ---------- 404 ----------
PAGINAS.append(pagina('404.html', 'Página não encontrada | Trypace', 'Essa página não existe. Veja os Garmin seminovos da Trypace.',
    f"""<section class="secao" style="padding-block:120px;text-align:center"><div class="wrap">
  <h1 style="font-size:clamp(44px,6vw,64px);font-weight:700">Essa página saiu pra correr.</h1>
  <p class="lead" style="margin:16px auto 32px;max-width:40ch">O endereço não existe ou mudou. O estoque continua aqui.</p>
  <p style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap"><a class="btn btn-lima" href="loja.html">Ver a loja</a><a class="btn btn-borda" href="index.html">Início</a></p>
</div></section>""", indexar=False))

# ---------- Para agentes de IA e buscadores ----------
catalogo = {'loja': 'Trypace', 'site': SITE, 'atualizado': HOJE.isoformat(), 'moeda': 'BRL', 'cidade': 'Joinville, SC, Brasil',
            'como_comprar': f'Monte a sacola no site e finalize pelo direct do Instagram ({IG_DM}). Pagamento e entrega são combinados na conversa.',
            'aviso': 'Loja independente de relógios seminovos. Não é loja oficial Garmin.',
            'produtos': [{'id': m['id'], 'nome': m['nome_completo'], 'marca': m['marca'], 'condicao': 'seminovo revisado', 'preco': m['preco'],
                          'url': SITE + m['url'], 'perfil': [PARA_QUEM[x] for x in m['perfil'].split() if x in PARA_QUEM], 'resumo': m['resumo'],
                          'especificacoes': dict(specs(m))} for m in sorted(MODELOS, key=lambda x: x['preco'])]}
open(OUT + 'catalogo.json', 'w').write(json.dumps(catalogo, ensure_ascii=False, indent=1))
llms = f"""# Trypace

> Loja independente de Garmin Forerunner seminovos e revisados em Joinville, SC. Vendas pelo Instagram @{HANDLE}. Não é loja oficial Garmin.

Como comprar: o cliente monta a sacola no site e toca em "Finalizar pedido". O site copia uma mensagem com os modelos e o total e abre o direct do Instagram ({IG_DM}). Pagamento, retirada em Joinville e envio para outras cidades são combinados na conversa. Também é possível dar um Garmin usado como parte do pagamento (página Upgrade); o valor do usado é avaliado no direct.

Preços em reais (BRL), atualizados em {HOJE.strftime('%d/%m/%Y')}. Estoque de seminovos muda rápido: confirme disponibilidade no direct.

## Relógios
""" + ''.join(f"- [{m['nome_completo']}]({SITE}{m['url']}): {brl(m['preco'])}. {m['resumo']} Bateria {m['bat']}, GPS {'multibanda' if m['multibanda'] else 'simples'}, tela {m['tela']}, {m['peso']}.\n" for m in sorted(MODELOS, key=lambda x: x['preco'])) + f"""
## Páginas
- [Loja]({SITE}loja.html): catálogo por categoria (para começar, performance, triathlon).
- [Escolha o Garmin por mim]({SITE}escolha.html): quiz de 4 perguntas que indica um modelo do estoque.
- [Comparar]({SITE}comparar.html): até 3 relógios lado a lado. Aceita ?a=fr265&b=fr255&c=fr955 com os ids do catálogo.
- [Upgrade]({SITE}upgrade.html): troca de um Garmin usado por um modelo mais novo.

## Dados
- [Catálogo em JSON]({SITE}catalogo.json): todos os modelos, preços, links e especificações.
- [Sitemap]({SITE}sitemap.xml)

## Perguntas frequentes
""" + ''.join(f"- {q} {r}\n" for q, r in FAQ)
open(OUT + 'llms.txt', 'w').write(llms)
BOTS = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'Claude-User', 'PerplexityBot', 'Perplexity-User', 'Google-Extended', 'Applebot-Extended', 'Bingbot', 'Googlebot']
open(OUT + 'robots.txt', 'w').write('User-agent: *\nAllow: /\nDisallow: /_fonte/\n\n' + ''.join(f'User-agent: {b}\nAllow: /\n\n' for b in BOTS) + f'Sitemap: {SITE}sitemap.xml\n')
open(OUT + '_headers', 'w').write("""/assets/*
  Cache-Control: public, max-age=31536000, immutable

/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin

/*.html
  Cache-Control: public, max-age=0, must-revalidate

/llms.txt
  Content-Type: text/plain; charset=utf-8
  Cache-Control: public, max-age=3600

/catalogo.json
  Content-Type: application/json; charset=utf-8
  Access-Control-Allow-Origin: *
  Cache-Control: public, max-age=3600
""")

# ---------- Sitemap ----------
urls = ''.join(f'<url><loc>{SITE}{"" if p == "index.html" else p}</loc><lastmod>{HOJE.isoformat()}</lastmod></url>' for p in PAGINAS if p != '404.html')
open(OUT + 'sitemap.xml', 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
print('ok', len(PAGINAS), 'páginas:', ', '.join(PAGINAS))
