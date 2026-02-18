import { useState, useEffect } from 'react'
import OverlayPanel from './components/OverlayPanel';
import SettingsModal from './components/SettingsModal';
import './index.css';

interface Metrics {
    io: Record<string, { read_bytes_sec: number; write_bytes_sec: number }>;
    space: Array<{
        device: string;
        mountpoint: string;
        total: number;
        used: number;
        free: number;
        percent: number;
        fstype: string;
    }>;
    temp: Record<string, number>;
    timestamp: number;
}

function App() {
    const [metrics, setMetrics] = useState<Metrics | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [customPaths, setCustomPaths] = useState<string[] | null>(null);
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [isOverlay, setIsOverlay] = useState(false);

    useEffect(() => {
        if (window.electron && window.electron.invoke) {
            window.electron.invoke('get-settings').then((settings: any) => {
                setCustomPaths(settings.customPaths || []);
            });
        } else {
            setCustomPaths([]);
        }
    }, []);

    useEffect(() => {
        if (customPaths === null) return;
        const fetchMetrics = async () => {
            try {
                const response = await fetch('http://127.0.0.1:8001/metrics', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ custom_paths: customPaths })
                });
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const data = await response.json();
                setMetrics(data);
                setError(null);
            } catch (e: any) {
                setError(e.toString());
            }
        };
        const intervalId = setInterval(fetchMetrics, 1000);
        fetchMetrics();
        return () => clearInterval(intervalId);
    }, [customPaths]);

    const toggleOverlay = async () => {
        const newState = !isOverlay;
        setIsOverlay(newState);
        if (window.electron && window.electron.invoke) {
            try {
                await window.electron.invoke('toggle-overlay', newState);
            } catch (e) {
                console.error("IPC invoke failed", e);
            }
        }
    };

    const saveCustomPaths = async (newPaths: string[]) => {
        setCustomPaths(newPaths);
        if (window.electron && window.electron.invoke) {
            await window.electron.invoke('save-settings', { customPaths: newPaths });
        }
    };

    const formatBytes = (bytes: number) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const formatRate = (bytes: number) => formatBytes(bytes) + '/s';

    if (isOverlay) {
        return (
            <div onClick={toggleOverlay} style={{ cursor: 'pointer', userSelect: 'none' }} title="Click to exit overlay">
                <OverlayPanel metrics={metrics} />
            </div>
        );
    }

    return (
        <div className="app-container">
            <header className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h1 className="text-2xl font-bold">Disk Monitor</h1>
                <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={() => setIsSettingsOpen(true)} style={{ padding: '8px 16px', cursor: 'pointer', backgroundColor: '#555', color: 'white', border: 'none', borderRadius: '4px' }}>
                        Settings
                    </button>
                    <button onClick={toggleOverlay} style={{ padding: '8px 16px', cursor: 'pointer', backgroundColor: '#646cff', color: 'white', border: 'none', borderRadius: '4px' }}>
                        Switch to Overlay
                    </button>
                </div>
            </header>

            {customPaths && (
                <SettingsModal
                    isOpen={isSettingsOpen}
                    onClose={() => setIsSettingsOpen(false)}
                    customPaths={customPaths}
                    onSavePaths={saveCustomPaths}
                />
            )}

            {error && (
                <div style={{ color: '#ff6b6b', marginBottom: '20px', padding: '10px', backgroundColor: 'rgba(255,0,0,0.1)', borderRadius: '4px' }}>
                    <strong>Connection Error:</strong> {error}
                </div>
            )}

            {metrics && (
                <div className="metrics-grid-container">
                    <div className="metrics-grid" style={{
                        gridTemplateColumns: `repeat(auto-fit, minmax(210px, 1fr))`,
                        gridAutoRows: 'auto'
                    }}>
                        {metrics.space.map((disk) => {
                            const io = metrics.io[disk.device] || { read_bytes_sec: 0, write_bytes_sec: 0 };
                            const temp = metrics.temp[disk.device] || 'N/A';

                            return (
                                <div key={disk.device} className="disk-card" style={{ backgroundColor: '#333' }}>
                                    <h3 style={{ marginTop: 0, display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{disk.mountpoint}</span>
                                        <span style={{ fontSize: '0.7em', color: '#999', alignSelf: 'center' }}>{disk.device}</span>
                                    </h3>

                                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                                        <div className="progress-bar-container">
                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '0.85rem' }}>
                                                <span className="disk-type-label" style={{ color: '#aaa' }}>{disk.fstype}</span>
                                                <span style={{ fontWeight: 'bold' }}>{disk.percent}% Used</span>
                                            </div>
                                            <div className="disk-progress-bar-wrapper">
                                                <div style={{ width: `${disk.percent}%`, height: '100%', backgroundColor: disk.percent > 90 ? '#ff4444' : '#4caf50', transition: 'width 0.5s' }}></div>
                                            </div>
                                            <div className="disk-usage-text-extra" style={{ fontSize: '0.75rem', color: '#ccc', marginTop: '4px', textAlign: 'right' }}>
                                                {formatBytes(disk.used)} / {formatBytes(disk.total)}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="disk-io-stats" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', fontSize: '0.85rem', marginTop: '12px' }}>
                                        <div style={{ textAlign: 'center', backgroundColor: '#444', padding: '6px', borderRadius: '4px' }}>
                                            <div style={{ color: '#aaa', fontSize: '0.7rem', textTransform: 'uppercase' }}>Read</div>
                                            <div style={{ fontWeight: 'bold', color: '#4facfe', fontSize: '0.75rem' }}>{formatRate(io.read_bytes_sec)}</div>
                                        </div>
                                        <div style={{ textAlign: 'center', backgroundColor: '#444', padding: '6px', borderRadius: '4px' }}>
                                            <div style={{ color: '#aaa', fontSize: '0.7rem', textTransform: 'uppercase' }}>Write</div>
                                            <div style={{ fontWeight: 'bold', color: '#ff6b6b', fontSize: '0.75rem' }}>{formatRate(io.write_bytes_sec)}</div>
                                        </div>
                                        <div style={{ textAlign: 'center', backgroundColor: '#444', padding: '6px', borderRadius: '4px' }}>
                                            <div style={{ color: '#aaa', fontSize: '0.7rem', textTransform: 'uppercase' }}>Temp</div>
                                            <div style={{ fontWeight: 'bold', color: temp !== 'N/A' && temp > 50 ? '#ff4444' : '#fff', fontSize: '0.75rem' }}>{temp !== 'N/A' ? temp + '°C' : 'N/A'}</div>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {!metrics && !error && <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading metrics...</div>}
        </div>
    )
}

export default App
