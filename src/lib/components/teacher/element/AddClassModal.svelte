<script lang="ts">
    import { createEventDispatcher, getContext } from 'svelte';
    import { fly, fade } from 'svelte/transition';
    import type { Writable } from 'svelte/store';
    import { browser } from '$app/environment';

    const dispatch = createEventDispatcher();

    export let selectedClassId: string | number | null = null;
    export let className = "";
    export let courseName = "";

    let newClassName = "";
    let newCourseName = "";
    
    // Sync values for edit mode
    $: if (selectedClassId) {
        newClassName = className || "";
        newCourseName = courseName || "";
    }

    // ---- language ----
    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    function closeModal() {
        dispatch('close');
    }

    function handleSubmit(event: Event) {
        event.preventDefault();

        if (!newClassName.trim() || !newCourseName.trim()) {
            return;
        }

        const payload = {
            id: selectedClassId, 
            name: newClassName.toUpperCase(),
            course: newCourseName
        };
        
        dispatch('save', payload);
        closeModal();
    }

    // Responsive helper
    const modalTransition = (node: HTMLElement) => {
        const isMobile = browser && window.innerWidth < 768;
        return isMobile 
            ? fly(node, { y: 200, duration: 400, opacity: 1 }) 
            : fly(node, { y: -20, duration: 300 });
    };
</script>

<main class="fixed inset-0 z-[1000] flex items-end md:items-center justify-center bg-slate-900/70 dark:bg-black/80 md:p-5 backdrop-blur-sm transition-all" transition:fade={{ duration: 200 }}>
    
    <form on:submit={handleSubmit}
          class="w-full md:max-w-[480px] rounded-t-[24px] md:rounded-[24px] bg-white dark:bg-gray-900 p-8 md:p-10 shadow-2xl border-t md:border border-gray-100 dark:border-gray-800 flex flex-col gap-6"
          transition:modalTransition>
        
        <div class="flex items-center justify-between border-b border-gray-50 dark:border-gray-800 pb-4">
            <h3 class="text-xl md:text-2xl font-bold text-slate-800 dark:text-white">
                {selectedClassId ? $i18n.t('Edit class') : $i18n.t('Add a new class')}
            </h3>
            <button type="button" on:click={closeModal} class="md:hidden text-gray-400">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
        </div>

        <div class="space-y-5">
            <div class="flex flex-col gap-2">
                <label for="ClassName" class="text-sm font-bold text-slate-600 dark:text-gray-400 ml-1">
                    {$i18n.t("Class name")}
                </label>
                <input type="text" id="ClassName" 
                    bind:value={newClassName}
                    placeholder="e.g. GRADE 10"
                    required
                    class="w-full rounded-xl border border-slate-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 p-4 text-[15px] text-slate-900 dark:text-white outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all uppercase placeholder:normal-case"/>
            </div>

            <div class="flex flex-col gap-2">
                <label for="CoursName" class="text-sm font-bold text-slate-600 dark:text-gray-400 ml-1">
                    {$i18n.t("Course name")}
                </label>
                <input type="text" id="CoursName" 
                    bind:value={newCourseName} 
                    placeholder="e.g. Mathematics"
                    required
                    class="w-full rounded-xl border border-slate-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 p-4 text-[15px] text-slate-900 dark:text-white outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all"/>
            </div>
        </div>

        <div class="flex flex-col-reverse md:flex-row justify-end gap-3 mt-4">
            <button type="button" 
                    class="w-full md:w-auto rounded-xl bg-slate-100 dark:bg-gray-800 px-8 py-3.5 text-sm font-bold text-slate-600 dark:text-gray-300 transition-all active:scale-95" 
                    on:click={closeModal}>
                {$i18n.t("Cancel")}
            </button>
            
            <button type="submit" 
                    class="w-full md:w-auto rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-8 py-3.5 text-sm font-bold text-white shadow-lg shadow-indigo-500/20 transition-all active:scale-95 hover:brightness-110">
                {selectedClassId ? $i18n.t('Update') : $i18n.t('Créer')}
            </button>
        </div>
    </form>
</main>

<style>
    :global(body) {
        overflow: hidden;
    }
</style>