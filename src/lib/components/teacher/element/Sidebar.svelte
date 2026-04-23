<script lang="ts">
    import { page } from '$app/stores';
    import { getContext, onMount } from 'svelte';
    import type { Writable } from 'svelte/store';
    import { fade, fly } from 'svelte/transition';

    // ==== Icons ===
    import DashboardIcon from '$lib/components/icons/Dashboard.svelte';
    import ClassesIcon from '$lib/components/icons/Classroom.svelte';
    import StudentsIcon from '$lib/components/icons/Students.svelte';
    import AssignmentsIcon from '$lib/components/icons/Assignment.svelte';
    import MessageIcon from '$lib/components/icons/Messages.svelte';
    import SettingsIcon from '$lib/components/icons/Settings.svelte';

    const MenuItems = [
        { name: 'Dashboard', href: '/teacher/Dashboard', icon: DashboardIcon },
        { name: 'Classeroom', href: '/teacher/Classes', icon: ClassesIcon },
        { name: 'Student', href: '/teacher/Students', icon: StudentsIcon },
        { name: 'Assignments', href: '/teacher/Assignments', icon: AssignmentsIcon },
        { name: 'Messages', href: '/teacher/Messages', icon: MessageIcon },
        { name: 'Profile & Settings', href: '/teacher/Setting', icon: SettingsIcon },
    ];

    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    // Desktop Collapse State
    let isCollapsed = false;
    // Mobile Menu State
    let isMobileMenuOpen = false;

    function toggleDesktopSidebar() {
        isCollapsed = !isCollapsed;
        if (typeof window !== 'undefined') {
            localStorage.setItem('sidebarCollapsed', JSON.stringify(isCollapsed));
        }
    }

    function toggleMobileMenu() {
        isMobileMenuOpen = !isMobileMenuOpen;
    }

    onMount(() => {
        const storedState = localStorage.getItem('sidebarCollapsed');
        if (storedState !== null) {
            isCollapsed = JSON.parse(storedState);
        }
    });
</script>

{#if isMobileMenuOpen}
    <button  on:click={() => isMobileMenuOpen = false} 
        class="fixed inset-0 bg-black/20 backdrop-blur-sm z-[80] md:hidden"
        transition:fade={{ duration: 200 }}>
    </button>
{/if}

{#if isMobileMenuOpen}
    <div class="fixed bottom-24 right-6 z-[90] flex flex-col gap-3 md:hidden">
        {#each MenuItems as item, i}
            {@const isActive = $page.url.pathname === item.href}
            <a href={item.href} 
                on:click={() => isMobileMenuOpen = false}
                transition:fly={{ y: 20, delay: i * 50, duration: 300 }}
                class="w-12 h-12 flex items-center justify-center rounded-full shadow-xl transition-all border border-slate-200 dark:border-gray-700
                {isActive 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400'}">
                <span class="w-5 h-5">
                    <svelte:component this={item.icon} />
                </span>
            </a>
        {/each}
    </div>
{/if}

<button 
    on:click={toggleMobileMenu}
    class="md:hidden fixed bottom-6 right-6 z-[100] bg-blue-600 text-white p-4 rounded-full shadow-2xl active:scale-90 transition-transform">
    {#if isMobileMenuOpen}
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
        </svg>
    {:else}
        <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 6h16M4 12h16m-7 6h7" />
        </svg>
    {/if}
</button>


<aside class="hidden md:flex relative m-0 p-0 min-h-screen flex-col items-center border-r border-[#e2e8f0] dark:border-gray-800 bg-[#F5F7F9] dark:bg-gray-900 shadow-[5px_0_15px_rgba(0,0,0,0.02)] transition-all duration-300 ease-in-out
    {isCollapsed ? 'w-16' : 'w-64'}">
    
    <div class="w-full flex items-center justify-center p-4 pt-8 mb-4 h-20 relative">
        <div class="transition-all duration-300 flex items-center justify-center w-full">
            <img
                src="/static/favicon.png"
                alt="logo"
                class="dark:brightness-150 {isCollapsed ? 'h-8' : 'h-20 mr-2'}"
            >
        </div>
        
        <button on:click={toggleDesktopSidebar} class="absolute -right-3.5 top-10 z-50 bg-white dark:bg-gray-800 border border-slate-200 dark:border-gray-700 rounded-full p-1.5 shadow-md hover:shadow-lg transition-all group active:scale-90 cursor-pointer">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-slate-500 transition-transform duration-300 {isCollapsed ? '' : 'rotate-180'}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M9 5l7 7-7 7" />
            </svg>
        </button>
    </div>

    <div class="w-full px-4 py-2">
        {#if !isCollapsed}
            <div class="text-xs text-gray-500 dark:text-gray-400 uppercase font-semibold mb-1">
                {$i18n.t('Teacher') + ' Portal'}
            </div>
        {/if}
    </div>

    <nav class="w-full px-2">
        <ul class="list-none p-0 m-0 flex flex-col gap-2">
            {#each MenuItems as item}
                {@const isActive = $page.url.pathname.startsWith(item.href)}
                <li class="flex items-center justify-center">
                    <a href={item.href} title={isCollapsed ? $i18n.t(item.name): ''} class="flex items-center transition-all duration-200 group
                    {isActive 
                        ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/30' 
                        : 'text-gray-800 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-800'}
                    {isCollapsed ? 'w-12 h-12 justify-center rounded-full px-0 py-0 text-sm font-semibold' : 'w-full gap-4 px-4 py-3 rounded-full text-sm font-semibold'}">
                        <span class="w-6 h-6 transition-all
                        {isActive ? 'text-white' : 'text-gray-500 group-hover:text-gray-900 dark:text-gray-400 dark:group-hover:text-gray-100'}">
                            <svelte:component this={item.icon} />
                        </span>
                        {#if !isCollapsed}
                            <span class="text-sm font-medium whitespace-nowrap">{$i18n.t(item.name)}</span>
                        {/if}
                    </a>
                </li>
            {/each}

        </ul>
    </nav>

    {#if !isCollapsed}
        <div class="absolute bottom-0 left-0 right-0 p-4 hidden md:block">
            <div class="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                <span>© 2025 OpenTutorAI</span>
                <button class="hover:text-gray-800 dark:hover:text-gray-300">
                    {$i18n.t('Help')}
                </button>
            </div>
        </div>
    {/if}
</aside>

<style>

    span {
        overflow: hidden;
    }
</style>