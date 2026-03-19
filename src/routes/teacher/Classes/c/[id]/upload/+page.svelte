<script lang="ts">
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { createCourse } from '$lib/apis/course_content';
    import { uploadCourseFile } from '$lib/apis/cours_files';
    import { browser } from '$app/environment';
    import { getContext, onMount } from 'svelte';
    import { toast } from 'svelte-sonner';
    import { getClassById } from '$lib/apis/classe';
    import type { Writable } from 'svelte/store';

    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    const getToken = () => (browser ? localStorage.getItem('token') ?? '' : '');
    let classe: any = null;
    let loading = false;

    let title = '';
    let description = '';
    let type = 'course';
    let file: File | null = null;
    let isDragging = false;

    $: classId = $page.params.id;

    function handleFile(e: Event) {
        const input = e.target as HTMLInputElement;
        file = input.files?.[0] ?? null;
    }

    function handleDrop(e: DragEvent) {
        e.preventDefault();
        isDragging = false;
        file = e.dataTransfer?.files?.[0] ?? null;
    }

    type Section = "courses" | "td" | "tp" | "exams";
    async function submitForm() {
        if (!file) {
            toast.error($i18n.t('Please select a file'));
            return;
        }
        loading = true;
        try {
            const token = getToken();
            const course = await createCourse(token, {title, description, type, classe_id: classId});
            
            let section: Section = "courses";
            if (type === "td") section = "td";
            if (type === "tp") section = "tp";
            if (type === "exam") section = "exams";

            await uploadCourseFile(token, course.id, section, file);
            
            toast.success($i18n.t('Content added successfully'));
            goto(`/teacher/Classes/c/${classId}`);
        } catch (err) {
            console.error(err);
            toast.error($i18n.t('Error saving content'));
        } finally {
            loading = false;
        }
    }

    onMount(async () => {
        try {
            classe = await getClassById(getToken(), classId);
            title = classe.name;
        } catch (err) {
            console.error('Error loading class', err);
        }
    });

    const TYPE_OPTIONS = [
        { value: 'course', label: 'Course', icon: '📖' },
        { value: 'td',     label: 'TD',     icon: '✏️' },
        { value: 'tp',     label: 'TP',     icon: '🔬' },
        { value: 'exam',   label: 'Exam',   icon: '📝' },
    ];
</script>


<div class="p-5">
    <button on:click={() => goto(`/teacher/Classes/c/${classId}`)}
        class="group inline-flex items-center gap-2 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-white mb-6 transition-all">
        <div class="flex items-center justify-center w-8 h-8 rounded-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 group-hover:scale-110 shadow-sm transition-all">
            <svg class="w-4 h-4" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M10 12L6 8l4-4" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <span>{$i18n.t('Back')}</span>
    </button>

    <header class="mb-8">
        <h1 class="text-2xl sm:text-2xl font-black text-gray-900 dark:text-white tracking-tight">
            {$i18n.t('Add New Content')}
        </h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1 flex items-center gap-2">
            {$i18n.t('Class:')}
            <span class="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded text-xs font-bold uppercase tracking-wider">
                {classe?.name ?? $i18n.t('Loading...')}
            </span>
        </p>
    </header>

    <div class="bg-white dark:bg-[#121216] border border-gray-200 dark:border-gray-800 rounded-3xl shadow-xl shadow-gray-200/50 dark:shadow-none overflow-hidden">
        <form on:submit|preventDefault={submitForm} class="flex flex-col">
            <div class="p-6 sm:p-8 space-y-8">
                <div class="space-y-2">
                    <label for="title" class="text-sm font-bold text-gray-700 dark:text-gray-300 flex items-center gap-2">
                        {$i18n.t('Title')} <span class="text-rose-500">*</span>
                    </label>
                    <input id="title" type="text" bind:value={title} placeholder={$i18n.t('e.g. Chapter 1: Foundations')} required
                        class="w-full bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-2xl px-4 py-3 text-sm focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 dark:text-white outline-none transition-all"/>
                </div>

                <div class="space-y-3">
                    <label class="text-sm font-bold text-gray-700 dark:text-gray-300" for="category">
                        {$i18n.t('Category')} <span class="text-rose-500">*</span>
                    </label>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        {#each TYPE_OPTIONS as opt}
                            <button type="button" on:click={() => type = opt.value}
                                class="flex flex-col items-center justify-center gap-2 p-3 rounded-2xl border-2 transition-all duration-200
                                    {type === opt.value
                                        ? 'bg-blue-50 dark:bg-blue-500/10 border-blue-500 text-blue-700 dark:text-blue-400 shadow-md ring-2 ring-blue-500/20'
                                        : 'bg-white dark:bg-gray-800/30 border-gray-100 dark:border-gray-700 text-gray-500 dark:text-gray-500 hover:border-gray-300 dark:hover:border-gray-600'}">
                                <span class="text-2xl">{opt.icon}</span>
                                <span class="text-[11px] uppercase font-black tracking-widest">{$i18n.t(opt.label)}</span>
                            </button>
                        {/each}
                    </div>
                </div>

                <div class="space-y-2">
                    <label for="desc" class="text-sm font-bold text-gray-700 dark:text-gray-300">
                       {$i18n.t('Description')} <span class="text-xs font-normal text-gray-400 dark:text-gray-500">({$i18n.t('Optional')})</span>
                    </label>
                    <textarea id="desc" bind:value={description} rows="3"
                        placeholder={$i18n.t('What should students know about this file?')}
                        class="w-full bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-2xl px-4 py-3 text-sm focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 dark:text-white outline-none transition-all resize-none"></textarea>
                </div>

                <div class="space-y-2">
                    <label class="text-sm font-bold text-gray-700 dark:text-gray-300" for="file">
                        {$i18n.t('Attachment')} <span class="text-rose-500">*</span>
                    </label>
                    
                    <div on:dragover|preventDefault={() => isDragging = true}
                        on:dragleave={() => isDragging = false}
                        on:drop={handleDrop}
                        class="relative min-h-[160px] rounded-3xl border-2 border-dashed flex flex-col items-center justify-center transition-all
                            {isDragging ? 'border-blue-500 bg-blue-50 dark:bg-blue-500/10 scale-[0.99]' : ''}
                            {!file && !isDragging ? 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600' : ''}
                            {file ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-500/5' : ''}">
                        <input type="file" on:change={handleFile} required
                            class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"/>
                        {#if file}
                            <div class="flex flex-col items-center animate-in fade-in zoom-in duration-300">
                                <div class="w-14 h-14 bg-emerald-100 dark:bg-emerald-500/20 rounded-2xl flex items-center justify-center mb-3">
                                    <svg class="w-7 h-7 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                                    </svg>
                                </div>
                                <p class="text-sm font-bold text-gray-800 dark:text-gray-200 max-w-[200px] truncate">{file.name}</p>
                                <p class="text-xs text-gray-500">{(file.size / 1024).toFixed(0)} KB</p>
                            </div>
                        {:else}
                            <div class="text-center p-4">
                                <div class="w-14 h-14 bg-gray-100 dark:bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-3 text-gray-400">
                                    <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                                    </svg>
                                </div>
                                <p class="text-sm font-bold text-gray-700 dark:text-gray-300">{$i18n.t('Click or drag file')}</p>
                                <p class="text-xs text-gray-400 mt-1">{$i18n.t('PDF, DOCX, ZIP up to 10MB')}</p>
                            </div>
                        {/if}
                    </div>
                </div>
            </div>

            <div class="px-8 py-6 bg-gray-50/50 dark:bg-gray-800/30 border-t border-gray-100 dark:border-gray-800 flex flex-col sm:flex-row items-center justify-between gap-4">
                <button type="submit" disabled={loading}
                    class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3 rounded-2xl bg-blue-600 hover:bg-blue-700 active:scale-95 text-white font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/25">
                    {#if loading}
                        <svg class="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        {$i18n.t('Saving...')}
                    {:else}
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                        </svg>
                        {$i18n.t('Create Content')}
                    {/if}
                </button>
            </div>

        </form>
    </div>
</div>


<style>
    :global(.dark) input:focus, :global(.dark) textarea:focus {
        box-shadow: 0 0 20px -5px rgba(59, 130, 246, 0.2);
    }
</style>