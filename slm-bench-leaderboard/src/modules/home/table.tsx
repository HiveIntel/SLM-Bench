import React from 'react';

const modelData = [
    {
        name: "Llama-3.2-1B",
        provider: "Meta",
        license: "Apache 2.0",
        parameters: "1.24B",
        contextWindow: 128000,
        trainingTime: "Unknown",
        size: "5.8GB",
        throughput: "1250",
        latency: "55",
        gold: 80,
        silver: 65,
        bronze: 50
    },
    {
        name: "GPT-Neo-1.3B",
        provider: "EleutherAI",
        license: "Apache 2.0",
        parameters: "1.37B",
        contextWindow: 2048,
        trainingTime: "10 days (32 GPUs)",
        size: "2.46GB",
        throughput: "1500",
        latency: "50",
        gold: 75,
        silver: 60,
        bronze: 45
    },
    {
        name: "Zephyr-7B",
        provider: "Hugging Face",
        license: "Apache 2.0",
        parameters: "7.00B",
        contextWindow: 8192,
        trainingTime: "20 days (64 GPUs)",
        size: "13.74GB",
        throughput: "1300",
        latency: "52",
        gold: 70,
        silver: 55,
        bronze: 40
    },
    {
        name: "Phi-1.5",
        provider: "Microsoft",
        license: "Proprietary",
        parameters: "2.70B",
        contextWindow: 2048,
        trainingTime: "12 days (32 GPUs)",
        size: "2.45GB",
        throughput: "1400",
        latency: "52",
        gold: 65,
        silver: 50,
        bronze: 35
    },
    {
        name: "Mistral-7B",
        provider: "Mistral AI",
        license: "Apache 2.0",
        parameters: "7.00B",
        contextWindow: 8192,
        trainingTime: "15 days (128 GPUs)",
        size: "13.0GB",
        throughput: "1400",
        latency: "55",
        gold: 60,
        silver: 45,
        bronze: 30
    },
    {
        name: "ShearedLlama-2.7B",
        provider: "Hugging Face",
        license: "Apache 2.0",
        parameters: "2.70B",
        contextWindow: 2048,
        trainingTime: "12 days (32 GPUs)",
        size: "5.0GB",
        throughput: "1300",
        latency: "54",
        gold: 55,
        silver: 40,
        bronze: 25
    },
    {
        name: "StableLM-3B",
        provider: "Stability AI",
        license: "Apache 2.0",
        parameters: "3.00B",
        contextWindow: 2048,
        trainingTime: "14 days (64 GPUs)",
        size: "6.5GB",
        throughput: "1250",
        latency: "50",
        gold: 50,
        silver: 35,
        bronze: 20
    },
    {
        name: "Pythia-2.8B",
        provider: "EleutherAI",
        license: "Apache 2.0",
        parameters: "2.80B",
        contextWindow: 2048,
        trainingTime: "12 days (32 GPUs)",
        size: "5.5GB",
        throughput: "1350",
        latency: "50",
        gold: 45,
        silver: 30,
        bronze: 15
    },
    {
        name: "TinyLlama-1.1B",
        provider: "Hugging Face",
        license: "Apache 2.0",
        parameters: "1.10B",
        contextWindow: 2048,
        trainingTime: "8 days (16 GPUs)",
        size: "2.0GB",
        throughput: "1600",
        latency: "45",
        gold: 40,
        silver: 25,
        bronze: 10
    },
    {
        name: "LLaMA-2-7B",
        provider: "Meta",
        license: "LLAMA 2 L",
        parameters: "6.47B",
        contextWindow: 4096,
        trainingTime: "21 days (64 GPUs)",
        size: "13.0GB",
        throughput: "1200",
        latency: "62",
        gold: 35,
        silver: 20,
        bronze: 5
    },
    {
        name: "Open-LLaMA-3B",
        provider: "OpenLM",
        license: "Apache 2.0",
        parameters: "3.00B",
        contextWindow: 4096,
        trainingTime: "18 days (64 GPUs)",
        size: "6.8GB",
        throughput: "1300",
        latency: "60",
        gold: 30,
        silver: 15,
        bronze: 0
    },
    {
        name: "Gemma-2B",
        provider: "Google",
        license: "Proprietary",
        parameters: "2.00B",
        contextWindow: 2048,
        trainingTime: "14 days (32 GPUs)",
        size: "4.67GB",
        throughput: "1450",
        latency: "54",
        gold: 25,
        silver: 10,
        bronze: 0
    },
    {
        name: "Dolly-v2-3B",
        provider: "DataBricks",
        license: "Apache 2.0",
        parameters: "3.00B",
        contextWindow: 2048,
        trainingTime: "10 days (32 GPUs)",
        size: "5.8GB",
        throughput: "1250",
        latency: "55",
        gold: 20,
        silver: 5,
        bronze: 0
    },
    {
        name: "Gemma-3-1B",
        provider: "Google",
        license: "Apache 2.0",
        parameters: "1.00B",
        contextWindow: 32000,
        trainingTime: "30 days (512 GPUs",
        size: "5.8GB",
        throughput: "1250",
        latency: "55",
        gold: 15,
        silver: 0,
        bronze: 0
    },
    {
        name: "Phi-3",
        provider: "Microsoft",
        license: "Apache 2.0",
        parameters: "3.82B",
        contextWindow: 128000,
        trainingTime: "7 days (512 GPUs)",
        size: "5.8GB",
        throughput: "1250",
        latency: "55",
        gold: 10,
        silver: 0,
        bronze: 0
    },
];

const modelDataA10G = [
    {
        name: "Llama-3.2-1B",
        provider: "Meta",
        license: "Apache 2.0",
        parameters: "1.24B",
        contextWindow: 128000,
        trainingTime: "Unknown",
        size: "5.8GB",
        throughput: "1250",
        latency: "55",
        gold: 80,
        silver: 65,
        bronze: 50
    },
    {
        name: "GPT-Neo-1.3B",
        provider: "EleutherAI",
        license: "Apache 2.0",
        parameters: "1.37B",
        contextWindow: 2048,
        trainingTime: "10 days (32 GPUs)",
        size: "2.46GB",
        throughput: "1500",
        latency: "50",
        gold: 75,
        silver: 60,
        bronze: 45
    },
    {
        name: "Zephyr-7B",
        provider: "Hugging Face",
        license: "Apache 2.0",
        parameters: "7.00B",
        contextWindow: 8192,
        trainingTime: "20 days (64 GPUs)",
        size: "13.74GB",
        throughput: "1300",
        latency: "52",
        gold: 70,
        silver: 55,
        bronze: 40
    },
    {
        name: "Phi-1.5",
        provider: "Microsoft",
        license: "Proprietary",
        parameters: "2.70B",
        contextWindow: 2048,
        trainingTime: "12 days (32 GPUs)",
        size: "2.45GB",
        throughput: "1400",
        latency: "52",
        gold: 65,
        silver: 50,
        bronze: 35
    },
    {
        name: "Mistral-7B",
        provider: "Mistral AI",
        license: "Apache 2.0",
        parameters: "7.00B",
        contextWindow: 8192,
        trainingTime: "15 days (128 GPUs)",
        size: "13.0GB",
        throughput: "1400",
        latency: "55",
        gold: 60,
        silver: 45,
        bronze: 30
    },
    {
        name: "ShearedLlama-2.7B",
        provider: "Hugging Face",
        license: "Apache 2.0",
        parameters: "2.70B",
        contextWindow: 2048,
        trainingTime: "12 days (32 GPUs)",
        size: "5.0GB",
        throughput: "1300",
        latency: "54",
        gold: 55,
        silver: 40,
        bronze: 25
    },
    {
        name: "StableLM-3B",
        provider: "Stability AI",
        license: "Apache 2.0",
        parameters: "3.00B",
        contextWindow: 2048,
        trainingTime: "14 days (64 GPUs)",
        size: "6.5GB",
        throughput: "1250",
        latency: "50",
        gold: 50,
        silver: 35,
        bronze: 20
    },
    {
        name: "Pythia-2.8B",
        provider: "EleutherAI",
        license: "Apache 2.0",
        parameters: "2.80B",
        contextWindow: 2048,
        trainingTime: "12 days (32 GPUs)",
        size: "5.5GB",
        throughput: "1350",
        latency: "50",
        gold: 45,
        silver: 30,
        bronze: 15
    },
    {
        name: "TinyLlama-1.1B",
        provider: "Hugging Face",
        license: "Apache 2.0",
        parameters: "1.10B",
        contextWindow: 2048,
        trainingTime: "8 days (16 GPUs)",
        size: "2.0GB",
        throughput: "1600",
        latency: "45",
        gold: 40,
        silver: 25,
        bronze: 10
    },
    {
        name: "LLaMA-2-7B",
        provider: "Meta",
        license: "LLAMA 2 L",
        parameters: "6.47B",
        contextWindow: 4096,
        trainingTime: "21 days (64 GPUs)",
        size: "13.0GB",
        throughput: "1200",
        latency: "62",
        gold: 35,
        silver: 20,
        bronze: 5
    },
    {
        name: "Open-LLaMA-3B",
        provider: "OpenLM",
        license: "Apache 2.0",
        parameters: "3.00B",
        contextWindow: 4096,
        trainingTime: "18 days (64 GPUs)",
        size: "6.8GB",
        throughput: "1300",
        latency: "60",
        gold: 30,
        silver: 15,
        bronze: 0
    },
    {
        name: "Gemma-2B",
        provider: "Google",
        license: "Proprietary",
        parameters: "2.00B",
        contextWindow: 2048,
        trainingTime: "14 days (32 GPUs)",
        size: "4.67GB",
        throughput: "1450",
        latency: "54",
        gold: 25,
        silver: 10,
        bronze: 0
    },
    {
        name: "Dolly-v2-3B",
        provider: "DataBricks",
        license: "Apache 2.0",
        parameters: "3.00B",
        contextWindow: 2048,
        trainingTime: "10 days (32 GPUs)",
        size: "5.8GB",
        throughput: "1250",
        latency: "55",
        gold: 20,
        silver: 5,
        bronze: 0
    },
    {
        name: "Gemma-3-1B",
        provider: "Google",
        license: "Apache 2.0",
        parameters: "1.00B",
        contextWindow: 32000,
        trainingTime: "30 days (512 GPUs",
        size: "5.8GB",
        throughput: "1250",
        latency: "55",
        gold: 15,
        silver: 0,
        bronze: 0
    },
    {
        name: "Phi-3",
        provider: "Microsoft",
        license: "Apache 2.0",
        parameters: "3.82B",
        contextWindow: 128000,
        trainingTime: "7 days (512 GPUs)",
        size: "5.8GB",
        throughput: "1250",
        latency: "55",
        gold: 10,
        silver: 0,
        bronze: 0
    },
];

const MedalTable = () => {
    const styles = {
        section: {
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '1.5rem'
        } as React.CSSProperties,
        header: {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '1rem'
        } as React.CSSProperties,
        headerTitle: {
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
        } as React.CSSProperties,
        title: {
            fontSize: '1.25rem',
            fontWeight: 700
        } as React.CSSProperties,
        infoBox: {
            backgroundColor: '#F9FAFB',
            borderRadius: '0.5rem',
            padding: '1rem',
            marginBottom: '1.5rem'
        } as React.CSSProperties,
        infoTitle: {
            fontWeight: 600,
            marginBottom: '0.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
        } as React.CSSProperties,
        icon: {
            width: '1.25rem',
            height: '1.25rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
        } as React.CSSProperties,
        infoList: {
            fontSize: '0.875rem',
            color: '#4B5563',
            marginLeft: '1.75rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.5rem'
        } as React.CSSProperties,
        medalItem: {
            display: 'flex',
            gap: '0.5rem'
        } as React.CSSProperties,
        tableContainer: {
            overflowX: 'auto'
        } as React.CSSProperties,
        table: {
            width: '100%',
            minWidth: '1000px'
        } as React.CSSProperties,
        thead: {
            backgroundColor: '#F9FAFB'
        } as React.CSSProperties,
        th: {
            padding: '0.75rem',
            textAlign: 'left' as const,
            color: '#4B5563',
            fontWeight: 500
        } as React.CSSProperties,
        thCenter: {
            padding: '0.75rem',
            textAlign: 'center' as const,
            color: '#4B5563',
            fontWeight: 500
        } as React.CSSProperties,
        tbody: {
            borderTop: '1px solid #E5E7EB'
        } as React.CSSProperties,
        tr: {
            borderBottom: '1px solid #E5E7EB',
            transition: 'background-color 0.2s'
        } as React.CSSProperties,
        trHover: {
            backgroundColor: '#F9FAFB'
        } as React.CSSProperties,
        td: {
            padding: '0.75rem'
        } as React.CSSProperties,
        tdCenter: {
            padding: '0.75rem',
            textAlign: 'center' as const
        } as React.CSSProperties,
        modelName: {
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
        } as React.CSSProperties,
        modelNameText: {
            color: '#2563EB'
        } as React.CSSProperties,
        medalCount: {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.25rem'
        } as React.CSSProperties
    };

    return (
        <section style={styles.section}>
            <div style={styles.header}>
                <div style={styles.headerTitle}>
                    <h2 style={styles.title}>Model Performance Scoreboard</h2>
                </div>
            </div>

            <div style={styles.infoBox}>
                <h3 style={styles.infoTitle}>
                    <span style={styles.icon}>ℹ️</span>
                    Medal Distribution
                </h3>
                <div style={styles.infoList}>
                    <ul style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <li style={styles.medalItem}>
                            <span>🥇</span>
                            <span><strong>Gold Medal</strong>: Outstanding performance across metrics</span>
                        </li>
                        <li style={styles.medalItem}>
                            <span>🥈</span>
                            <span><strong>Silver Medal</strong>: Strong performance with good balance</span>
                        </li>
                        <li style={styles.medalItem}>
                            <span>🥉</span>
                            <span><strong>Bronze Medal</strong>: Solid baseline performance</span>
                        </li>
                    </ul>
                </div>
            </div>

            <div style={styles.infoBox}>
                <h3 style={styles.infoTitle}>
                    <span style={styles.icon}>ℹ️</span>
                    GPU - L4
                </h3>
            </div>

            <div style={styles.tableContainer}>
                <table style={styles.table}>
                    <thead style={styles.thead}>
                        <tr>
                            <th style={styles.th}>Model</th>
                            <th style={styles.th}>Provider</th>
                            <th style={styles.th}>Parameters</th>
                            <th style={styles.th}>Context Window</th>
                            <th style={styles.th}>Training Time</th>
                            <th style={styles.thCenter}>Gold Medals</th>
                            <th style={styles.thCenter}>Silver Medals</th>
                            <th style={styles.thCenter}>Bronze Medals</th>
                        </tr>
                    </thead>
                    <tbody style={styles.tbody}>
                        {modelData.map((model, index) => (
                            <tr key={index} style={styles.tr}>
                                <td style={styles.td}>
                                    <div style={styles.modelName}>
                                        <span style={styles.modelNameText}>{model.name}</span>
                                    </div>
                                </td>
                                <td style={styles.td}>{model.provider}</td>
                                <td style={styles.td}>{model.parameters}</td>
                                <td style={styles.td}>{model.contextWindow}</td>
                                <td style={styles.td}>{model.trainingTime}</td>
                                <td style={styles.tdCenter}>
                                    <div style={styles.medalCount}>
                                        <span>🥇</span>
                                        <span>{model.gold}</span>
                                    </div>
                                </td>
                                <td style={styles.tdCenter}>
                                    <div style={styles.medalCount}>
                                        <span>🥈</span>
                                        <span>{model.silver}</span>
                                    </div>
                                </td>
                                <td style={styles.tdCenter}>
                                    <div style={styles.medalCount}>
                                        <span>🥉</span>
                                        <span>{model.bronze}</span>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div style={
                { marginTop: '2rem' }
            }></div>

            <div style={styles.infoBox}>
                <h3 style={styles.infoTitle}>
                    <span style={styles.icon}>ℹ️</span>
                    GPU - A10G
                </h3>
            </div>

            <div style={styles.tableContainer}>
                <table style={styles.table}>
                    <thead style={styles.thead}>
                        <tr>
                            <th style={styles.th}>Model</th>
                            <th style={styles.th}>Provider</th>
                            <th style={styles.th}>Parameters</th>
                            <th style={styles.th}>Context Window</th>
                            <th style={styles.th}>Training Time</th>
                            <th style={styles.thCenter}>Gold Medals</th>
                            <th style={styles.thCenter}>Silver Medals</th>
                            <th style={styles.thCenter}>Bronze Medals</th>
                        </tr>
                    </thead>
                    <tbody style={styles.tbody}>
                        {modelDataA10G.map((model, index) => (
                            <tr key={index} style={styles.tr}>
                                <td style={styles.td}>
                                    <div style={styles.modelName}>
                                        <span style={styles.modelNameText}>{model.name}</span>
                                    </div>
                                </td>
                                <td style={styles.td}>{model.provider}</td>
                                <td style={styles.td}>{model.parameters}</td>
                                <td style={styles.td}>{model.contextWindow}</td>
                                <td style={styles.td}>{model.trainingTime}</td>
                                <td style={styles.tdCenter}>
                                    <div style={styles.medalCount}>
                                        <span>🥇</span>
                                        <span>{model.gold}</span>
                                    </div>
                                </td>
                                <td style={styles.tdCenter}>
                                    <div style={styles.medalCount}>
                                        <span>🥈</span>
                                        <span>{model.silver}</span>
                                    </div>
                                </td>
                                <td style={styles.tdCenter}>
                                    <div style={styles.medalCount}>
                                        <span>🥉</span>
                                        <span>{model.bronze}</span>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </section>
    );
};

export default MedalTable;