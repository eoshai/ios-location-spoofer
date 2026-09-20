# 📍 iOS Location Spoofer

Painel web local (Flask + Leaflet) para simular a localização GPS de um iPhone conectado por USB, usando a biblioteca [`pymobiledevice3`](https://github.com/doronz88/pymobiledevice3).

Você escolhe um ponto no mapa (ou busca por endereço/coordenadas), clica em **Aplicar Localização** e o iPhone passa a reportar essa posição. Também é possível simular uma caminhada/corrida/trajeto de carro seguindo as ruas.

> ⚠️ **Uso responsável:** a ferramenta foi feita para testes de desenvolvimento, privacidade e estudo. Usá-la para burlar regras de apps ou jogos pode violar os termos de uso deles e resultar em banimento de conta. A responsabilidade pelo uso é sua.

---

## ✨ Funcionalidades

- 🗺️ Mapa interativo em modo escuro (Leaflet + CARTO), com prédios 3D em zoom alto
- 🔎 Busca por endereço (Nominatim/OpenStreetMap) ou por coordenadas (`-23.5505, -46.6333`)
- 🔒 **Trava de estabilização (Anti-Drift):** reenvia a coordenada a cada X segundos para evitar que o GPS real "volte"; com duração máxima configurável
- 🚶 **Modo Caminhada:** clique na origem e no destino, a rota é calculada pelas ruas (OSRM) e o iPhone "percorre" o trajeto a 5, 12 ou 50 km/h
- 💿 Botão para montar o Developer Disk Image direto do painel
- ♻️ Botão para restaurar a localização real

---

## 📋 Requisitos

| Item | Detalhe |
|---|---|
| Computador | Windows, macOS ou Linux |
| Python | 3.10 ou superior |
| iPhone | Conectado por cabo USB, desbloqueado e com o computador marcado como **"Confiar"** |
| Modo Desenvolvedor | Ativado no iPhone (**Ajustes → Privacidade e Segurança → Modo Desenvolvedor**) |
| Drivers (Windows) | iTunes ou "Dispositivos Apple" instalado, para o computador reconhecer o iPhone |
| Internet | Necessária para os mapas, busca, rotas e para baixar o Developer Disk Image na primeira vez |

> O app usa o caminho `developer dvt simulate-location`, que é o indicado pelo `pymobiledevice3` para **iOS 17 ou superior**.

---

## 🚀 Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/eoshai/ios-location-spoofer.git
cd ios-location-spoofer

# 2. (Recomendado) Crie um ambiente virtual
python -m venv venv

# Windows (PowerShell)
venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt
```

---

## ▶️ Como usar

1. Conecte o iPhone por USB, desbloqueie e toque em **Confiar neste computador**.
2. Ative o **Modo Desenvolvedor** no iPhone (ele reinicia; depois confirme a ativação).
3. Inicie o servidor:
   ```bash
   python app.py
   ```
4. Abra **http://127.0.0.1:5000** no navegador.
5. Clique em **Montar Developer Disk** (só é necessário uma vez por conexão/reinício do iPhone) e aguarde a mensagem de sucesso.
6. Clique no mapa (ou pesquise um local) e depois em **Aplicar Localização**.
7. Para voltar ao normal, clique em **Resetar para Localização Real**.

### Modo Caminhada

1. Ative a chave **Modo Caminhada**.
2. Escolha a velocidade.
3. Clique no ponto de partida e depois no destino.
4. O trajeto é desenhado em verde e a posição do iPhone é atualizada a cada 1,5 s. Use **Interromper Trajeto** para parar.

---

## 🧠 Como funciona

```
Navegador (Leaflet)  ──HTTP──▶  Flask (app.py)  ──subprocess──▶  pymobiledevice3  ──USB──▶  iPhone
```

| Rota | Método | Função |
|---|---|---|
| `/` | GET | Serve a interface web |
| `/mount` | POST | Monta o Developer Disk Image (`mounter auto-mount`) |
| `/set_location` | POST | Define a localização (`{"lat": .., "lng": ..}`) |
| `/clear_location` | POST | Limpa a simulação e volta ao GPS real |

O servidor escuta apenas em `127.0.0.1` (somente sua máquina).

---

## 🛠️ Solução de problemas

| Sintoma | O que tentar |
|---|---|
| `pymobiledevice3 não encontrado` | Ative o ambiente virtual e rode `pip install -r requirements.txt` |
| `No such option: --userspace` | Atualize: `pip install -U pymobiledevice3` |
| Erro ao montar o disco | iPhone desbloqueado? Modo Desenvolvedor ativo? Cabo/porta USB ok? Há internet? |
| "O disco está montado?" ao aplicar | Clique em **Montar Developer Disk** primeiro |
| Nenhum dispositivo encontrado | Teste `pymobiledevice3 usbmux list`. No Windows, instale iTunes/Dispositivos Apple |
| A localização "volta" para a real | Aumente a frequência da Trava (intervalo de 1–3 s) e mantenha o iPhone desbloqueado |
| Busca de endereço não funciona | O Nominatim limita requisições; espere alguns segundos e tente de novo |
| Mapa em branco | Verifique a conexão com a internet (Leaflet e os tiles vêm de CDNs) |

---

## ⚠️ Limitações conhecidas

- A rota do Modo Caminhada usa o servidor público do OSRM com perfil de **carro**, então caminhos exclusivos de pedestres não são considerados.
- Cada atualização de posição executa um comando do `pymobiledevice3`, o que tem um custo de alguns segundos por chamada. Por isso o servidor descarta atualizações enquanto a anterior ainda está em andamento.
- Os serviços públicos (Nominatim, OSRM, CARTO) têm limites de uso e podem ficar indisponíveis.

---

## 📦 Dependências

- [Flask](https://flask.palletsprojects.com/)
- [pymobiledevice3](https://github.com/doronz88/pymobiledevice3)
- [Leaflet](https://leafletjs.com/), [OSM Buildings](https://osmbuildings.org/) (via CDN)
- Serviços: [Nominatim](https://nominatim.org/), [OSRM](https://project-osrm.org/), [CARTO](https://carto.com/)

---

## 📄 Licença

Distribuído sob a licença MIT. Veja o arquivo `LICENSE`.
