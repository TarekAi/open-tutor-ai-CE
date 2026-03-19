<script lang="ts">
    import { getContext,onMount } from 'svelte';
    import Dashboard from '$lib/components/teacher/pages/Dashboard.svelte';
    import { getMyClasses, getTeacherStats } from '$lib/apis/classe';
    import { browser } from '$app/environment';
    import type { Writable } from 'svelte/store';

    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    let ClassOptions: any[] = [];
    let classesError = "";
    let selectedClass = "";
    let isLoading = true;

    let statsData = {
        stats: { activeStudents: 0, aiResponseRate: 0, successRate: 0, engagement: 0 },
        charts: { 
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            weeklyActive: [], 
            previousWeekly: [], 
            engagementTrend: [] 
        }
    };

    const getToken = () => (browser ? localStorage.getItem('token') ?? '' : '');

    async function loadStats(classId: string) {
        if (!browser) return;
        isLoading = true;
        classesError = ""; 
        
        try {
            const token = getToken();
            const cid = (classId && classId !== "undefined") ? classId : undefined;
            const data = await getTeacherStats(token, cid);
            
            if (data && data.stats && data.charts) {
                statsData = data;
            }
        } catch (err: any) {
            console.error("Stats Error:", err);
            classesError = 'Could not load stats. Check connection.';
        } finally {
            isLoading = false;
        }
    }

    onMount(async () => {
        try {
            const token = getToken();
            ClassOptions = await getMyClasses(token) || [];
        } catch (err: any) {
            console.error("Classes Error:", err);
            classesError = "Failed to load classes.";
            isLoading = false;
        }
    });

    $: if (browser && typeof selectedClass === 'string') {
        loadStats(selectedClass);
    }
</script>

<div class="px-4 sm:px-8 py-2 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
    <div class="flex items-center gap-4 w-full sm:w-auto">
        <div class="relative group w-full sm:w-auto">            
            <select bind:value={selectedClass}
                class="w-full sm:min-w-[160px] h-[42px] px-4 pr-10 border border-gray-200 dark:border-gray-800 rounded-xl bg-white dark:bg-gray-900 text-[13px] font-bold text-gray-700 dark:text-gray-200 outline-none appearance-none cursor-pointer hover:border-blue-500 transition-all shadow-sm">
                <option value="">{$i18n.t('All Classes')}</option>
                {#each ClassOptions as cls}
                    <option value={cls.id}>{cls.name}</option>
                {/each}
            </select>
        </div>
    </div>
</div>

{#if classesError}
    <div class="mx-4 sm:mx-8 mt-2 p-3 bg-red-50 dark:bg-red-500/10 border border-red-100 dark:border-red-500/20 rounded-xl text-red-500 text-[11px] font-bold uppercase tracking-wider flex items-center gap-2">
        <span>⚠️</span> {classesError}
    </div>
{/if}

<Dashboard {statsData} {isLoading} />