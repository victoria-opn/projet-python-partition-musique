(() => {
    const root = document.getElementById('dashboard');
    let socket, retry, stopped = false;
    function update(data) {
        if (data.type === 'admin.stats') {
            if (Array.isArray(data.jobs)) {
                document.getElementById('live-jobs').replaceChildren();
                [...data.jobs].reverse().forEach(update);
            }
            root.querySelectorAll('[data-stat]').forEach(node => { node.textContent = data[node.dataset.stat] ?? 'Indisponible'; });
            const list = document.getElementById('tonalites'); list.replaceChildren();
            (data.tonalites || []).forEach(entry => { const item = document.createElement('li'); item.textContent = `${entry.tonalite} : ${entry.nombre}`; list.append(item); });
        } else if (data.type === 'admin.job') {
            const body = document.getElementById('live-jobs');
            let row = Array.from(body.rows).find(row => row.dataset.job === data.job_id);
            if (!row) { row = body.insertRow(0); row.dataset.job = data.job_id; for (let i = 0; i < 5; i++) row.insertCell(); }
            [data.job_id, data.user, data.status, `${data.progress} %`, data.etape || data.error || ''].forEach((value, i) => { row.cells[i].textContent = value; });
            while (body.rows.length > 30) body.deleteRow(30);
        }
    }
    async function refresh() {
        try {
            const response = await fetch(root.dataset.statsUrl, {credentials: 'same-origin'});
            if (!response.ok || response.redirected) throw new Error();
            update(await response.json());
        } catch { document.getElementById('connection').textContent = 'Connexion interrompue, nouvelle tentative…'; }
    }
    function connect() {
        if (stopped) return;
        socket = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/admin/`);
        socket.onopen = () => { document.getElementById('connection').textContent = 'Connecté en direct'; refresh(); };
        socket.onmessage = event => { try { update(JSON.parse(event.data)); } catch { refresh(); } };
        socket.onclose = () => { if (!stopped) { refresh(); retry = setTimeout(connect, 2000); } };
        socket.onerror = () => socket.close();
    }
    const poll = setInterval(refresh, 10000); connect();
    window.addEventListener('pagehide', () => { stopped = true; clearTimeout(retry); clearInterval(poll); socket?.close(); });
})();
