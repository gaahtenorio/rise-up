async function getAgencias(filtro = '', uf = '') {
    try {
        const params = new URLSearchParams();
        if (filtro) params.append('q', filtro);
        if (uf)     params.append('uf', uf);

        const url = '/api/agencias' + (params.toString() ? '?' + params.toString() : '');
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Erro ao carregar agências: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Erro na API:', error);
        return [];
    }
}

function formatAddress(agencia) {
    const partes = [
        agencia.logradouro,
        agencia.numero,
        agencia.bairro ? `- ${agencia.bairro}` : '',
        agencia.municipio,
        agencia.uf ? `- ${agencia.uf}` : ''
    ].filter(Boolean);
    return partes.join(', ');
}
