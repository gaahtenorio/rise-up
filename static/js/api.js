/**
 * Busca agências no endpoint interno do servidor.
 * @param {string} filtro - Texto livre (nome, prefixo ou cidade)
 * @param {string} uf     - Sigla do estado (ex: "PE")
 * @returns {Promise<Array>}
 */
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

/**
 * Formata o endereço completo de uma agência.
 * @param {Object} agencia
 * @returns {string}
 */
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
