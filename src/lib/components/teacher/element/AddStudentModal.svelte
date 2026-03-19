<script lang="ts">
    import { createEventDispatcher, getContext } from 'svelte';
    import { fade, fly, scale } from 'svelte/transition';
    import { browser } from '$app/environment';
    import { toast } from 'svelte-sonner';
    import QRCode from 'qrcode';
    import { addStudentToClass } from '$lib/apis/classe';
    import type { Writable } from 'svelte/store';

    const getToken = () => (browser ? localStorage.getItem('token') ?? '' : '');

    export let classId: string;
    $: inviteLink = `https://tutorClass.app/join/${classId}`;

    const dispatch = createEventDispatcher();
    
    let activeStep = 'selection';
    let copied = false;
    let studentName = '';
    let studentEmail = '';
    let isSubmitting = false;

    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    // Had l-array rji'nah reactive ($:) bach l-labels yt-traduizaw f l-blassa
    $: methods = [
        {
            id: 'invite',
            title: $i18n.t('Invite via Link or QR'),
            desc: $i18n.t('Fastest way. Scan or click to join.'),
            icon: `<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/><line x1="7" y1="7" x2="7.01" y2="7"/><line x1="7" y1="17" x2="7.01" y2="17"/><line x1="17" y1="7" x2="17.01" y2="7"/>`,
            colorClass: 'text-blue-600 dark:text-blue-400',
            bgClass: 'bg-blue-50 dark:bg-blue-900/30',
            hoverBorder: 'hover:border-blue-500'
        },
        {
            id: 'manual',
            title: $i18n.t('Add manually'),
            desc: $i18n.t('Type names one by one.'),
            icon: `<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/>`,
            colorClass: 'text-purple-600 dark:text-purple-400',
            bgClass: 'bg-purple-50 dark:bg-purple-900/30',
            hoverBorder: 'hover:border-purple-500'
        }
    ];

    function selectMethod(id: string) { activeStep = id; }
    function goBack() { activeStep = 'selection'; studentName = ''; studentEmail = ''; }
    
    async function downloadQR() {
    try {
        const canvas = document.querySelector('canvas');
        if (!canvas) return;

        const url = canvas.toDataURL("image/png");
        const a = document.createElement("a");
        a.href = url;
        a.download = `class-qr-${classId}.png`;
        a.click();

        toast.success($i18n.t("QR Code downloaded!"));
    } catch (err) {
        console.error(err);
        toast.error($i18n.t("Error downloading QR"));
    }
}

    async function copyLink() {
        try {
            await navigator.clipboard.writeText(inviteLink);
            copied = true;
            setTimeout(() => (copied = false), 2000);
            toast.success($i18n.t("Copied to Clipboard!"));
        } catch (err) { console.error('Err:', err); }
    }

    function qrAction(node: HTMLCanvasElement, text: string) {
        const update = (newText: string) => {
            QRCode.toCanvas(node, newText, { 
                width: browser && window.innerWidth < 640 ? 130 : 160, 
                margin: 2, 
                color: { dark: '#0f172a', light: '#ffffff' } 
            });
        };
        update(text);
        return { update(newText: string) { update(newText); }};
    }

    async function handleManualAdd() {
        if (!studentEmail) return;
        isSubmitting = true;
        try {
            const response = await addStudentToClass(getToken(), {
                name: studentName,
                email: studentEmail,
                classId: classId
            });
            dispatch('save', response);
            studentName = '';
            studentEmail = '';
            toast.success($i18n.t("Student added successfully!"));
        } catch (error) {
            toast.error($i18n.t("Error adding student"));
        } finally {
            isSubmitting = false;
        }
    }

    const modalTransition = (node: HTMLElement) => {
        return window.innerWidth < 768 
            ? fly(node, { y: 100, duration: 300 }) 
            : scale(node, { duration: 200, start: 0.95 });
    };
</script>

<main class="fixed inset-0 z-[1000] flex items-end md:items-center justify-center bg-slate-900/70 dark:bg-black/80 md:p-5 backdrop-blur-sm">
    <div class="w-full max-h-[92vh] md:max-w-[500px] rounded-t-[24px] md:rounded-[24px] bg-white dark:bg-gray-950 p-6 md:p-8 shadow-2xl border-t md:border border-gray-100 dark:border-gray-800 flex flex-col" 
         transition:modalTransition>
        
        <header class="flex items-center justify-between border-b border-gray-50 dark:border-gray-800 pb-4 mb-2">
            <div class="flex items-center gap-2">
                {#if activeStep !== 'selection'}
                    <button class="p-2 -ml-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors" on:click={goBack}>
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="text-indigo-600">
                            <path d="M15 18l-6-6 6-6"/>
                        </svg>
                    </button>
                {/if}
                <h2 class="text-lg md:text-xl font-bold text-gray-900 dark:text-white">
                    {activeStep === 'selection' ? $i18n.t('Add Students') : activeStep === 'invite' ? $i18n.t('Invite Students') : $i18n.t('Add Manually')}
                </h2>
            </div>
            <button class="h-10 w-10 flex items-center justify-center rounded-full bg-gray-50 dark:bg-gray-900 text-gray-400 hover:text-red-500 transition-all" on:click={() => dispatch('close')}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
        </header>

        <div class="overflow-y-auto py-4">
            {#if activeStep === 'selection'}
                <div in:fade={{ duration: 200 }}>
                    <p class="mb-6 text-sm text-gray-500 dark:text-gray-400">{$i18n.t('Select Method Description')}</p>
                    <div class="flex flex-col gap-3">
                        {#each methods as method}
                            <button class="group flex items-center border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50 p-4 rounded-2xl transition-all active:scale-[0.98] md:hover:bg-white dark:md:hover:bg-gray-900 {method.hoverBorder}" on:click={() => selectMethod(method.id)}>
                                <div class="mr-4 flex h-12 w-12 shrink-0 items-center justify-center rounded-xl {method.bgClass} {method.colorClass}">
                                    <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">{@html method.icon}</svg>
                                </div>
                                <div class="flex-1 text-left">
                                    <h3 class="text-[15px] font-bold text-gray-800 dark:text-gray-200">{method.title}</h3>
                                    <p class="text-[12px] text-gray-500 dark:text-gray-400 leading-tight">{method.desc}</p>
                                </div>
                                <svg class="w-5 h-5 text-gray-300 dark:text-gray-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 18l6-6-6-6"/></svg>
                            </button>
                        {/each}
                    </div>
                </div>

            {:else if activeStep === 'invite'}
                <div class="flex flex-col gap-6 items-center text-center" in:fade>
                    <div class="bg-white p-3 rounded-2xl shadow-inner border dark:border-gray-800 mt-2">
                        <canvas use:qrAction={inviteLink}></canvas>
                    </div>
                    
                    <div class="w-full flex items-center gap-3">
                        <div class="h-px flex-1 bg-gray-100 dark:bg-gray-800"></div>
                        <span class="text-[11px] font-bold text-gray-400 uppercase tracking-widest">{$i18n.t('or link')}</span>
                        <div class="h-px flex-1 bg-gray-100 dark:bg-gray-800"></div>
                    </div>

                    <div class="w-full space-y-3">
                        <div class="flex flex-col gap-2 p-3 rounded-xl border border-dashed border-indigo-200 dark:border-indigo-900/50 bg-indigo-50/30 dark:bg-indigo-900/10">
                            <span class="text-xs font-mono text-indigo-600 dark:text-indigo-400 break-all select-all">{inviteLink}</span>
                        </div>
                        <button on:click={copyLink} class="w-full flex items-center justify-center gap-2 rounded-xl {copied ? 'bg-emerald-500' : 'bg-indigo-600'} py-3.5 text-sm font-bold text-white shadow-lg transition-all active:scale-95">
                            {#if copied}
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                                <span>{$i18n.t('Copied to Clipboard!')}</span>
                            {:else}
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                                <span>{$i18n.t('Copy Invitation Link')}</span>
                            {/if}
                        </button>
                        <button 
                            on:click={downloadQR} 
                            class="w-full flex items-center justify-center gap-2 rounded-xl bg-gray-900 dark:bg-gray-800 py-3.5 text-sm font-bold text-white shadow-lg transition-all active:scale-95">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                <polyline points="7 10 12 15 17 10"/>
                                <line x1="12" y1="15" x2="12" y2="3"/>
                            </svg>
                            <span>{$i18n.t('Download QR Code')}</span>
                        </button>
                    </div>
                </div>

            {:else if activeStep === 'manual'}
                <form on:submit|preventDefault={handleManualAdd} class="flex flex-col gap-5" in:fade>
                    <div class="space-y-4">
                        <div class="space-y-1.5">
                            <label for="studentEmail" class="text-xs font-bold uppercase tracking-wider text-gray-500 ml-1">{$i18n.t('Email Address')}</label>
                            <input id="studentEmail" type="email" bind:value={studentEmail} placeholder="student@exemple.com" required
                                class="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 p-3.5 text-[15px] outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all dark:text-white" />
                        </div>
                        <div class="space-y-1.5">
                            <label for="studentName" class="text-xs font-bold uppercase tracking-wider text-gray-500 ml-1">{$i18n.t('Full Name (Optional)')}</label>
                            <input id="studentName" type="text" bind:value={studentName} placeholder="e.g. Mohamed Alaoui"
                                class="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 p-3.5 text-[15px] outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all dark:text-white" />
                        </div>
                        <button type="submit" disabled={isSubmitting || !studentEmail}
                            class="w-full mt-2 bg-indigo-600 py-4 rounded-xl font-bold text-white shadow-lg shadow-indigo-500/20 active:scale-[0.98] disabled:opacity-50 transition-all flex items-center justify-center gap-2">
                            {#if isSubmitting}
                                <div class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                <span>{$i18n.t('Adding...')}</span>
                            {:else}
                                <span>{$i18n.t('Add to Class')}</span>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
                            {/if}
                        </button>
                    </div>
                </form>
            {/if}
        </div>

        {#if activeStep === 'selection'}
            <footer class="mt-auto pt-4 border-t border-gray-50 dark:border-gray-800 text-center">
                <p class="text-xs text-gray-400">
                    {$i18n.t('Need help?')} <a href="/docs" class="text-indigo-500 font-semibold underline-offset-4 hover:underline">{$i18n.t('View Tutorial')}</a>
                </p>
            </footer>
        {/if}
    </div>
</main>

<style>
    :global(body) {
        overflow: hidden;
    }
</style>