/**
 * Version Manager UI - Domains Section
 */

const { useState, useEffect } = React;

// Domains List
const DomainsList = ({ onSelectDomain, onDataChange }) => {
    const [domains, setDomains] = useState([]);
    const [filter, setFilter] = useState('');
    const [showCreate, setShowCreate] = useState(false);
    const [showEdit, setShowEdit] = useState(null);
    const [showDelete, setShowDelete] = useState(null);
    const [showSuccess, setShowSuccess] = useState(false);
    const [newDomain, setNewDomain] = useState('');

    useEffect(() => {
        loadDomains();
    }, []);

    const loadDomains = async () => {
        try {
            const data = await api.get('/domains/list');
            const grouped = data.reduce((acc, d) => {
                if (!acc[d.name]) acc[d.name] = { name: d.name, versions: [] };
                acc[d.name].versions.push(d);
                return acc;
            }, {});
            setDomains(Object.values(grouped));
        } catch (err) {
            console.error('Error loading domains:', err);
        }
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            const version = new Date().toISOString().slice(0, 19).replace(/[T:]/g, '-');
            await api.post(`/domains/${newDomain}/create`, {
                version: version
            });
            setShowCreate(false);
            setNewDomain('');
            setShowSuccess(true);
            loadDomains();
        } catch (err) {
            alert('Error creating domain: ' + err.message);
        }
    };

    const handleEdit = async (e) => {
        e.preventDefault();
        try {
            if (showEdit.newName !== showEdit.name) {
                await api.put(`/domains/${showEdit.name}/rename`, {name: showEdit.newName});
            }
            setShowEdit(null);
            setShowSuccess(true);
            loadDomains();
        } catch (err) {
            alert('Error updating domain: ' + err.message);
        }
    };

    const handleDelete = async () => {
        try {
            await api.delete(`/domains/${showDelete.name}`);
            setShowDelete(null);
            setShowSuccess(true);
            loadDomains();
            // Notify parent that data changed (images may have been deleted)
            if (onDataChange) onDataChange();
        } catch (err) {
            alert('Error deleting domain: ' + err.message);
        }
    };

    const filteredDomains = domains.filter(d => 
        d.name.toLowerCase().includes(filter.toLowerCase())
    );

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">🏷️ Domains</h1>
                <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Add Domain</button>
            </div>

            <div className="filter-bar">
                <input
                    type="text"
                    className="form-input filter-input"
                    placeholder="Filter domains..."
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                />
            </div>

            <div className="card">
                <table className="table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Versions</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredDomains.length === 0 ? (
                            <tr><td colSpan="3" className="text-center">No domains found</td></tr>
                        ) : filteredDomains.map(d => (
                            <tr key={d.name}>
                                <td>
                                    <a href="#" className="link" onClick={() => onSelectDomain(d.name)}>
                                        {d.name}
                                    </a>
                                </td>
                                <td>{d.versions.length}</td>
                                <td>
                                    <button className="btn btn-icon" title="Edit" onClick={() => setShowEdit({ ...d, newName: d.name })}>✏️</button>
                                    <button className="btn btn-icon" title="Delete" onClick={() => setShowDelete(d)}>🗑️</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Create Modal */}
            <FormModal isOpen={showCreate} title="Create New Domain" onClose={() => setShowCreate(false)} onSubmit={handleCreate}>
                <div className="form-group">
                    <label className="form-label">Domain Name</label>
                    <input
                        type="text"
                        className="form-input"
                        value={newDomain}
                        onChange={(e) => setNewDomain(e.target.value.toLowerCase().replace(/[^a-z0-9_-]/g, ''))}
                        placeholder="my-domain"
                        required
                    />
                </div>
            </FormModal>

            {/* Edit Modal */}
            <FormModal isOpen={!!showEdit} title="Edit Domain" onClose={() => setShowEdit(null)} onSubmit={handleEdit}>
                {showEdit && (
                    <div className="form-group">
                        <label className="form-label">Domain Name</label>
                        <input
                            type="text"
                            className="form-input"
                            value={showEdit.newName}
                            onChange={(e) => setShowEdit({ ...showEdit, newName: e.target.value.toLowerCase().replace(/[^a-z0-9_-]/g, '') })}
                            required
                        />
                    </div>
                )}
            </FormModal>

            {/* Delete Confirmation */}
            <ConfirmModal
                isOpen={!!showDelete}
                title="Delete Domain"
                message={`Do you want to delete the entire domain "${showDelete?.name}" with all its versions and associated images?`}
                onConfirm={handleDelete}
                onCancel={() => setShowDelete(null)}
            />

            <SuccessModal isOpen={showSuccess} message="Operation completed!" onClose={() => setShowSuccess(false)} />
        </div>
    );
};

// Domain Versions View
const DomainVersions = ({ domainName, onBack, onDataChange }) => {
    const [versions, setVersions] = useState([]);
    const [filter, setFilter] = useState('');
    const [envFilter, setEnvFilter] = useState('all');
    const [activeOnly, setActiveOnly] = useState(false);
    const [showEdit, setShowEdit] = useState(null);
    const [showDelete, setShowDelete] = useState(null);
    const [showSuccess, setShowSuccess] = useState(false);
    const [showImages, setShowImages] = useState(null);
    const [editingImage, setEditingImage] = useState(null);
    const [imageFilter, setImageFilter] = useState('');
    const [testedFilter, setTestedFilter] = useState('all');
    const [availableVersions, setAvailableVersions] = useState([]);

    // Get available promote options based on current deployed value
    const getPromoteOptions = (deployed) => {
        switch (deployed) {
            case 'dev': return ['staging'];
            case 'staging': return ['prod'];
            default: return [];
        }
    };

    // Check if all images in domain version are tested
    const allImagesTested = (domainVersion) => {
        if (!domainVersion.images || domainVersion.images.length === 0) return true;
        return domainVersion.images.every(img => img.tested);
    };

    // Check if domain version can be promoted
    const canPromote = (domainVersion) => {
        // Domain must be tested
        return domainVersion.tested === true;
    };

    useEffect(() => {
        loadVersions();
    }, [domainName]);

    const loadVersions = async () => {
        try {
            const data = await api.get(`/domains/${domainName}`);
            setVersions(data);
        } catch (err) {
            console.error('Error loading versions:', err);
        }
    };

    const loadImageVersions = async (imageName) => {
        try {
            const data = await api.get(`/images/${imageName}/list`);
            // Sort versions in descending order (latest first) since they're in timestamp format
            const versions = data.map(img => img.version).sort((a, b) => b.localeCompare(a));
            setAvailableVersions(versions);
        } catch (err) {
            console.error('Error loading image versions:', err);
            setAvailableVersions([]);
        }
    };

    const handleStartEditImage = async (img) => {
        setEditingImage({ name: img.name, version: img.version, newVersion: img.version });
        await loadImageVersions(img.name);
    };

    const handleEdit = async (e) => {
        e.preventDefault();
        try {
            // Handle promote first (resets tested status and sets active)
            if (showEdit.newDeployed && showEdit.newDeployed !== showEdit.deployed) {
                await api.put(`/domains/promote`, {
                    name: domainName,
                    version: showEdit.version,
                    deployed: showEdit.newDeployed
                });
                
                // If promoting active domain version from dev to staging, create new dev version
                if (showEdit.deployed === 'dev' && showEdit.newDeployed === 'staging' && showEdit.active) {
                    await handleCreateVersion();
                }
                
                // Promote sets the domain as active, so skip other status changes
            } else {
                // Handle tested status change (only if not promoted)
                if (showEdit.newTested !== showEdit.tested) {
                    await api.put('/domains/tested', { name: domainName, version: showEdit.version, tested: showEdit.newTested });
                }
                // Handle active status change (only if not promoted, since promote sets active)
                if (showEdit.newActive !== showEdit.active) {
                    await api.put(`/domains/${domainName}/active`, { name: domainName, version: showEdit.version });
                }
            }
            setShowEdit(null);
            setShowSuccess(true);
            loadVersions();
        } catch (err) {
            alert('Error updating version: ' + err.message);
        }
    };

    const handleDelete = async () => {
        try {
            await api.delete(`/domains/${domainName}/${showDelete.version}`);
            setShowDelete(null);
            setShowSuccess(true);
            loadVersions();
            // Notify parent that data changed (images may have been deleted)
            if (onDataChange) onDataChange();
        } catch (err) {
            alert('Error deleting version: ' + err.message);
        }
    };

    const handleUpdateImageVersion = async (e) => {
        e.preventDefault();
        try {
            // Update the domain with the new image version
            await api.put('/domains/update', {
                name: domainName,
                version: showImages.version,
                images: [{ name: editingImage.name, version: editingImage.newVersion }]
            });
            setEditingImage(null);
            setShowSuccess(true);
            loadVersions();
            // Update showImages with refreshed data
            const updatedVersions = await api.get(`/domains/${domainName}`);
            const updatedVersion = updatedVersions.find(v => v.version === showImages.version);
            if (updatedVersion) {
                setShowImages(updatedVersion);
            }
        } catch (err) {
            alert('Error updating image version: ' + err.message);
        }
    };

    const handleToggleTested = async (imageName, imageVersion, currentTested) => {
        try {
            const newTested = !currentTested;
            await api.put(`/images/${imageName}/tested`, {
                version: imageVersion,
                tested: newTested
            });
            setShowSuccess(true);
            loadVersions();
            // Update showImages with refreshed data
            const updatedVersions = await api.get(`/domains/${domainName}`);
            const updatedVersion = updatedVersions.find(v => v.version === showImages.version);
            if (updatedVersion) {
                setShowImages(updatedVersion);
            }
        } catch (err) {
            alert('Error updating tested status: ' + err.message);
        }
    };

    const handleCreateVersion = async () => {
        try {
            // Auto-generate version timestamp in format YYYY-MM-DD-hh-mm-ss
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            const version = `${year}-${month}-${day}-${hours}-${minutes}-${seconds}`;
            
            await api.post(`/domains/${domainName}/create`, {
                version: version
            });
            setShowSuccess(true);
            loadVersions();
            // Notify parent that data changed
            if (onDataChange) onDataChange();
        } catch (err) {
            alert('Error creating domain version: ' + err.message);
        }
    };

    const filteredVersions = versions.filter(v => {
        if (activeOnly && !v.active) return false;
        if (envFilter !== 'all' && v.deployed !== envFilter) return false;
        if (filter && !v.version.includes(filter)) return false;
        return true;
    });

    return (
        <div>
            <div className="page-header">
                <div className="breadcrumb">
                    <a href="#" onClick={onBack}>Domains</a> / <span>{domainName}</span>
                </div>
                <h1 className="page-title">🏷️ {domainName}</h1>
                <button className="btn btn-primary" onClick={handleCreateVersion}>+ New Version</button>
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
                    value={envFilter}
                    onChange={(e) => setEnvFilter(e.target.value)}
                    style={{ width: 'auto' }}
                >
                    <option value="all">All environments</option>
                    <option value="dev">dev</option>
                    <option value="staging">staging</option>
                    <option value="prod">prod</option>
                </select>
                <label className="checkbox-label">
                    <input
                        type="checkbox"
                        checked={activeOnly}
                        onChange={(e) => setActiveOnly(e.target.checked)}
                    />
                    {' '}Active only
                </label>
            </div>

            <div className="card">
                <table className="table">
                    <thead>
                        <tr>
                            <th>Version</th>
                            <th>Deployed</th>
                            <th>Tested</th>
                            <th>Active</th>
                            <th>Images</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredVersions.length === 0 ? (
                            <tr><td colSpan="6" className="text-center">No versions found</td></tr>
                        ) : filteredVersions.map(v => (
                            <tr key={v.version}>
                                <td>
                                    <a href="#" className="link" onClick={() => setShowImages(v)}>
                                        <code>{v.version}</code>
                                    </a>
                                </td>
                                <td><Badge type={v.deployed}>{v.deployed}</Badge></td>
                                <td><Badge type={v.tested ? 'tested' : 'default'}>{v.tested ? '✓' : '—'}</Badge></td>
                                <td><Badge type={v.active ? 'active' : 'default'}>{v.active ? '✓ Active' : '—'}</Badge></td>
                                <td>{v.images?.length || 0}</td>
                                <td>
                                    <button className="btn btn-icon" title="Edit" onClick={() => setShowEdit({ ...v, newTested: v.tested, newActive: v.active })}>✏️</button>
                                    <button className="btn btn-icon" title="Delete" onClick={() => setShowDelete(v)}>🗑️</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Edit Modal */}
            <FormModal isOpen={!!showEdit} title="Edit Domain Version" onClose={() => setShowEdit(null)} onSubmit={handleEdit} className="modal-fixed">
                {showEdit && (
                    <>
                        <div className="form-group">
                            <label className="form-label">Version</label>
                            <input type="text" className="form-input" value={showEdit.version} disabled />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Current Environment</label>
                            <input type="text" className="form-input" value={showEdit.deployed} disabled />
                        </div>
                        {getPromoteOptions(showEdit.deployed).length > 0 && (
                            <div className="form-group">
                                <label className="form-label">Promote to</label>
                                <select
                                    className="form-select"
                                    value={showEdit.newDeployed || ''}
                                    onChange={(e) => setShowEdit({ ...showEdit, newDeployed: e.target.value || null })}
                                    disabled={!canPromote(showEdit)}
                                >
                                    <option value="">-- Keep current --</option>
                                    {getPromoteOptions(showEdit.deployed).map(env => (
                                        <option key={env} value={env}>{env}</option>
                                    ))}
                                </select>
                                {!canPromote(showEdit) && (
                                    <small className="form-hint text-warning">
                                        ⚠️ Cannot promote: Domain version is not tested
                                    </small>
                                )}
                                {showEdit.newDeployed && canPromote(showEdit) && (
                                    <small className="form-hint">
                                        {showEdit.deployed === 'dev' && showEdit.newDeployed === 'staging' 
                                            ? 'Note: Promoting will set this version as Active and reset tested status'
                                            : 'Note: Promoting will set this version as Active'}
                                    </small>
                                )}
                            </div>
                        )}
                        <div className="form-group">
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    checked={showEdit.newDeployed 
                                        ? (showEdit.deployed === 'dev' && showEdit.newDeployed === 'staging' ? false : showEdit.tested)
                                        : showEdit.newTested}
                                    onChange={(e) => setShowEdit({ ...showEdit, newTested: e.target.checked })}
                                    disabled={!!showEdit.newDeployed || !allImagesTested(showEdit)}
                                />
                                {' '}Tested
                                {showEdit.newDeployed && showEdit.deployed === 'dev' && showEdit.newDeployed === 'staging' && (
                                    <span style={{ color: '#888' }}> (will be reset)</span>
                                )}
                                {!showEdit.newDeployed && !allImagesTested(showEdit) && (
                                    <span style={{ color: '#888' }}> (all images must be tested first)</span>
                                )}
                            </label>
                        </div>
                        <div className="form-group">
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    checked={showEdit.newDeployed ? true : showEdit.newActive}
                                    onChange={(e) => setShowEdit({ ...showEdit, newActive: e.target.checked })}
                                    disabled={!!showEdit.newDeployed}
                                />
                                {' '}Active
                                {showEdit.newDeployed && <span style={{ color: '#888' }}> (will be set)</span>}
                            </label>
                        </div>
                    </>
                )}
            </FormModal>

            {/* Delete Confirmation */}
            <ConfirmModal
                isOpen={!!showDelete}
                title="Delete Domain Version"
                message={`Do you want to delete version "${showDelete?.version}" and its associated images?`}
                onConfirm={handleDelete}
                onCancel={() => setShowDelete(null)}
            />

            {/* Images Modal */}
            {showImages && (
                <div className="modal-overlay" onClick={() => { setShowImages(null); setEditingImage(null); setImageFilter(''); setTestedFilter('all'); setAvailableVersions([]); }}>
                    <div className="modal modal-fixed-lg" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3 className="modal-title">Images in Version: {showImages.version}</h3>
                            <button className="btn-close" onClick={() => { setShowImages(null); setEditingImage(null); setImageFilter(''); setTestedFilter('all'); setAvailableVersions([]); }}>×</button>
                        </div>
                        <div className="modal-body">
                            {(!showImages.images || showImages.images.length === 0) ? (
                                <p className="text-center">No images associated with this version</p>
                            ) : (
                                <>
                                    <div className="filter-bar" style={{ marginBottom: '1rem' }}>
                                        <input
                                            type="text"
                                            className="form-input filter-input"
                                            placeholder="Filter images by name..."
                                            value={imageFilter}
                                            onChange={(e) => setImageFilter(e.target.value)}
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
                                    <table className="table">
                                        <thead>
                                            <tr>
                                                <th>Image Name</th>
                                                <th>Version</th>
                                                <th>Tested</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {showImages.images
                                                .filter(img => {
                                                    // Filter by name
                                                    if (imageFilter && !img.name.toLowerCase().includes(imageFilter.toLowerCase())) return false;
                                                    // Filter by tested status
                                                    if (testedFilter === 'tested' && !img.tested) return false;
                                                    if (testedFilter === 'untested' && img.tested) return false;
                                                    return true;
                                                })
                                                .map((img, idx) => (
                                                <tr key={idx}>
                                                    <td>{img.name}</td>
                                                    <td>
                                                        {editingImage && editingImage.name === img.name ? (
                                                            <select
                                                                className="form-select"
                                                                value={editingImage.newVersion}
                                                                onChange={(e) => setEditingImage({ ...editingImage, newVersion: e.target.value })}
                                                                autoFocus
                                                            >
                                                                {availableVersions.map(ver => (
                                                                    <option key={ver} value={ver}>{ver}</option>
                                                                ))}
                                                            </select>
                                                        ) : (
                                                            <code>{img.version}</code>
                                                        )}
                                                    </td>
                                                    <td>
                                                        <span
                                                            style={{ cursor: 'pointer' }}
                                                            onClick={() => handleToggleTested(img.name, img.version, img.tested)}
                                                            title="Click to toggle tested status"
                                                        >
                                                            <Badge type={img.tested ? 'tested' : 'default'}>{img.tested ? '✓ Tested' : 'Not tested'}</Badge>
                                                        </span>
                                                    </td>
                                                    <td>
                                                        {editingImage && editingImage.name === img.name ? (
                                                            <>
                                                                <button className="btn btn-icon" title="Save" onClick={handleUpdateImageVersion}>✓</button>
                                                                <button className="btn btn-icon" title="Cancel" onClick={() => { setEditingImage(null); setAvailableVersions([]); }}>✕</button>
                                                            </>
                                                        ) : (
                                                            <button className="btn btn-icon" title="Edit Version" onClick={() => handleStartEditImage(img)}>✏️</button>
                                                        )}
                                                    </td>
                                                </tr>
                                            ))}
                                            {showImages.images.filter(img => {
                                                // Filter by name
                                                if (imageFilter && !img.name.toLowerCase().includes(imageFilter.toLowerCase())) return false;
                                                // Filter by tested status
                                                if (testedFilter === 'tested' && !img.tested) return false;
                                                if (testedFilter === 'untested' && img.tested) return false;
                                                return true;
                                            }).length === 0 && (
                                                <tr><td colSpan="4" className="text-center">No images match the filter</td></tr>
                                            )}
                                        </tbody>
                                    </table>
                                </>
                            )}
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-secondary" onClick={() => { setShowImages(null); setEditingImage(null); setImageFilter(''); setTestedFilter('all'); setAvailableVersions([]); }}>Close</button>
                        </div>
                    </div>
                </div>
            )}

            <SuccessModal isOpen={showSuccess} message="Updated successfully!" onClose={() => setShowSuccess(false)} />
        </div>
    );
};
