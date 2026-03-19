<script lang="ts">
    import { user, theme } from '$lib/stores'; 
    import { createEventDispatcher, getContext, onMount } from 'svelte';
    import { generateInitialsImage } from '$lib/utils';
    import type { Writable } from 'svelte/store';

    import Smile from '$lib/components/icons/FaceSmile.svelte';
    import Info from '$lib/components/icons/Info.svelte';
    import SearchIcon from '$lib/components/icons/Search.svelte';

    interface I18n { t: (key: string) => string; locale: string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    const dispatch = createEventDispatcher();

    let showUserDropdown = false;
    let showNotifications = false;
    let notificationCount = 0;
    let notificationRef: HTMLDivElement;

    $: profileImageUrl = $user?.profile_image_url || generateInitialsImage($user?.name || 'User');
    $: isRTL = $i18n.locale === 'ar';

    function toggleNotificationPanel() {
        showNotifications = !showNotifications;
        if (showNotifications) showUserDropdown = false;
    }

    function showProfilePanel() {
        showUserDropdown = !showUserDropdown;
        if (showUserDropdown) showNotifications = false;
    }

    function closeAllDropdowns() {
        showUserDropdown = false;
        showNotifications = false;
    }

    // === Logic Theme ====
    function applyTheme(currentTheme: string) {
        if (typeof window === 'undefined') return;
        let themeToApply = currentTheme;
        if (currentTheme === 'system') {
            themeToApply = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        if (themeToApply === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }

    function toggleTheme() {
        const isDark = document.documentElement.classList.contains('dark');
        const newTheme = isDark ? 'light' : 'dark';
        theme.set(newTheme);
        localStorage.setItem('theme', newTheme);
        dispatch('themeToggle', { theme: newTheme });
    }

    $: if ($theme) { applyTheme($theme);}

    onMount(() => {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const handleSystemThemeChange = () => { if ($theme === 'system') applyTheme('system'); };
        mediaQuery.addEventListener('change', handleSystemThemeChange);

        const handleClickOutside = (event: MouseEvent) => {
            const target = event.target as HTMLElement;
            if (!target.closest('.action-buttons')) {
                closeAllDropdowns();
            }
        };

        document.addEventListener('click', handleClickOutside);
        return () => {
            document.removeEventListener('click', handleClickOutside);
            mediaQuery.removeEventListener('change', handleSystemThemeChange);
        };
    });
</script>

<div class="flex flex-row items-center gap-4 p-4 header transition-colors duration-200 bg-white dark:bg-gray-950 w-full" dir={isRTL ? 'rtl' : 'ltr'}>
    
    <div class="m-0 p-0 hidden md:block flex-shrink-0">
        <div class="flex flex-col">
            <div class="flex items-center">
                <h2 class="m-0 p-0 text-2xl font-light dark:text-white">
                    {$i18n.t("Hello")}, <span>{$user?.name?.split(' ')[0]}</span>!
                </h2>
                <Smile className="h-6 w-6 text-yellow-400 {isRTL ? 'mr-2' : 'ml-2'}" /> 
            </div>
            <p class="text-xs text-slate-500 dark:text-gray-400 mt-1 font-medium tracking-wide">
                {$i18n.t("Manage your classes and track student progress.")}
            </p>
        </div>
    </div>

    <div class="flex h-[51px] flex-1 md:flex-none md:w-[400px] {isRTL ? 'md:mr-auto' : 'md:ml-auto'} items-center justify-between rounded-[30px] bg-white px-4 shadow-md dark:bg-gray-900 dark:shadow-none dark:border dark:border-gray-800">
        
        <div class="flex min-w-[80px] flex-1 items-center gap-2.5 rounded-2xl px-1 sm:px-4 py-1">
            <SearchIcon className="h-[18px] w-[18px] text-gray-400 dark:text-gray-500" />
            <input type="text" class="w-full border-none bg-transparent text-[13px] focus:outline-none dark:text-white dark:placeholder-gray-500" 
                placeholder="{$i18n.t("Search")}"
                on:click|stopPropagation={() => {showUserDropdown = false; showNotifications = false;}}>
        </div>

        <div class="action-buttons flex items-center gap-1 sm:gap-2">
        
            <div class="relative flex items-center" bind:this={notificationRef}>
                <button class="flex h-8 w-8 items-center justify-center rounded-full transition hover:bg-gray-100 dark:hover:bg-gray-800" 
                    on:click|stopPropagation={toggleNotificationPanel}
                    aria-label={`Notifications${notificationCount > 0 ? ` (${notificationCount} unread)` : ''}`}>
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600 dark:text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                        </svg>
                        {#if notificationCount > 0}
                            <span class="absolute {isRTL ? '-left-1' : '-right-1'} -top-1 flex min-w-[16px] items-center justify-center rounded-full border-2 border-white bg-red-500 px-1 text-[10px] font-bold text-white dark:border-gray-900">
                                {notificationCount}
                            </span>
                        {/if}
                </button>

                {#if showNotifications}
                    <div class="absolute {isRTL ? 'left-0' : 'right-0'} top-[calc(100%+12px)] z-[100] w-[280px] overflow-hidden rounded-xl border border-slate-100 bg-white shadow-xl animate-in fade-in slide-in-from-top-2 dark:border-gray-800 dark:bg-gray-900">
                        <div class="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-800/50">
                            <h3 class="m-0 text-sm font-semibold text-slate-800 dark:text-gray-200">
                                {$i18n.t("Notifications")}</h3>
                            {#if notificationCount > 0}
                                <button class="rounded px-2 py-1 text-[11px] text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20" 
                                on:click={() => (notificationCount = 0)}>
                                    {$i18n.t("Mark all as read")}
                                </button>
                            {/if}
                        </div>
                        <div class="flex max-h-[250px] flex-col gap-1 overflow-y-auto p-2">
                            <div class="py-5 text-center text-sm text-slate-400 dark:text-gray-500">{$i18n.t("No new notifications")}</div>
                        </div>
                        <div class="border-t border-slate-100 p-2 text-center dark:border-gray-800">
                            <button class="w-full rounded-md bg-slate-50 py-2 text-sm text-slate-600 transition hover:bg-slate-100 hover:text-blue-600 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-blue-400">
                                {$i18n.t("View all notifications")}
                            </button>
                        </div>
                    </div>
                {/if}
            </div>

            <div class="relative flex items-center">
                <button class="relative flex h-9 w-9 items-center justify-center rounded-full transition-all hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none active:scale-90"
                    on:click|stopPropagation={toggleTheme}>
                    {#if $theme === 'dark' || ($theme === 'system' && typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches)}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-400 transition-all rotate-0 scale-100" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                    {:else}
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-700 transition-all -rotate-12 scale-100" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                        </svg>
                    {/if}
                </button>
            </div>

            <div>
                <button class="flex h-8 w-8 items-center justify-center rounded-full hover:bg-gray-100 dark:hover:bg-gray-800">
                    <Info className="h-5 w-5 text-gray-600 dark:text-gray-300" />
                </button>
            </div>

            <div class="relative flex items-center">
                <button aria-label="User Profile" on:click|stopPropagation={showProfilePanel} class="flex items-center">
                    <img src={profileImageUrl} alt="UserAvatar" class="h-[35px] w-[35px] cursor-pointer rounded-full border-2 border-transparent transition-all hover:scale-105 hover:border-slate-200 dark:hover:border-gray-700">
                </button>
                {#if showUserDropdown}
                    <div class="absolute {isRTL ? 'left-0' : 'right-0'} top-[calc(100%+12px)] z-50 w-[220px] overflow-hidden rounded-xl border border-slate-100 bg-white shadow-xl animate-in fade-in slide-in-from-top-2 dark:border-gray-800 dark:bg-gray-900">
                        <div class="flex flex-col bg-slate-50 px-4 py-3 dark:bg-gray-800/50">
                            <span class="text-sm font-semibold text-slate-800 dark:text-gray-100">{$user?.name}</span>
                            <span class="text-xs text-slate-500 dark:text-gray-400">{$user?.email}</span>
                        </div>

                        <div class="border-y border-slate-100 p-1.5 dark:border-gray-800">
                            <a href="/teacher/Setting" class="group flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm text-slate-600 transition hover:bg-slate-50 hover:text-blue-600 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-blue-400">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-[18px] w-[18px] text-slate-400 group-hover:text-blue-600 dark:text-gray-500 dark:group-hover:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                                </svg>
                                {$i18n.t("My Profile")}
                            </a>
                            <a href="/teacher/Setting" class="group flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm text-slate-600 transition hover:bg-slate-50 hover:text-blue-600 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-blue-400">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-[18px] w-[18px] text-slate-400 group-hover:text-blue-600 dark:text-gray-500 dark:group-hover:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                                </svg>
                                {$i18n.t("Account Settings")}
                            </a>
                        </div>

                        <div class="p-1.5">
                            <button 
                                class="group flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm text-slate-600 transition hover:bg-rose-50 hover:text-rose-600 dark:text-gray-300 dark:hover:bg-rose-900/20 dark:hover:text-rose-400"
                                on:click|stopPropagation={() => {localStorage.removeItem('token'); location.href = '/auth';}}>

                                <svg xmlns="http://www.w3.org/2000/svg" class="h-[18px] w-[18px] text-slate-400 group-hover:text-rose-600 dark:text-gray-500 dark:group-hover:text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                                </svg>
                                {$i18n.t("Sign Out")}
                            </button>
                        </div>
                    </div>
                {/if}
            </div>

        </div>
    </div>
</div>