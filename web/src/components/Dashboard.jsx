import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { Bar, Pie, Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement } from 'chart.js';
import jsPDF from 'jspdf';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement);

const Dashboard = ({ auth }) => {
    const [file, setFile] = useState(null);
    const [history, setHistory] = useState([]);
    const [currentData, setCurrentData] = useState(null); // Full data for table
    const [currentSummary, setCurrentSummary] = useState(null); // Summary for charts
    const [loading, setLoading] = useState(false);
    const [selectedFileId, setSelectedFileId] = useState(null);

    const headers = { 'Authorization': `Basic ${auth}` };

    const fetchHistory = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/history/`, { headers });
            setHistory(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);

        setLoading(true);
        try {
            const res = await axios.post(`${API_BASE_URL}/upload/`, formData, { headers });
            setCurrentSummary(res.data.summary_data);
            
            fetchDataDetail(res.data.id);
            fetchHistory(); 
            setSelectedFileId(res.data.id);
        } catch (err) {
            alert("Upload failed: " + (err.response?.data?.error || err.message));
        }
        setLoading(false);
    };

    const fetchDataDetail = async (id) => {
        try {
            const res = await axios.get(`${API_BASE_URL}/data/${id}/`, { headers });
            setCurrentData(res.data);
            setSelectedFileId(id);
            // Find summary from history if not current
            const histItem = history.find(h => h.id === id);
            if (histItem) setCurrentSummary(histItem.summary_data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleHistoryClick = (item) => {
        fetchDataDetail(item.id);
        setCurrentSummary(item.summary_data);
    };

    const generatePDF = () => {
        const doc = new jsPDF();
        doc.text("ChemEquip Report", 10, 10);
        if (currentSummary) {
            doc.text(`Total Count: ${currentSummary.total_count}`, 10, 20);
            doc.text("Averages:", 10, 30);
            doc.text(`Flowrate: ${currentSummary.averages.Flowrate.toFixed(2)}`, 15, 40);
            doc.text(`Pressure: ${currentSummary.averages.Pressure.toFixed(2)}`, 15, 50);
            doc.text(`Temperature: ${currentSummary.averages.Temperature.toFixed(2)}`, 15, 60);
        }
        doc.save("report.pdf");
    };

    // Chart Data Preparation
    const typeChartData = currentSummary ? {
        labels: Object.keys(currentSummary.type_distribution),
        datasets: [{
            label: 'Equipment Type Distribution',
            data: Object.values(currentSummary.type_distribution),
            backgroundColor: ['#2ecc71', '#3498db', '#9b59b6', '#f1c40f', '#e74c3c'],
        }]
    } : null;

    return (
        <div className="container">
            <header className="dashboard-header">
                <h1 style={{ margin: 0, color: 'var(--primary-blue)' }}>ChemEquip Hybrid</h1>
                <button className="btn" onClick={() => window.location.reload()}>Logout</button>
            </header>

            <div className="dashboard-content">
                <aside className="sidebar">
                    <h3>History (Last 5)</h3>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {history.map(item => (
                            <li key={item.id}
                                style={{ padding: '10px', borderBottom: '1px solid #eee', cursor: 'pointer', background: selectedFileId === item.id ? '#e8f6f3' : 'transparent' }}
                                onClick={() => handleHistoryClick(item)}>
                                {item.filename} <br />
                                <small>{new Date(item.uploaded_at).toLocaleString()}</small>
                            </li>
                        ))}
                    </ul>
                </aside>

                <main className="main-view">
                    <div style={{ marginBottom: '20px', padding: '20px', background: '#f9f9f9', borderRadius: '8px' }}>
                        <h3>Upload New Dataset</h3>
                        <form onSubmit={handleUpload} style={{ display: 'flex', gap: '10px' }}>
                            <input type="file" onChange={e => setFile(e.target.files[0])} accept=".csv" />
                            <button type="submit" className="btn" disabled={loading}>{loading ? 'Uploading...' : 'Upload'}</button>
                        </form>
                    </div>

                    {currentSummary && (
                        <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <h2>Analysis Summary</h2>
                                <button className="btn" style={{ backgroundColor: '#e67e22' }} onClick={generatePDF}>Download PDF Report</button>
                            </div>

                            <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
                                <div style={{ background: 'var(--primary-green)', color: 'white', padding: '15px', borderRadius: '5px', flex: 1 }}>
                                    <h3>count</h3>
                                    <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{currentSummary.total_count}</p>
                                </div>
                                <div style={{ background: 'var(--primary-blue)', color: 'white', padding: '15px', borderRadius: '5px', flex: 1 }}>
                                    <h3>Avg Pressure</h3>
                                    <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{currentSummary.averages.Pressure.toFixed(2)}</p>
                                </div>
                                <div style={{ background: '#9b59b6', color: 'white', padding: '15px', borderRadius: '5px', flex: 1 }}>
                                    <h3>Avg Temp</h3>
                                    <p style={{ fontSize: '24px', fontWeight: 'bold' }}>{currentSummary.averages.Temperature.toFixed(2)}</p>
                                </div>
                            </div>

                            <div className="chart-container">
                                <div style={{ height: '300px' }}>
                                    {typeChartData && <Pie data={typeChartData} options={{ maintainAspectRatio: false }} />}
                                </div>
                                <div style={{ height: '300px' }}>
                                    {/* Placeholder for Line Chart if we had time series or index based data */}
                                    {typeChartData && <Bar data={typeChartData} options={{ maintainAspectRatio: false, plugins: { title: { display: true, text: 'Type Counts' } } }} />}
                                </div>
                            </div>
                        </div>
                    )}

                    {currentData && (
                        <div>
                            <h3>Raw Data</h3>
                            <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                                <table>
                                    <thead>
                                        <tr>
                                            {Object.keys(currentData[0]).map(k => <th key={k}>{k}</th>)}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {currentData.slice(0, 100).map((row, i) => ( // Limit to 100 for perf in example
                                            <tr key={i}>
                                                {Object.values(row).map((val, j) => <td key={j}>{val}</td>)}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                {currentData.length > 100 && <p>Showing first 100 rows...</p>}
                            </div>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
};

export default Dashboard;
