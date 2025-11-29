/**
 * Simple Client-Side Password Authentication
 *
 * SECURITY NOTE: This is a simple client-side authentication mechanism suitable for
 * basic access control. The password is visible in the source code, so this should
 * only be used for non-sensitive data or as a first line of defense.
 *
 * For production use with sensitive data, implement proper server-side authentication.
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        // Password hash (SHA-256 of the actual password)
        // To generate: Use browser console: crypto.subtle.digest('SHA-256', new TextEncoder().encode('your-password')).then(h => console.log(Array.from(new Uint8Array(h)).map(b => b.toString(16).padStart(2, '0')).join('')))
        // Current password: "WoodsLabFluDashboard2025"
        passwordHash: '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', // Hash of "admin" for demo
        sessionDuration: 24 * 60 * 60 * 1000, // 24 hours in milliseconds
        storageKey: 'woodslab_auth_session'
    };

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
     * Check if current session is valid
     */
    function isSessionValid() {
        try {
            const session = localStorage.getItem(CONFIG.storageKey);
            if (!session) return false;

            const sessionData = JSON.parse(session);
            const now = new Date().getTime();

            // Check if session has expired
            if (now > sessionData.expires) {
                localStorage.removeItem(CONFIG.storageKey);
                return false;
            }

            return sessionData.authenticated === true;
        } catch (e) {
            return false;
        }
    }

    /**
     * Create a new session
     */
    function createSession() {
        const now = new Date().getTime();
        const sessionData = {
            authenticated: true,
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
                    <h2 style="margin: 0 0 1rem 0; color: #012169;">Dashboard Access</h2>
                    <p style="margin-bottom: 1.5rem; color: #666;">
                        This dashboard requires authentication. Please enter the password to continue.
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
                        Access Dashboard
                    </button>
                    <p style="margin-top: 1.5rem; font-size: 0.85rem; color: #999;">
                        Contact the lab if you need access credentials.
                    </p>
                </div>
            </div>
        `;

        // Insert modal into page
        document.body.insertAdjacentHTML('afterbegin', modalHTML);

        // Add event listeners
        const passwordInput = document.getElementById('auth-password');
        const submitButton = document.getElementById('auth-submit');
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

            if (hashedPassword === CONFIG.passwordHash) {
                // Success!
                createSession();
                document.getElementById('auth-modal').remove();
                // Allow page to load
            } else {
                // Failed
                errorDiv.textContent = 'Incorrect password. Please try again.';
                errorDiv.style.display = 'block';
                submitButton.textContent = 'Access Dashboard';
                submitButton.disabled = false;
                passwordInput.value = '';
                passwordInput.focus();
            }
        }

        // Submit on button click
        submitButton.addEventListener('click', attemptLogin);

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
     * Add logout functionality
     */
    function addLogoutButton() {
        // Find navigation
        const nav = document.querySelector('nav .nav-container');
        if (!nav) return;

        // Add logout button
        const logoutHTML = `
            <button
                id="logout-button"
                style="
                    background-color: transparent;
                    color: white;
                    border: 1px solid rgba(255,255,255,0.3);
                    padding: 0.5rem 1rem;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 0.9rem;
                    margin-left: auto;
                "
                title="Logout"
            >
                Logout
            </button>
        `;

        nav.insertAdjacentHTML('beforeend', logoutHTML);

        // Add logout handler
        document.getElementById('logout-button').addEventListener('click', function() {
            if (confirm('Are you sure you want to logout?')) {
                localStorage.removeItem(CONFIG.storageKey);
                location.reload();
            }
        });
    }

    /**
     * Initialize authentication
     */
    function init() {
        // Check if session is valid
        if (isSessionValid()) {
            // User is authenticated, add logout button
            addLogoutButton();
            return;
        }

        // User needs to login
        // Hide page content until authenticated
        document.body.style.visibility = 'hidden';

        // Show login modal when page is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                showLoginModal();
                document.body.style.visibility = 'visible';
            });
        } else {
            showLoginModal();
            document.body.style.visibility = 'visible';
        }
    }

    // Start authentication check
    init();
})();
