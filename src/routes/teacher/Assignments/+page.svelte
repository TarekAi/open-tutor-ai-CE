<script lang="ts">
    import AssignementModal from '$lib/components/teacher/element/AssignementModal.svelte';
    import ConfirmModal from '$lib/components/teacher/element/ConfirmModal.svelte';

    import updateIcon from '$lib/components/icons/Pencil.svelte';
    import { getContext, onMount } from 'svelte';
    import { toast } from 'svelte-sonner';
    import { browser } from '$app/environment';
    import { getMyAssignment, createNewAssignment ,deleteAssignmentById , updateAssignment , getAssignmentStats} from '$lib/apis/assignment';
    import type { AssignmentResponse, AssignmentCreateRequest } from '$lib/apis/assignment';
    import type { Writable } from 'svelte/store';

    let stats = {
        total: 0,
        pending: 0,
        avg_rate: '0%',
        completion: '0%',
        total_change: '0%',
        avg_rate_change: '0%',
        pending_change: '0%',
        completion_change: '0%'
    };
    
    let showAssignementModal: boolean = false;
    let selectedAssignmentData: AssignmentCreateRequest | null = null;
    let selectedAssignmentId: string | null = null;

    let showMoreDropdown: string | number | null = null;
    let loading = true;
    let Assignements: AssignmentResponse[] = [];

    let assignmentToDelete :string | null =null;
    let showDeleteModal=false;

    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    // Stats m-traduizyin dynamicamente
    $: StatsMenu = [
        { label: $i18n.t('Total Assignments'), value: stats.total, change: stats.total_change }, 
        { label: $i18n.t('Avg Submission Rate'), value: stats.avg_rate, change: stats.avg_rate_change }, 
        { label: $i18n.t('Pending Review'), value: stats.pending, change: stats.pending_change }, 
        { label: $i18n.t('Completion Rate'), value: stats.completion, change: stats.completion_change }
    ];

    const getToken = () => (browser ? (localStorage.getItem('token') ?? '') : '');
    
    function openModal() { showAssignementModal = true; selectedAssignmentId = null; selectedAssignmentData = null; }
    function MoreDropdown(id: string | number) { showMoreDropdown = showMoreDropdown === id ? null : id; }
    function closeAllDropdowns() { showMoreDropdown = null; }

    async function SaveAssignment(event: CustomEvent<{title: string; description: string; classe_id: string; deadline: Date; points: number;}>) {
        const AssignmentData = event.detail;
        const token = getToken();
        if (!token) {
            toast.error($i18n.t('Session expired, please login again'));
            return;
        }
        try {
            if (selectedAssignmentId) {
                await updateAssignment(token, selectedAssignmentId, AssignmentData);
                toast.success($i18n.t('Assignment updated successfully'));
            } else {
                await createNewAssignment(token, AssignmentData);
                toast.success($i18n.t('Assignment created successfully'));
            }
            await loadAssignment();
            await loadStats();
            showAssignementModal = false;
        } catch (err: any) {
            toast.error($i18n.t('Error saving assignment'));
        }
    }

    function ModifyAssignment(assignmentId: string): void {
        const assignment = Assignements.find(c => c.id === assignmentId);
        if (assignment) {
            selectedAssignmentId = assignment.id;
            selectedAssignmentData = { ...assignment }; 
            showAssignementModal = true;
            closeAllDropdowns();
        }
    }

   function DeleteAssignment(AssignementId: string) {
        assignmentToDelete = AssignementId;
        showDeleteModal = true;
    }

    async function confirmDelete() {
        if (!assignmentToDelete) return;
        try {
            const token = getToken();
            await deleteAssignmentById(token, assignmentToDelete);
            Assignements = Assignements.filter(a => a.id !== assignmentToDelete);
            await loadStats();
            toast.success($i18n.t('Assignment deleted successfully'));
            showDeleteModal = false;
            assignmentToDelete = null;
        } catch (err) {
            console.error(err);
            toast.error($i18n.t('Error during deletion'));
        }
    }

    async function loadAssignment() {
        const token = getToken();
        if (!token) return;
        loading = true;
        try {
            Assignements = await getMyAssignment(token);
        } catch (err: any) {
            toast.error($i18n.t('Failed to load assignments'));
        } finally {
            loading = false;
        }
    }

    async function loadStats() {
        const token = getToken();
        try {
            stats = await getAssignmentStats(token);
        } catch (err) {
            console.error("Failed to load stats", err);
        }
    }

    onMount(() => {
        loadAssignment();
        loadStats(); 
        const handleClickOutside = (event: MouseEvent) => {
            if (!(event.target as HTMLElement).closest('.more-container')) {
                showMoreDropdown = null;
            }
        };
        document.addEventListener('click', handleClickOutside);
        return () => document.removeEventListener('click', handleClickOutside);
    });
</script>

<main class="m-0 p-4 md:p-[30px] pt-4 md:pt-0 bg-[#f8fafc] dark:bg-gray-950 min-h-screen transition-colors duration-200">
    <div class="grid grid-cols-2 lg:flex lg:flex-row justify-between gap-3 md:gap-[20px]">
        {#each StatsMenu as stat}
            <div class="w-full lg:w-[219px] h-auto md:h-[108px] bg-white dark:bg-gray-900 rounded-[20px] md:rounded-[27px] border border-[#f1f5f9] dark:border-gray-800 shadow-[0_1px_3px_rgba(0,0,0,0.05)] transition-all duration-300 md:hover:-translate-y-[5px] p-4 md:p-[20px] box-border">
                <p class="text-[#45484e] dark:text-gray-400 font-['Inter'] text-[12px] md:text-[14px] font-normal opacity-100 truncate">
                    {stat.label}
                </p>
                <h3 class="py-1 md:py-[10px] text-[18px] md:text-[24px] font-bold font-['Inter'] leading-none text-[#0F172A] dark:text-white">
                    {stat.value}
                </h3>
                <p class="font-['Inter'] font-normal text-[10px] md:text-[12px] leading-none text-[#22C55E] text-right">
                    {stat.change}
                </p>
            </div>
        {/each}
    </div>

    <div class="flex justify-end mt-6 md:mt-[20px]">
        <button class="w-full md:w-auto bg-[#3B82F6] text-white border-none py-[12px] px-[20px] rounded-[12px] md:rounded-[15px] text-[15px] md:text-[16px] font-medium cursor-pointer transition-colors duration-300 hover:bg-[#2563EB]"
            on:click={openModal}>
            {$i18n.t('Create Assignment')}
        </button>
        {#if showAssignementModal}
            <AssignementModal
                assignmentId={selectedAssignmentId}
                title={selectedAssignmentData?.title || ''}
                description={selectedAssignmentData?.description || ''}
                classe_id={selectedAssignmentData?.classe_id || ''}
                deadline={selectedAssignmentData?.deadline || ''}
                points={selectedAssignmentData?.points || 0}
                on:close={() => {
                    showAssignementModal = false;
                    selectedAssignmentData = null;
                }}
                on:save={SaveAssignment}
            />
        {/if}
    </div>

    <div class="mt-6 md:mt-[30px]">
        {#each Assignements as assignment (assignment.id)}
            <div class="bg-white dark:bg-gray-900 border border-[#F3F4F6] dark:border-gray-800 rounded-[16px] md:rounded-[12px] p-4 md:p-[24px] mb-[16px] font-['Inter'] transition-all duration-200 hover:shadow-md md:hover:-translate-y-[4px] md:hover:shadow-[0_12px_20px_-5px_rgba(0,0,0,0.05)]">
                <div class="flex justify-between items-start">
                    <div class="flex-grow mr-2 md:mr-[16px]">
                        <h3 class="text-[1rem] md:text-[1.1rem] font-semibold text-[#111827] dark:text-white mb-[4px]">{assignment.title}</h3>
                        <p class="text-[0.8rem] md:text-[0.85rem] text-[#6B7280] dark:text-gray-400 m-0 line-clamp-2 md:line-clamp-none">{assignment.description}</p>
                    </div>

                    <div class="flex items-center gap-4 md:gap-[30px]">
                        <div class="hidden sm:flex items-center gap-[6px] px-[12px] py-[4px] rounded-[20px] text-[0.75rem] font-medium 
                            {assignment.status === 'Active' ? 'bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400' : 
                            assignment.status === 'Pending' ? 'bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400' : 
                            'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'}">
                            <span class="w-[6px] h-[6px] rounded-full bg-current"></span>
                            {$i18n.t(assignment.status)}
                        </div>

                        <div class="relative more-container">
                            <button class="bg-none border-none text-[#9CA3AF] hover:text-gray-600 dark:hover:text-white cursor-pointer text-2xl p-1"
                                on:click|stopPropagation={() => MoreDropdown(assignment.id)}
                                aria-label="More options">⋮</button>
                            {#if showMoreDropdown === assignment.id}
                                <div class="absolute right-0 mt-2 w-48 origin-top-right bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-slate-100 dark:border-gray-700 z-[100] overflow-hidden animate-in">
                                    <div class="py-1">
                                        <button class="w-full px-4 py-3 sm:py-2.5 flex items-center gap-3 text-sm text-slate-600 dark:text-gray-300 hover:bg-slate-50 dark:hover:bg-gray-700 transition-colors"
                                            on:click|stopPropagation={() => ModifyAssignment(assignment.id)}>
                                            <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>
                                            <span>{$i18n.t('Update')}</span>
                                        </button>
                                        <button class="w-full px-4 py-3 sm:py-2.5 flex items-center gap-3 text-sm text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/30 transition-colors"
                                            on:click|stopPropagation={() => DeleteAssignment(assignment.id)}>
                                            <svg class="w-4 h-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
                                            <span>{$i18n.t('Delete')}</span>
                                        </button>
                                    </div>
                                </div>
                            {/if}
                        </div>
                    </div>
                </div>

                <div class="flex flex-wrap gap-x-4 gap-y-2 mt-[12px] text-[0.75rem] md:text-[0.8rem] text-[#6B7280] dark:text-gray-400">
                    <span class="flex items-center gap-1">📚 {assignment.classe_name}</span>
                    <span class="flex items-center gap-1">🗓️ {$i18n.t('Due')}: {new Date(assignment.deadline).toLocaleDateString('en-GB')}</span>
                </div>

                <hr class="border-0 border-t border-[#F3F4F6] dark:border-gray-800 my-4 md:my-[20px]" />

                <div class="flex flex-col md:flex-row gap-4 md:gap-[48px] md:items-center">
                    <div class="flex justify-between md:flex-col md:gap-[4px]">
                        <span class="text-[0.75rem] text-[#9CA3AF]">{$i18n.t('Submissions')}</span>
                        <span class="text-[0.9rem] font-semibold text-[#111827] dark:text-white">
                            {Math.min(assignment.current_submissions, assignment.max_submissions)} / {assignment.max_submissions}
                        </span>
                    </div>
                    
                    <div class="flex-grow md:max-w-[300px]">
                        <div class="flex justify-between mb-1 md:mb-[8px]">
                            <span class="text-[0.75rem] text-[#9CA3AF]">{$i18n.t('Submission Rate')}</span>
                            <span class="text-[0.85rem] md:text-[0.9rem] font-semibold text-[#111827] dark:text-white">
                                {assignment.max_submissions > 0 
                                    ? Math.min(Math.round((assignment.current_submissions / assignment.max_submissions) * 100), 100) 
                                    : 0}%
                            </span>
                        </div>
                        <div class="h-[6px] md:h-[8px] bg-[#F3F4F6] dark:bg-gray-800 rounded-full overflow-hidden">
                            <div class="h-full transition-all duration-300
                                {assignment.status === 'Active' ? 'bg-green-500' : 
                                assignment.status === 'Pending' ? 'bg-amber-500' : 
                                'bg-[#3B82F6]'}" 
                                style="width: {assignment.max_submissions > 0 
                                    ? Math.min((assignment.current_submissions / assignment.max_submissions) * 100, 100) 
                                    : 0}%">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        {:else}
            <div class="flex flex-col items-center justify-center py-12 px-6 bg-white dark:bg-gray-900 border-2 border-dashed border-[#E2E8F0] dark:border-gray-800 rounded-[24px] text-center mt-6">
                <div class="bg-[#F8FAFC] dark:bg-gray-800 text-[#94A3B8] w-16 h-16 md:w-[100px] md:h-[100px] rounded-full flex items-center justify-center mb-4">
                    <svg class="w-8 h-8 md:w-16 md:h-16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                        <polyline points="14 2 14 8 20 8" />
                    </svg>
                </div>
                <h3 class="text-lg font-semibold dark:text-white">{$i18n.t('No assignments yet')}</h3>
                <p class="text-sm text-[#64748B] dark:text-gray-400 mt-2 mb-6">{$i18n.t('Start by creating your first assignment!')}</p>
                <button class="bg-[#EFF6FF] dark:bg-blue-900/30 text-[#3B82F6] dark:text-blue-400 py-2 px-6 rounded-xl font-semibold" on:click={openModal}>
                    + {$i18n.t('Quick Create')}
                </button>
            </div>
        {/each}
    </div>

    <ConfirmModal
        bind:open={showDeleteModal}
        title={$i18n.t('Delete Assignment')}
        message={$i18n.t('Are you sure you want to delete this assignment? This action cannot be undone.')}
        confirmText={$i18n.t('Delete')}
        cancelText={$i18n.t('Cancel')}
        onConfirm={confirmDelete}
    />
</main>