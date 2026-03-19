<!-- chat/+page.svelte -->
<script lang="ts">
	import Chat from '$lib/components/student/tutor/Chat.svelte';
	import { page } from '$app/stores';
	import { isFullscreenAvatar } from '$lib/stores';
	
	let chatData = {};
	let isRightBarVisible = false;
	
	function handleChatEvent(event) {
		// Process chat events and update rightbar if needed
		chatData = {...chatData, ...event.detail};
	}

	function toggleRightBar() {
		isRightBarVisible = !isRightBarVisible;
	}
</script>

<div class="chat-layout flex h-full overflow-hidden relative bg-white dark:bg-gray-900 {$isFullscreenAvatar ? '' : 'p-2'}">
	<!-- Main Chat component takes most of the space -->
	<div class="chat-container flex-1 h-full overflow-hidden bg-[#F5F7F9] dark:bg-gray-900 {$isFullscreenAvatar ? '' : 'rounded-2xl shadow-sm mr-2'}">
		<Chat chatIdProp={$page.params.id} on:chatEvent={handleChatEvent} />
		
		<!-- Toggle button for mobile - hide in fullscreen -->
		{#if !$isFullscreenAvatar}
			<button
				class="toggle-rightbar hidden max-[1210px]:block fixed right-4 bottom-4 bg-blue-500 hover:bg-blue-600 text-white rounded-full p-2 shadow-lg z-99999"
				on:click={toggleRightBar}
				aria-label={isRightBarVisible ? 'Hide sidebar' : 'Show sidebar'}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					class="w-4 h-4"
				>
					{#if isRightBarVisible}
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					{:else}
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M15 19l-7-7 7-7"
						/>
					{/if}
				</svg>
			</button>
		{/if}
	</div>

</div>

<style>
	.chat-layout {
		/* Ensure this layout container takes full height within parent */
		height: 100%;
		width: 100%;
	}
	
	.chat-container{
		/* Ensure proper scroll containment */
		height: 100%;
	}
	
	.toggle-rightbar {
		transition: transform 0.3s ease-in-out;
	}

	.toggle-rightbar:hover {
		transform: scale(1.1);
	}
</style>