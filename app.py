from flask import Flask, render_template_string, request, jsonify
import subprocess
import sys
import threading

app = Flask(__name__)

# Página HTML com o mapa interativo (Cyberpunk Dark Mode com novas ferramentas de Automação de GPS)
HTML_INTERFACE = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel de Controle de GPS - iOS</title>

    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

    <style>
        :root {
            --bg-void: #000000;
            --bg-panel: #121212;
            --bg-panel-alt: #181818;
            --border-color: #2a2a2a;
            --neon: #00ff66;
            --neon-glow: rgba(0, 255, 102, 0.35);
            --text-primary: #e8e8ea;
            --text-muted: #7a7a80;
            --danger: #ff3b5c;
            --danger-glow: rgba(255, 59, 92, 0.3);
            --info: #00c8ff;
        }

        * { box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            margin: 0;
            background: var(--bg-void);
            color: var(--text-primary);
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }

        header {
            background: linear-gradient(180deg, #0d0d0d, #000000);
            color: var(--neon);
            padding: 14px 22px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            box-shadow: 0 0 20px rgba(0, 255, 102, 0.08);
            z-index: 20;
        }

        h1 {
            margin: 0;
            font-size: 1.05rem;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            text-shadow: 0 0 8px var(--neon-glow);
        }

        .status-pill {
            font-size: 0.78rem;
            color: var(--neon);
            display: flex;
            align-items: center;
            gap: 6px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .status-dot {
            height: 8px;
            width: 8px;
            background: var(--neon);
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px var(--neon), 0 0 16px var(--neon-glow);
            animation: pulse 1.8s infinite ease-in-out;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.35; }
        }

        .container {
            display: flex;
            flex: 1;
            height: calc(100vh - 58px);
            position: relative;
        }

        #map-wrap {
            flex: 1;
            position: relative;
            height: 100%;
        }

        #map {
            width: 100%;
            height: 100%;
            background: var(--bg-void);
        }

        .sidebar {
            width: 340px;
            background: var(--bg-panel);
            border-left: 1px solid var(--border-color);
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            z-index: 10;
            overflow-y: auto;
        }

        .card {
            background: var(--bg-panel-alt);
            border-radius: 12px;
            padding: 14px;
            border: 1px solid var(--border-color);
        }

        .card-title {
            font-size: 0.72rem;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 10px;
            font-weight: 600;
            letter-spacing: 1px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .coord-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 4px 0;
        }

        .coord-label { color: var(--text-muted); font-size: 0.85rem; }

        .coord-val {
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 0.95rem;
            color: var(--neon);
            text-shadow: 0 0 6px var(--neon-glow);
        }

        /* Elementos de Formulário */
        .input-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-bottom: 10px;
        }
        .input-group:last-child { margin-bottom: 0; }
        
        .input-group label {
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .input-group input, .input-group select {
            background: var(--bg-void);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 10px;
            color: var(--text-primary);
            font-family: inherit;
            font-size: 0.88rem;
            outline: none;
            transition: border-color 0.2s;
        }
        .input-group input:focus, .input-group select:focus {
            border-color: var(--neon);
        }

        /* Chave Seletora (Toggle Switch) */
        .toggle-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 4px 0;
        }
        .toggle-label { font-size: 0.88rem; font-weight: 500; }
        .switch {
            position: relative;
            display: inline-block;
            width: 46px;
            height: 24px;
        }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: var(--bg-void);
            border: 1px solid var(--border-color);
            transition: .3s;
            border-radius: 24px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 16px;
            width: 16px;
            left: 3px;
            bottom: 3px;
            background-color: var(--text-muted);
            transition: .3s;
            border-radius: 50%;
        }
        input:checked + .slider {
            background-color: rgba(0, 255, 102, 0.1);
            border-color: var(--neon);
        }
        input:checked + .slider:before {
            transform: translateX(22px);
            background-color: var(--neon);
            box-shadow: 0 0 8px var(--neon);
        }

        button {
            border: none;
            border-radius: 10px;
            padding: 12px;
            font-size: 0.88rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.2s ease;
            width: 100%;
            font-family: inherit;
        }

        .btn-success {
            background: var(--neon);
            color: #000000;
            box-shadow: 0 0 15px rgba(0, 255, 102, 0.3);
        }

        .btn-success:hover {
            background: #33ff85;
            box-shadow: 0 0 25px rgba(0, 255, 102, 0.55);
            transform: translateY(-1px);
        }

        /* ADICIONE ESTE BLOCO AQUI */
        .btn-secondary {
            background: var(--bg-panel-alt);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            margin-bottom: 8px;
        }
        .btn-secondary:hover {
            background: #222225;
            border-color: var(--text-muted);
        }

        .btn-warning {
            background: transparent;
            color: var(--info);
            border: 1px solid var(--info);
        }
        .btn-warning:hover {
            background: var(--info);
            color: #000000;
            box-shadow: 0 0 15px rgba(0, 200, 255, 0.4);
        }

        .btn-danger {
            background: transparent;
            color: var(--danger);
            border: 1px solid var(--danger);
            margin-top: auto;
        }

        .btn-danger:hover {
            background: var(--danger);
            color: #000000;
            box-shadow: 0 0 20px rgba(255, 59, 92, 0.5);
        }

        #status-msg {
            text-align: center;
            font-size: 0.82rem;
            margin-top: 2px;
            font-weight: 500;
            color: var(--text-muted);
            min-height: 2.4em;
            letter-spacing: 0.3px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0 4px;
        }

        .countdown-badge {
            background: rgba(255, 59, 92, 0.15);
            color: var(--danger);
            border: 1px solid var(--danger);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-family: monospace;
        }

        /* ==== Barra de pesquisa flutuante ==== */
        .search-box {
            position: absolute;
            top: 16px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            width: min(420px, 85%);
            display: flex;
            align-items: center;
            background: rgba(18, 18, 18, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 4px 6px 4px 14px;
            box-shadow: 0 4px 25px rgba(0,0,0,0.6), 0 0 0 1px rgba(0,255,102,0.05);
        }

        .search-box svg {
            width: 16px;
            height: 16px;
            stroke: var(--neon);
            flex-shrink: 0;
        }

        .search-box input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: var(--text-primary);
            font-size: 0.92rem;
            padding: 10px 10px;
            font-family: inherit;
        }

        .search-box input::placeholder { color: var(--text-muted); }

        .search-loading {
            width: 14px;
            height: 14px;
            border: 2px solid var(--border-color);
            border-top-color: var(--neon);
            border-radius: 50%;
            display: none;
            animation: spin 0.7s linear infinite;
            margin-right: 6px;
        }

        .search-loading.active { display: inline-block; }

        @keyframes spin { to { transform: rotate(360deg); } }

        .search-results {
            position: absolute;
            top: 62px;
            left: 50%;
            transform: translateX(-50%);
            width: min(420px, 85%);
            z-index: 999;
            background: var(--bg-panel);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(0,0,0,0.6);
            display: none;
        }

        .search-results.active { display: block; }

        .search-result-item {
            padding: 10px 14px;
            font-size: 0.85rem;
            color: var(--text-primary);
            cursor: pointer;
            border-bottom: 1px solid var(--border-color);
        }

        .search-result-item:hover {
            background: var(--bg-panel-alt);
            color: var(--neon);
        }

        /* Popups e Controles do Leaflet */
        .leaflet-popup-content-wrapper { background: var(--bg-panel); color: var(--text-primary); border: 1px solid var(--border-color); }
        .leaflet-popup-tip { background: var(--bg-panel); }
        .leaflet-bar a { background-color: var(--bg-panel); color: var(--neon); border-bottom: 1px solid var(--border-color); }
        .leaflet-bar a:hover { background-color: var(--bg-panel-alt); }
    </style>
</head>
<body>

    <header>
        <h1>iOS Location Spoofer</h1>
        <div class="status-pill">
            <span class="status-dot"></span> Servidor Ativo
        </div>
    </header>

    <div class="container">
        <div id="map-wrap">
            <div id="map"></div>

            <div class="search-box">
                <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
                <input id="search-input" type="text" placeholder="Endereço ou coordenadas (ex: -23.5505, -46.6333)..." autocomplete="off" />
                <span id="search-loading" class="search-loading"></span>
            </div>
            <div id="search-results" class="search-results"></div>
        </div>

        <div class="sidebar">
            <button id="btn-mount" class="btn-secondary" onclick="montarDisco()">Montar Developer Disk</button>
            <!-- Card de Coordenadas -->
            <div class="card">
                <div class="card-title">Coordenadas Atuais</div>
                <div class="coord-row">
                    <span class="coord-label">Lat</span>
                    <span id="lat-display" class="coord-val">-</span>
                </div>
                <div class="coord-row">
                    <span class="coord-label">Lng</span>
                    <span id="lng-display" class="coord-val">-</span>
                </div>
            </div>

            <!-- Card Anti-Oscilação (Trava Antibriga) -->
            <div class="card">
                <div class="card-title">
                    Trava de Estabilização (Anti-Drift)
                    <span id="countdown" class="countdown-badge" style="display: none;">OFF</span>
                </div>
                <div class="input-group">
                    <label>Intervalo de Disparo (segundos)</label>
                    <input type="number" id="loop-interval" value="3" min="1" max="60" />
                </div>
                <div class="input-group">
                    <label>Duração Máxima (minutos)</label>
                    <input type="number" id="loop-duration" value="60" min="1" placeholder="Vazio = Infinito" />
                </div>
            </div>

            <!-- Card Modo Caminhada -->
            <div class="card">
                <div class="card-title">Automação de Rota</div>
                <div class="toggle-container">
                    <span class="toggle-label">Modo Caminhada</span>
                    <label class="switch">
                        <input type="checkbox" id="walk-mode-toggle" onchange="toggleWalkMode()">
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="input-group" style="margin-top: 10px;">
                    <label>Velocidade Simulada</label>
                    <select id="walk-speed">
                        <option value="5">🚶 Caminhada (5 km/h)</option>
                        <option value="12">🏃 Corrida (12 km/h)</option>
                        <option value="50">🚗 Carro (50 km/h)</option>
                    </select>
                </div>
                <button id="btn-stop-walk" class="btn-danger" style="display: none; padding: 8px; margin-top: 10px; font-size: 0.78rem;" onclick="interromperCaminhada()">Interromper Trajeto</button>
            </div>

            <button id="btn-change" class="btn-success" onclick="aplicarLocalizacao()">Aplicar Localização</button>

            <div id="status-msg">Clique no mapa para selecionar um local</div>

            <button class="btn-danger" onclick="resetarLocalizacao()">Resetar para Localização Real</button>
        </div>
    </div>

    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <script>
        const map = L.map('map', { zoomControl: true }).setView([-23.55052, -46.633308], 5);

        // ADICIONE ESTA FUNÇÃO BEM AQUI
        function montarDisco() {
            atualizarStatus("Montando imagem de desenvolvedor no iOS...", "#00c8ff");
            fetch('/mount', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    atualizarStatus("Developer Disk montado com sucesso! Pronto para simular.", "#00ff66");
                } else {
                    atualizarStatus("Erro ao montar disco: " + data.error, "#ff3b5c");
                }
            })
            .catch(() => atualizarStatus("Erro de conexão com o servidor.", "#ff3b5c"));
        }

        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '© OpenStreetMap contributors © CARTO',
            subdomains: 'abcd',
            maxZoom: 20
        }).addTo(map);

        let marker = null;
        let selectedLat = null;
        let selectedLng = null;

        // Gerenciamento de Loops Globais
        let stabilizationInterval = null;
        let countdownTimeout = null;
        let tempoRestanteSegundos = 0;

        // Gerenciamento do Modo Caminhada
        let walkModeActive = false;
        let pontoInicio = null;
        let pontoDestino = null;
        let walkInterval = null;
        let rotaPolyline = null;
        let marcadorCaminhada = null;

        // Elementos de busca
        const searchInput = document.getElementById('search-input');
        const searchLoading = document.getElementById('search-loading');
        const searchResults = document.getElementById('search-results');
        let searchDebounce = null;

        // Clique no mapa
        map.on('click', function(e) {
            if (walkModeActive) {
                gerenciarCliquesCaminhada(e.latlng);
                return;
            }

            selectedLat = e.latlng.lat;
            selectedLng = e.latlng.lng;
            atualizarDisplays(selectedLat, selectedLng);
            atualizarMarcador(e.latlng);

            // Se a trava estiver rodando, muda a coordenada mirada dinamicamente
            if (stabilizationInterval) {
                atualizarStatus("Alvo de estabilização alterado no mapa!", "#00c8ff");
            }
        });

        function atualizarDisplays(lat, lng) {
            document.getElementById('lat-display').innerText = lat.toFixed(6);
            document.getElementById('lng-display').innerText = lng.toFixed(6);
        }

        function atualizarMarcador(latlng) {
            if (marker) {
                marker.setLatLng(latlng);
            } else {
                marker = L.marker(latlng).addTo(map);
            }
        }

        // ===================== ENGENHARIA DE ESTABILIZAÇÃO (ANTI-OSCILAÇÃO) =====================
        function aplicarLocalizacao() {
            if (selectedLat === null || selectedLng === null) {
                atualizarStatus("Selecione um local no mapa primeiro!", "#ff9500");
                return;
            }

            // Limpa loops anteriores para não encavalar
            pararLoopsEstabilizacao();
            interromperCaminhada();

            const intervaloInput = parseInt(document.getElementById('loop-interval').value) || 3;
            const duracaoInput = document.getElementById('loop-duration').value;

            atualizarStatus("Iniciando trava de sinal contra o GPS real...", "#00c8ff");
            
            // Primeiro disparo imediato
            dispararComandoBackend(selectedLat, selectedLng);

            // Inicia o intervalo de reenvio constante
            stabilizationInterval = setInterval(() => {
                dispararComandoBackend(selectedLat, selectedLng);
            }, intervaloInput * 1000);

            // Gerencia tempo de corte (Duração máxima)
            const badge = document.getElementById('countdown');
            if (duracaoInput) {
                tempoRestanteSegundos = parseInt(duracaoInput) * 60;
                badge.style.display = "inline-block";
                badge.innerText = formatarTempo(tempoRestanteSegundos);

                countdownTimeout = setInterval(() => {
                    tempoRestanteSegundos--;
                    if (tempoRestanteSegundos <= 0) {
                        atualizarStatus("Tempo limite da trava atingido. Limpando...", "#ff3b5c");
                        resetarLocalizacao();
                    } else {
                        badge.innerText = formatarTempo(tempoRestanteSegundos);
                    }
                }, 1000);
            } else {
                badge.style.display = "inline-block";
                badge.innerText = "INF";
            }
        }

        function dispararComandoBackend(lat, lng) {
            fetch('/set_location', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lat: lat, lng: lng })
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    if (!walkModeActive) {
                        atualizarStatus("Sinal travado com sucesso! Injetando coordenadas novamente...", "#00ff66");
                    }
                } else {
                    atualizarStatus("Erro no túnel USB: " + data.error, "#ff3b5c");
                }
            })
            .catch(err => console.error("Erro na requisição periódica:", err));
        }

        function pararLoopsEstabilizacao() {
            if (stabilizationInterval) { clearInterval(stabilizationInterval); stabilizationInterval = null; }
            if (countdownTimeout) { clearInterval(countdownTimeout); countdownTimeout = null; }
            document.getElementById('countdown').style.display = "none";
        }

        function formatarTempo(segundos) {
            const m = Math.floor(segundos / 60);
            const s = segundos % 60;
            return `${m}:${s < 10 ? '0' : ''}${s}`;
        }

        // ===================== ENGENHARIA DO MODO CAMINHADA (ROTA) =====================
        function toggleWalkMode() {
            walkModeActive = document.getElementById('walk-mode-toggle').checked;
            interromperCaminhada();
            pararLoopsEstabilizacao();

            if (walkModeActive) {
                atualizarStatus("Modo Caminhada ativado. Clique no ponto inicial e depois no destino.", "#00c8ff");
                pontoInicio = null;
                pontoDestino = null;
            } else {
                atualizarStatus("Modo Caminhada desligado.", "#7a7a80");
            }
        }

        function gerenciarCliquesCaminhada(latlng) {
            if (!pontoInicio) {
                pontoInicio = latlng;
                atualizarMarcador(latlng);
                selectedLat = latlng.lat; selectedLng = latlng.lng;
                atualizarDisplays(latlng.lat, latlng.lng);
                atualizarStatus("Ponto de partida definido! Agora clique no local de destino.", "#00c8ff");
            } else if (!pontoDestino) {
                pontoDestino = latlng;
                atualizarStatus("Trajeto calculado! Iniciando simulação de caminhada...", "#00ff66");
                document.getElementById('btn-stop-walk').style.display = "block";
                iniciarSimulacaoTrajeto();
            }
        }

        function iniciarSimulacaoTrajeto() {
            const velocidadeKmh = parseFloat(document.getElementById('walk-speed').value);
            
            // 1. Consulta o servidor de rotas pelas ruas (OSRM)
            atualizarStatus("Calculando rota pelas ruas...", "#00c8ff");
            fetch(`https://router.project-osrm.org/route/v1/driving/${pontoInicio.lng},${pontoInicio.lat};${pontoDestino.lng},${pontoDestino.lat}?overview=full&geometries=geojson`)
            .then(res => res.json())
            .then(data => {
                if (!data.routes || data.routes.length === 0) {
                    atualizarStatus("Não foi possível traçar uma rota por ruas aqui.", "#ff3b5c");
                    return;
                }

                // Extrai todos os micro-pontos da rua calculada
                const coordenadasRota = data.routes[0].geometry.coordinates.map(coord => L.latLng(coord[1], coord[0]));

                // Desenha a linha verde exata da rua no mapa
                if (rotaPolyline) map.removeLayer(rotaPolyline);
                rotaPolyline = L.polyline(coordenadasRota, {color: '#00ff66', weight: 5, shadowBlur: 5}).addTo(map);

                const metrosPorSegundo = velocidadeKmh / 3.6;
                const intervaloAtualizacaoSegundos = 1.5; 
                const distanciaPorSalto = metrosPorSegundo * intervaloAtualizacaoSegundos;

                let indicePontoAtual = 0;
                let latAtual = coordenadasRota[0].lat;
                let lngAtual = coordenadasRota[0].lng;

                // 2. Loop de movimentação detalhado pelas ruas
                walkInterval = setInterval(() => {
                    if (indicePontoAtual >= coordenadasRota.length - 1) {
                        atualizarStatus("Você chegou ao destino seguindo as ruas!", "#00ff66");
                        interromperCaminhada();
                        return;
                    }

                    const proximoAlvo = coordenadasRota[indicePontoAtual + 1];
                    const dx = proximoAlvo.lat - latAtual;
                    const dy = proximoAlvo.lng - lngAtual;
                    const distanciaAteProximoPonto = Math.sqrt(dx*dx + dy*dy) * 111320; // em metros

                    if (distanciaAteProximoPonto <= distanciaPorSalto) {
                        // Se o pulo passa do próximo ponto da rua, avança para o próximo nó da rota
                        indicePontoAtual++;
                        latAtual = proximoAlvo.lat;
                        lngAtual = proximoAlvo.lng;
                    } else {
                        // Anda um pedaço em direção ao próximo ponto da rua
                        const razao = distanciaPorSalto / distanciaAteProximoPonto;
                        latAtual += dx * razao;
                        lngAtual += dy * razao;
                    }

                    const novaPosicao = L.latLng(latAtual, lngAtual);
                    atualizarMarcador(novaPosicao);
                    atualizarDisplays(latAtual, lngAtual);

                    // Atualiza o iPhone em tempo real
                    selectedLat = latAtual;
                    selectedLng = lngAtual;
                    dispararComandoBackend(latAtual, lngAtual);
                    
                    atualizarStatus(`Simulando trajeto: ${velocidadeKmh} km/h pelas ruas...`, "#00ff66");
                }, intervaloAtualizacaoSegundos * 1000);
            })
            .catch(() => atualizarStatus("Erro ao conectar com o servidor de rotas.", "#ff3b5c"));
        }

        function interromperCaminhada() {
            if (walkInterval) { clearInterval(walkInterval); walkInterval = null; }
            if (rotaPolyline) { map.removeLayer(rotaPolyline); rotaPolyline = null; }
            document.getElementById('btn-stop-walk').style.display = "none";
            pontoInicio = null;
            pontoDestino = null;
        }

        // ===================== MÓDULO DE BUSCA NOMINATIM =====================
        function selecionarResultado(lat, lng, label) {
            const latlng = L.latLng(lat, lng);
            map.setView(latlng, 17);

            selectedLat = lat;
            selectedLng = lng;
            atualizarDisplays(lat, lng);
            atualizarMarcador(latlng);

            searchInput.value = label;
            searchResults.classList.remove('active');
            searchResults.innerHTML = '';
            atualizarStatus("Local encontrado!", "#00ff66");

            if (walkModeActive) {
                gerenciarCliquesCaminhada(latlng);
            }
        }

        function tentarParsearCoordenadas(texto) {
            const match = texto.trim().match(/^(-?\d{1,3}(?:\.\d+)?)\s*[,\s]\s*(-?\d{1,3}(?:\.\d+)?)$/);
            if (!match) return null;
            const lat = parseFloat(match[1]);
            const lng = parseFloat(match[2]);
            if (isNaN(lat) || isNaN(lng)) return null;
            if (lat < -90 || lat > 90 || lng < -180 || lng > 180) return null;
            return { lat, lng };
        }

        function buscarEndereco(query) {
            const coords = tentarParsearCoordenadas(query);
            if (coords) {
                searchResults.classList.remove('active');
                selecionarResultado(coords.lat, coords.lng, coords.lat.toFixed(6) + ', ' + coords.lng.toFixed(6));
                return;
            }

            searchLoading.classList.add('active');
            fetch('https://nominatim.openstreetmap.org/search?format=json&limit=5&q=' + encodeURIComponent(query))
                .then(res => res.json())
                .then(results => {
                    searchLoading.classList.remove('active');
                    searchResults.innerHTML = '';

                    if (!results || results.length === 0) {
                        atualizarStatus("Endereço não encontrado.", "#ff3b5c");
                        searchResults.classList.remove('active');
                        return;
                    }

                    results.forEach(place => {
                        const item = document.createElement('div');
                        item.className = 'search-result-item';
                        item.innerText = place.display_name;
                        item.onclick = () => selecionarResultado(parseFloat(place.lat), parseFloat(place.lon), place.display_name);
                        searchResults.appendChild(item);
                    });
                    searchResults.classList.add('active');
                })
                .catch(() => {
                    searchLoading.classList.remove('active');
                    atualizarStatus("Erro ao buscar endereço.", "#ff3b5c");
                });
        }

        searchInput.addEventListener('input', function() {
            const query = searchInput.value.trim();
            clearTimeout(searchDebounce);
            if (query.length < 3) { searchResults.classList.remove('active'); return; }
            searchDebounce = setTimeout(() => buscarEndereco(query), 500);
        });

        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') { clearTimeout(searchDebounce); const query = searchInput.value.trim(); if (query) buscarEndereco(query); }
        });

        document.addEventListener('click', function(e) {
            if (!searchResults.contains(e.target) && e.target !== searchInput) { searchResults.classList.remove('active'); }
        });

        // ===================== SISTEMA DE RESET =====================
        function resetarLocalizacao() {
            pararLoopsEstabilizacao();
            interromperCaminhada();
            document.getElementById('walk-mode-toggle').checked = false;
            walkModeActive = false;

            atualizarStatus("Limpando simulação no iOS...", "#00c8ff");
            fetch('/clear_location', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    atualizarStatus("GPS original restaurado com sucesso!", "#00ff66");
                    if(marker) { map.removeLayer(marker); marker = null; }
                    document.getElementById('lat-display').innerText = "-";
                    document.getElementById('lng-display').innerText = "-";
                    selectedLat = null; selectedLng = null;
                } else {
                    atualizarStatus("Erro ao limpar dados do dispositivo.", "#ff3b5c");
                }
            });
        }

        function atualizarStatus(texto, cor) {
            const msg = document.getElementById('status-msg');
            msg.innerText = texto;
            msg.style.color = cor;
        }

        // ===================== PRÉDIOS 3D =====================
        (function initBuildings3D() {
            const script = document.createElement('script');
            script.src = 'https://cdn.osmbuildings.org/classic/v3.0.0/OSMBuildings-Leaflet.js';
            script.onload = function() {
                try {
                    if (typeof OSMBuildings === 'undefined') return;
                    new OSMBuildings(map, { minZoom: 15, color: '#0a2e18', shadows: false });
                } catch (err) { console.warn('Erro ao carregar prédios 3D:', err); }
            };
            document.head.appendChild(script);
        })();
    </script>
</body>
</html>
"""

PYMD3 = [sys.executable, "-m", "pymobiledevice3"]
_set_lock = threading.Lock()


def _run(args, timeout):
    """Executa o pymobiledevice3 e devolve (ok, mensagem_de_erro)."""
    try:
        subprocess.run(PYMD3 + args, check=True, capture_output=True, text=True, timeout=timeout)
        return True, None
    except subprocess.TimeoutExpired:
        return False, "Tempo esgotado. O iPhone está conectado, desbloqueado e com o disco montado?"
    except subprocess.CalledProcessError as e:
        detalhe = (e.stderr or e.stdout or str(e)).strip().splitlines()
        return False, detalhe[-1] if detalhe else str(e)
    except FileNotFoundError:
        return False, "pymobiledevice3 não encontrado. Rode: pip install -r requirements.txt"


@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)


@app.route('/mount', methods=['POST'])
def mount_developer_disk():
    ok, err = _run(["mounter", "auto-mount", "--userspace"], timeout=180)
    return jsonify({"success": ok, "error": err})


@app.route('/set_location', methods=['POST'])
def set_location():
    data = request.get_json(silent=True) or {}
    try:
        lat = float(data.get('lat'))
        lng = float(data.get('lng'))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Coordenadas inválidas."}), 400
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return jsonify({"success": False, "error": "Coordenadas fora do intervalo válido."}), 400

    # Evita empilhar vários processos se o anterior ainda não terminou
    if not _set_lock.acquire(blocking=False):
        return jsonify({"success": True, "skipped": True})
    try:
        ok, err = _run(
            ["developer", "dvt", "simulate-location", "set", "--userspace", "--", str(lat), str(lng)],
            timeout=30,
        )
    finally:
        _set_lock.release()
    return jsonify({"success": ok, "error": f"O disco está montado? Detalhes: {err}" if err else None})


@app.route('/clear_location', methods=['POST'])
def clear_location():
    ok, err = _run(["developer", "dvt", "simulate-location", "clear", "--userspace"], timeout=30)
    return jsonify({"success": ok, "error": err})


if __name__ == '__main__':
    # debug=False: o modo debug do Flask expõe um console que executa código
    app.run(host='127.0.0.1', port=5000, debug=False)