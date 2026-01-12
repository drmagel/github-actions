/**
 * Version Manager UI - Images Section
 */

const { useState, useEffect } = React;

// Images List
const ImagesList = ({ onSelectImage }) => {
    const [images, setImages] = useState([]);
    const [filter, setFilter] = useState('');
    const [showCreate, setShowCreate] = useState(false);
    const [showEdit, setShowEdit] = useState(null);
    const [showDelete, setShowDelete] = useState(null);
    const [showSuccess, setShowSuccess] = useState(false);
    const [domains, setDomains] = useState([]);
    const [newImage, setNewImage] = useState({ name: '', domain: '' });
    const [newDomainName, setNewDomainName] = useState('');
    const [showNewDomain, setShowNewDomain] = useState(false);
    const [existingImageDomain, setExistingImageDomain] = useState(null);
    const [showNewDomainInEdit, setShowNewDomainInEdit] = useState(false);
    const [newDomainNameInEdit, setNewDomainNameInEdit] = useState('');

    useEffect(() => {
        loadImages();
        loadDomains();
    }, []);

    const loadImages = async () => {
        try {
            // Get image-domain mappings
            const imageData = await api.get('/images/list');
            
            // Get all image versions
            const versionsData = await api.get('/images/list/versions');
            
            // Group versions by image name
            const versionsByImage = {};
            versionsData.forEach(v => {
                if (!versionsByImage[v.name]) {
                    versionsByImage[v.name] = [];
                }
                versionsByImage[v.name].push(v);
            });
            
            // Map to expected structure with versions
            const images = imageData.map(img => ({
                name: img.image,
                domain: img.domain,
                versions: versionsByImage[img.image] || []
            }));
            
            setImages(images);
        } catch (err) {
            console.error('Error loading images:', err);
        }
    };

    const loadDomains = async () => {
        try {
            const data = await api.get('/domains/list');
            const uniqueDomains = [...new Set(data.map(d => d.name))];
            setDomains(uniqueDomains);
        } catch (err) {
            console.error('Error loading domains:', err);
        }
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            let domainToUse = existingImageDomain ? '' : newImage.domain;
            
            // If creating a new domain, create it first
            if (showNewDomain && newDomainName) {
                const now = new Date();
                const year = now.getFullYear();
                const month = String(now.getMonth() + 1).padStart(2, '0');
                const day = String(now.getDate()).padStart(2, '0');
                const hours = String(now.getHours()).padStart(2, '0');
                const minutes = String(now.getMinutes()).padStart(2, '0');
                const seconds = String(now.getSeconds()).padStart(2, '0');
                const domainVersion = `${year}-${month}-${day}-${hours}-${minutes}-${seconds}`;
                
                await api.post(`/domains/${newDomainName}/create`, {
                    version: domainVersion
                });
                domainToUse = newDomainName;
            }
            
            // Create the ImageDomain entry (relationship between image and domain)
            await api.post('/images/create', {
                name: newImage.name,
                domain: domainToUse
            });
            
            // Reset all states
            setShowCreate(false);
            setNewImage({ name: '', domain: '' });
            setNewDomainName('');
            setShowNewDomain(false);
            setExistingImageDomain(null);
            setShowSuccess(true);
            
            // Refresh both lists (this will update the image if versions exist)
            loadImages();
            loadDomains();
        } catch (err) {
            alert('Error creating image: ' + err.message);
        }
    };

    const handleEdit = async (e) => {
        e.preventDefault();
        try {
            if (showEdit.newName !== showEdit.name) {
                await api.put(`/images/${showEdit.name}/rename`, {name: showEdit.newName});
            }
            if (showEdit.newDomain !== showEdit.domain) {
                await api.put(`/images/${showEdit.newName || showEdit.name}/domain`, {domain: showEdit.newDomain});
            }
            setShowEdit(null);
            setShowSuccess(true);
            loadImages();
        } catch (err) {
            alert('Error updating image: ' + err.message);
        }
    };

    const handleDelete = async () => {
        try {
            await api.delete(`/images/${showDelete.name}`);
            setShowDelete(null);
            setShowSuccess(true);
            loadImages();
        } catch (err) {
            alert('Error deleting image: ' + err.message);
        }
    };

    const handleNameInput = (value) => {
        const sanitized = value.toLowerCase().replace(/[^a-z0-9_-]/g, '');
        setNewImage({ ...newImage, name: sanitized });
        
        // Check if image with this name already exists
        const existing = images.find(img => img.name === sanitized);
        if (existing) {
            setExistingImageDomain(existing.domain);
        } else {
            setExistingImageDomain(null);
        }
    };

    const filteredImages = images.filter(img => 
        img.name.toLowerCase().includes(filter.toLowerCase())
    );

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">📦 Images</h1>
                <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Add Image</button>
            </div>
            
            <div className="filter-bar">
                <input
                    type="text"
                    className="form-input filter-input"
                    placeholder="Filter images..."
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                />
            </div>

            <div className="card">
                <table className="table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Domain</th>
                            <th>Versions</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredImages.length === 0 ? (
                            <tr><td colSpan="4" className="text-center">No images found</td></tr>
                        ) : filteredImages.map(img => (
                            <tr key={img.name}>
                                <td>
                                    <a href="#" className="link" onClick={() => onSelectImage(img.name)}>
                                        {img.name}
                                    </a>
                                </td>
                                <td>{img.domain}</td>
                                <td>{img.versions.length}</td>
                                <td>
                                    <button className="btn btn-icon" title="Edit" onClick={() => setShowEdit({ ...img, newName: img.name, newDomain: img.domain })}>✏️</button>
                                    <button className="btn btn-icon" title="Delete" onClick={() => setShowDelete(img)}>🗑️</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Create Modal */}
            <FormModal isOpen={showCreate} title="Create New Image" onClose={() => { setShowCreate(false); setExistingImageDomain(null); setShowNewDomain(false); setNewDomainName(''); }} onSubmit={handleCreate}>
                <div className="form-group">
                    <label className="form-label">Name</label>
                    <input
                        type="text"
                        className="form-input"
                        value={newImage.name}
                        onChange={(e) => handleNameInput(e.target.value)}
                        placeholder="my-image-name"
                        required
                    />
                    <small className="form-hint">Allowed: a-z, 0-9, _, -</small>
                    {existingImageDomain && (
                        <small className="form-hint text-info">
                            ℹ️ Image exists - new version will use domain: <strong>{existingImageDomain}</strong>
                        </small>
                    )}
                </div>
                <div className="form-group">
                    <label className="form-label">
                        Domain {existingImageDomain && <span className="text-muted">(optional - will inherit from existing)</span>}
                    </label>
                    {existingImageDomain ? (
                        <div className="form-input disabled" style={{backgroundColor: '#f5f5f5', cursor: 'not-allowed'}}>
                            {existingImageDomain}
                        </div>
                    ) : !showNewDomain ? (
                        <>
                            <select
                                className="form-select"
                                value={newImage.domain}
                                onChange={(e) => setNewImage({ ...newImage, domain: e.target.value })}
                                required
                            >
                                <option value="">Select domain...</option>
                                {domains.map(d => <option key={d} value={d}>{d}</option>)}
                            </select>
                            <button type="button" className="btn btn-link" onClick={() => setShowNewDomain(true)}>
                                + Create new domain
                            </button>
                        </>
                    ) : (
                        <>
                            <input
                                type="text"
                                className="form-input"
                                value={newDomainName}
                                onChange={(e) => {
                                    setNewDomainName(e.target.value);
                                    setNewImage({ ...newImage, domain: e.target.value });
                                }}
                                placeholder="new-domain-name"
                                required
                            />
                            <button type="button" className="btn btn-link" onClick={() => setShowNewDomain(false)}>
                                Select existing domain
                            </button>
                        </>
                    )}
                </div>
            </FormModal>

            {/* Edit Modal */}
            <FormModal isOpen={!!showEdit} title="Edit Image" onClose={() => { setShowEdit(null); setShowNewDomainInEdit(false); setNewDomainNameInEdit(''); }} onSubmit={handleEdit}>
                {showEdit && (
                    <>
                        <div className="form-group">
                            <label className="form-label">Name</label>
                            <input
                                type="text"
                                className="form-input"
                                value={showEdit.newName}
                                onChange={(e) => setShowEdit({ ...showEdit, newName: e.target.value.toLowerCase().replace(/[^a-z0-9_-]/g, '') })}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Domain</label>
                            {!showNewDomainInEdit ? (
                                <>
                                    <select
                                        className="form-select"
                                        value={showEdit.newDomain}
                                        onChange={(e) => setShowEdit({ ...showEdit, newDomain: e.target.value })}
                                        required
                                    >
                                        <option value="">Select domain...</option>
                                        {domains.map(d => <option key={d} value={d}>{d}</option>)}
                                    </select>
                                    <button type="button" className="btn btn-link" onClick={() => setShowNewDomainInEdit(true)}>
                                        + Create new domain
                                    </button>
                                </>
                            ) : (
                                <>
                                    <input
                                        type="text"
                                        className="form-input"
                                        value={newDomainNameInEdit}
                                        onChange={(e) => {
                                            const sanitized = e.target.value.toLowerCase().replace(/[^a-z0-9_-]/g, '');
                                            setNewDomainNameInEdit(sanitized);
                                            setShowEdit({ ...showEdit, newDomain: sanitized });
                                        }}
                                        placeholder="new-domain-name"
                                        required
                                    />
                                    <button type="button" className="btn btn-link" onClick={() => {
                                        setShowNewDomainInEdit(false);
                                        setNewDomainNameInEdit('');
                                        setShowEdit({ ...showEdit, newDomain: showEdit.domain });
                                    }}>
                                        Select existing domain
                                    </button>
                                </>
                            )}
                        </div>
                    </>
                )}
            </FormModal>

            {/* Delete Confirmation */}
            <ConfirmModal
                isOpen={!!showDelete}
                title="Delete Image"
                message={`Do you want to delete image "${showDelete?.name}"?`}
                onConfirm={handleDelete}
                onCancel={() => setShowDelete(null)}
            />

            {/* Success Modal */}
            <SuccessModal isOpen={showSuccess} message="Operation completed successfully!" onClose={() => setShowSuccess(false)} />
        </div>
    );
};

// Image Versions View
const ImageVersions = ({ imageName, onBack }) => {
    const [versions, setVersions] = useState([]);
    const [filter, setFilter] = useState('');
    const [testedFilter, setTestedFilter] = useState('all');
    const [showSuccess, setShowSuccess] = useState(false);

    useEffect(() => {
        loadVersions();
    }, [imageName]);

    const loadVersions = async () => {
        try {
            const data = await api.get(`/images/${imageName}/list`);
            setVersions(data);
        } catch (err) {
            console.error('Error loading versions:', err);
        }
    };

    const handleToggleTested = async (imageVersion, currentTested) => {
        try {
            const newTested = !currentTested;
            await api.put(`/images/${imageName}/tested`, {
                version: imageVersion,
                tested: newTested
            });
            
            // Optimistically update local state
            const updatedVersions = versions.map(v => 
                v.version === imageVersion
                    ? { ...v, tested: newTested }
                    : v
            );
            setVersions(updatedVersions);
            
            setShowSuccess(true);
        } catch (err) {
            alert('Error updating tested status: ' + err.message);
        }
    };

    const filteredVersions = versions.filter(v => {
        // Filter by version string
        if (filter && !v.version.includes(filter)) return false;
        // Filter by tested status
        if (testedFilter === 'tested' && !v.tested) return false;
        if (testedFilter === 'untested' && v.tested) return false;
        return true;
    });

    return (
        <div>
            <div className="page-header">
                <div className="breadcrumb">
                    <a href="#" onClick={onBack}>Images</a> / <span>{imageName}</span>
                </div>
                <h1 className="page-title">📦 {imageName}</h1>
            </div>

            <div className="filter-bar">
                <input
                    type="text"
                    className="form-input filter-input"
                    placeholder="Filter versions..."
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                />
                <select
                    className="form-select"
                    value={testedFilter}
                    onChange={(e) => setTestedFilter(e.target.value)}
                    style={{ width: 'auto' }}
                >
                    <option value="all">All</option>
                    <option value="tested">Tested</option>
                    <option value="untested">Not tested</option>
                </select>
            </div>

            <div className="card">
                <table className="table">
                    <thead>
                        <tr>
                            <th>Version</th>
                            <th>Domain</th>
                            <th>Tested</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredVersions.map(v => (
                            <tr key={v.version}>
                                <td><code>{v.version}</code></td>
                                <td>{v.domain}</td>
                                <td>
                                    <span
                                        style={{ cursor: 'pointer' }}
                                        onClick={() => handleToggleTested(v.version, v.tested)}
                                        title="Click to toggle tested status"
                                    >
                                        <Badge type={v.tested ? 'tested' : 'default'}>{v.tested ? '✓ Tested' : 'Not tested'}</Badge>
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <SuccessModal isOpen={showSuccess} message="Updated successfully!" onClose={() => setShowSuccess(false)} />
        </div>
    );
};
