/* eslint-disable @next/next/no-img-element */
"use client"

import React from 'react';
import { Route } from 'lucide-react';
import MedalTable from './table';
import DataAnalysisSection from './data';

export default function HomeClient() {
  return (
    <div className="w-full overflow-hidden no-scrollbar">
      <div className="min-h-screen bg-grid-pattern">
        <section className="max-w-7xl mx-auto px-4 py-12">
          <div className="flex flex-col items-center text-center gap-6">
            <div className="relative flex justify-center items-center gap-4">
              <h1 className="text-xl lg:text-5xl font-bold text-yellow-800 opacity-40">Small Language Models Benchmarking</h1>
              <div className="hidden lg:flex items-center justify-center">
                <Route className="w-12 h-12 text-yellow-400" />
              </div>
            </div>
            <div className="flex flex-col gap-4 lg:my-4">
              <h2 className="text-lg lg:text-4xl font-semibold">
                All we know about Small LLMs
              </h2>
              {/* <div className="bg-gradient-to-r from-blue-200 to-purple-200 py-2 px-6 rounded-lg">
                <span className="text-2xl font-bold text-gray-800">
                  on Edge Devices
                </span>
              </div> */}
            </div>
            <div className='lg:w-3/4 bg-gray-100 rounded-md flex flex-col justify-center items-start p-4'>
              <h3 className="text-lg font-bold">
                #Citation
              </h3>
              <p className="text-md font-medium text-justify">
                <span className='text-yellow-800 opacity-40'>Title:</span> SLM-Bench: A Comprehensive Benchmark of Small Language Models on Environmental Impacts.
              </p>
              <p className="text-md font-medium text-justify">
                <span className='text-yellow-800 opacity-40'>Abstract:</span> Small Language Models (SLMs) offer computational efficiency and accessibility, yet a systematic evaluation of their performance and environmental impact remains lacking. We introduce SLM-Bench, the first benchmark specifically designed to assess SLMs across multiple dimensions, including accuracy, computational efficiency, and sustainability metrics. SLM-Bench evaluates 15 SLMs on 9 NLP tasks using 23 datasets spanning 14 domains, providing a rigorous comparison of their effectiveness. Unlike prior benchmarks, SLM-Bench quantifies 11 metrics across correctness, computation, and consumption, enabling a holistic assessment of efficiency trade-offs. Our evaluation considers controlled hardware conditions, ensuring fair comparisons across models. We develop an open-source benchmarking pipeline with standardized evaluation protocols to facilitate reproducibility and further research. Our findings highlight the diverse trade-offs among SLMs, where some models excel in accuracy while others achieve superior energy efficiency. SLM-Bench sets a new standard for SLM evaluation, bridging the gap between resource efficiency and real-world applicability.
              </p>
              <p className="text-md font-medium text-justify">
                <span className='text-yellow-800 opacity-40'>Github:</span> <a href='https://anonymous.4open.science/r/slm-bench-experiments-87F6' target='_blank' className='text-blue-500 underline'>https://anonymous.4open.science/r/slm-bench-experiments-87F6</a>
              </p>
            </div>
            <div className="flex flex-col lg:flex-row gap-4 mt-4">
              <button className="relative inline-flex items-center justify-center p-0.5 mb-2 me-2 overflow-hidden font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-purple-600 to-blue-500 group-hover:from-purple-600 group-hover:to-blue-500 hover:text-white dark:text-white focus:ring-4 focus:outline-none focus:ring-blue-300 dark:focus:ring-blue-800">
                <span className="w-full flex justify-center items-center gap-2 text-md relative px-5 py-2.5 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent">
                  <img src="https://cdn-icons-png.flaticon.com/128/3800/3800833.png" alt='alt' className='w-6 h-6' />
                  Accuracy
                </span>
              </button>
              <button className="relative inline-flex items-center justify-center p-0.5 mb-2 me-2 overflow-hidden font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-cyan-500 to-blue-500 group-hover:from-cyan-500 group-hover:to-blue-500 hover:text-white dark:text-white focus:ring-4 focus:outline-none focus:ring-cyan-200 dark:focus:ring-cyan-800">
                <span className="w-full flex justify-center items-center gap-2 text-md  relative px-5 py-2.5 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent">
                  <img src="https://cdn-icons-png.flaticon.com/128/10165/10165422.png" alt='alt' className='w-6 h-6' />
                  Cost on Device
                </span>
              </button>
              <button className="relative inline-flex items-center justify-center p-0.5 mb-2 me-2 overflow-hidden font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-green-400 to-blue-600 group-hover:from-green-400 group-hover:to-blue-600 hover:text-white dark:text-white focus:ring-4 focus:outline-none focus:ring-green-200 dark:focus:ring-green-800">
                <span className="w-full flex justify-center items-center gap-2 text-md  relative px-5 py-2.5 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent">
                  <img src="https://cdn-icons-png.flaticon.com/128/17638/17638445.png" alt='alt' className='w-6 h-6' />
                  Runtime
                </span>
              </button>
              <button className="relative inline-flex items-center justify-center p-0.5 mb-2 me-2 overflow-hidden font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-purple-500 to-pink-500 group-hover:from-purple-500 group-hover:to-pink-500 hover:text-white dark:text-white focus:ring-4 focus:outline-none focus:ring-purple-200 dark:focus:ring-purple-800">
                <span className="w-full flex justify-center items-center gap-2 text-md  relative px-5 py-2.5 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent">
                  <img src="https://cdn-icons-png.flaticon.com/128/3103/3103468.png" alt='alt' className='w-6 h-6' />
                  Power Consumption
                </span>
              </button>
              <button className="relative inline-flex items-center justify-center p-0.5 mb-2 me-2 overflow-hidden font-medium text-gray-900 rounded-lg group bg-gradient-to-br from-pink-500 to-orange-400 group-hover:from-pink-500 group-hover:to-orange-400 hover:text-white dark:text-white focus:ring-4 focus:outline-none focus:ring-pink-200 dark:focus:ring-pink-800">
                <span className="w-full flex justify-center items-center gap-2 text-md  relative px-5 py-2.5 transition-all ease-in duration-75 bg-white dark:bg-gray-900 rounded-md group-hover:bg-transparent group-hover:dark:bg-transparent">
                  <img src="https://cdn-icons-png.flaticon.com/128/8636/8636541.png" alt='alt' className='w-6 h-6' />
                  CO2 Emissions
                </span>
              </button>
            </div>
          </div>
        </section>
        <MedalTable />
        <div className='w-full flex justify-center items-center'>
          <img src="https://res.cloudinary.com/farmcode/image/upload/v1748152920/other/eif3wfkcdpl6wixdl9ma.png" alt='alt' className='lg:w-3/4' />
        </div>
        <DataAnalysisSection />
      </div>
    </div>
  )
}