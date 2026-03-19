<script lang="ts">
    import { onMount, getContext } from 'svelte';
    import { toast } from 'svelte-sonner';
    import { user, theme } from '$lib/stores'; 
    import { getGravatarUrl } from '$lib/apis/utils';
    import { generateInitialsImage } from '$lib/utils';
    import { updateUserPassword, updateUserProfile, getSessionUser } from '$lib/apis/auths';
    import { getLanguages } from '$lib/i18n';
    
    import { type Writable } from 'svelte/store';
    import type { i18n as i18nType } from 'i18next';

    export let saveHandler: Function = () => {};

    let profileImageInputElement: HTMLInputElement;
    $: $user = $user;
    let name: string = '';
    let profileImageUrl: string = '';

    let show = false;
    let currentPassword = '';
    let newPassword = '';
    let newPasswordConfirm = '';

    let i18n = getContext<Writable<i18nType>>('i18n'); 
    let languages: Awaited<ReturnType<typeof getLanguages>> = [];
    let lang = $i18n.language;

    let selectedTheme = 'light';
    
    // --- Image Logic ---
    const handleImageChange = (e: Event) => {
        const files = profileImageInputElement.files;
        if (!files || files.length === 0) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            const img = new Image();
            img.src = event.target?.result as string;
            img.onload = () => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = 250; canvas.height = 250;
                const aspectRatio = img.width / img.height;
                let newW = 250, newH = 250;
                if (aspectRatio > 1) newH = 250 / aspectRatio; else newW = 250 * aspectRatio;
                ctx?.drawImage(img, (250 - newW) / 2, (250 - newH) / 2, newW, newH);
                profileImageUrl = canvas.toDataURL('image/jpeg', 0.8);
            };
        };
        reader.readAsDataURL(files[0]);
    };

    const setInitials = () => { profileImageUrl = generateInitialsImage(name || $user?.name || ''); };
    const setGravatar = async () => {
        try {
            const url = await getGravatarUrl(localStorage.token, $user?.email || '');
            if (url) { profileImageUrl = url; toast.success("Gravatar loaded!"); }
            else { toast.error("No Gravatar found."); }
        } catch (e) { toast.error("Error fetching Gravatar"); }
    };
    const removeImage = () => { profileImageUrl = '/user.png'; };

    // --- Password Action ---
    const updatePasswordHandler = async () => {
        if (newPassword !== newPasswordConfirm) {
            toast.error("The passwords you entered don't match.");
            return;
        }
        try {
            const res = await updateUserPassword(localStorage.token, currentPassword, newPassword);
            if (res) {
                toast.success('Password updated successfully.');
                currentPassword = ''; newPassword = ''; newPasswordConfirm = '';
            }
        } catch (error) {
            toast.error(`${error}`);
        }
    };

    const applyTheme = (_theme: string) => {
        let themeToApply = _theme === 'system' 
            ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
            : _theme;
        document.documentElement.classList.remove('light', 'dark');
        document.documentElement.classList.add(themeToApply);
    };

    const themeChangeHandler = (_theme: string) => {
        theme.set(_theme); 
        localStorage.setItem('theme', _theme); 
        applyTheme(_theme); 
        selectedTheme = _theme;
    };

    const submitHandler = async () => {
        if (name !== $user?.name && (profileImageUrl === generateInitialsImage($user?.name) || profileImageUrl === '')) {
            profileImageUrl = generateInitialsImage(name);
        }
        const updatedUser = await updateUserProfile(localStorage.token, name, profileImageUrl).catch(e => toast.error(`${e}`));
        if (updatedUser) {
            const sessionUser = await getSessionUser(localStorage.token).catch(e => null);
            await user.set(sessionUser);
            return true;
        }
        return false;
    };

    onMount(async() => {
        name = $user?.name || '';
        profileImageUrl = $user?.profile_image_url || '/user.png';
        selectedTheme = localStorage.theme ?? 'system';
        applyTheme(selectedTheme);
        languages = await getLanguages();
        lang = $i18n.language;
    });
</script>

<div class="flex flex-col bg-[#F8FAFC] dark:bg-gray-950 text-[#334155] dark:text-gray-200 p-4 sm:p-6 font-sans w-full gap-5 transition-colors duration-200">

    <section class="flex flex-col sm:flex-row gap-6 sm:gap-10 bg-white dark:bg-gray-900 p-5 sm:p-6 rounded-3xl border border-[#e2e8f0] dark:border-gray-800 items-center sm:items-start">
        <input type="file" hidden accept="image/*" bind:this={profileImageInputElement} on:change={handleImageChange} />
        
        <div class="relative flex-shrink-0">
            <div class="w-24 h-24 sm:w-[100px] sm:h-[100px] rounded-full overflow-hidden border-[3px] border-blue-500 bg-[#f1f5f9] dark:bg-gray-800 shadow-sm">
                <img src={profileImageUrl || '/user.png'} alt="Profile" class="w-full h-full object-cover"/>
            </div>
            <button class="absolute bottom-1 right-1 bg-blue-600 text-white border-2 border-white dark:border-gray-900 rounded-full p-2 shadow-lg hover:scale-110 active:scale-90 transition-all" type="button" on:click={() => profileImageInputElement.click()}>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="14" height="14">
                    <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>
                </svg>
            </button>
        </div>

        <div class="flex-grow w-full">
            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3 text-center sm:text-left">{$i18n.t('Profile Image')}</h3>
            <div class="flex flex-wrap justify-center sm:justify-start gap-2 mb-6">
                <button class="bg-gray-100 dark:bg-gray-800 px-4 py-2 rounded-xl text-xs font-bold hover:bg-gray-200 dark:hover:bg-gray-700 transition-all" type="button" on:click={setInitials}>{$i18n.t('Initials')}</button>
                <button class="bg-gray-100 dark:bg-gray-800 px-4 py-2 rounded-xl text-xs font-bold hover:bg-gray-200 dark:hover:bg-gray-700 transition-all" type="button" on:click={setGravatar}>{$i18n.t('Gravatar')}</button>
                <button class="bg-red-50 dark:bg-red-900/20 text-red-600 px-4 py-2 rounded-xl text-xs font-bold hover:bg-red-100 transition-all" type="button" on:click={removeImage}>{$i18n.t('Remove')}</button>
            </div>

            <div class="w-full max-w-md mx-auto sm:mx-0">
                <label class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2" for="fullname">{$i18n.t('Full Name')}</label>
                <input id="fullname" type="text" class="w-full px-4 py-3 rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-800 dark:text-white outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all" bind:value={name} required/>
            </div>
        </div>
    </section>

    <section class="bg-white dark:bg-gray-900 p-5 sm:p-6 rounded-3xl border border-[#e2e8f0] dark:border-gray-800">
        <button class="w-full flex justify-between items-center" type="button" on:click={() => {show = !show;}}>
            <span class="text-base font-bold text-gray-900 dark:text-gray-100">{$i18n.t('Security & Password')}</span>
            <span class="text-blue-600 bg-blue-50 dark:bg-gray-900 p-2 rounded-lg transition-transform" style="transform: rotate({show ? '180deg' : '0deg'})">▼</span>
        </button>

        {#if show}
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
                <div class="w-full sm:col-span-2">
                    <label class="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-widest" for="Current password">{$i18n.t('Current Password')}</label>
                    <input type="password" placeholder="••••••••" class="w-full px-4 py-3 rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800" bind:value={currentPassword} />
                </div>
                <div class="w-full">
                    <label class="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-widest" for="new Password">{$i18n.t('New Password')}</label>
                    <input type="password" placeholder="••••••••" class="w-full px-4 py-3 rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800" bind:value={newPassword} />
                </div>
                <div class="w-full">
                    <label class="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-widest" for="Confirm">{$i18n.t('Confirm Password')}</label>
                    <input type="password" placeholder="••••••••" class="w-full px-4 py-3 rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800" bind:value={newPasswordConfirm} />
                </div>
                <div class="w-full sm:col-span-2">
                    <button class="w-full sm:w-auto bg-blue-600 text-white px-8 py-3 rounded-2xl font-bold hover:bg-blue-700 active:scale-95 transition-all mt-2" on:click={updatePasswordHandler}>
                        {$i18n.t('Update password')}
                    </button>
                </div>
            </div>
        {/if}
    </section>

    <section class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="bg-white dark:bg-gray-900 p-5 rounded-3xl border border-gray-100 dark:border-gray-800">
            <label class="block text-xs font-bold text-gray-400 mb-3 uppercase tracking-widest" for="theme">{$i18n.t('Theme')}</label>
            <select id="theme" class="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl py-3 px-4 font-semibold outline-none custom-select-bg" bind:value={selectedTheme} on:change={() => themeChangeHandler(selectedTheme)}>
                <option value="system">💻 {$i18n.t('System')}</option>
                <option value="dark">🌑 {$i18n.t('Dark')}</option>
                <option value="light">☀️ {$i18n.t('Light')}</option>
            </select>
        </div>

        <div class="bg-white dark:bg-gray-900 p-5 rounded-3xl border border-gray-100 dark:border-gray-800">
            <label class="block text-xs font-bold text-gray-400 mb-3 uppercase tracking-widest" for="language">{$i18n.t('Language')}</label>
            <select id="language" class="w-full bg-gray-50 dark:bg-gray-800 border-none rounded-xl py-3 px-4 font-semibold outline-none custom-select-bg" bind:value={lang} on:change={() => { $i18n.changeLanguage(lang); localStorage.setItem('lang', lang); }}>
                {#each languages as l}
                    <option value={l.code}>{l.title}</option>
                {/each}
            </select>
        </div>
    </section>

    <footer class="mt-6 flex justify-center sm:justify-end">
        <button class="w-full sm:w-auto bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-12 py-4 rounded-full font-bold shadow-xl shadow-blue-500/20 hover:scale-105 active:scale-95 transition-all" type="button" on:click={async () => {
                const res = await submitHandler();
                if (res) { toast.success($i18n.t('Settings Saved!')); saveHandler(); }
            }}>
            {$i18n.t('Save Changes')}
        </button>
    </footer>
</div>

<style>
    .custom-select-bg {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: right 16px center;
        appearance: none;
    }
</style>