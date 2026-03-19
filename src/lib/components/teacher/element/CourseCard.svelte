<script lang="ts">
    import ArrowsPointingOut from '$lib/components/icons/ArrowsPointingOut.svelte'
    import ArrowDownTray from '$lib/components/icons/ArrowDownTray.svelte'
    import GarbageBin from '$lib/components/icons/GarbageBin.svelte'

    import type { Writable } from 'svelte/store';
    import { getContext } from 'svelte';

    export let item: any
    export let isTeacher: boolean
    export let cfg: any 

    export let onView: (item: any) => void
    export let onDownload: (item: any) => void
    export let onDelete: (item: any) => void

    export let formatSize: (n: number) => string
    export let formatDate: (d: string) => string

    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');
</script>

<div class="group flex flex-col border border-gray-100 dark:border-gray-800 rounded-[24px] bg-white dark:bg-[#16171d] 
hover:shadow-md transition-all duration-300 overflow-hidden">

    <div class="flex items-center gap-4 p-5">
        
        <div class="flex-shrink-0 w-12 h-12 rounded-2xl {cfg.bg} flex items-center justify-center transition-transform duration-300 group-hover:scale-105">
            <svg class="w-6 h-6 {cfg.color}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
            </svg>
        </div>

        <div class="flex-1 min-w-0">
            <h4 class="text-[15px] font-bold text-gray-800 dark:text-gray-100 truncate">
                {item.title}
            </h4>
            
            <div class="flex items-center gap-2 mt-1">
                <span class="px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-wider {cfg.bg} {cfg.color} border border-current/5">
                    {item.type || 'PDF'}
                </span>
                <span class="text-gray-300 dark:text-gray-700 text-xs">•</span>
                <span class="text-[11px] font-semibold text-gray-400 dark:text-gray-500">
                    {formatSize(item.size)}
                </span>
                <span class="text-gray-300 dark:text-gray-700 text-xs">•</span>
                <span class="text-[11px] font-semibold text-gray-400 dark:text-gray-500">
                    {formatDate(item.date)}
                </span>
            </div>
        </div>
    </div>

    <div class="px-4 py-3 bg-gray-50/60 dark:bg-[#1c1d25] border-t border-gray-100 dark:border-gray-800/50
    flex items-center justify-between gap-2">
        
        <div class="flex items-center gap-2">
            <button
                on:click={() => onView(item)}
                title={$i18n.t('View')}
                class="w-9 h-9 flex items-center justify-center rounded-xl bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700
                text-gray-600 dark:text-gray-400 hover:text-blue-600 hover:border-blue-200 shadow-sm transition-all active:scale-90">
                <ArrowsPointingOut className="w-4 h-4" />
            </button>

            <button
                on:click={() => onDownload(item)}
                title={$i18n.t('Download')}
                class="w-9 h-9 flex items-center justify-center rounded-xl bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700
                text-gray-600 dark:text-gray-400 hover:text-blue-600 hover:border-blue-200 shadow-sm transition-all active:scale-90">
                <ArrowDownTray className="w-4 h-4" />
            </button>
        </div>

        {#if isTeacher}
        <button
            on:click={() => onDelete(item)}
            class="flex items-center gap-2 px-4 py-2 rounded-xl text-[11px] font-black uppercase tracking-widest
            bg-rose-50 dark:bg-rose-950/20 text-rose-500 border border-rose-100/50 dark:border-rose-900/30
            hover:bg-rose-500 hover:text-white transition-all active:scale-95">
            <GarbageBin className="w-3.5 h-3.5" />
            <span class="hidden sm:inline">{$i18n.t('Delete')}</span>
        </button>
        {/if}
    </div>

</div>