import React, { useState } from 'react';

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
    customPaths: string[];
    onSavePaths: (paths: string[]) => void;
}

const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose, customPaths, onSavePaths }) => {
    const [paths, setPaths] = useState<string[]>(customPaths);
    const [newPath, setNewPath] = useState('');

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
        onSavePaths(paths);
        onClose();
    };

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
        }}>
            <div style={{
                backgroundColor: '#333', padding: '20px', borderRadius: '8px', width: '400px',
                border: '1px solid #555', color: '#fff'
            }}>
                <h2 style={{ marginTop: 0 }}>Settings</h2>

                <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9em' }}>Custom Paths (NTFS/SMB):</label>
                    <div style={{ display: 'flex', gap: '5px', marginBottom: '10px' }}>
                        <input
                            type="text"
                            value={newPath}
                            onChange={(e) => setNewPath(e.target.value)}
                            placeholder="e.g. Z:\Data or \\Server\Share"
                            style={{ flex: 1, padding: '5px', borderRadius: '4px', border: '1px solid #555', backgroundColor: '#222', color: '#fff' }}
                        />
                        <button onClick={handleAddPath} style={{ padding: '5px 10px', cursor: 'pointer', backgroundColor: '#4caf50', border: 'none', borderRadius: '4px', color: '#fff' }}>Add</button>
                    </div>

                    <ul style={{ listStyle: 'none', padding: 0, maxHeight: '150px', overflowY: 'auto', border: '1px solid #444', borderRadius: '4px' }}>
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
