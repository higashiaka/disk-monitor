import React from 'react';

interface OverlayPanelProps {
    metrics: any;
}

const OverlayPanel: React.FC<OverlayPanelProps> = ({ metrics }) => {
    if (!metrics) return null;

    return (
        <div style={{ backgroundColor: 'rgba(0,0,0,0.7)', color: 'white', padding: '10px', borderRadius: '5px', fontSize: '12px' }}>
            {metrics.io && Object.entries(metrics.io).map(([diskName, io]: [string, any]) => (
                <div key={diskName} style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>{diskName}:</span>
                    <span>R: {io.read_bytes_sec.toFixed(0)} / W: {io.write_bytes_sec.toFixed(0)}</span>
                </div>
            ))}
        </div>
    );
};

export default OverlayPanel;
