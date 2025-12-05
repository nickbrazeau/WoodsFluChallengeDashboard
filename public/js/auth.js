/**
 * Client-Side Password Authentication with Public/Private Mode
 *
 * SECURITY NOTE: This is a simple client-side authentication mechanism suitable for
 * basic access control. The password is visible in the source code, so this should
 * only be used for non-sensitive data or as a first line of defense.
 *
 * Public mode (default): No password required, PHI-scrubbed data
 * Private mode: Password required, full data including storage locations
 *
 * For production use with sensitive data, implement proper server-side authentication.
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        // Password hash (SHA-256 of the actual password) for PRIVATE access
        // To generate: Use browser console: crypto.subtle.digest('SHA-256', new TextEncoder().encode('your-password')).then(h => console.log(Array.from(new Uint8Array(h)).map(b => b.toString(16).padStart(2, '0')).join('')))
        // Current password: "admin" (demo - change in production)
        privatePasswordHash: '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', // Hash of "admin"
        sessionDuration: 24 * 60 * 60 * 1000, // 24 hours in milliseconds
        storageKey: 'woodslab_auth_session'
    };

    /**
     * Get current access level from session
     * @returns {'public'|'private'}
     */
    function getAccessLevel() {
        try {
            const session = localStorage.getItem(CONFIG.storageKey);
            if (!session) return 'public';

            const sessionData = JSON.parse(session);
            const now = Date.now();

            // Check if session has expired
            if (now > sessionData.expires) {
                localStorage.removeItem(CONFIG.storageKey);
                return 'public';
            }

            return sessionData.accessLevel || 'public';
        } catch (e) {
            return 'public';
        }
    }

    /**
     * Hash a password using SHA-256
     */
    async function hashPassword(password) {
        const encoder = new TextEncoder();
        const data = encoder.encode(password);
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    }

    /**
     * Create a new session with specified access level
     */
    function createSession(accessLevel) {
        const now = Date.now();
        const sessionData = {
            authenticated: true,
            accessLevel: accessLevel,
            expires: now + CONFIG.sessionDuration,
            created: now
        };
        localStorage.setItem(CONFIG.storageKey, JSON.stringify(sessionData));
    }

    /**
     * Show login modal
     */
    function showLoginModal() {
        // Create modal HTML
        const modalHTML = `
            <div id="auth-modal" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.8);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <div style="
                    background-color: white;
                    padding: 2rem;
                    border-radius: 8px;
                    max-width: 400px;
                    width: 90%;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                ">
                    <h2 style="margin: 0 0 1rem 0; color: #012169;">Login for Full Access</h2>
                    <p style="margin-bottom: 1.5rem; color: #666;">
                        Enter password to access full data including storage locations.
                    </p>
                    <div style="margin-bottom: 1rem;">
                        <input
                            type="password"
                            id="auth-password"
                            placeholder="Enter password"
                            style="
                                width: 100%;
                                padding: 0.75rem;
                                border: 1px solid #ddd;
                                border-radius: 4px;
                                font-size: 1rem;
                                box-sizing: border-box;
                            "
                            autofocus
                        />
                    </div>
                    <div id="auth-error" style="
                        display: none;
                        padding: 0.75rem;
                        background-color: #fee;
                        border: 1px solid #fcc;
                        border-radius: 4px;
                        color: #c00;
                        margin-bottom: 1rem;
                        font-size: 0.9rem;
                    ">
                        Incorrect password. Please try again.
                    </div>
                    <button
                        id="auth-submit"
                        style="
                            width: 100%;
                            padding: 0.75rem;
                            background-color: #012169;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            font-size: 1rem;
                            cursor: pointer;
                            font-weight: 500;
                        "
                    >
                        Login
                    </button>
                    <button
                        id="auth-cancel"
                        style="
                            width: 100%;
                            padding: 0.75rem;
                            background-color: transparent;
                            color: #666;
                            border: 1px solid #ddd;
                            border-radius: 4px;
                            font-size: 1rem;
                            cursor: pointer;
                            font-weight: 500;
                            margin-top: 0.5rem;
                        "
                    >
                        Cancel (Return to Public View)
                    </button>
                </div>
            </div>
        `;

        // Insert modal into page
        document.body.insertAdjacentHTML('afterbegin', modalHTML);

        // Add event listeners
        const passwordInput = document.getElementById('auth-password');
        const submitButton = document.getElementById('auth-submit');
        const cancelButton = document.getElementById('auth-cancel');
        const errorDiv = document.getElementById('auth-error');

        async function attemptLogin() {
            const password = passwordInput.value;
            if (!password) {
                errorDiv.textContent = 'Please enter a password.';
                errorDiv.style.display = 'block';
                return;
            }

            // Show loading state
            submitButton.textContent = 'Verifying...';
            submitButton.disabled = true;

            // Hash and check password
            const hashedPassword = await hashPassword(password);

            if (hashedPassword === CONFIG.privatePasswordHash) {
                // Success! Switch to private mode
                createSession('private');
                document.getElementById('auth-modal').remove();
                updateNavigation();
                location.reload(); // Reload to fetch private data
            } else {
                // Failed
                errorDiv.textContent = 'Incorrect password. Please try again.';
                errorDiv.style.display = 'block';
                submitButton.textContent = 'Login';
                submitButton.disabled = false;
                passwordInput.value = '';
                passwordInput.focus();
            }
        }

        function cancelLogin() {
            document.getElementById('auth-modal').remove();
        }

        // Submit on button click
        submitButton.addEventListener('click', attemptLogin);

        // Cancel on button click
        cancelButton.addEventListener('click', cancelLogin);

        // Submit on Enter key
        passwordInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                attemptLogin();
            }
        });

        // Focus password input
        passwordInput.focus();
    }

    /**
     * Logout - clear session and switch to public mode
     */
    function logout() {
        if (confirm('Logout and return to public view?')) {
            localStorage.removeItem(CONFIG.storageKey);
            location.reload();
        }
    }

    /**
     * Update navigation based on access level
     */
    function updateNavigation() {
        const accessLevel = getAccessLevel();
        const nav = document.querySelector('nav .nav-container');
        if (!nav) return;

        // Remove existing auth elements
        const existingAuthElements = nav.querySelectorAll('.auth-element');
        existingAuthElements.forEach(el => el.remove());

        if (accessLevel === 'private') {
            // Add mode indicator badge
            const badge = document.createElement('span');
            badge.className = 'auth-element mode-badge private';
            badge.textContent = 'Private View (Full Data)';
            badge.title = 'You have full access including storage locations';
            nav.appendChild(badge);

            // Add logout button
            const logoutBtn = document.createElement('button');
            logoutBtn.className = 'auth-element btn-logout';
            logoutBtn.textContent = 'Logout';
            logoutBtn.onclick = logout;
            nav.appendChild(logoutBtn);
        } else {
            // Add login button
            const loginBtn = document.createElement('button');
            loginBtn.className = 'auth-element btn-login';
            loginBtn.textContent = 'Login for Full Access';
            loginBtn.onclick = showLoginModal;
            nav.appendChild(loginBtn);

            // Add public mode indicator
            const badge = document.createElement('span');
            badge.className = 'auth-element mode-badge public';
            badge.textContent = 'Public View';
            badge.title = 'Login for full access including storage locations';
            nav.appendChild(badge);
        }
    }

    /**
     * Initialize authentication
     */
    function init() {
        // Public mode is default - no blocking modal
        // Just update navigation to show current mode
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', updateNavigation);
        } else {
            updateNavigation();
        }
    }

    // Make getAccessLevel available globally for other scripts
    window.getAccessLevel = getAccessLevel;
    window.showLoginModal = showLoginModal;

    // Start authentication check
    init();
})();
