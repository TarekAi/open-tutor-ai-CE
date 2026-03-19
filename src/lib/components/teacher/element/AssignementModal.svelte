<script lang="ts">
    import { getContext, onMount } from 'svelte';
    import { createEventDispatcher } from 'svelte';
    import { browser } from '$app/environment';
    import { getMyClasses } from '$lib/apis/classe';
    import type { Writable } from 'svelte/store';

    export let assignmentId: string | number | null = null;
    export let title = '';
    export let description = '';
    export let classe_id = '';
    export let deadline;
    export let points = 0;

    const dispatch = createEventDispatcher();
    const getToken = () => (browser ? (localStorage.getItem('token') ?? '') : '');
    const token = getToken();

    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    let assignmentTitle = title;
    let assignmentDescription = description;
    let assignmentClass = classe_id;
    let assignmentDueDate = deadline;
    let assignmentMaxPoints = points;
    let ClassOptions: any[] = [];
    let assignmentsError = '';

    $: {
        assignmentTitle = title || '';
        assignmentDescription = description || '';
        assignmentClass = classe_id || '';
        assignmentDueDate = deadline ? formatDate(deadline) : '';
        assignmentMaxPoints = points || 0;
    }

    function closeModal() {
        dispatch('close');
    }

    function formatDate(dateInput: any) {
        if (!dateInput) return '';
        const date = new Date(dateInput);
        if (isNaN(date.getTime())) return ''; 
        return date.toISOString().split('T')[0]; 
    }

    async function AddAssignment() {
        if (!assignmentTitle.trim()  || !assignmentDueDate.trim() || assignmentMaxPoints < 0 || !assignmentClass) {
            alert($i18n.t('Please fill all fields'));
            return;
        }
        const payload = {
            title: assignmentTitle,
            description: assignmentDescription,
            classe_id: assignmentClass,
            deadline: assignmentDueDate,
            points: assignmentMaxPoints
        };
        dispatch('save', payload);
        closeModal();
    }

    onMount(async () => {
        try {
            ClassOptions = await getMyClasses(token);
        } catch (err: any) {
            assignmentsError = err || 'Failed to load classes';
            console.error(err);
        }
    });
</script>

<main class="fixed inset-0 z-[1000] flex items-end md:items-center justify-center bg-slate-900/70 dark:bg-black/80 md:p-5 backdrop-blur-sm transition-all">
    <div class="flex h-[95vh] md:h-auto max-h-[95vh] md:max-h-[90vh] w-full md:max-w-[520px] origin-bottom md:origin-center animate-pop flex-col overflow-hidden rounded-t-[24px] md:rounded-[24px] bg-white dark:bg-gray-900 p-6 md:p-8 shadow-2xl transition-colors duration-200">
        
        <div class="flex flex-shrink-0 items-center justify-between border-b border-gray-200 dark:border-gray-800 pb-4">
            <h2 class="m-0 text-lg md:text-xl font-semibold text-gray-900 dark:text-white">
                {$i18n.t(assignmentId ? 'Modify the Assignment' : 'Create an Assignment')}
            </h2>
            <button class="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 transition-all md:hover:rotate-90"
                on:click={closeModal}
                aria-label="Close">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M18 6L6 18M6 6l12 12" />
                </svg>
            </button>
        </div>

        <div class="flex-grow overflow-y-auto py-6 font-['Inter']">
            <div class="mb-5 flex flex-col gap-2">
                <label for="title" class="text-sm font-medium text-gray-700 dark:text-gray-300">{$i18n.t('Assignment Title')}</label>
                <input id="title" type="text" placeholder="{$i18n.t('Enter assignment title')}" bind:value={assignmentTitle}
                    class="rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 p-3.5 text-[15px] text-gray-900 dark:text-white outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all"/>
            </div>

            <div class="mb-5 flex flex-col gap-2">
                <label for="desc" class="text-sm font-medium text-gray-700 dark:text-gray-300">{$i18n.t('Description')}</label>
                <textarea id="desc" rows="3" bind:value={assignmentDescription}
                    class="rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 p-3.5 text-[15px] text-gray-900 dark:text-white outline-none focus:border-blue-500 transition-all"
                    placeholder="{$i18n.t('Enter assignment description...')}"
                />
            </div>

            <div class="mb-5 flex flex-col gap-2">
                <label for="class" class="text-sm font-medium text-gray-700 dark:text-gray-300">{$i18n.t('Class')}</label>
                <select id="class" bind:value={assignmentClass}
                    class="rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 p-3.5 text-[15px] text-gray-900 dark:text-white outline-none focus:border-blue-500 appearance-none bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20fill%3D%22none%22%20viewBox%3D%220%200%2024%2024%20stroke%3D%22currentColor%22%3E%3Cpath%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%20stroke-width%3D%222%22%20d%3D%22M19%209l-7%207-7-7%22%20%2F%3E%3C%2Fsvg%3E')] bg-[length:1.25rem] bg-[right_0.875rem_center] bg-no-repeat transition-all">
                    <option value="" disabled selected>{$i18n.t('Choose option...')}</option>
                    {#each ClassOptions as classOption}
                        <option value={classOption.id}>
                            {classOption.name} {classOption.course ? `- ${classOption.course}` : ''}
                        </option>
                    {/each}
                </select>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
                <div class="flex flex-col gap-2">
                    <label for="date" class="text-sm font-medium text-gray-700 dark:text-gray-300">{$i18n.t('Due Date')}</label>
                    <input id="date" type="date" bind:value={assignmentDueDate}
                        class="rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 p-3.5 text-[15px] text-gray-900 dark:text-white outline-none focus:border-blue-500 transition-all"/>
                </div>
                <div class="flex flex-col gap-2">
                    <label for="points" class="text-sm font-medium text-gray-700 dark:text-gray-300">{$i18n.t('Max Points')}</label>
                    <input id="points" type="number" min="0" bind:value={assignmentMaxPoints}
                        class="rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 p-3.5 text-[15px] text-gray-900 dark:text-white outline-none focus:border-blue-500 transition-all"/>
                </div>
            </div>
        </div>

        <div class="flex-shrink-0 flex flex-col-reverse md:flex-row gap-3 border-t border-gray-200 dark:border-gray-800 pt-5 mt-auto">
            <button class="w-full md:flex-1 rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 py-3.5 text-[15px] font-semibold text-gray-700 dark:text-gray-300 transition-all active:bg-gray-100 dark:active:bg-gray-700"
                on:click={closeModal}>
                {$i18n.t('Cancel')}
            </button>
            <button class="w-full md:flex-1 rounded-xl border-none bg-blue-600 py-3.5 text-[15px] font-bold text-white transition-all shadow-lg shadow-blue-500/20 active:scale-[0.98] hover:bg-blue-700"
                on:click={AddAssignment}>
                {$i18n.t(assignmentId ? 'Modify Assignment': 'Create Assignment')}
            </button>
        </div>
    </div>
</main>

<style>
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(100%); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInPop {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }

    /* Use slideUp on mobile, scale on desktop */
    .animate-pop {
        animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @media (min-width: 768px) {
        .animate-pop {
            animation: fadeInPop 0.2s ease-out;
        }
    }

    /* Hide scrollbar for cleaner look */
    .overflow-y-auto::-webkit-scrollbar {
        width: 4px;
    }
    .overflow-y-auto::-webkit-scrollbar-thumb {
        background: #e2e8f0;
        border-radius: 10px;
    }
</style>