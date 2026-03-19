<script lang="ts">
    import { onMount, tick } from 'svelte';
    import Chart from 'chart.js/auto';
    import { getContext } from 'svelte';
    import type { Writable } from 'svelte/store';

    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    
    export let statsData: any = null;
    export let isLoading: boolean = false;

    let chartCanvas: HTMLCanvasElement;
    let engCanvas: HTMLCanvasElement;
    let chartObj: any;
    let engObj: any;


    $: dashboardStats = [
        { 
            label: $i18n.t('Active Students'), 
            val: statsData?.stats?.activeStudents?.toLocaleString() || '0', 
            trend: `${Math.abs(statsData?.trends?.activeStudents || 0)}%`, 
            type: (statsData?.trends?.activeStudents || 0) >= 0 ? 'up' : 'down' 
        },
        { 
            label: $i18n.t('AI Response'), 
            val: '0%', 
            trend: '0%', 
            type: 'up' 
        },
        { 
            label: $i18n.t('Success Rate'), 
            val: `${statsData?.stats?.successRate || 0}%`, 
            trend: `${Math.abs(statsData?.trends?.successRate || 0)}%`, 
            type: (statsData?.trends?.successRate || 0) >= 0 ? 'up' : 'down' 
        },
        { 
            label: $i18n.t('Engagement'), 
            val: `${statsData?.stats?.engagement || 0}%`, 
            trend: `${Math.abs(statsData?.trends?.engagement || 0)}%`, 
            type: (statsData?.trends?.engagement || 0) >= 0 ? 'up' : 'down' 
        }
    ];

    async function renderCharts() {
        await tick();
        if (!chartCanvas || !engCanvas || !statsData?.charts) return;
        if (chartObj) chartObj.destroy();
        if (engObj) engObj.destroy();
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.color = '#9ca3af';

        const weeklyActive = statsData.charts.weeklyActive?.length ? statsData.charts.weeklyActive : [0, 0, 0, 0, 0, 0, 0];
        const previousWeekly = statsData.charts.previousWeekly?.length ? statsData.charts.previousWeekly : [0, 0, 0, 0, 0, 0, 0];
        const engagementTrend = statsData.charts.engagementTrend?.length ? statsData.charts.engagementTrend : [0, 0, 0, 0, 0, 0, 0];
        const labels = statsData.charts.labels?.length ? statsData.charts.labels : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

        // 1. Weekly Active Students Chart
        chartObj = new Chart(chartCanvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    { 
                        label: $i18n.t('Current Week'), 
                        data: weeklyActive, 
                        borderColor: '#6366f1',
                        backgroundColor: '#6366f1',
                        borderWidth: 2,
                        fill: false, 
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 6
                    },
                    { 
                        label: $i18n.t('Previous Week'), 
                        data: previousWeekly, 
                        borderColor: '#f97316',
                        backgroundColor: '#f97316',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: false, 
                interaction: { mode: 'index', intersect: false },
                plugins: { 
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#374151',
                        padding: 12,
                        cornerRadius: 8,
                        titleFont: { size: 13 },
                        bodyFont: { size: 13 },
                        displayColors: false
                    }
                },
                scales: {
                    x: { grid: { display: false }, border: { display: false } },
                    y: { 
                        beginAtZero: true, 
                        grid: {  display : false  },
                        border: { display: false },
                        ticks: {
                            callback: function(value) {
                                return value; 
                            }
                        }
                    }
                }
            }
        });

        // 2. Engagement Over Time Chart 
        engObj = new Chart(engCanvas, {
            type: 'line',
            data: {
                labels: labels, 
                datasets: [{ 
                    label: $i18n.t('Engagement'), 
                    data: engagementTrend, 
                    borderColor: '#6366f1',
                    backgroundColor: '#6366f1',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6
                }]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: false, 
                interaction: { mode: 'index', intersect: false },
                plugins: { 
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#374151',
                        padding: 12,
                        cornerRadius: 8,
                        displayColors: false
                    }
                },
                scales: {
                    x: { grid: { display: false }, border: { display: false } },
                    y: { 
                        beginAtZero: true, 
                        grid: { display:false },
                        border: { display: false }
                    }
                }
            }
        });
    }

    $: if (statsData && !isLoading) {
        renderCharts();
    }

    onMount(() => {
        if (statsData) renderCharts();
    });
</script>

<div class="p-4 w-full {isLoading ? 'opacity-40 transition-opacity' : ''} transition-colors duration-500 ">
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {#each dashboardStats as stat}
            <div class="bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-[1.2rem] p-6 shadow-sm flex flex-col relative transition-all group hover:border-blue-500/30">
                <span class="text-gray-400 dark:text-gray-500 text-[10px] font-black uppercase tracking-widest">
                    {stat.label}
                </span>
                <span class="text-[24px] font-black text-gray-800 dark:text-white mt-1 tracking-tight">
                    {stat.val}
                </span>
                
                <div class="absolute top-4 right-4 text-[9px] font-bold flex items-center gap-0.5 px-1.5 py-0.5 rounded-md
                    {stat.type === 'up' ? 'text-[#10B981] bg-emerald-50 dark:bg-emerald-500/10' : 'text-rose-500 bg-rose-50 dark:bg-rose-500/10'}">
                     <span>{stat.type === 'up' ? '↑' : '↓'}</span> 
                    {stat.trend}
                </div>
            </div>
        {/each}
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        
        <div class="bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-[1.5rem] p-5 shadow-sm">
            <div class="flex items-center justify-between mb-4">
                <div>
                    <h4 class="text-[12px] font-black text-gray-800 dark:text-white tracking-tight uppercase">{$i18n.t('Weekly Students')}</h4>
                    <p class="text-[9px] text-gray-400 font-medium uppercase tracking-wider">{$i18n.t('Activity')}</p>
                </div>
                <div class="flex gap-3 text-[9px] text-gray-500 dark:text-gray-400 font-black uppercase tracking-tighter">
                    <div class="flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-[#6366f1]"></span> {$i18n.t('Current')}</div>
                    <div class="flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-[#f97316]"></span> {$i18n.t('Previous')}</div>
                </div>
            </div>
            <div class="h-[220px] relative w-full">
                <canvas bind:this={chartCanvas}></canvas>
            </div>
        </div>

        <div class="bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-[1.5rem] p-5 shadow-sm">
            <div class="flex items-center justify-between mb-4">
                <div>
                    <h4 class="text-[12px] font-black text-gray-800 dark:text-white tracking-tight uppercase">{$i18n.t('Engagement Rate')}</h4>
                    <p class="text-[9px] text-gray-400 font-medium uppercase tracking-wider">{$i18n.t('Metrics')}</p>
                </div>
                <button class="text-gray-400 hover:text-blue-500 transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path></svg>
                </button>
            </div>
            <div class="h-[220px] relative w-full">
                <canvas bind:this={engCanvas}></canvas>
            </div>
        </div>

    </div>
</div>