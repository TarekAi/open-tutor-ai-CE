<script lang="ts">
    import { getMyClasses, getStudentsByClassId } from '$lib/apis/classe';
    import { onMount, getContext } from 'svelte';
    import { browser } from '$app/environment';
    import type { Writable } from 'svelte/store';
    import { toast } from 'svelte-sonner';
    import { fly } from 'svelte/transition';

    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    let classes: any[] = [];
    let allEnrollments: any[] = [];
    let selectedClassId: string = 'all';
    let loading = true;
    
    const getToken = () => (browser ? localStorage.getItem('token') ?? '' : '');

    $: filteredStudents = (() => {
        let studentsMap = new Map();
        let dataToProcess = selectedClassId === 'all' ? allEnrollments 
            : allEnrollments.filter(en => en.classId === selectedClassId);

        dataToProcess.forEach(en => {
            if (!en.user) return;
            const studentId = en.user.id;
            
            if (!studentsMap.has(studentId)) {
                studentsMap.set(studentId, {
                    id: studentId, 
                    name: en.user.name,
                    email: en.user.email,
                    avatar: en.user.profile_image_url || `https://ui-avatars.com/api/?name=${en.user.name}&background=random`,
                    points: 0,
                    courseCount: 0
                });
            }
            let s = studentsMap.get(studentId);
            s.points += en.points || 0;
            s.courseCount += 1;
        });

        return Array.from(studentsMap.values())
            .sort((a, b) => b.points - a.points)
            .map((s, i) => ({ ...s, rank: i + 1 }));
    })();

    async function loadData() {
        const token = getToken();
        if (!token) return;
        try {
            loading = true;
            classes = await getMyClasses(token);
            const promises = classes.map(async (cls) => {
                try {
                    const students = await getStudentsByClassId(token, cls.id);
                    return students.map((s: any) => ({ ...s, classId: cls.id }));
                } catch (e) { return []; }
            });
            const results = await Promise.all(promises);
            allEnrollments = results.flat();
        } catch (err) {
            console.error("Error loading students:", err);
            toast.error($i18n.t('Failed to load students'));
        } finally {
            loading = false;
        }
    }
    onMount(loadData);
</script>

<div class="p-3 md:p-6 lg:p-8 bg-[#f8fafc] dark:bg-black font-['Inter']">
    <div class="max-w-7xl mx-auto bg-white dark:bg-[#0a0a0a] rounded-[20px] md:rounded-[32px] shadow-sm border border-slate-200 dark:border-white/10 overflow-hidden">
        
        <div class="p-5 md:p-8 border-b border-slate-100 dark:border-white/5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 bg-white dark:bg-[#0a0a0a]">
            <div class="flex items-center gap-4">
                <div class="p-3 bg-indigo-600 rounded-2xl text-white shadow-lg shadow-indigo-500/20">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>
                </div>
                <div>
                    <h3 class="text-xl md:text-2xl font-black text-slate-800 dark:text-white m-0 uppercase tracking-tight italic">{$i18n.t('Leaderboard')}</h3>
                    <p class="text-xs md:text-sm text-slate-400 dark:text-gray-500 font-medium leading-none mt-1.5 uppercase tracking-widest">{$i18n.t('Top performing students')}</p>
                </div>
            </div>

            <div class="relative w-full sm:w-auto min-w-[240px] group">
                <select bind:value={selectedClassId}
                    class="w-full bg-slate-50 dark:bg-white/5 text-slate-700 dark:text-white py-3.5 pl-11 pr-10 rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all cursor-pointer appearance-none font-bold text-sm">
                    <option value="all" class="dark:bg-black font-sans">🌐 {$i18n.t('Global Ranking')}</option>
                    {#each classes as cls}
                        <option value={cls.id} class="dark:bg-black font-sans">📚 {cls.name}</option>
                    {/each}
                </select>
                <div class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-indigo-500 transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
                </div>
            </div>
        </div>

        {#if loading}
            <div class="flex flex-col items-center justify-center p-24 md:p-40 bg-white dark:bg-[#0a0a0a]">
                <div class="relative w-14 h-14">
                    <div class="absolute inset-0 rounded-full border-[3px] border-indigo-500/10"></div>
                    <div class="absolute inset-0 rounded-full border-[3px] border-t-indigo-600 animate-spin"></div>
                </div>
                <p class="mt-8 text-slate-400 dark:text-gray-600 text-[10px] font-black animate-pulse uppercase tracking-[0.3em]">{$i18n.t('Syncing Data...')}</p>
            </div>
        {:else}
            <div class="bg-white dark:bg-[#0a0a0a]">
                <table class="w-full border-separate border-spacing-0 hidden md:table">
                    <thead>
                        <tr class="bg-slate-50/50 dark:bg-white/[0.02]">
                            <th class="py-5 px-8 text-left text-[10px] font-black text-slate-400 dark:text-gray-500 uppercase tracking-[0.15em]">{$i18n.t('Rank')}</th>
                            <th class="py-5 px-8 text-left text-[10px] font-black text-slate-400 dark:text-gray-500 uppercase tracking-[0.15em]">{$i18n.t('Student')}</th>
                            <th class="py-5 px-8 text-center text-[10px] font-black text-slate-400 dark:text-gray-500 uppercase tracking-[0.15em]">{$i18n.t('Activity')}</th>
                            <th class="py-5 px-8 text-right text-[10px] font-black text-slate-400 dark:text-gray-500 uppercase tracking-[0.15em]">{$i18n.t('Performance')}</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 dark:divide-white/5">
                        {#each filteredStudents as student, i (student.id)}
                            <tr in:fly={{ y: 15, delay: i * 30 }} class="group hover:bg-slate-50 dark:hover:bg-white/[0.03] transition-all duration-200">
                                <td class="py-5 px-8">
                                    <span class="w-10 h-10 flex items-center justify-center rounded-xl 
                                        {student.rank === 1 ? 'bg-amber-100 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400 border border-amber-200/50 shadow-sm shadow-amber-500/10' : 
                                         student.rank === 2 ? 'bg-slate-100 text-slate-600 dark:bg-white/10' : 
                                         student.rank === 3 ? 'bg-orange-50 text-orange-600 dark:bg-orange-500/20' : 
                                         'bg-slate-50 dark:bg-white/5 text-slate-400'} 
                                        font-black text-sm">
                                        {student.rank}
                                    </span>
                                </td>
                                <td class="py-5 px-8">
                                    <div class="flex items-center gap-4">
                                        <div class="relative shrink-0">
                                            <img src={student.avatar} alt="" class="w-12 h-12 rounded-2xl object-cover ring-4 ring-white dark:ring-[#111] shadow-sm" />
                                            {#if student.rank === 1}<div class="absolute -top-2.5 -right-2.5 text-lg drop-shadow-md">👑</div>{/if}
                                        </div>
                                        <div class="flex flex-col min-w-0">
                                            <span class="font-bold text-slate-800 dark:text-gray-100 text-sm truncate">{student.name}</span>
                                            <span class="text-[11px] text-slate-400 dark:text-gray-500 truncate font-medium uppercase tracking-wider">{student.email}</span>
                                        </div>
                                    </div>
                                </td>
                                <td class="py-5 px-8 text-center">
                                    <span class="inline-flex items-center px-3 py-1.5 rounded-xl bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 text-[10px] font-black uppercase tracking-widest">
                                        {student.courseCount} {$i18n.t('Classes')}
                                    </span>
                                </td>
                                <td class="py-5 px-8">
                                    <div class="flex items-center justify-end gap-6">
                                        <div class="flex flex-col items-end">
                                            <div class="flex items-center gap-1.5">
                                                <span class="text-xl font-black text-emerald-600 dark:text-emerald-400 tabular-nums italic">
                                                    {student.points.toLocaleString()}
                                                </span>
                                                <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                                            </div>
                                            <span class="text-[8px] font-black text-slate-400 dark:text-gray-600 uppercase tracking-[0.2em]">{$i18n.t('Total XP')}</span>
                                        </div>
                                        
                                        <a href="/teacher/Students/{student.id}?classId={selectedClassId === 'all' ? (allEnrollments.find(e => e.user.id === student.id)?.classId) : selectedClassId}" 
                                        class="p-3 bg-slate-50 dark:bg-white/5 hover:bg-indigo-600 hover:text-white hover:-translate-y-0.5 dark:hover:bg-indigo-600 text-slate-400 dark:text-gray-500 rounded-xl transition-all duration-200 border border-slate-200 dark:border-white/10"
                                        title={$i18n.t('Manage Student')}>
                                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>
                                            </svg>
                                        </a>
                                    </div>
                                </td>
                            </tr>
                        {:else}
                            <tr>
                                <td colspan="4" class="py-24 text-center">
                                    <div class="opacity-20 flex flex-col items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="mb-4"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="17" y1="8" x2="22" y2="13"/><line x1="22" y1="8" x2="17" y2="13"/></svg>
                                        <p class="text-slate-500 font-black text-xs uppercase tracking-widest">{$i18n.t('No student data available')}</p>
                                    </div>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>

                <div class="md:hidden divide-y divide-slate-100 dark:divide-white/5">
                    {#each filteredStudents as student, i (student.id)}
                        <div in:fly={{ y: 15, delay: i * 20 }} class="p-4 flex flex-col gap-4 active:bg-slate-50 dark:active:bg-white/5 transition-colors">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center gap-3">
                                    <div class="relative shrink-0">
                                        <img src={student.avatar} alt="" class="w-12 h-12 rounded-2xl object-cover ring-2 ring-slate-100 dark:ring-white/10 shadow-sm" />
                                        <span class="absolute -top-1.5 -left-1.5 w-6 h-6 flex items-center justify-center rounded-lg bg-indigo-600 text-white text-[10px] font-black shadow-md shadow-indigo-500/20">
                                            #{student.rank}
                                        </span>
                                    </div>
                                    <div class="flex flex-col min-w-0">
                                        <span class="font-bold text-slate-800 dark:text-gray-100 text-sm truncate leading-tight">{student.name}</span>
                                        <span class="text-[10px] text-slate-400 dark:text-gray-500 truncate font-medium uppercase tracking-tight">{student.email}</span>
                                    </div>
                                </div>
                                <a href="/teacher/Students/{student.id}?classId={selectedClassId === 'all' ? (allEnrollments.find(e => e.user.id === student.id)?.classId) : selectedClassId}" 
                                    class="p-2.5 bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-gray-400 rounded-xl">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>
                                    </svg>
                                </a>
                            </div>
                            
                            <div class="flex items-center justify-between bg-slate-50 dark:bg-white/[0.02] p-3 rounded-2xl border border-slate-100 dark:border-white/5">
                                <div class="flex flex-col">
                                    <span class="text-[8px] font-black text-slate-400 uppercase tracking-widest">{$i18n.t('Performance')}</span>
                                    <div class="flex items-center gap-1.5">
                                        <span class="text-lg font-black text-emerald-600 dark:text-emerald-400 italic">{student.points.toLocaleString()}</span>
                                        <span class="text-[9px] font-bold text-slate-400 dark:text-gray-600">{$i18n.t('XP')}</span>
                                    </div>
                                </div>
                                <div class="h-8 w-[1px] bg-slate-200 dark:bg-white/10"></div>
                                <div class="flex flex-col items-end">
                                    <span class="text-[8px] font-black text-slate-400 uppercase tracking-widest">{$i18n.t('Enrolled in')}</span>
                                    <span class="text-sm font-bold text-indigo-600 dark:text-indigo-400 italic">{student.courseCount} {$i18n.t('Classes')}</span>
                                </div>
                            </div>
                        </div>
                    {:else}
                         <div class="py-20 text-center opacity-20">
                            <p class="text-slate-500 font-black text-xs uppercase tracking-widest">{$i18n.t('No student data available')}</p>
                        </div>
                    {/each}
                </div>
            </div>
        {/if}
    </div>
</div>