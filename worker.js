// Cloudflare Worker entry point
export default {
    async fetch(request, env) {
        const url = new URL(request.url);
        const path = url.pathname.slice(1);

        // --- Simple Cookie Auth ---
        const getCookie = (name) => {
            const match = request.headers.get('Cookie')?.match(new RegExp('(^| )' + name + '=([^;]+)'));
            return match ? match[2] : null;
        };

        // --- Handle Logout ---
        if (url.pathname === '/logout') {
            return new Response('', {
                status: 302,
                headers: {
                    'Set-Cookie': 'kss_auth=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly; SameSite=Lax',
                    'Location': '/login',
                    'Cache-Control': 'no-store'
                }
            });
        }

        // --- Serve Login Page ---
        const serveLogin = (error = '') => {
            return new Response(`
        <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="UTF-8">
            <title>KSS Login</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="icon" href="https://lifaet.github.io/assets/images/favicon.ico" type="image/x-icon">
            <style>
                body {
                    background-image: url('https://i.pinimg.com/originals/21/7d/a2/217da299cc918fad9b76eb99e4bb75b3.gif') !important;
                    font-family: monospace;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                }

                .login-box {
                    padding: 2em 2.5em;
                    border-radius: 10px;
                    box-shadow: 0 2px 16px #0002;
                    flex-direction: column;
                    align-items: center;
                }

                h2 {
                    color: #1976d2;
                    margin-bottom: 1em;
                    text-align: center;
                    width: 100%;
                }

                input {
                    font-family: inherit;
                    padding: 0.5em;
                    margin-bottom: 1em;
                    width: 100%;
                    border: 1px solid #ffffffdf;
                    border-radius: 6px;
                }

                button {
                    background: #1976d2;
                    color: #ffffffdf;
                    border: none;
                    border-radius: 6px;
                    padding: 0.5em 2em;
                    font-size: 1em;
                    font-weight: 600;
                    cursor: pointer;
                    margin: 0 auto;
                    display: block;
                }

                .error {
                    color: #d32f2f;
                    margin-bottom: 1em;
                    text-align: center;
                    width: 100%;
                }
            </style>
        </head>

        <body>
            <form class="login-box" method="POST" action="/login">
                <h2>KSS Login</h2>
                ${error ? `<div class="error">${error}</div>` : ''}
                <input type="text" name="username" placeholder="Username" autocomplete="username" required>
                <input type="password" name="password" placeholder="Password" autocomplete="current-password" required>
                <button type="submit">Login</button>
            </form>
        </body>

        </html>
            `, {
                headers: {
                    'Content-Type': 'text/html',
                    'Cache-Control': 'no-store'
                }
            });
        };

        // --- Handle Login POST ---
        if (url.pathname === '/login' && request.method === 'POST') {
            const form = await request.formData();
            const username = form.get('username');
            const password = form.get('password');
            if (username === 'admin' && password === 'admin') {
                return new Response('', {
                    status: 302,
                    headers: {
                        'Set-Cookie': 'kss_auth=1; Path=/; HttpOnly; SameSite=Lax',
                        'Location': '/',
                    }
                });
            } else {
                return serveLogin('Invalid username or password');
            }
        }

        // --- If not authenticated, show login page ---
        if (getCookie('kss_auth') !== '1') {
            if (url.pathname === '/login') {
                return serveLogin();
            }
            // If not on /login, redirect to login page
            return new Response('', {
                status: 302,
                headers: { 'Location': '/login' }
            });
        }

        // --- Handle API Endpoints ---
        if (path.startsWith('list')) {
            const prefix = url.searchParams.get('prefix') || '';
            try {
                const listed = await env.MY_BUCKET.list({
                    prefix: prefix,
                    delimiter: '/'
                });
                const objects = listed.objects.filter(obj => obj.key !== prefix);
                return new Response(JSON.stringify({
                    objects: objects,
                    folders: listed.delimitedPrefixes
                }), {
                    headers: { 'Content-Type': 'application/json' },
                });
            } catch (e) {
                console.error("Error listing R2 bucket:", e);
                return new Response('Error listing files', { status: 500 });
            }
        } else if (path.startsWith('view-text')) {
            const fileKey = url.searchParams.get('key');
            if (!fileKey) {
                return new Response('Missing file key', { status: 400 });
            }
            try {
                const object = await env.MY_BUCKET.get(fileKey);
                if (object === null) {
                    return new Response('File not found', { status: 404 });
                }
                const contentType = object.httpMetadata?.contentType || 'application/octet-stream';
                if (!contentType.startsWith('text/') && !contentType.includes('json') && !contentType.includes('xml')) {
                    return new Response('Not a viewable text file type', { status: 415 });
                }
                const textContent = await object.text();
                return new Response(textContent, {
                    headers: { 'Content-Type': contentType },
                });
            } catch (e) {
                console.error(`Error fetching text content for ${fileKey}:`, e);
                return new Response('Error fetching file content', { status: 500 });
            }
        } else if (path.startsWith('delete')) {
            const key = url.searchParams.get('key');
            if (!key) {
                return new Response('Missing key', { status: 400 });
            }
            try {
                if (key.endsWith('/')) {
                    const listed = await env.MY_BUCKET.list({ prefix: key });
                    for (const obj of listed.objects) {
                        await env.MY_BUCKET.delete(obj.key);
                    }
                } else {
                    await env.MY_BUCKET.delete(key);
                }
                return new Response('Deleted', { status: 200 });
            } catch (e) {
                console.error("Error deleting object(s):", e);
                return new Response('Error deleting object(s)', { status: 500 });
            }
        }

        // --- Serve HTML Page with JavaScript for File Index ---
        const serveHtml = () => {
            const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>KSS File Manager</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="https://lifaet.github.io/assets/images/favicon.ico" type="image/x-icon">
    <style>
        :root {
            --bg-main: #f5f7fa;
            --bg-panel: #fff;
            --border: #e3e8ee;
            --text-main: #23272a;
            --text-muted: #6c757d;
            --accent: #1976d2;
            --accent-hover: #1251a3;
            --danger-bg: #ffeaea;
            --danger: #d32f2f;
            --danger-hover: #b71c1c;
            --table-row-hover: #f0f4fa;
            --btn-bg: #e3e8ee;
            --btn-bg-hover: #1976d2;
        }
        body {
            font-family: 'Fira Mono', 'Consolas', 'Menlo', 'Monaco', monospace;
            margin: 2em;
            background: var(--bg-main);
            color: var(--text-main);
        }
        .slide-up { 
            opacity: 0; 
            transform: translateY(8px); 
            animation: slideUp 0.18s cubic-bezier(.4,2,.6,1) forwards; 
        }
        @keyframes slideUp {
            to { opacity: 1; transform: none; }
        }
        .slide-heading {
            opacity: 0;
            transform: translateX(-10px);
            animation: slideHeading 0.18s cubic-bezier(.4,2,.6,1) forwards;
        }
        @keyframes slideHeading {
            to { opacity: 1; transform: none; }
        }
        h1 { 
            font-size: 2.2em; 
            margin-bottom: 0.2em; 
            font-weight: 800; 
            letter-spacing: -1px;
            color: var(--accent);
            text-align: center;
        }
        h2 {
            font-size: 1.1em;
            color: var(--text-muted);
            font-weight: 500;
            margin: 0.5em 0 1.2em 0;
            text-align: center;
        }
        .breadcrumb-nav { margin-bottom: 1em; }
        .breadcrumb-nav a { 
            color: var(--accent); 
            text-decoration: none; 
            margin-right: 0.2em; 
            font-weight: 600;
        }
        .breadcrumb-nav a:hover { 
            color: var(--accent-hover);
            text-decoration: underline;
        }
        .back-btn {
            display: inline-flex;
            align-items: center;
            gap: 0.5em;
            margin-bottom: 1em;
            background: var(--accent);
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 0.4em 1.4em;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 1px 4px #0002;
            transition: background 0.18s, color 0.18s;
        }
        .back-btn:hover {
            background: var(--accent-hover);
            color: #fff;
        }
        .back-btn svg {
            width: 1.1em;
            height: 1.1em;
            vertical-align: middle;
            fill: currentColor;
        }
        .message { margin: 1em 0; color: #b58900; }
        .table-container {
            background: var(--bg-panel);
            border-radius: 14px;
            box-shadow: 0 2px 16px #0002;
            overflow-x: auto;
            padding: 0.5em 0.5em 0.5em 0.5em;
            border: 1px solid var(--border);
        }
        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            background: transparent;
        }
        th, td {
            padding: 1.1em 1em;
            text-align: left;
        }
        th {
            background: var(--bg-panel);
            color: var(--accent);
            font-weight: 700;
            font-size: 1.08rem;
            border-bottom: 2px solid var(--border);
            text-align: center;
        }
        td {
            font-size: 1.04rem;
            border-bottom: 1px solid var(--border);
            vertical-align: middle;
        }
        td:not(:first-child) {
            text-align: center;
        }
        td:first-child {
            text-align: left;
        }
        tr {
            background: var(--bg-panel);
            transition: background 0.13s;
        }
        tr:hover {
            background: var(--table-row-hover);
        }
        tr:last-child td {
            border-bottom: none;
        }
        .actions {
            display: flex;
            gap: 0.5em;
            align-items: center;
            justify-content: center;
        }
        .btn, button {
            font-family: inherit;
            font-size: 1em;
            border: none;
            outline: none;
            border-radius: 6px;
            padding: 0.38em 1.3em;
            cursor: pointer;
            background: var(--btn-bg);
            color: var(--accent);
            font-weight: 500;
            box-shadow: 0 1px 2px #0002;
            position: relative;
            overflow: hidden;
            transition: background 0.18s, color 0.18s;
            letter-spacing: 0.5px;
        }
        .btn:hover, button:hover {
            background: var(--btn-bg-hover);
            color: #fff;
        }
        .danger {
            background: var(--danger-bg);
            color: var(--danger);
        }
        .danger:hover {
            background: var(--danger-hover);
            color: #fff;
        }
        a.btn {
            text-decoration: none;
            display: inline-block;
        }
        a.item-link {
            color: var(--text-main);
            font-weight: 700;
            text-decoration: none;
            background: none;
            border-bottom: none;
            transition: color 0.18s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        a.item-link:hover {
            color: var(--accent);
            text-decoration: underline;
        }
        #text-viewer-modal { display: none; position: fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(245,247,250,0.92); align-items: center; justify-content: center; z-index: 1000; }
        #text-viewer-modal .modal-content { background: var(--bg-panel); color: var(--text-main); padding: 1em; border-radius: 10px; max-width: 700px; width: 95vw; max-height: 80vh; overflow-y: auto; box-shadow: 0 2px 16px #0002;}
        #text-viewer-modal .modal-header { display: flex; justify-content: space-between; align-items: center; }
        #text-viewer-modal .modal-close-button { background: none; border: none; font-size: 1.3em; cursor: pointer; color: #888; }
        #text-viewer-modal .modal-close-button:hover { color: var(--danger); }
        pre { background: #f5f7fa; color: var(--text-main); padding: 0.7em; border-radius: 6px; overflow-x: auto; }
        @media (max-width: 600px) {
            .table-container { padding: 0.2em; }
            th, td { padding: 0.5em 0.4em; }
            #text-viewer-modal .modal-content { padding: 0.7em; }
        }
        .logout-btn {
            position: fixed;
            top: 1.5em;
            right: 2em;
            z-index: 1001;
            background: #d32f2f;
            color: #fff;
            border: none;
            border-radius: 6px;
            padding: 0.4em 1.4em;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 1px 4px #0002;
            transition: background 0.18s, color 0.18s;
        }
        .logout-btn:hover {
            background: #b71c1c;
        }
    </style>
</head>
<body>
    <button id="logout-btn" class="logout-btn">Log Out</button>
    <div class="slide-up">
        <h1 class="slide-heading">KSS File Manager</h1>
        <h2>Browse, preview, download, and manage KSS files and folders in the cloud.</h2>
        <nav id="breadcrumb-nav" class="breadcrumb-nav"></nav>
        <button id="back-btn" class="back-btn" style="display:none;">
            <svg viewBox="0 0 24 24"><path d="M15.41 7.41 14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
            Back
        </button>
        <div id="messages" class="message"></div>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Size</th>
                        <th>Last Modified</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="file-list-body"></tbody>
            </table>
        </div>
    </div>
    <div id="text-viewer-modal">
        <div class="modal-content">
            <div class="modal-header">
                <span id="modal-file-name"></span>
                <button id="modal-close-button" class="modal-close-button">&times;</button>
            </div>
            <pre id="modal-text-content"></pre>
        </div>
    </div>
    <script type="module">
        let currentPrefix = '';
        const messagesDiv = document.getElementById('messages');
        const fileListBody = document.getElementById('file-list-body');
        const breadcrumbNav = document.getElementById('breadcrumb-nav');
        const textViewerModal = document.getElementById('text-viewer-modal');
        const modalFileName = document.getElementById('modal-file-name');
        const modalTextContent = document.getElementById('modal-text-content');
        const modalCloseButton = document.getElementById('modal-close-button');
        const backBtn = document.getElementById('back-btn');

        const formatBytes = (bytes, decimals = 2) => {
            if (bytes === 0) return '0 Bytes';
            const k = 1024, dm = decimals < 0 ? 0 : decimals;
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
        };

        const displayMessage = (msg, type = 'info') => {
            messagesDiv.textContent = msg;
            messagesDiv.style.display = '';
            messagesDiv.style.color = type === 'error' ? '#d32f2f' : '#b58900';
        };
        const hideMessage = () => { messagesDiv.textContent = ''; messagesDiv.style.display = 'none'; };

        const isTextFile = (fileName) => {
            const textExtensions = ['.txt', '.md', '.json', '.js', '.csv', '.log'];
            const ext = ('.' + fileName.split('.').pop()).toLowerCase();
            return textExtensions.includes(ext);
        };

        const showTextViewer = async (fileKey, fileName) => {
            modalFileName.textContent = fileName.toUpperCase();
            modalTextContent.textContent = 'Loading...';
            textViewerModal.style.display = 'flex';
            try {
                const response = await fetch(\`/view-text?key=\${encodeURIComponent(fileKey)}\`);
                if (!response.ok) throw new Error(await response.text());
                modalTextContent.textContent = await response.text();
            } catch (e) {
                modalTextContent.textContent = \`Could not load file content. Error: \${e.message}\`;
            }
        };
        const hideTextViewer = () => {
            textViewerModal.style.display = 'none';
            modalTextContent.textContent = '';
            modalFileName.textContent = '';
        };

        const confirmDelete = async (key, isFolder = false) => {
            if (!confirm(\`Are you sure you want to delete \${isFolder ? "folder" : "file"} "\${key}"?\`)) return;
            displayMessage('Deleting...');
            try {
                const response = await fetch(\`/delete?key=\${encodeURIComponent(key)}\`, { method: 'POST' });
                if (!response.ok) throw new Error(await response.text());
                displayMessage('Deleted successfully.');
                fetchFiles();
            } catch (e) {
                displayMessage('Delete failed: ' + e.message, 'error');
            }
        };

        // Update the URL and fetch files for folder navigation
        const navigateToFolder = (prefix) => {
            currentPrefix = prefix;
            const url = prefix ? '/' + prefix : '/';
            window.history.pushState({prefix}, '', url);
            fetchFiles();
        };

        const renderBreadcrumbs = () => {
            breadcrumbNav.innerHTML = '';
            const segments = currentPrefix.split('/').filter(s => s !== '');
            const homeLink = document.createElement('a');
            homeLink.href = '#'; homeLink.textContent = 'Home';
            homeLink.onclick = (e) => { e.preventDefault(); navigateToFolder(''); };
            breadcrumbNav.appendChild(homeLink);
            let cumulativePrefix = '';
            segments.forEach((segment, index) => {
                cumulativePrefix += segment + '/';
                const span = document.createElement('span');
                span.textContent = ' / ';
                breadcrumbNav.appendChild(span);
                const segmentLink = document.createElement('a');
                segmentLink.href = '#'; segmentLink.textContent = segment.toUpperCase();
                segmentLink.onclick = (e) => { e.preventDefault(); navigateToFolder(cumulativePrefix); };
                breadcrumbNav.appendChild(segmentLink);
            });
        };

        const updateBackButton = () => {
            if (!currentPrefix || currentPrefix === '') {
                backBtn.style.display = 'none';
            } else {
                backBtn.style.display = '';
            }
        };

        const fetchFiles = async () => {
            displayMessage('Loading files...');
            renderBreadcrumbs();
            updateBackButton();
            try {
                const response = await fetch(\`/list?prefix=\${encodeURIComponent(currentPrefix)}\`);
                if (!response.ok) throw new Error(\`HTTP error! status: \${response.status}\`);
                const data = await response.json();
                fileListBody.innerHTML = '';
                // Folders
                data.folders.forEach(folderPrefix => {
                    const folderName = folderPrefix.replace(currentPrefix, '').replace('/', '');
                    const row = document.createElement('tr');
                    row.innerHTML = \`
                        <td><a href="/\${folderPrefix}" class="item-link" data-prefix="\${folderPrefix}">\${folderName.toUpperCase()}</a></td>
                        <td>FOLDER</td><td></td><td></td>
                        <td class="actions">
                            <button class="btn danger" data-key="\${folderPrefix}" data-type="folder">Delete</button>
                        </td>
                    \`;
                    fileListBody.appendChild(row);
                });
                // Files
                data.objects.forEach(file => {
                    const fileName = file.key.replace(currentPrefix, '');
                    const isText = isTextFile(fileName);
                    const row = document.createElement('tr');
                    row.innerHTML = \`
                        <td><a href="/\${file.key}" class="item-link" data-key="\${file.key}" data-type="file">\${fileName.toUpperCase()}</a></td>
                        <td>FILE</td>
                        <td>\${formatBytes(file.size)}</td>
                        <td>\${new Date(file.uploaded).toLocaleString()}</td>
                        <td class="actions">
                            \${isText ? \`<button class="btn" data-key="\${file.key}" data-name="\${fileName}" data-action="view">View</button>\` : ''}
                            <a href="/\${file.key}" target="_blank" rel="noopener noreferrer" class="btn">Download</a>
                            <button class="btn danger" data-key="\${file.key}" data-type="file">Delete</button>
                        </td>
                    \`;
                    fileListBody.appendChild(row);
                });
                // Attach event listeners
                fileListBody.querySelectorAll('a.item-link[data-prefix]').forEach(link => {
                    link.onclick = (e) => {
                        e.preventDefault();
                        navigateToFolder(link.dataset.prefix);
                    };
                });
                fileListBody.querySelectorAll('a.item-link[data-type="file"]').forEach(link => {
                    link.onclick = (e) => {
                        e.preventDefault();
                        // Update URL and show file content
                        window.history.pushState({file: link.dataset.key}, '', '/' + link.dataset.key);
                        showTextViewer(link.dataset.key, link.textContent);
                    };
                });
                fileListBody.querySelectorAll('button[data-action="view"]').forEach(button => {
                    button.onclick = (e) => {
                        e.preventDefault();
                        window.history.pushState({file: button.dataset.key}, '', '/' + button.dataset.key);
                        showTextViewer(button.dataset.key, button.dataset.name);
                    };
                });
                fileListBody.querySelectorAll('button.danger').forEach(button => {
                    button.onclick = (e) => {
                        e.preventDefault();
                        const key = button.dataset.key;
                        const isFolder = button.dataset.type === 'folder';
                        confirmDelete(key, isFolder);
                    };
                });
                hideMessage();
            } catch (e) {
                displayMessage('Failed to load files. ' + e.message, 'error');
            }
        };

        backBtn.onclick = () => {
            if (!currentPrefix) return;
            const parts = currentPrefix.split('/').filter(Boolean);
            if (parts.length > 0) {
                parts.pop();
                currentPrefix = parts.length > 0 ? parts.join('/') + '/' : '';
                window.history.pushState({prefix: currentPrefix}, '', currentPrefix ? '/' + currentPrefix : '/');
                fetchFiles();
            }
        };

        modalCloseButton.onclick = hideTextViewer;
        textViewerModal.onclick = (e) => { if (e.target === textViewerModal) hideTextViewer(); };

        document.getElementById('logout-btn').onclick = () => {
            window.location.href = "/logout";
        };

        // Handle browser navigation (back/forward)
        window.onpopstate = (event) => {
            const state = event.state || {};
            if (state.prefix !== undefined) {
                currentPrefix = state.prefix;
                fetchFiles();
                hideTextViewer();
            } else if (state.file) {
                showTextViewer(state.file, state.file.split('/').pop());
            } else {
                // On direct navigation, parse URL
                const pathFromUrl = decodeURIComponent(window.location.pathname.slice(1));
                if (!pathFromUrl || pathFromUrl.endsWith('/')) {
                    currentPrefix = pathFromUrl;
                    fetchFiles();
                    hideTextViewer();
                } else {
                    showTextViewer(pathFromUrl, pathFromUrl.split('/').pop());
                }
            }
        };

        // On page load, parse the URL to set the initial folder or file
        window.onload = () => {
            const pathFromUrl = decodeURIComponent(window.location.pathname.slice(1));
            if (!pathFromUrl || pathFromUrl.endsWith('/')) {
                currentPrefix = pathFromUrl;
                fetchFiles();
            } else {
                showTextViewer(pathFromUrl, pathFromUrl.split('/').pop());
            }

            // Attach logout handler after DOM is loaded
            document.getElementById('logout-btn').onclick = () => {
                window.location.href = "/logout";
            };
        };
    </script>
</body>
</html>
            `;
            return new Response(htmlContent, {
                headers: { 'Content-Type': 'text/html' },
            });
        };

        if (path === '' || path === 'index.html') {
            return serveHtml();
        }

        // --- Folder navigation: If path is a folder prefix, serve HTML index ---
        if (path && !path.startsWith('list') && !path.startsWith('view-text') && !path.startsWith('delete')) {
            let folderPrefix = path.endsWith('/') ? path : path + '/';
            const listed = await env.MY_BUCKET.list({ prefix: folderPrefix, limit: 1 });
            if (listed.objects.length > 0 || listed.delimitedPrefixes.length > 0) {
                return serveHtml();
            }
        }

        // --- Serve Individual Files from R2 ---
        try {
            const object = await env.MY_BUCKET.get(path);

            if (object === null) {
                return new Response('Object Not Found', { status: 404 });
            }

            const headers = new Headers();
            object.writeHttpMetadata(headers);
            headers.set('ETag', object.httpEtag);

            return new Response(object.body, {
                headers,
            });
        } catch (e) {
            console.error(`Error fetching object ${path} from R2:`, e);
            return new Response('Error fetching object', { status: 500 });
        }
    },
};