/* eslint-disable @next/next/no-img-element */
import React from 'react';
import { Boxes } from 'lucide-react';

const DataAnalysisSection = () => {
    return (
        <section style={{
            maxWidth: "1200px",
            margin: "0 auto",
            padding: "2rem 1rem"
        }}>
            <div style={{
                display: "flex",
                alignItems: "center",
                gap: "0.5rem",
                marginBottom: "1rem"
            }}>
                <Boxes style={{
                    width: "1.5rem",
                    height: "1.5rem",
                    color: "#ef4444"
                }} />
                <h2 style={{
                    fontSize: "1.25rem",
                    fontWeight: "700"
                }}>Our Proposed & Results</h2>
            </div>
            <div style={{
                display: "grid",
                gridTemplateColumns: "1fr",
                gap: "2rem",
            }}>
                <div style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "2rem"
                }}>
                    <div style={{
                        backgroundColor: "white",
                        borderRadius: "0.5rem",
                        padding: "1.5rem",
                        boxShadow: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                        border: "1px solid #f3f4f6"
                    }}>
                        <h3 style={{
                            fontSize: "1.125rem",
                            fontWeight: "700",
                            marginBottom: "1rem"
                        }}>Overview of SLMs</h3>
                        <p
                            className='text-justify'
                            style={{
                                color: "#4b5563",
                                marginBottom: "1.5rem"
                            }}>
                            Small Language Models (SLMs) have gained significant traction in both research and industry, with continuous advancements in recent years. Since the release of GPT-Neo-1.3B in 2021, the field has witnessed a steady stream of new models, each contributing to the expanding capabilities of lightweight AI systems.
                        </p>
                        <p
                            className='text-justify'
                            style={{
                                color: "#4b5563",
                                marginBottom: "1.5rem"
                            }}>
                            By late 2022 and throughout 2023, notable models such as <strong>Dolly-v2</strong>, <strong>Pythia</strong>, <strong>LLaMA-2</strong>, <strong>TinyLlama</strong>, and <strong>Mistral</strong> emerged, demonstrating substantial improvements in performance and efficiency. This momentum continued with the introduction of models like <strong>Zephyr</strong>, <strong>ShearedLLaMA</strong>, <strong>Gemma</strong>, and <strong>Phi</strong>, reflecting growing competitiveness in the SLM landscape.
                        </p>
                        <p
                            className='text-justify'
                            style={{
                                color: "#4b5563",
                                marginBottom: "1.5rem"
                            }}>
                            More recently, the evolution of SLMs has accelerated with the release of <strong>Open-LLaMA-3B</strong>, <strong>LLaMA-3-8B</strong>, <strong>Gemma-3-1B</strong>, and <strong>Phi-3-3.8B</strong> between mid-2024 and early 2025. These new models mark a significant step forward in the development of compact yet powerful language models. As innovation continues, SLMs are expected to play an increasingly vital role in AI research and real-world applications.
                        </p>
                        <div style={{ position: "relative" }}>
                            <div style={{
                                width: "100%",
                                height: "200px",
                                backgroundColor: "#FFF1CC",
                                borderRadius: "0.5rem",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                paddingTop: "1rem",
                                paddingBottom: "1rem"
                            }}>
                                <img
                                    src="https://res.cloudinary.com/farmcode/image/upload/v1748153303/other/rhey1axw1ku9lsqgeawz.png"
                                    alt="alt"
                                    style={{
                                        objectFit: "contain",
                                        width: "100%",
                                        height: "100%"
                                    }}
                                />
                            </div>
                        </div>
                    </div>
                    <div style={{
                        backgroundColor: "white",
                        borderRadius: "0.5rem",
                        padding: "1.5rem",
                        boxShadow: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                        border: "1px solid #f3f4f6"
                    }}>
                        <h3 style={{
                            fontSize: "1.125rem",
                            fontWeight: "700",
                            marginBottom: "1rem"
                        }}>Evaluation of SLM-Bench and Its Impact on SLM Development</h3>
                        <p
                            className='text-justify'
                            style={{
                                color: "#4b5563",
                                marginBottom: "1.5rem"
                            }}>
                            SLM-Bench provides a comprehensive evaluation framework for Small Language Models (SLMs), assessing performance across diverse datasets, tasks, and domains. It ensures rigorous testing in areas like reasoning, classification, and text generation while covering fields such as healthcare, mathematics, and linguistics. Beyond accuracy, it evaluates efficiency through energy consumption, CO₂ emissions, and computational costs, promoting sustainable AI development. This holistic approach helps optimize SLMs for real-world applications while maintaining responsible AI deployment. As SLMs evolve, benchmarks like SLM-Bench will be essential in driving innovation and efficiency.
                        </p>
                        <div style={{ position: "relative" }}>
                            <div style={{
                                borderRadius: "0.5rem",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                paddingTop: "1rem",
                                paddingBottom: "1rem"
                            }}>
                                <img
                                    src="https://res.cloudinary.com/farmcode/image/upload/v1741449837/other/akwddql5kijakqwmbfgq.png"
                                    alt="alt"
                                    style={{
                                        objectFit: "contain",
                                    }}
                                />
                            </div>
                        </div>
                    </div>
                    <div style={{
                        backgroundColor: "white",
                        borderRadius: "0.5rem",
                        padding: "1.5rem",
                        boxShadow: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                        border: "1px solid #f3f4f6"
                    }}>
                        <h3 style={{
                            fontSize: "1.125rem",
                            fontWeight: "700",
                            marginBottom: "1rem"
                        }}>A Comprehensive Pipeline for Evaluating Small Language Models</h3>
                        <p
                            className='text-justify'
                            style={{
                                color: "#4b5563",
                                marginBottom: "1.5rem"
                            }}>
                            SLM-Bench employs a structured evaluation pipeline to assess Small Language Models (SLMs) across multiple tasks, datasets, and performance metrics. It measures correctness through accuracy, F1 score, BLEU, ROUGE, and METEOR, while also considering efficiency factors like runtime, energy consumption, and computational cost. The process involves data loading, preprocessing, model execution, and post-processing, followed by evaluation and reporting. By integrating both correctness and efficiency metrics, SLM-Bench ensures a comprehensive assessment of SLM capabilities. This framework is crucial for optimizing models for real-world applications while promoting sustainable AI development.
                        </p>
                        <div style={{ position: "relative" }}>
                            <div style={{
                                borderRadius: "0.5rem",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                paddingTop: "1rem",
                                paddingBottom: "1rem"
                            }}>
                                <img
                                    src="https://res.cloudinary.com/farmcode/image/upload/v1741449837/other/znzw9mfqbmdxb0xchacq.png"
                                    alt="alt"
                                    style={{
                                        objectFit: "contain",
                                    }}
                                />
                            </div>
                        </div>
                    </div>
                    <div style={{
                        backgroundColor: "white",
                        borderRadius: "0.5rem",
                        padding: "1.5rem",
                        boxShadow: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                        border: "1px solid #f3f4f6"
                    }}>
                        <h3 style={{
                            fontSize: "1.125rem",
                            fontWeight: "700",
                            marginBottom: "1rem"
                        }}>Performance Comparison of Small Language Models</h3>
                        <p
                            className='text-justify'
                            style={{
                                color: "#4b5563",
                                marginBottom: "1.5rem"
                            }}>
                            The radar charts visualize the correctness of different Small Language Models (SLMs), highlighting their strengths and weaknesses across various dimensions. Zephyr-7B and Mistral-7B demonstrate superior correctness, outperforming other models, while GPT-Neo-1.3B exhibits strong performance in certain aspects but lags in overall correctness. ShearedLlama-2.7B and Phi-1.5B show competitive results but remain behind leading models. These comparisons provide valuable insights into model efficiency, guiding further improvements in SLM development.
                        </p>
                        <div style={{ position: "relative" }}>
                            <div style={{
                                borderRadius: "0.5rem",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                paddingTop: "1rem",
                                paddingBottom: "1rem"
                            }}>
                                <img
                                    src="https://res.cloudinary.com/farmcode/image/upload/v1748152920/other/ryc7yjzxlkwxncxgwk5s.png"
                                    alt="alt"
                                    style={{
                                        objectFit: "contain",
                                    }}
                                />
                            </div>
                        </div>
                    </div>
                    {/* <div style={{
                        backgroundColor: "white",
                        borderRadius: "0.5rem",
                        padding: "1.5rem",
                        boxShadow: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                        border: "1px solid #f3f4f6"
                    }}>
                        <h3 style={{
                            fontSize: "1.125rem",
                            fontWeight: "700",
                            marginBottom: "1rem"
                        }}>Performance Progress of SLMs Over Time</h3>
                        <p
                            className='text-justify'
                            style={{
                                color: "#4b5563",
                                marginBottom: "1.5rem"
                            }}>
                            The chart illustrates significant improvements in Small Language Model (SLM) performance from 2022 to 2024 across multiple tasks. Notably, model effectiveness has increased by 10.4%, 13.5%, and 13.5% for three different tasks, reflecting advancements in accuracy, reasoning, and overall capabilities. The ranking distribution highlights how newer models like Mistral-7B and Zephyr-7B consistently secure higher positions compared to earlier models. These improvements indicate a trend towards more robust and efficient SLMs, reinforcing their growing impact in AI applications.
                        </p>
                        <div style={{ position: "relative" }}>
                            <div style={{
                                borderRadius: "0.5rem",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                paddingTop: "1rem",
                                paddingBottom: "1rem"
                            }}>
                                <img
                                    src="https://res.cloudinary.com/farmcode/image/upload/v1740134336/other/cmk3q68krhg1ppywi19g.png"
                                    alt="alt"
                                    style={{
                                        objectFit: "contain",
                                    }}
                                />
                            </div>
                        </div>
                    </div> */}
                </div>
            </div>
        </section>
    );
};

export default DataAnalysisSection;