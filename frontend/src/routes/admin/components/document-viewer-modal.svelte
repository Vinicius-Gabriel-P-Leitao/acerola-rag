<script lang="ts">
	import { fly, fade } from 'svelte/transition';
	import ShSpinner from '$lib/components/sh-spinner/sh-spinner.svelte';
	import XIcon from '@lucide/svelte/icons/x';

	let {
		open = $bindable(),
		doc,
		loading
	} = $props<{
		open: boolean;
		doc: { source: string; content: string } | null;
		loading: boolean;
	}>();
</script>

{#if open}
	<div
		class="fixed inset-0 z-50 bg-black/50"
		transition:fade
		onclick={() => (open = false)}
		role="presentation"
	></div>

	<!-- Mobile -->
	<div
		class="fixed inset-x-0 bottom-0 z-50 flex h-[88vh] flex-col rounded-t-2xl bg-card md:hidden"
		transition:fly={{ y: 400 }}
	>
		<div class="flex items-center justify-between border-b px-4 py-3">
			<p class="max-w-[80%] truncate font-semibold">{doc?.source || 'Carregando...'}</p>
			<button onclick={() => (open = false)}><XIcon class="size-5" /></button>
		</div>

		<!-- Container do conteúdo: flex-1 e SEM overflow -->
		<div class="flex min-h-0 flex-1 flex-col p-4">
			{#if loading}
				<div class="flex flex-1 items-center justify-center">
					<ShSpinner class="size-6" />
				</div>
			{:else if doc}
				<!-- Textarea: h-full e flex-1 garantem que o scroll fique só aqui -->
				<textarea
					readonly
					class="w-full flex-1 resize-none rounded-md border bg-muted p-3 font-mono text-xs focus:outline-none"
					value={doc.content}
				></textarea>
			{/if}
		</div>
	</div>

	<!-- Desktop -->
	<div
		class="pointer-events-none fixed inset-0 z-50 hidden items-center justify-center p-6 md:flex"
	>
		<div
			class="pointer-events-auto flex h-[80vh] w-full max-w-4xl flex-col rounded-xl bg-card shadow-xl"
			transition:fly={{ y: -16 }}
		>
			<div class="flex items-center justify-between border-b px-6 py-4">
				<p class="font-semibold">{doc?.source || 'Carregando...'}</p>
				<button onclick={() => (open = false)}><XIcon class="size-5" /></button>
			</div>

			<!-- Container do conteúdo: flex-1 e SEM overflow -->
			<div class="flex min-h-0 flex-1 flex-col p-6">
				{#if loading}
					<div class="flex flex-1 items-center justify-center">
						<ShSpinner class="size-6" />
					</div>
				{:else if doc}
					<textarea
						readonly
						class="w-full flex-1 resize-none rounded-md border bg-muted p-4 font-mono text-sm focus:outline-none"
						value={doc.content}
					></textarea>
				{/if}
			</div>
		</div>
	</div>
{/if}
