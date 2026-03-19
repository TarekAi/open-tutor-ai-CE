<script lang="ts">
    import type { Writable } from 'svelte/store';
    import { getContext } from 'svelte';

    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    export let open = false;
    
    export let title = $i18n.t('Confirm Action');
    export let message = $i18n.t('Are you sure you want to proceed? This action cannot be undone.');
    export let confirmText = $i18n.t('Delete');
    export let cancelText = $i18n.t('Cancel');
    
    export let onConfirm: () => void;

    function confirm() {
        onConfirm?.();
        open = false;
    }

    function cancel() {
        open = false;
    }
</script>

{#if open}
    <div class="fixed inset-0 z-[999] flex items-center justify-center p-4" 
        role="dialog" 
        aria-modal="true" 
        aria-labelledby="modal-title">
        
        <div 
            class="absolute inset-0 bg-black/60 backdrop-blur-sm" 
            on:click={cancel} 
            aria-hidden="true"/>

        <div class="relative w-full max-w-md bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-2xl overflow-hidden transition-all">
            
            <div class="h-px bg-gradient-to-r from-transparent via-red-500 to-transparent opacity-60" />

            <div class="px-6 pt-6 pb-5 flex gap-4 items-start">
                <div class="flex-shrink-0 w-10 h-10 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-100 dark:border-red-500/20 flex items-center justify-center">
                    <svg class="w-5 h-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                        <line x1="12" y1="9" x2="12" y2="13"/>
                        <line x1="12" y1="17" x2="12.01" y2="17"/>
                    </svg>
                </div>

                <div class="flex-1 min-w-0">
                    <h2 id="modal-title" class="text-base font-semibold text-gray-900 dark:text-gray-50 tracking-tight">
                        {title}
                    </h2>
                    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                        {message}
                    </p>
                </div>
            </div>

            <div class="flex items-center justify-end gap-3 px-6 py-4 bg-gray-50 dark:bg-gray-900/60 border-t border-gray-100 dark:border-gray-800/80">
                <button 
                    on:click={cancel}
                    class="px-4 py-2 text-sm font-medium rounded-lg text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-300 dark:hover:border-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-300 transition-all cursor-pointer shadow-sm">
                    {cancelText}
                </button>

                <button
                    on:click={confirm}
                    class="px-4 py-2 text-sm font-medium rounded-lg text-white bg-red-600 hover:bg-red-500 active:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-gray-950 transition-all cursor-pointer shadow-sm shadow-red-900/20">
                    {confirmText}
                </button>
            </div>
        </div>
    </div>
{/if}