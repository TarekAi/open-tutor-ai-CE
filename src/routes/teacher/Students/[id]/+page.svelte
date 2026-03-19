<script lang="ts">
    import { onMount, getContext } from 'svelte';
    import { page } from '$app/stores';
    import { browser } from '$app/environment';
    import { toast } from 'svelte-sonner';
    import type { Writable } from 'svelte/store';
    import { fly } from 'svelte/transition';
    import { getStudentsByClassId, updateStudentGrade, getMyClasses, updateClass } from '$lib/apis/classe';

    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    let student: any = null;
    let loading = true;
    let saving = false;
    let grade = 0;
    let teacherNote = "";
    
    let courseName = ""; 
    let className = "";
    let isEditingCourse = false;
    let newCourseValue = "";

    const studentId = $page.params.id;
    const classId = $page.url.searchParams.get('classId');
    const getToken = () => (browser ? localStorage.getItem('token') ?? '' : '');

    // List dial l-feedback l-sari3
    const quickTags = [
        "Excellent participation", 
        "Needs more focus", 
        "Very respectful", 
        "Improved significantly", 
        "Homework always ready"
    ];

    async function fetchData() {
        const token = getToken();
        if (!classId) {
            toast.error($i18n.t('Class ID is missing'));
            loading = false;
            return;
        }

        try {
            loading = true;
            const [classes, students] = await Promise.all([
                getMyClasses(token),
                getStudentsByClassId(token, classId)
            ]);

            const currentClass = classes.find(c => c.id === classId);
            if (currentClass) {
                courseName = currentClass.course || "";
                className = currentClass.name;
                newCourseValue = courseName;
            }

            student = students.find((s: any) => s.user_id === studentId || s.user?.id === studentId);
            if (student) {
                grade = student.grade || 0;
                teacherNote = student.notes || "";
            }
        } catch (err) {
            toast.error($i18n.t('Failed to load data'));
        } finally {
            loading = false;
        }
    }

    async function handleUpdateCourse() {
        if (!classId) return;
        try {
            await updateClass(getToken(), classId, {
                name: className,
                course: newCourseValue
            });
            courseName = newCourseValue;
            isEditingCourse = false;
            toast.success($i18n.t('Course name updated!'));
        } catch (err) {
            toast.error($i18n.t('Failed to update course name'));
        }
    }

    function addTag(tag: string) {
        const translatedTag = $i18n.t(tag);
        if (!teacherNote.includes(translatedTag)) {
            teacherNote = teacherNote ? `${teacherNote} ${translatedTag}.` : `${translatedTag}.`;
        }
    }

    async function handleSave() {
        if (grade < 0 || grade > 20) {
            toast.error($i18n.t('Grade must be between 0 and 20'));
            return;
        }
        saving = true;
        try {
            await updateStudentGrade(getToken(), classId!, studentId, {
                grade,
                notes: teacherNote
            });
            toast.success($i18n.t('Updated successfully!'));
        } catch (err) {
            toast.error($i18n.t('Update failed'));
        } finally {
            saving = false;
        }
    }

    onMount(fetchData);
</script>

<div class="bg-[#f8fafc] dark:bg-[#050505] font-['Inter'] p-2">
    {#if loading}
        <div class="flex flex-col items-center justify-center min-h-[60vh]">
            <div class="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
    {:else if student}
        <div class="w-full" in:fly={{ y: 15, duration: 450 }}>
            <button on:click={() => history.back()} class="mb-5 flex items-center gap-2 text-slate-400 hover:text-indigo-600 font-bold text-xs uppercase tracking-widest transition-all group">
                <svg class="group-hover:-translate-x-1 transition-transform" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
                {$i18n.t('Back')}
            </button>

            <div class="bg-white dark:bg-[#0a0a0a] rounded-[24px] border border-slate-200 dark:border-white/10 shadow-2xl overflow-hidden">
                <div class="p-6 md:p-8 bg-gradient-to-br from-slate-50 to-white dark:from-white/[0.02] dark:to-transparent border-b border-slate-100 dark:border-white/5 flex flex-wrap items-center justify-between gap-6">
                    <div class="flex items-center gap-4">
                        <div class="relative">
                            <img src={student.user?.profile_image_url || `https://ui-avatars.com/api/?name=${student.user?.name}&background=6366f1&color=fff`} 
                                alt="" class="w-12 h-12 md:w-14 md:h-14 rounded-xl object-cover shadow-md ring-2 ring-white dark:ring-white/5" />
                        </div>
                        
                        <div>
                            <h1 class="text-base md:text-lg font-black tracking-tight uppercase leading-tight text-slate-800 dark:text-white">
                                {student.user?.name}
                            </h1>
                            <p class="text-slate-400 text-[10px] font-bold uppercase tracking-wider mt-0.5">
                                {student.user?.email}
                            </p>
                        </div>
                    </div>
                    <div class="bg-indigo-50/50 dark:bg-indigo-500/5 px-5 py-4 rounded-2xl border border-indigo-100 dark:border-indigo-500/20 flex items-center gap-4 min-w-[240px]">
                        <div class="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white shrink-0 shadow-lg shadow-indigo-500/30">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M8 7h6"/><path d="M8 11h8"/></svg>
                        </div>
                        <div class="flex-1">
                            <span class="text-[9px] font-black text-indigo-400 uppercase tracking-widest block mb-1">{$i18n.t('Subject Name')}</span>
                            {#if isEditingCourse}
                                <div class="flex gap-2">
                                    <input bind:value={newCourseValue} 
                                           class="bg-white dark:bg-black/40 border border-indigo-200 dark:border-indigo-500/30 rounded-lg px-2 py-1 text-sm font-bold focus:outline-none w-full"
                                           on:keydown={(e) => e.key === 'Enter' && handleUpdateCourse()} />
                                    <button on:click={handleUpdateCourse} class="text-emerald-500 hover:scale-110 transition-transform">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                                    </button>
                                </div>
                            {:else}
                                <div class="flex items-center justify-between group cursor-pointer" on:click={() => isEditingCourse = true}>
                                    <span class="text-sm font-black uppercase text-slate-700 dark:text-indigo-100">{courseName || $i18n.t('Set Course Name')}</span>
                                    <svg class="opacity-0 group-hover:opacity-100 text-indigo-400 transition-opacity" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg>
                                </div>
                            {/if}
                        </div>
                    </div>
                </div>

                <div class="p-6 md:p-8 space-y-8">
                    <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
                        <div class="md:col-span-8 space-y-4">
                            <label class="text-[10px] font-black uppercase tracking-[0.2em] text-indigo-500 block">{$i18n.t('Student Grade')}</label>
                            <div class="flex items-center gap-5 bg-slate-50 dark:bg-white/[0.03] p-4 rounded-2xl border border-slate-100 dark:border-white/5">
                                <input type="number" bind:value={grade} min="0" max="20" step="0.5"
                                       class="w-20 bg-white dark:bg-white/10 border-2 border-slate-200 dark:border-white/10 rounded-xl py-3 text-2xl font-black text-center focus:border-indigo-500 outline-none transition-all tabular-nums shadow-sm" />
                                <div class="flex-1">
                                    <div class="h-2.5 bg-slate-200 dark:bg-white/10 rounded-full overflow-hidden">
                                        <div class="h-full bg-indigo-500 transition-all duration-700 ease-out" style="width: {(grade/20)*100}%"></div>
                                    </div>
                                    <div class="flex justify-between mt-2 font-black text-[9px] text-slate-400 uppercase tracking-tighter">
                                        <span>{$i18n.t('Min 0')}</span><span>{$i18n.t('Max 20')}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="md:col-span-4 bg-indigo-50/50 dark:bg-indigo-500/5 rounded-2xl p-5 border border-indigo-100 dark:border-indigo-500/10 flex flex-col justify-center items-center md:items-start">
                            <span class="text-[10px] font-black uppercase text-indigo-400 tracking-widest">{$i18n.t('Calculated Status')}</span>
                            <div class="text-lg font-black mt-1 {grade >= 10 ? 'text-emerald-500' : 'text-rose-500'} uppercase">
                                {grade >= 10 ? $i18n.t('Passed') : $i18n.t('Needs Support')}
                            </div>
                        </div>
                    </div>

                    <div class="space-y-4">
                        <label class="text-[10px] font-black uppercase tracking-[0.2em] text-indigo-500 block">{$i18n.t('Teacher Feedback')}</label>
                        <textarea bind:value={teacherNote} rows="4" placeholder={$i18n.t('How is the student performing?...')}
                                  class="w-full bg-slate-50 dark:bg-white/5 border-2 border-slate-200 dark:border-white/10 rounded-2xl px-5 py-4 text-[15px] font-medium focus:border-indigo-500 outline-none transition-all resize-none shadow-inner min-h-[120px]"></textarea>
                        
                        <div class="flex flex-wrap gap-2">
                            {#each quickTags as tag}
                                <button on:click={() => addTag(tag)}
                                    class="px-4 py-2 rounded-xl bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 text-[10px] font-bold hover:bg-indigo-600 hover:text-white transition-all shadow-sm uppercase tracking-wider">
                                    + {$i18n.t(tag)}
                                </button>
                            {/each}
                        </div>
                    </div>

                    <button on:click={handleSave} disabled={saving}
                            class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black py-4.5 rounded-2xl shadow-xl shadow-indigo-500/25 transition-all active:scale-[0.98] uppercase tracking-[0.3em] text-xs flex items-center justify-center gap-3 disabled:opacity-50 h-[60px]">
                        {#if saving}
                            <div class="w-5 h-5 border-3 border-white/30 border-t-white rounded-full animate-spin"></div>
                        {:else}
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
                            {$i18n.t('Save')}
                        {/if}
                    </button>
                </div>
            </div>
        </div>
    {:else}
        <div class="text-center py-20">
            <p class="text-slate-400 font-bold uppercase tracking-widest">{$i18n.t('Student profile not found.')}</p>
        </div>
    {/if}
</div>