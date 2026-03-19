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

<div class="flex flex-row w-full h-screen m-auto overflow-hidden bg-[#f8fbff] dark:bg-black transition-colors duration-300">

    {#if !$isFullscreenAvatar}
        <aside class="hidden md:block h-full shrink-0 border-r border-slate-200 dark:border-gray-800">
            <Sidebar />
        </aside>
    {/if}

    <div class="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {#if !$isFullscreenAvatar}
            <header class="z-30 shrink-0">
                <Header/>
            </header>
        {/if}

        <main class=" overflow-y-auto relative p-3">
            <slot />

            <div class="md:hidden">
                <Sidebar />
            </div>
        </main>
    </div>
</div>

<style>
    :global(body) { 
        margin: 0; 
        padding: 0; 
        overflow: hidden; 
        font-family: 'Inter', sans-serif;
    }
    :global(.dark) {
        color-scheme: dark;
    }
</style>