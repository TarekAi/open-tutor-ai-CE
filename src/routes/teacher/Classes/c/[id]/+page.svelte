<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import { getContext, onMount } from 'svelte';
    import { browser } from '$app/environment';
    import { getClassById } from '$lib/apis/classe';
    import { getClassContent, deleteCourse } from '$lib/apis/course_content';
    import { toast } from 'svelte-sonner';
    import PdfPreview from '$lib/components/teacher/element/PdfPreview.svelte';
    import CourseCard from '$lib/components/teacher/element/CourseCard.svelte';
    import ConfirmModal from '$lib/components/teacher/element/ConfirmModal.svelte';
    import type { Writable } from 'svelte/store';

    // --- État et Variables ---
    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    let previewUrl = '';
    let showPreview = false;
    let showDeleteModal = false;
    let courseToDelete: any = null;
    let classe: any = null;
    let isTeacher = true;

    $: classId = $page.params.id;

    // TABS rji'nahom labels f-l-JSON bach i-t-traduizaw
    const TABS = ['Courses', 'TD', 'TP', 'Exams'] as const;
    type Tab = (typeof TABS)[number];
    let activeTab: Tab = 'Courses';

    let contentMap: Record<Tab, any[]> = {
        Courses: [],
        TD: [],
        TP: [],
        Exams: []
    };

    $: items = contentMap[activeTab] ?? [];

    // --- Configuration des Types de fichiers ---
    const typeConfig: Record<string, { label: string; color: string; bg: string }> = {
        pdf: { label: 'PDF', color: 'text-rose-500', bg: 'bg-rose-100 dark:bg-rose-900/30' },
        doc: { label: 'DOC', color: 'text-indigo-500', bg: 'bg-indigo-100 dark:bg-indigo-900/30' },
        docx: { label: 'DOC', color: 'text-indigo-500', bg: 'bg-indigo-100 dark:bg-indigo-900/30' },
        xls: { label: 'EXCEL', color: 'text-green-500', bg: 'bg-green-100 dark:bg-green-900/30' },
        xlsx: { label: 'EXCEL', color: 'text-green-500', bg: 'bg-green-100 dark:bg-green-900/30' },
        ppt: { label: 'PPT', color: 'text-orange-500', bg: 'bg-orange-100 dark:bg-orange-900/30' },
        pptx: { label: 'PPT', color: 'text-orange-500', bg: 'bg-orange-100 dark:bg-orange-900/30' },
        zip: { label: 'ZIP', color: 'text-emerald-500', bg: 'bg-emerald-100 dark:bg-emerald-900/30' }
    };

    const getToken = () => (browser ? (localStorage.getItem('token') ?? '') : '');

    function getType(t: string) {
        if (!t) return typeConfig['doc'];
        const ext = t.split('/').pop()?.toLowerCase();
        return typeConfig[ext!] ?? typeConfig['doc'];
    }

    function formatSize(bytes: number) {
        if (!bytes) return '—';
        const kb = bytes / 1024;
        return kb < 1024 ? kb.toFixed(0) + ' KB' : (kb / 1024).toFixed(1) + ' MB';
    }

    function formatDate(date: string) {
        // Hna n-khlliwha 'en-US' oula n-bedlouha 3la hsab i18n ila bghiti
        return new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    const goUpload = () => goto(`/teacher/Classes/c/${classId}/upload`);
    const goGenerator = () => goto(`/teacher/Classes/c/${classId}/generator`);

    function handleView(item: any) {
        previewUrl = encodeURI(`http://localhost:8080${item.file.url}`);
        showPreview = true;
    }

    async function handleDownload(item: any) {
        const url = `http://localhost:8080${item.file.url}`;
        const response = await fetch(url);
        const blob = await response.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = item.file.name;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(blobUrl);
    }

    function handleDelete(item: any) {
        courseToDelete = item;
        showDeleteModal = true;
    }

    async function confirmDeleteCourse() {
        if (!courseToDelete) return;
        try {
            await deleteCourse(getToken(), courseToDelete.id);
            contentMap = {
                ...contentMap,
                [activeTab]: contentMap[activeTab].filter((i) => i.id !== courseToDelete.id)
            };
            toast.success($i18n.t('File deleted'));
            showDeleteModal = false;
            courseToDelete = null;
        } catch (err) {
            toast.error($i18n.t('Failed to delete file'));
        }
    }

    onMount(async () => {
        try {
            const token = getToken();
            const [classData, contentData] = await Promise.all([
                getClassById(token, classId),
                getClassContent(token, classId)
            ]);
            classe = classData;
            contentMap = {
                Courses: contentData.courses,
                TD: contentData.tds,
                TP: contentData.tps,
                Exams: contentData.exams
            };
        } catch (err) {
            console.error(err);
        }
    });
</script>

<div class="min-h-screen bg-gray-50 dark:bg-black selection:bg-blue-500/30">
    <div class="max-w-6xl mx-auto p-4">
        <button on:click={() => goto('/teacher/Classes')}
            class="group inline-flex items-center gap-2.5 text-sm font-medium text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white mb-5 transition-all duration-300 hover:-translate-x-1">
            <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800 group-hover:border-blue-400 dark:group-hover:border-gray-600 shadow-sm transition-all duration-300">
                <svg class="w-4 h-4" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10 12L6 8l4-4" />
                </svg>
            </span>
            {$i18n.t('Back')}
        </button>

        <div class="mb-8">
            <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight text-gray-900 dark:text-transparent dark:bg-clip-text dark:bg-gradient-to-r dark:from-white dark:to-gray-400 mb-3">
                {classe?.name ?? '—'}
            </h1>
            <p class="text-gray-500 dark:text-gray-400 text-base md:text-lg max-w-2xl">
                {$i18n.t('Manage your content, upload new materials, or let AI generate exercises for this class.')}
            </p>
        </div>

        <div class="grid md:grid-cols-2 gap-5 mb-14">
            <button on:click={goUpload} class="group relative text-left rounded-[20px] p-7 transition-all duration-300 bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800/80 hover:border-blue-400 dark:hover:border-gray-700 hover:-translate-y-1 hover:shadow-[0_12px_40px_-12px_rgba(59,130,246,0.15)] overflow-hidden">
                <div class="pointer-events-none absolute -top-12 -right-12 w-48 h-48 rounded-full bg-blue-400/10 dark:bg-blue-500/5 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                <div class="flex items-start gap-5 relative z-10">
                    <div class="shrink-0 w-14 h-14 flex items-center justify-center bg-blue-50 dark:bg-gray-900 rounded-2xl border border-blue-100 dark:border-gray-800 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                        <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
                        </svg>
                    </div>
                    <div>
                        <div class="flex items-center gap-2 mb-2">
                            <h2 class="text-lg font-bold text-gray-900 dark:text-white">{$i18n.t('Upload Course')}</h2>
                            <span class="text-[10px] uppercase tracking-wider font-bold px-2.5 py-1 rounded-full bg-blue-100 dark:bg-gray-900 text-blue-700 dark:text-gray-300 border dark:border-gray-800">{$i18n.t('Manual')}</span>
                        </div>
                        <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{$i18n.t('Upload PDFs, presentation slides, documents, and existing course materials directly.')}</p>
                    </div>
                </div>
            </button>

            <button on:click={goGenerator} class="group relative text-left rounded-[20px] p-7 transition-all duration-300 bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800/80 hover:border-indigo-400 dark:hover:border-gray-700 hover:-translate-y-1 hover:shadow-[0_12px_40px_-12px_rgba(99,102,241,0.15)] overflow-hidden">
                <div class="pointer-events-none absolute -top-12 -right-12 w-48 h-48 rounded-full bg-indigo-400/10 dark:bg-indigo-500/5 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
                <div class="flex items-start gap-5 relative z-10">
                    <div class="shrink-0 w-14 h-14 flex items-center justify-center bg-indigo-50 dark:bg-gray-900 rounded-2xl border border-indigo-100 dark:border-gray-800 group-hover:scale-110 group-hover:-rotate-3 transition-all duration-300">
                        <svg class="w-8 h-8 text-indigo-600 dark:text-indigo-400" viewBox="0 0 32 32" fill="none">
                            <text x="16" y="20" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-weight="800" fill="currentColor">{$i18n.t('AI')}</text>
                            <circle cx="6" cy="6" r="1.5" fill="currentColor" opacity="0.6" />
                            <circle cx="26" cy="26" r="1.5" fill="currentColor" opacity="0.6" />
                        </svg>
                    </div>
                    <div>
                        <div class="flex items-center gap-2 mb-2">
                            <h2 class="text-lg font-bold text-gray-900 dark:text-white">{$i18n.t('AI Generator')}</h2>
                            <span class="text-[10px] uppercase tracking-wider font-bold px-2.5 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 border dark:border-indigo-500/20">{$i18n.t('✦ Smart')}</span>
                        </div>
                        <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{$i18n.t('Let AI auto-generate comprehensive quizzes, lesson plans, and detailed exercises.')}</p>
                    </div>
                </div>
            </button>
        </div>

        <div class="bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800/80 rounded-[20px] overflow-hidden shadow-sm">
            
            <div class="flex items-center justify-between px-7 pt-6 pb-2">
                <div>
                    <h2 class="text-xl font-bold text-gray-900 dark:text-white">{$i18n.t('Class Content')}</h2>
                    <p class="text-sm text-gray-400 dark:text-gray-500 mt-1">
                        {$i18n.t('Showing')} {items.length} {$i18n.t('item(s) in')} {$i18n.t(activeTab)}
                    </p>
                </div>
            </div>

            <div class="flex items-center gap-2 px-5 mt-4 border-b border-gray-200 dark:border-gray-800/80 overflow-x-auto no-scrollbar">
                {#each TABS as tab}
                    <button on:click={() => (activeTab = tab)}
                        class="relative px-5 py-3 text-sm font-semibold transition-all duration-300 border-b-2 -mb-px whitespace-nowrap
                            {activeTab === tab
                            ? 'border-blue-500 text-gray-900 dark:text-white'
                            : 'border-transparent text-gray-500 dark:text-gray-500 hover:text-gray-800 dark:hover:text-gray-300'}">
                        {$i18n.t(tab)}
                        {#if contentMap[tab]?.length > 0}
                            <span class="ml-2 text-[10px] font-bold px-2 py-0.5 rounded-full border transition-colors duration-300
                                {activeTab === tab
                                ? 'bg-gray-100 dark:bg-white text-gray-900 dark:text-black border-transparent'
                                : 'bg-gray-50 dark:bg-black text-gray-500 dark:text-gray-400 dark:border-gray-800'}">
                                {contentMap[tab].length}
                            </span>
                        {/if}
                    </button>
                {/each}
            </div>

            <div class="p-7">
                {#if items.length === 0}
                    <div class="flex flex-col items-center justify-center py-20 text-center">
                        <div class="w-16 h-16 rounded-3xl bg-gray-50 dark:bg-black border border-gray-200 dark:border-gray-800 flex items-center justify-center mb-5 shadow-inner dark:shadow-white/5">
                            <svg class="w-7 h-7 text-gray-400 dark:text-gray-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
                            </svg>
                        </div>
                        <h3 class="text-gray-900 dark:text-white font-bold text-lg mb-2">{$i18n.t('No content yet')}</h3>
                        <p class="text-sm text-gray-500 dark:text-gray-400 max-w-sm mb-8 leading-relaxed">{$i18n.t('Your class is looking a bit empty. Upload existing files or let AI magically generate your first item.')}</p>
                        <div class="flex flex-wrap items-center justify-center gap-4">
                            <button on:click={goUpload} class="text-sm font-semibold px-5 py-2.5 rounded-xl bg-white dark:bg-black border border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-300 hover:border-gray-400 dark:hover:border-gray-600 hover:text-gray-900 dark:hover:text-white transition-all shadow-sm flex items-center gap-2">
                                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                                {$i18n.t('Upload File')}
                            </button>
                            <button on:click={goGenerator} class="text-sm font-bold px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white transition-all shadow-[0_4px_20px_-4px_rgba(79,70,229,0.4)] hover:shadow-[0_8px_25px_-4px_rgba(79,70,229,0.5)] hover:-translate-y-0.5 flex items-center gap-2">
                                ✦ {$i18n.t('Generate Content with AI')}
                            </button>
                        </div>
                    </div>
                {:else}
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                        {#each items as item (item.id)}
                            {@const cfg = getType(item.type)}
                            <CourseCard
                                {item}
                                {cfg}
                                {isTeacher}
                                onView={handleView}
                                onDownload={handleDownload}
                                onDelete={handleDelete}
                                {formatSize}
                                {formatDate}/>
                        {/each}
                    </div>
                {/if}
            </div>
        </div>
    </div>

    <ConfirmModal
        bind:open={showDeleteModal}
        title={$i18n.t('Delete File')}
        message={$i18n.t('Are you sure you want to delete this file? This action cannot be undone.')}
        confirmText={$i18n.t('Delete')}
        cancelText={$i18n.t('Cancel')}
        onConfirm={confirmDeleteCourse}/>

    <PdfPreview url={previewUrl} show={showPreview} onClose={() => (showPreview = false)} />
</div>

<style>
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>