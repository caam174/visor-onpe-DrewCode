<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Escrutinio Centralizado - Paneles Desplegables</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <style>
        body {
            background-color: #090d16;
            color: #f1f5f9;
            font-family: ui-sans-serif, system-ui, sans-serif;
        }
        /* Remueve la flecha nativa por defecto para estandarizar el diseño */
        summary::-webkit-details-marker { display: none; }
        summary { list-style: none; }
    </style>
</head>
<body class="min-h-screen p-4 md:p-8 flex flex-col justify-between">

    <header class="w-full max-w-6xl mx-auto mb-6 border-b border-slate-800 pb-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
            <h1 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                <span>🇵🇪</span> Sistema de Fiscalización y Conteo de Actas
            </h1>
            <p class="text-xs text-slate-400 mt-0.5 uppercase tracking-wider font-mono">Estructura Modular con Componentes Colapsables</p>
        </div>
        <div class="bg-slate-900 border border-slate-700 px-3 py-1.5 rounded text-right font-mono text-xs text-cyan-400">
            Sincronización: <span id="live-clock">00:00:00</span>
        </div>
    </header>

    <main class="w-full max-w-6xl mx-auto flex flex-col gap-4 my-auto">
        
        <details open class="group bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden transition-all duration-300">
            <summary class="flex items-center justify-between p-5 bg-gradient-to-r from-slate-900 to-slate-850 cursor-pointer select-none border-b border-slate-800/50 group-open:border-amber-500/20">
                <div class="flex items-center gap-3">
                    <span class="text-amber-400">📊</span>
                    <h2 class="text-md font-bold text-slate-200 uppercase tracking-wide font-mono">
                        Monitoreo de Brecha de Actas Impugnadas
                    </h2>
                </div>
                <span class="text-xs text-slate-400 font-mono transition-transform duration-300 group-open:rotate-180">
                    ▼
                </span>
            </summary>
            
            <div class="p-6 font-mono bg-slate-950/40 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                    <span class="text-xs text-slate-400 uppercase">1. Carga Inicial Impugnada</span>
                    <div id="actas-iniciales" class="text-3xl font-bold text-white mt-2">0</div>
                </div>
                <div class="bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                    <span class="text-xs text-slate-400 uppercase">2. Resueltas por el JEE</span>
                    <div id="actas-procesadas" class="text-3xl font-bold text-emerald-400 mt-2">0</div>
                </div>
                <div class="bg-amber-950/20 p-4 rounded-xl border border-amber-500/30 shadow-inner">
                    <span class="text-xs text-amber-400 uppercase font-bold">3. Actas Pendientes (Brecha)</span>
                    <div id="actas-pendientes" class="text-3xl font-bold text-white mt-2">0</div>
                </div>
            </div>
        </details>

        <details class="group bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden transition-all duration-300">
            <summary class="flex items-center justify-between p-5 bg-gradient-to-r from-slate-900 to-slate-850 cursor-pointer select-none border-b border-slate-800/50 group-open:border-cyan-500/20">
                <div class="flex items-center gap-3">
                    <span class="text-cyan-400">⚖️</span>
                    <h2 class="text-md font-bold text-slate-200 uppercase tracking-wide font-mono">
                        Cuadrado del Acta y Consistencia de Votos
                    </h2>
                </div>
                <span class="text-xs text-slate-400 font-mono transition-transform duration-300 group-open:rotate-180">
                    ▼
                </span>
            </summary>
            
            <div class="p-6 font-mono bg-slate-950/40 grid grid-cols-1 sm:grid-cols-4 gap-4 text-center">
                <div class="bg-slate-950/80 p-3 rounded border border-slate-800">
                    <div class="text-xs text-slate-400">Votos Válidos</div>
                    <div id="votos-validos" class="text-xl font-bold text-slate-200 mt-1">0</div>
                </div>
                <div class="bg-slate-950/80 p-3 rounded border border-slate-800">
                    <div class="text-xs text-slate-400">Votos Blanco</div>
                    <div id="votos-blanco" class="text-xl font-bold text-slate-200 mt-1">0</div>
                </div>
                <div class="bg-slate-950/80 p-3 rounded border border-slate-800">
                    <div class="text-xs text-slate-400">Votos Nulos</div>
                    <div id="votos-nulos" class="text-xl font-bold text-slate-200 mt-1">0</div>
                </div>
                <div class="bg-cyan-950/20 p-3 rounded border border-cyan-500/30">
                    <div class="text-xs text-cyan-400 font-bold">Total Emitidos</div>
                    <div id="votos-totales" class="text-xl font-bold text-cyan-300 mt-1">0</div>
                </div>
            </div>
        </details>

    </main>

    <footer class="w-full max-w-6xl mx-auto text-center text-[11px] text-slate-600 font-mono mt-6 border-t border-slate-900 pt-4">
        Validación Algorítmica Basada en Ley Orgánica de Elecciones | Restricción de Integridad Cerrada.
    </footer>

    <script>
        function initClock() {
            const clockEl = document.getElementById('live-clock');
            setInterval(() => {
                const now = new Date();
                clockEl.innerText = now.toLocaleTimeString('es-PE', { hour12: false });
            }, 1000);
        }

        const DATA_STORE = {
            actasImpugnadasIniciales: 2450, 
            actasImpugnadasProcesadas: 1820,
            votosValidos: 4520300,
            votosBlanco: 120450,
            votosNulos: 340120
        };

        function renderDashboard() {
            const iniciales = DATA_STORE.actasImpugnadasIniciales;
            const procesadas = DATA_STORE.actasImpugnadasProcesadas;
            const brechaAbsoluta = iniciales - procesadas;

            document.getElementById('actas-iniciales').innerText = iniciales.toLocaleString('es-PE');
            document.getElementById('actas-procesadas').innerText = procesadas.toLocaleString('es-PE');
            document.getElementById('actas-pendientes').innerText = brechaAbsoluta.toLocaleString('es-PE');

            const totales = DATA_STORE.votosValidos + DATA_STORE.votosBlanco + DATA_STORE.votosNulos;

            document.getElementById('votos-validos').innerText = DATA_STORE.votosValidos.toLocaleString('es-PE');
            document.getElementById('votos-blanco').innerText = DATA_STORE.votosBlanco.toLocaleString('es-PE');
            document.getElementById('votos-nulos').innerText = DATA_STORE.votosNulos.toLocaleString('es-PE');
            document.getElementById('votos-totales').innerText = totales.toLocaleString('es-PE');
        }

        window.onload = () => {
            initClock();
            renderDashboard();
        };
    </script>
</body>
</html>
