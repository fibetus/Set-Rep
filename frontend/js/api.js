const API_BASE = '/api/v1';

function getToken() {
    return localStorage.getItem('access');
}

function setToken(token, refresh) {
    localStorage.setItem('access', token);
    localStorage.setItem('refresh', refresh);
}

function clearToken() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
}

async function apiRequest(url, method='GET', data=null, auth=true) {
    let headers = { 'Content-Type': 'application/json' };
    if (auth && getToken()) headers['Authorization'] = 'Bearer ' + getToken();
    let opts = { method, headers };
    if (data) opts.body = JSON.stringify(data);

    let resp = await fetch(API_BASE + url, opts);
    if (resp.status === 401 && auth && localStorage.getItem('refresh')) {
        // Try refresh
        let refreshResp = await fetch(API_BASE + '/auth/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: localStorage.getItem('refresh') })
        });
        if (refreshResp.ok) {
            let tokens = await refreshResp.json();
            setToken(tokens.access, localStorage.getItem('refresh'));
            return apiRequest(url, method, data, auth); // retry
        } else {
            clearToken();
            window.location = 'login.html';
            return;
        }
    }
    return resp;
} 