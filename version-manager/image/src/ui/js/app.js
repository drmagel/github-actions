/**
 * Version Manager UI - Main Application
 * 
 * This file contains the main App component that orchestrates the UI.
 * Other components are loaded from separate files:
 * - api.js: API helper and AuthContext
 * - modals.js: Modal components (ConfirmModal, SuccessModal, FormModal, Badge)
 * - login.js: LoginPage component
 * - images.js: ImagesList and ImageVersions components
 * - domains.js: DomainsList and DomainVersions components
 */

const { useState, useEffect } = React;

// Session storage key
const SESSION_KEY = 'vm_user';

const App = () => {
    // Initialize user from sessionStorage to persist across page reloads
    const [user, setUser] = useState(() => {
        return sessionStorage.getItem(SESSION_KEY);
    });
    const [section, setSection] = useState('domains');
    const [selectedImage, setSelectedImage] = useState(null);
    const [selectedDomain, setSelectedDomain] = useState(null);
    // Refresh key to force ImagesList to reload when data changes
    const [imagesRefreshKey, setImagesRefreshKey] = useState(0);

    const handleLogin = (username) => {
        sessionStorage.setItem(SESSION_KEY, username);
        setUser(username);
    };

    const handleLogout = () => {
        sessionStorage.removeItem(SESSION_KEY);
        setUser(null);
    };

    // Called when domains are deleted to trigger images refresh
    const handleDataChange = () => {
        setImagesRefreshKey(k => k + 1);
    };

    if (!user) {
        return <LoginPage onLogin={handleLogin} />;
    }

    const renderContent = () => {
        if (section === 'images') {
            if (selectedImage) {
                return <ImageVersions key={imagesRefreshKey} imageName={selectedImage} onBack={() => setSelectedImage(null)} />;
            }
            return <ImagesList key={imagesRefreshKey} onSelectImage={setSelectedImage} />;
        }
        if (section === 'domains') {
            if (selectedDomain) {
                return <DomainVersions domainName={selectedDomain} onBack={() => setSelectedDomain(null)} onDataChange={handleDataChange} />;
            }
            return <DomainsList onSelectDomain={setSelectedDomain} onDataChange={handleDataChange} />;
        }
    };

    return (
        <AuthContext.Provider value={user}>
            <div className="app-container">
                <aside className="sidebar">
                    <div className="sidebar-header">
                        <span>🔧 Version Manager</span>
                    </div>
                    <ul className="sidebar-nav">
                        <li>
                            <a
                              href="#"
                              className={section === 'domains' ? 'active' : ''}
                              onClick={() => { setSection('domains'); setSelectedDomain(null); setSelectedImage(null); }}
                            >
                              🏷️ Domains
                            </a>
                        </li>
                        <li>
                            <a
                                href="#"
                                className={section === 'images' ? 'active' : ''}
                                onClick={() => { setSection('images'); setSelectedImage(null); setSelectedDomain(null); }}
                            >
                                📦 Images
                            </a>
                        </li>
                    </ul>
                    <div className="sidebar-footer">
                        <div className="user-info">👤 {user}</div>
                        <button className="btn btn-link" onClick={handleLogout}>Logout</button>
                    </div>
                </aside>
                <main className="main-content">
                    {renderContent()}
                </main>
            </div>
        </AuthContext.Provider>
    );
};

// Render
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
