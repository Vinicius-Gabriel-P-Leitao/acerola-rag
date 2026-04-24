<script lang="ts">
	import { documentsStore, type DocumentMeta } from '$lib/hooks/store/use-documents.hook';
	import ShInput from '$lib/components/sh-input/sh-input.svelte';
	import ShButton from '$lib/components/sh-button/sh-button.svelte';
	import ShSkeleton from '$lib/components/sh-skeleton/sh-skeleton.svelte';
	// ShPagination removido se não estiver sendo usado no HTML abaixo
	import EyeIcon from '@lucide/svelte/icons/eye';
	import TrashIcon from '@lucide/svelte/icons/trash-2';

	let { onView, onDelete } = $props<{
		onView: (source: string) => void;
		onDelete: (doc: DocumentMeta) => void;
	}>();

	let searchInput = $state('');
	let searchDebounce: ReturnType<typeof setTimeout>;

	function onSearchInput() {
		clearTimeout(searchDebounce);
		searchDebounce = setTimeout(() => documentsStore.setSearch(searchInput), 300);
	}

	const formatSize = (bytes: number) =>
		bytes < 1024 ? `${bytes} B` : `${(bytes / 1024).toFixed(1)} KB`;
	const formatDate = (iso: string) => iso.slice(0, 19).replace('T', ' ');
</script>

<section class="rounded-xl border border-border bg-card p-4 shadow-sm">
	<h2 class="mb-3 font-semibold text-card-foreground">📚 Documentos indexados</h2>
	<ShInput
		class="mb-3"
		placeholder="🔍 Buscar por nome…"
		bind:value={searchInput}
		oninput={onSearchInput}
	/>

	{#if $documentsStore.loading && $documentsStore.items.length === 0}
		<div class="flex flex-col gap-2">
			{#each { length: 3 } as _, i (i)}
				<!-- Chave (i) adicionada aqui -->
				<ShSkeleton class="h-10 w-full" />
			{/each}
		</div>
	{:else if $documentsStore.items.length === 0}
		<p class="text-sm text-muted-foreground">Nenhum documento encontrado.</p>
	{:else}
		<div class="flex flex-col divide-y">
			{#each $documentsStore.items as doc (doc.source)}
				<div class="flex items-center gap-2 py-2.5">
					<div class="min-w-0 flex-1">
						<p class="truncate text-sm font-medium">{doc.source}</p>
						<p class="text-xs text-muted-foreground">
							{doc.file_type} · {formatSize(doc.file_size_bytes)} · {formatDate(doc.uploaded_at)}
						</p>
					</div>

					<ShButton variant="ghost" size="icon-sm" onclick={() => onView(doc.source)}>
						<EyeIcon class="size-4" />
					</ShButton>

					<ShButton
						variant="ghost"
						size="icon-sm"
						class="text-destructive hover:text-destructive"
						onclick={() => onDelete(doc)}
					>
						<TrashIcon class="size-4" />
					</ShButton>
				</div>
			{/each}
		</div>
	{/if}
</section>
