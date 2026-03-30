import React, { useState } from 'react';

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
    customPaths: string[];
    remoteBackendUrl: string;
    onSave: (paths: string[], remoteBackendUrl: string) => void;
}

const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose, customPaths, remoteBackendUrl, onSave }) => {
    const [paths, setPaths] = useState<string[]>(customPaths);
    const [newPath, setNewPath] = useState('');
    const [remoteUrl, setRemoteUrl] = useState(remoteBackendUrl);

    if (!isOpen) return null;

    const handleAddPath = () => {
        if (newPath.trim() && !paths.includes(newPath.trim())) {
            setPaths([...paths, newPath.trim()]);
            setNewPath('');
        }
    };

    const handleRemovePath = (pathToRemove: string) => {
        setPaths(paths.filter(p => p !== pathToRemove));
    };

    const handleSave = () => {
        onSave(paths, remoteUrl);
        onClose();
    };

    const isRemoteMode = remoteUrl.trim() !== '';

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
        }}>
            <div style={{
                backgroundColor: '#333', padding: '20px', borderRadius: '8px', width: '440px',
                border: '1px solid #555', color: '#fff'
            }}>
                <h2 style={{ marginTop: 0 }}>Settings</h2>

                {/* Remote Backend Section */}
                <div style={{ marginBottom: '20px', padding: '12px', backgroundColor: '#2a2a2a', borderRadius: '6px', border: '1px solid #444' }}>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '0.9em', fontWeight: 'bold', color: '#4facfe' }}>
                        Remote Backend
                    </label>
                    <p style={{ margin: '0 0 8px 0', fontSize: '0.78em', color: '#aaa', lineHeight: '1.4' }}>
                        Run <code style={{ color: '#ffd700', backgroundColor: '#1a1a1a', padding: '1px 4px', borderRadius: '3px' }}>backend_server.exe</code> on
                        another PC and paste the URL it shows here.
                        Leave blank to use the built-in local backend.
                    </p>
                    <input
                        type="text"
                        value={remoteUrl}
                        onChange={(e) => setRemoteUrl(e.target.value)}
                        placeholder="e.g. http://192.168.1.100:8001"
                        style={{ width: '100%', boxSizing: 'border-box', padding: '6px 8px', borderRadius: '4px', border: `1px solid ${isRemoteMode ? '#4facfe' : '#555'}`, backgroundColor: '#222', color: '#fff', fontSize: '0.9em' }}
                    />
                    {isRemoteMode && (
                        <p style={{ margin: '6px 0 0 0', fontSize: '0.75em', color: '#ffd700' }}>
                            ⚠ Remote mode active — local backend will not start. Restart the app to apply changes.
                        </p>
                    )}
                    {!isRemoteMode && (
                        <p style={{ margin: '6px 0 0 0', fontSize: '0.75em', color: '#4caf50' }}>
                            ✓ Local mode — using built-in backend on this PC.
                        </p>
                    )}
                </div>

                {/* Custom Paths Section */}
                <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9em' }}>Custom Paths (NTFS/SMB):</label>
                    <div style={{ display: 'flex', gap: '5px', marginBottom: '10px' }}>
                        <input
                            type="text"
                            value={newPath}
                            onChange={(e) => setNewPath(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleAddPath()}
                            placeholder="e.g. Z:\Data or \\Server\Share"
                            style={{ flex: 1, padding: '5px', borderRadius: '4px', border: '1px solid #555', backgroundColor: '#222', color: '#fff' }}
                        />
                        <button onClick={handleAddPath} style={{ padding: '5px 10px', cursor: 'pointer', backgroundColor: '#4caf50', border: 'none', borderRadius: '4px', color: '#fff' }}>Add</button>
                    </div>

                    <ul style={{ listStyle: 'none', padding: 0, maxHeight: '150px', overflowY: 'auto', border: '1px solid #444', borderRadius: '4px' }}>
                        {paths.length === 0 && (
                            <li style={{ padding: '8px 10px', color: '#666', fontSize: '0.85em' }}>No custom paths added.</li>
                        )}
                        {paths.map(path => (
                            <li key={path} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 10px', borderBottom: '1px solid #444' }}>
                                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{path}</span>
                                <button onClick={() => handleRemovePath(path)} style={{ color: '#ff6b6b', background: 'none', border: 'none', cursor: 'pointer' }}>X</button>
                            </li>
                        ))}
                    </ul>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
                    <button
                        onClick={() => window.electron.invoke('open-settings-folder')}
                        style={{ fontSize: '0.8em', color: '#aaa', background: 'none', border: 'none', textDecoration: 'underline', cursor: 'pointer' }}
                    >
                        Open Config File
                    </button>
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <button onClick={onClose} style={{ padding: '8px 16px', cursor: 'pointer', backgroundColor: '#555', border: 'none', borderRadius: '4px', color: '#fff' }}>Cancel</button>
                        <button onClick={handleSave} style={{ padding: '8px 16px', cursor: 'pointer', backgroundColor: '#646cff', border: 'none', borderRadius: '4px', color: '#fff' }}>Save</button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SettingsModal;
