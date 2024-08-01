import React, {useEffect, useState} from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';
import './GridLayout.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const generateZeroes = () => {
    const data = [];
    for (let i = 0; i < 20; i++) {
        data.push(0);
    }
    return data;
};

const generateChartData = (data, borderColor = 'rgb(17,103,157)') => {

    return {
        labels: Array.from({ length: data.length }, (_, i) => i + 1),
        datasets: [
            {
                label: 'Data',
                data: data,
                fill: false,
                backgroundColor: 'rgba(75,192,192,0.4)',
                borderColor: borderColor,
            },
        ],
    };
};

const GridLayout = () => {

    const changeBorder = (f, rms_values) => {
        const maxNumber = (Math.max(...rms_values))
        if (maxNumber >= 2000) {
            f('#b70d0d')
        }
        if (maxNumber >= 1500 && maxNumber < 2000) {
            f('#e14024')
        }
        if (maxNumber >= 1000 && maxNumber < 1500) {
            f('#e16c24')
        }
        if (maxNumber >= 500 && maxNumber < 1000) {
            f('#e1a524')
        }
        if (maxNumber >= 250 && maxNumber < 500) {
            f('#dbe124')
        }
        if (Math.max(...rms_values) < 250) {
            f('#11679D')
        }
    }

    useEffect(() => {
        const socket = new WebSocket('ws://localhost:12000');

        socket.onopen = () => {
            console.log('WebSocket connection established');
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data)
            data.forEach(
                (item) => {
                    if (item.mic_id === 3) {
                        changeBorder(setData1Border, item.rms_values)
                        setData1(item.rms_values)
                    }
                    if (item.mic_id === 5) {
                        changeBorder(setData2Border, item.rms_values)
                        setData2(item.rms_values)
                    }
                }
            )
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        socket.onclose = () => {
            const zeroes = generateZeroes()

            setData1(zeroes)
            setData2(zeroes)
            setData3(zeroes)
            setData4(zeroes)

            setData1Border('#11679D')
            setData2Border('#11679D')
            setData3Border('#11679D')
            setData4Border('#11679D')
            console.log('WebSocket connection closed');
        };

        // Cleanup function to close the WebSocket connection when the component unmounts
        return () => {
            socket.close();
        };
    }, []);
    const zeroes = generateZeroes()

    const [data1, setData1] = useState(zeroes)
    const [data2, setData2] = useState(zeroes)
    const [data3, setData3] = useState(zeroes)
    const [data4, setData4] = useState(zeroes)

    const [data1Border, setData1Border] = useState('#11679D')
    const [data2Border, setData2Border] = useState('#11679D')
    const [data3Border, setData3Border] = useState('#11679D')
    const [data4Border, setData4Border] = useState('#11679D')

    return (
        <div className="container">

            <header className="gr-header">
                <h1>Sonar</h1>
            </header>

            <div className={`grid-container box-count-${4}`}>

                <div className="grid-item">
                    <Line data={generateChartData(data1, data1Border)} />
                </div>

                <div className="grid-item">
                    <Line data={generateChartData(data2, data2Border)} />
                </div>

                <div className="grid-item">
                    <Line data={generateChartData(data3, data3Border)} />
                </div>

                <div className="grid-item">
                    <Line data={generateChartData(data4, data4Border)} />
                </div>

            </div>

        </div>
    );
};

export default GridLayout;
