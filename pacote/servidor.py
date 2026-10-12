#!/usr/bin/env python3
"""HTML salvável: mini-servidor local que deixa um HTML gravar dados dentro de si mesmo.

Uso:  python3 servidor.py <pasta> [arquivo.html]

- Entrega os arquivos da <pasta> só para este Mac (127.0.0.1).
- Recebe o botão "Salvar" da página e grava os dados no bloco
  <script type="application/json" id="dados-salvos">...</script> do próprio HTML.
- Antes de cada gravação, guarda uma cópia do HTML em ./backups (os 30 mais recentes por arquivo).
"""
import http.server
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

PORTA_INICIAL = 8765
LIMITE_BYTES = 5 * 1024 * 1024
BACKUPS_POR_ARQUIVO = 30
PASTA_BACKUPS = Path(__file__).resolve().parent / 'backups'
BLOCO = re.compile(
    r'(<script type="application/json" id="dados-salvos">)(.*?)(</script>)',
    re.DOTALL,
)


def html_salvavel(caminho):
    try:
        return len(BLOCO.findall(caminho.read_text(encoding='utf-8'))) == 1
    except (OSError, UnicodeDecodeError):
        return False


def fazer_backup(caminho):
    PASTA_BACKUPS.mkdir(exist_ok=True)
    carimbo = time.strftime('%Y-%m-%d_%H-%M-%S') + f'.{time.time_ns() % 1_000_000_000:09d}'
    destino = PASTA_BACKUPS / f'{carimbo}__{caminho.name}'
    destino.write_bytes(caminho.read_bytes())
    antigos = sorted(PASTA_BACKUPS.glob(f'*__{caminho.name}'))
    for velho in antigos[:-BACKUPS_POR_ARQUIVO]:
        velho.unlink()


def gravar(caminho, dados):
    texto = caminho.read_text(encoding='utf-8')
    if len(BLOCO.findall(texto)) != 1:
        raise ValueError('este HTML não tem (ou tem mais de um) bloco "dados-salvos"')
    # "<" vira <: o JSON continua válido e nada dentro dele consegue fechar o <script>.
    corpo = json.dumps(dados, ensure_ascii=False, indent=1).replace('<', '\\u003c')
    novo = BLOCO.sub(lambda m: m.group(1) + corpo + m.group(3), texto, count=1)
    fazer_backup(caminho)
    temporario = caminho.with_name('.' + caminho.name + '.salvando')
    temporario.write_text(novo, encoding='utf-8')
    os.replace(temporario, caminho)  # troca de uma vez: o arquivo nunca fica pela metade


class Manipulador(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def host_local(self):
        host = (self.headers.get('Host') or '').split(':')[0]
        return host in ('127.0.0.1', 'localhost')

    def responder_json(self, status, corpo):
        dados = json.dumps(corpo, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def arquivo_da_pasta(self, nome):
        nome = urllib.parse.unquote(nome or '')
        if not nome.endswith('.html') or '/' in nome or '\\' in nome or nome.startswith('.'):
            return None
        caminho = Path(self.directory) / nome
        return caminho if caminho.is_file() else None

    def do_GET(self):
        if not self.host_local():
            return self.send_error(403)
        url = urllib.parse.urlparse(self.path)
        if url.path == '/__salvavel/status':
            return self.responder_json(200, {'ok': True})
        if url.path == '/':
            return self.pagina_inicial()
        return super().do_GET()

    def pagina_inicial(self):
        nomes = sorted(p.name for p in Path(self.directory).glob('*.html') if html_salvavel(p))
        itens = ''.join(f'<li><a href="/{urllib.parse.quote(n)}">{n}</a></li>' for n in nomes)
        corpo = (
            '<!doctype html><meta charset="utf-8"><title>HTML salvável</title>'
            '<body style="font-family:-apple-system,sans-serif;max-width:640px;margin:40px auto;padding:0 16px">'
            '<h2>HTMLs salváveis nesta pasta</h2>'
            + (f'<ul>{itens}</ul>' if itens else '<p>Nenhum HTML desta pasta tem o bloco "dados-salvos".</p>')
            + '<p style="color:#666">Para desligar, feche a janela do Terminal.</p></body>'
        ).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        # O cabeçalho próprio impede que outro site, aberto no navegador, consiga mandar gravações para cá.
        if not self.host_local() or self.headers.get('X-Salvavel') != '1':
            return self.responder_json(403, {'ok': False, 'erro': 'pedido recusado'})
        if url.path != '/__salvavel/salvar':
            return self.responder_json(404, {'ok': False, 'erro': 'endereço desconhecido'})
        caminho = self.arquivo_da_pasta(urllib.parse.parse_qs(url.query).get('arquivo', [''])[0])
        if caminho is None:
            return self.responder_json(400, {'ok': False, 'erro': 'arquivo não encontrado nesta pasta'})
        tamanho = int(self.headers.get('Content-Length') or 0)
        if tamanho <= 0 or tamanho > LIMITE_BYTES:
            return self.responder_json(400, {'ok': False, 'erro': 'tamanho inválido'})
        try:
            dados = json.loads(self.rfile.read(tamanho).decode('utf-8'))
            if not isinstance(dados, dict):
                raise ValueError('os dados precisam ser um objeto JSON')
            gravar(caminho, dados)
        except Exception as erro:  # noqa: BLE001 - a página mostra a mensagem
            return self.responder_json(400, {'ok': False, 'erro': str(erro)})
        print(f'  {time.strftime("%H:%M:%S")}  salvo em {caminho.name}')
        return self.responder_json(200, {'ok': True, 'salvoEm': time.strftime('%Y-%m-%dT%H:%M:%S')})

    def log_message(self, *args):
        pass  # silencioso: só as gravações aparecem no Terminal


def porta_livre():
    for porta in range(PORTA_INICIAL, PORTA_INICIAL + 50):
        with socket.socket() as s:
            if s.connect_ex(('127.0.0.1', porta)) != 0:
                return porta
    raise SystemExit('Nenhuma porta livre entre 8765 e 8814.')


def main():
    if len(sys.argv) < 2:
        raise SystemExit('Uso: python3 servidor.py <pasta> [arquivo.html]')
    pasta = Path(sys.argv[1]).resolve()
    arquivo = sys.argv[2] if len(sys.argv) > 2 else ''
    if arquivo and not (pasta / arquivo).is_file():
        raise SystemExit(f'Não achei {arquivo} em {pasta}.')
    porta = porta_livre()
    endereco = f'http://127.0.0.1:{porta}/' + urllib.parse.quote(arquivo)

    def manipulador(*a, **kw):
        return Manipulador(*a, directory=str(pasta), **kw)

    servidor = http.server.ThreadingHTTPServer(('127.0.0.1', porta), manipulador)
    print('HTML salvável ligado')
    print(f'  pasta:    {pasta}')
    print(f'  endereço: {endereco}')
    print('  Para desligar, feche esta janela (ou aperte Ctrl+C).\n')
    subprocess.Popen(['open', endereco])
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print('\nDesligado.')


if __name__ == '__main__':
    main()
