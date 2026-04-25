<script lang="ts">
	import type { RagSource } from '$lib/hooks/store/use-history.hook';
	import { api } from '$lib/api';
	import ShInput from '$lib/components/sh-input/sh-input.svelte';
	import ShButton from '$lib/components/sh-button/sh-button.svelte';
	import ShSpinner from '$lib/components/sh-spinner/sh-spinner.svelte';
	import ShResponsiveDialog from '$lib/components/sh-responsive-dialog/sh-responsive-dialog.svelte';
	import FileTextIcon from '@lucide/svelte/icons/file-text';
	import ArrowLeftIcon from '@lucide/svelte/icons/arrow-left';
	import EyeIcon from '@lucide/svelte/icons/eye';

	let {
		open = $bindable(false),
		sources = []
	}: {
		open: boolean;
		sources: RagSource[];
	} = $props();

	let search = $state('');
	let viewingSource = $state<RagSource | null>(null);
	let docContent = $state<string | null>(null);
	let docLoading = $state(false);
	let docError = $state<string | null>(null);

	const filtered = $derived(
		search.trim()
			? sources.filter((s) => s.source_file.toLowerCase().includes(search.trim().toLowerCase()))
			: sources
	);

	async function openDocument(src: RagSource) {
		viewingSource = src;
		docContent = null;
		docError = null;
		docLoading = true;
		try {
			const data = await api.get<{ content: string }>(
				`/documents/${encodeURIComponent(src.source_file)}/content`
			);
			docContent = data.content;
		} catch {
			docError = 'Não foi possível carregar o conteúdo do documento.';
		} finally {
			docLoading = false;
		}
	}

	function backToList() {
		viewingSource = null;
		docContent = null;
		docError = null;
	}

	$effect(() => {
		if (!open) {
			viewingSource = null;
			docContent = null;
			docError = null;
			search = '';
		}
	});
</script>

<ShResponsiveDialog bind:open class="w-[95vw] sm:max-w-300 flex flex-col max-h-[90vh]" contentClass="flex min-h-0 flex-1 flex-col p-0 overflow-hidden">
	{#snippet title()}
		{#if viewingSource}
			<div class="flex items-center gap-2 min-w-0">
				<ShButton variant="ghost" size="icon-sm" onclick={backToList} aria-label="Voltar">
					<ArrowLeftIcon class="size-4" />
				</ShButton>
				<FileTextIcon class="size-4 shrink-0 text-muted-foreground" />
				<span class="truncate text-sm font-medium">{viewingSource.source_file}</span>
			</div>
		{:else}
			Fontes da conversa ({sources.length})
		{/if}
	{/snippet}

	{#if viewingSource}
		<!-- ── Conteúdo completo do documento ── -->
		{#if docLoading}
			<div class="flex flex-1 items-center justify-center py-10">
				<ShSpinner class="size-6" />
			</div>
		{:else if docError}
			<p class="flex-1 px-4 py-6 text-center text-sm text-destructive">{docError}</p>
		{:else if docContent}
			<textarea
				readonly
				class="h-[55vh] w-full resize-none rounded-md border bg-muted p-3 font-mono text-xs focus:outline-none md:h-[60vh] md:text-sm mx-4 mb-4"
				value={docContent}
			></textarea>
		{/if}
	{:else}
		<!-- ── Lista de fontes ── -->
		<div class="shrink-0 border-b border-border px-4 py-3">
			<ShInput placeholder="Buscar por arquivo…" bind:value={search} />
		</div>

		<div class="flex-1 overflow-y-auto px-4 py-3">
			{#if filtered.length === 0}
				<p class="py-6 text-center text-sm text-muted-foreground">
					{search.trim()
						? 'Nenhuma fonte encontrada para essa busca.'
						: 'Sem fontes disponíveis.'}
				</p>
			{:else}
				<div class="flex flex-col gap-3">
					{#each filtered as src (`${src.source_file}-${src.score}`)}
						<div class="rounded-lg border border-border bg-muted/20 p-4">
							<div class="mb-2 flex items-start justify-between gap-3">
								<span class="flex items-center gap-1.5 break-all text-sm font-medium text-foreground">
									<FileTextIcon class="mt-0.5 size-4 shrink-0 text-muted-foreground" />
									{src.source_file}
								</span>
								<div class="flex shrink-0 items-center gap-2">
									<span class="text-xs text-muted-foreground">
										{(src.score * 100).toFixed(0)}%
									</span>
									<ShButton
										variant="ghost"
										size="icon-sm"
										title="Ver documento completo"
										onclick={() => openDocument(src)}
									>
										<EyeIcon class="size-3.5" />
									</ShButton>
								</div>
							</div>
							<p class="whitespace-pre-wrap text-sm text-muted-foreground">{src.chunk_text}</p>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</ShResponsiveDialog>
