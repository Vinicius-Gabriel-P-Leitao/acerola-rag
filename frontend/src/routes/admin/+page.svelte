<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { documentsStore, type DocumentMeta } from '$lib/hooks/store/use-documents.hook';
	import ShButton from '$lib/components/sh-button/sh-button.svelte';
	import ShInput from '$lib/components/sh-input/sh-input.svelte';
	import ShTextarea from '$lib/components/sh-textarea/sh-textarea.svelte';
	import ShSpinner from '$lib/components/sh-spinner/sh-spinner.svelte';
	import ShSkeleton from '$lib/components/sh-skeleton/sh-skeleton.svelte';
	import ShDialog from '$lib/components/sh-dialog/sh-dialog.svelte';
	import ShDialogContent from '$lib/components/sh-dialog/sh-dialog-content.svelte';
	import ShDialogHeader from '$lib/components/sh-dialog/sh-dialog-header.svelte';
	import ShDialogTitle from '$lib/components/sh-dialog/sh-dialog-title.svelte';
	import ShDialogDescription from '$lib/components/sh-dialog/sh-dialog-description.svelte';
	import ShDialogFooter from '$lib/components/sh-dialog/sh-dialog-footer.svelte';
	import ShPagination from '$lib/components/sh-pagination/sh-pagination.svelte';
	import ShPaginationContent from '$lib/components/sh-pagination/sh-pagination-content.svelte';
	import ShPaginationItem from '$lib/components/sh-pagination/sh-pagination-item.svelte';
	import ShPaginationPrevious from '$lib/components/sh-pagination/sh-pagination-previous.svelte';
	import ShPaginationNext from '$lib/components/sh-pagination/sh-pagination-next.svelte';
	import UploadIcon from '@lucide/svelte/icons/upload';
	import TrashIcon from '@lucide/svelte/icons/trash-2';
	import EyeIcon from '@lucide/svelte/icons/eye';
	import FileTextIcon from '@lucide/svelte/icons/file-text';

	const QUEUE_ICONS: Record<string, string> = {
		pending: '⏳',
		processing: '⚙️',
		done: '✅',
		error: '❌'
	};

	let uploadFiles = $state<FileList | null>(null);
	let textTitle = $state('');
	let textContent = $state('');
	let searchInput = $state('');
	let searchDebounce: ReturnType<typeof setTimeout>;

	let viewDoc = $state<{ source: string; content: string } | null>(null);
	let viewLoading = $state(false);
	let viewOpen = $state(false);

	let deleteDoc = $state<DocumentMeta | null>(null);
	let deleteOpen = $state(false);
	let deleteLoading = $state(false);

	let queueInterval: ReturnType<typeof setInterval>;

	onMount(async () => {
		await documentsStore.fetchPage();
		await documentsStore.fetchQueue();
		queueInterval = setInterval(documentsStore.fetchQueue, 3000);
		return () => clearInterval(queueInterval);
	});

	async function handleUpload() {
		if (!uploadFiles?.length) return;
		try {
			await documentsStore.uploadFiles(Array.from(uploadFiles));
			toast.success('Arquivos enviados para indexação');
			uploadFiles = null;
			await documentsStore.fetchQueue();
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Erro no upload');
		}
	}

	async function handleIndexText() {
		if (!textTitle.trim() || !textContent.trim()) {
			toast.error('Preencha o título e o conteúdo');
			return;
		}
		try {
			const result = await documentsStore.indexText(textTitle, textContent);
			toast.success(`Job ${result.job_id} criado`);
			textTitle = '';
			textContent = '';
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Erro ao indexar');
		}
	}

	function onSearchInput() {
		clearTimeout(searchDebounce);
		searchDebounce = setTimeout(() => documentsStore.setSearch(searchInput), 300);
	}

	async function openViewer(source: string) {
		viewOpen = true;
		viewLoading = true;
		viewDoc = null;
		try {
			const content = await documentsStore.getContent(source);
			viewDoc = { source, content };
		} catch {
			toast.error('Erro ao carregar conteúdo');
			viewOpen = false;
		} finally {
			viewLoading = false;
		}
	}

	async function confirmDelete() {
		if (!deleteDoc) return;
		deleteLoading = true;
		try {
			const n = await documentsStore.deleteDocument(deleteDoc.source);
			toast.success(`${n} chunks removidos`);
			deleteOpen = false;
			deleteDoc = null;
		} catch {
			toast.error('Erro ao deletar documento');
		} finally {
			deleteLoading = false;
		}
	}

	function formatSize(bytes: number) {
		return bytes < 1024 ? `${bytes} B` : `${(bytes / 1024).toFixed(1)} KB`;
	}

	function formatDate(iso: string) {
		return iso.slice(0, 19).replace('T', ' ');
	}
</script>

<div class="flex h-full flex-col overflow-y-auto">
	<header
		class="border-border bg-background flex h-14 shrink-0 items-center border-b px-4"
		style="box-shadow: var(--shadow-header);"
	>
		<span class="font-semibold">Admin</span>
	</header>

	<div class="flex flex-col gap-6 p-4">
		<!-- Upload -->
		<section class="border-border bg-card rounded-xl border p-4" style="box-shadow: var(--shadow-soft-card);">
			<h2 class="text-card-foreground mb-3 font-semibold">📤 Upload de documentos</h2>
			<p class="text-muted-foreground mb-3 text-xs">PDF, Word, TXT, Markdown — máximo 20 arquivos</p>
			<input
				type="file"
				accept=".pdf,.docx,.doc,.txt,.md"
				multiple
				class="text-foreground mb-3 w-full text-sm"
				onchange={(e) => (uploadFiles = (e.target as HTMLInputElement).files)}
			/>
			{#if uploadFiles?.length}
				<ShButton onclick={handleUpload} size="sm" class="gap-2">
					<UploadIcon class="size-4" />
					Enviar {uploadFiles.length} arquivo(s)
				</ShButton>
			{/if}

			{#if $documentsStore.jobs.length > 0}
				<div class="mt-4">
					<p class="text-muted-foreground mb-2 text-xs font-medium">Fila de indexação</p>
					{#each $documentsStore.jobs as job}
						<p class="text-muted-foreground text-xs">
							{QUEUE_ICONS[job.status] ?? '•'}
							<code>{job.job_id.slice(0, 8)}</code> — {job.filename} ({job.status})
							{#if job.error}<span class="text-destructive"> ↳ {job.error}</span>{/if}
						</p>
					{/each}
				</div>
			{/if}
		</section>

		<!-- Index text -->
		<section class="border-border bg-card rounded-xl border p-4" style="box-shadow: var(--shadow-soft-card);">
			<h2 class="text-card-foreground mb-3 font-semibold">📝 Indexar texto puro</h2>
			<div class="flex flex-col gap-2">
				<ShInput bind:value={textTitle} placeholder="Título / nome do documento" />
				<ShTextarea bind:value={textContent} placeholder="Cole aqui o texto…" rows={4} />
				<ShButton onclick={handleIndexText} size="sm" class="self-start gap-2">
					<FileTextIcon class="size-4" />
					Indexar texto
				</ShButton>
			</div>
		</section>

		<!-- Documents list -->
		<section class="border-border bg-card rounded-xl border p-4" style="box-shadow: var(--shadow-soft-card);">
			<h2 class="text-card-foreground mb-3 font-semibold">📚 Documentos indexados</h2>

			<ShInput
				class="mb-3"
				placeholder="🔍 Buscar por nome…"
				bind:value={searchInput}
				oninput={onSearchInput}
			/>

			{#if $documentsStore.loading}
				<div class="flex flex-col gap-2">
					{#each { length: 3 } as _}
						<ShSkeleton class="h-10 w-full" />
					{/each}
				</div>
			{:else if $documentsStore.error}
				<p class="text-destructive text-sm">{$documentsStore.error}</p>
			{:else if $documentsStore.items.length === 0}
				<p class="text-muted-foreground text-sm">Nenhum documento encontrado.</p>
			{:else}
				<p class="text-muted-foreground mb-2 text-xs">
					{$documentsStore.total} documento(s) — página {$documentsStore.page}/{$documentsStore.totalPages}
				</p>

				<div class="flex flex-col divide-y">
					{#each $documentsStore.items as doc}
						<div class="flex items-center gap-2 py-2.5">
							<div class="min-w-0 flex-1">
								<p class="text-foreground truncate text-sm font-medium">{doc.source}</p>
								<p class="text-muted-foreground text-xs">
									{doc.file_type} · {formatSize(doc.file_size_bytes)} · {doc.word_count} palavras · {formatDate(doc.uploaded_at)}
								</p>
							</div>
							<ShButton
								variant="ghost"
								size="icon-sm"
								onclick={() => openViewer(doc.source)}
								title="Ver conteúdo"
							>
								<EyeIcon class="size-4" />
							</ShButton>
							<ShButton
								variant="ghost"
								size="icon-sm"
								class="text-destructive hover:text-destructive"
								onclick={() => { deleteDoc = doc; deleteOpen = true; }}
								title="Deletar"
							>
								<TrashIcon class="size-4" />
							</ShButton>
						</div>
					{/each}
				</div>

				{#if $documentsStore.totalPages > 1}
					<div class="mt-4">
						<ShPagination>
							<ShPaginationContent>
								<ShPaginationItem>
									<ShPaginationPrevious
										onclick={() => documentsStore.setPage($documentsStore.page - 1)}
										class={$documentsStore.page <= 1 ? 'pointer-events-none opacity-50' : ''}
									/>
								</ShPaginationItem>
								<ShPaginationItem>
									<ShPaginationNext
										onclick={() => documentsStore.setPage($documentsStore.page + 1)}
										class={$documentsStore.page >= $documentsStore.totalPages ? 'pointer-events-none opacity-50' : ''}
									/>
								</ShPaginationItem>
							</ShPaginationContent>
						</ShPagination>
					</div>
				{/if}
			{/if}
		</section>
	</div>
</div>

<!-- Content viewer dialog -->
<ShDialog bind:open={viewOpen}>
	<ShDialogContent class="max-w-2xl">
		<ShDialogHeader>
			<ShDialogTitle>Conteúdo do documento</ShDialogTitle>
			{#if viewDoc}
				<ShDialogDescription>{viewDoc.source}</ShDialogDescription>
			{/if}
		</ShDialogHeader>
		{#if viewLoading}
			<div class="flex justify-center py-8">
				<ShSpinner class="size-6" />
			</div>
		{:else if viewDoc}
			<textarea
				readonly
				class="border-input bg-muted text-foreground h-96 w-full rounded-md border p-3 font-mono text-xs"
				value={viewDoc.content}
			></textarea>
		{/if}
	</ShDialogContent>
</ShDialog>

<!-- Delete confirm dialog -->
<ShDialog bind:open={deleteOpen}>
	<ShDialogContent>
		<ShDialogHeader>
			<ShDialogTitle>Confirmar exclusão</ShDialogTitle>
			<ShDialogDescription>
				Deletar <strong>{deleteDoc?.source}</strong> e todos os seus chunks? Esta ação não pode ser
				desfeita.
			</ShDialogDescription>
		</ShDialogHeader>
		<ShDialogFooter>
			<ShButton variant="outline" onclick={() => (deleteOpen = false)}>Cancelar</ShButton>
			<ShButton variant="destructive" disabled={deleteLoading} onclick={confirmDelete}>
				{#if deleteLoading}<ShSpinner class="mr-2 size-4" />{/if}
				Deletar
			</ShButton>
		</ShDialogFooter>
	</ShDialogContent>
</ShDialog>
