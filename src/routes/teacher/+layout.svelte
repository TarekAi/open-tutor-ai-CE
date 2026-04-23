<script lang="ts">
    import Sidebar from '$lib/components/teacher/element/Sidebar.svelte';
    import Header from '$lib/components/teacher/element/Header.svelte';
    import { onMount } from 'svelte';
    import { theme, settings, models, isFullscreenAvatar } from '$lib/stores';
    import { getModels } from '$lib/apis';

    // Theme logic improved
    $: if (typeof document !== 'undefined') {
        const isDark = $theme === 'dark' || ($theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
        document.documentElement.classList.toggle('dark', isDark);
    }

    onMount(async () => {
        try {
            const modelList = await getModels(localStorage.token, $settings?.directConnections ?? null);
            models.set(modelList);
        } catch (e) {
            console.error("Failed to load models", e);
        }
    });
</script>

<div
    class="flex h-screen overflow-hidden bg-[#F4F7FE] dark:bg-gray-900 transition-colors duration-200 ease-in-out"
>

    {#if !$isFullscreenAvatar}
        <aside class="hidden md:block h-full shrink-0 border-r border-slate-200 dark:border-gray-800">
            <Sidebar />
        </aside>
    {/if}

    <div class="flex-1 flex flex-col min-w-0 h-screen overflow-hidden bg-[#F4F7FE] dark:bg-gray-900">
        {#if !$isFullscreenAvatar}
            <header class="z-30 shrink-0">
                <Header/>
            </header>
        {/if}

        <main class="flex-1 overflow-y-auto relative p-4 md:p-6 bg-[#F4F7FE] dark:bg-gray-900 text-gray-800 dark:text-gray-100">
            <slot />

            <div class="md:hidden">
                <Sidebar />
            </div>
        </main>
    </div>
</div>

<style>
    :global(.flex-1) {
        min-height: 0;
    }

    :global(body, html) {
        margin: 0; 
        padding: 0; 
        overflow: hidden; 
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell,
            'Open Sans', 'Helvetica Neue', sans-serif;
    }
    :global(.dark) {
        color-scheme: dark;
    }
</style>