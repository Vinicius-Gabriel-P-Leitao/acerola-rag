<script lang="ts">
	import { onMount } from 'svelte';
	import { fly, fade } from 'svelte/transition';
	import { toast } from 'svelte-sonner';
	import { documentsStore, type DocumentMeta } from '$lib/hooks/store/use-documents.hook';
	import { useHeader } from '$lib/hooks/ui/use-header.svelte';
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
	import ShPaginationLink from '$lib/components/sh-pagination/sh-pagination-link.svelte';
	import UploadIcon from '@lucide/svelte/icons/upload';
	import TrashIcon from '@lucide/svelte/icons/trash-2';
	import EyeIcon from '@lucide/svelte/icons/eye';
	import FileTextIcon from '@lucide/svelte/icons/file-text';
	import XIcon from '@lucide/svelte/icons/x';
	import ListIcon from '@lucide/svelte/icons/list';

	const QUEUE_ICONS: Record<string, string> = {
		pending: '⏳',
		processing: '⚙️',
		done: '✅',
		error: '❌'
	};

	let uploadFiles = $state<File[]>([]);
	let uploadLoading = $state(false); // Nova variável de estado
	let fileInputEl = $state<HTMLInputElement | null>(null);
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

	let selectedFilesOpen = $state(false);
	let queueOpen = $state(false);

	let queueInterval: ReturnType<typeof setInterval>;

	const headerStore = useHeader();
	headerStore.title = 'Admin';

	onMount(() => {
		documentsStore.fetchPage();
		documentsStore.fetchQueue();
		queueInterval = setInterval(documentsStore.fetchQueue, 3000);
		return () => clearInterval(queueInterval);
	});

	async function handleUpload() {
		if (uploadFiles.length === 0) return;
		uploadLoading = true; // Inicia carregamento
		try {
			await documentsStore.uploadFiles(uploadFiles);

			toast.success('Arquivos enviados para indexação');
			uploadFiles = [];

			if (fileInputEl) fileInputEl.value = '';

			await documentsStore.fetchQueue();
			selectedFilesOpen = false;
		} catch (error) {
			toast.error(error instanceof Error ? error.message : 'Erro no upload');
		} finally {
			uploadLoading = false; // Finaliza carregamento
		}
	}

	function removeSelectedFile(fileToRemove: File) {
		uploadFiles = uploadFiles.filter((file) => file !== fileToRemove);
		if (uploadFiles.length === 0) {
			if (fileInputEl) fileInputEl.value = '';

			selectedFilesOpen = false;
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
		} catch (error) {
			toast.error(error instanceof Error ? error.message : 'Erro ao indexar');
		}
	}

	function onSearchInput() {
		clearTimeout(searchDebounce);
		searchDebounce = setTimeout(() => documentsStore.setSearch(searchInput), 300);
	}

	async function openViewer(source: string) {
		viewLoading = true;
		viewOpen = true;
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
			const chunk = await documentsStore.deleteDocument(deleteDoc.source);
			toast.success(`${chunk} chunks removidos`);

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

<svelte:window
	onkeydown={(event) => {
		if (event.key === 'Escape' && viewOpen) viewOpen = false;
	}}
/>

<div class="flex flex-1 flex-col overflow-y-auto">
	<div class="mx-auto flex w-full max-w-full md:max-w-[60%] min-w-0 md:min-w-80 flex-col gap-6 p-4">
		<!-- Upload -->
		<section
			class="rounded-xl border border-border bg-card p-4"
			style="box-shadow: var(--shadow-soft-card);"
		>
			<h2 class="mb-1 font-semibold text-card-foreground">📤 Upload de documentos</h2>
			<p class="mb-4 text-xs text-muted-foreground">
				PDF, Docx, TXT, Markdown — máximo 20 arquivos
			</p>

			<input
				bind:this={fileInputEl}
				type="file"
				accept=".pdf,.docx,.doc,.txt,.md"
				multiple
				class="hidden"
				onchange={(e) => {
					const files = (e.target as HTMLInputElement).files;
					uploadFiles = files ? Array.from(files) : [];
				}}
			/>

			<!-- Drop zone -->
			<button
				type="button"
				onclick={() => fileInputEl?.click()}
				class="flex w-full cursor-pointer flex-col items-center gap-2 rounded-lg border-2 border-dashed border-border px-4 py-6 transition-colors hover:border-primary hover:bg-primary/5"
			>
				<UploadIcon class="size-8 text-muted-foreground" />
				<span class="text-sm font-medium">Clique para selecionar arquivos</span>
				<span class="text-xs text-muted-foreground">ou arraste aqui</span>
			</button>

			{#if uploadFiles.length > 0}
				<div class="mt-3 flex items-center justify-between">
					<ShButton
						variant="outline"
						size="sm"
						class="gap-2"
						onclick={() => (selectedFilesOpen = true)}
					>
						<ListIcon class="size-4" />
						Ver arquivos selecionados ({uploadFiles.length})
					</ShButton>
					<ShButton onclick={handleUpload} size="sm" class="gap-2" disabled={uploadLoading}>
						{#if uploadLoading}
							<ShSpinner class="size-4" />
						{:else}
							<UploadIcon class="size-4" />
						{/if}
						Enviar
					</ShButton>
				</div>
			{/if}

			{#if $documentsStore.jobs.length > 0}
				<div class="mt-4 flex items-center justify-between">
					<p class="text-sm font-medium text-muted-foreground">
						{$documentsStore.jobs.length} arquivo(s) na fila de processamento
					</p>
					<ShButton variant="outline" size="sm" class="gap-2" onclick={() => (queueOpen = true)}>
						<ListIcon class="size-4" />
						Ver fila de processos
					</ShButton>
				</div>
			{/if}
		</section>

		<!-- Index text -->
		<section
			class="rounded-xl border border-border bg-card p-4"
			style="box-shadow: var(--shadow-soft-card);"
		>
			<h2 class="mb-3 font-semibold text-card-foreground">📝 Indexar texto puro</h2>
			<div class="flex flex-col gap-2">
				<ShInput bind:value={textTitle} placeholder="Título / nome do documento" />
				<ShTextarea bind:value={textContent} placeholder="Cole aqui o texto…" rows={4} />
				<ShButton onclick={handleIndexText} size="sm" class="gap-2 self-start">
					<FileTextIcon class="size-4" />
					Indexar texto
				</ShButton>
			</div>
		</section>

		<!-- Documents list -->
		<section
			class="rounded-xl border border-border bg-card p-4"
			style="box-shadow: var(--shadow-soft-card);"
		>
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
						<ShSkeleton class="h-10 w-full" />
					{/each}
				</div>
			{:else if $documentsStore.error}
				<p class="text-sm text-destructive">{$documentsStore.error}</p>
			{:else if $documentsStore.items.length === 0}
				<p class="text-sm text-muted-foreground">Nenhum documento encontrado.</p>
			{:else}
				<p class="mb-2 text-xs text-muted-foreground">
					{$documentsStore.total} documento(s) — página {$documentsStore.page}/{documentsStore.totalPages}
				</p>

				<div class="flex flex-col divide-y">
					{#each $documentsStore.items as doc (doc.source)}
						<div class="flex items-center gap-2 py-2.5">
							<div class="min-w-0 flex-1">
								<p class="truncate text-sm font-medium text-foreground">{doc.source}</p>
								<p class="text-xs text-muted-foreground">
									{doc.file_type} · {formatSize(doc.file_size_bytes)} · {doc.word_count} palavras · {formatDate(
										doc.uploaded_at
									)}
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
								onclick={() => {
									deleteDoc = doc;
									deleteOpen = true;
								}}
								title="Deletar"
							>
								<TrashIcon class="size-4" />
							</ShButton>
						</div>
					{/each}
				</div>

				{#if documentsStore.totalPages > 1}
					<div class="mt-4">
						<ShPagination
							count={$documentsStore.total}
							perPage={$documentsStore.pageSize}
							page={$documentsStore.page}
						>
							<ShPaginationContent>
								<ShPaginationItem>
									<ShPaginationPrevious
										page={{ type: 'page', value: $documentsStore.page - 1 }}
										isActive={false}
										onclick={() => documentsStore.setPage($documentsStore.page - 1)}
										class={$documentsStore.page <= 1 ? 'pointer-events-none opacity-50' : ''}
									/>
								</ShPaginationItem>
								{#each Array(documentsStore.totalPages) as _, i (i)}
									<ShPaginationItem>
										<ShPaginationLink
											page={{ type: 'page', value: i + 1 }}
											isActive={$documentsStore.page === i + 1}
											onclick={() => documentsStore.setPage(i + 1)}
										>
											{i + 1}
										</ShPaginationLink>
									</ShPaginationItem>
								{/each}
								<ShPaginationItem>
									<ShPaginationNext
										page={{ type: 'page', value: $documentsStore.page + 1 }}
										isActive={false}
										onclick={() => documentsStore.setPage($documentsStore.page + 1)}
										class={$documentsStore.page >= documentsStore.totalPages
											? 'pointer-events-none opacity-50'
											: ''}
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

<!-- Content viewer — bottom sheet on mobile, large dialog on desktop -->
{#if viewOpen}
	<!-- Backdrop -->
	<div
		class="fixed inset-0 z-50 bg-black/50"
		transition:fade={{ duration: 150 }}
		onclick={() => (viewOpen = false)}
		role="presentation"
	></div>

	<!-- Mobile: bottom sheet -->
	<div
		class="fixed inset-x-0 bottom-0 z-50 flex max-h-[88vh] flex-col rounded-t-2xl bg-card md:hidden"
		transition:fly={{ y: 400, duration: 250 }}
	>
		<div class="flex items-center justify-between border-b px-4 py-3">
			<div>
				<p class="font-semibold">Conteúdo do documento</p>
				{#if viewDoc}<p class="truncate text-xs text-muted-foreground">{viewDoc.source}</p>{/if}
			</div>
			<button
				onclick={() => (viewOpen = false)}
				class="text-muted-foreground hover:text-foreground"
			>
				<XIcon class="size-5" />
			</button>
		</div>
		<div class="min-h-0 flex-1 overflow-y-auto p-4">
			{#if viewLoading}
				<div class="flex justify-center py-12"><ShSpinner class="size-6" /></div>
			{:else if viewDoc}
				<textarea
					readonly
					class="h-full min-h-[50vh] w-full resize-none rounded-md border border-input bg-muted p-3 font-mono text-xs text-foreground"
					value={viewDoc.content}
				></textarea>
			{/if}
		</div>
	</div>

	<!-- Desktop: centered large dialog -->
	<div
		class="fixed inset-0 z-50 hidden items-center justify-center p-6 md:flex"
		transition:fade={{ duration: 150 }}
	>
		<div
			class="flex h-[80vh] w-full max-w-4xl flex-col rounded-xl border border-border bg-card shadow-xl"
			transition:fly={{ y: -16, duration: 200 }}
		>
			<div class="flex items-center justify-between border-b border-border px-6 py-4">
				<div>
					<p class="font-semibold">Conteúdo do documento</p>
					{#if viewDoc}<p class="truncate text-sm text-muted-foreground">{viewDoc.source}</p>{/if}
				</div>
				<button
					onclick={() => (viewOpen = false)}
					class="text-muted-foreground hover:text-foreground"
				>
					<XIcon class="size-5" />
				</button>
			</div>
			<div class="min-h-0 flex-1 overflow-y-auto p-6">
				{#if viewLoading}
					<div class="flex justify-center py-12"><ShSpinner class="size-6" /></div>
				{:else if viewDoc}
					<textarea
						readonly
						class="h-full min-h-[60vh] w-full resize-none rounded-md border border-input bg-muted p-4 font-mono text-sm text-foreground"
						value={viewDoc.content}
					></textarea>
				{/if}
			</div>
		</div>
	</div>
{/if}

<!-- Delete confirm dialog -->
<ShDialog bind:open={deleteOpen}>
	<ShDialogContent>
		<ShDialogHeader>
			<ShDialogTitle>Confirmar exclusão</ShDialogTitle>
			<ShDialogDescription>
				Deletar <strong>{deleteDoc?.source}</strong> e todos os seus chunks? Esta ação não pode ser desfeita.
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

<!-- Selected Files Dialog -->
<ShDialog bind:open={selectedFilesOpen}>
	<ShDialogContent>
		<ShDialogHeader>
			<ShDialogTitle>Arquivos Selecionados</ShDialogTitle>
			<ShDialogDescription>Lista de arquivos prontos para envio.</ShDialogDescription>
		</ShDialogHeader>
		<div class="max-h-[60vh] overflow-y-auto pr-4">
			{#if uploadFiles.length > 0}
				<div class="flex flex-col gap-2">
					{#each uploadFiles as file (file.name)}
						<div class="flex items-center justify-between border-b pb-2">
							<div class="flex flex-col">
								<span class="text-sm font-medium">{file.name}</span>
								<span class="text-xs text-muted-foreground">{formatSize(file.size)}</span>
							</div>
							<ShButton
								variant="ghost"
								size="icon-sm"
								class="shrink-0 text-destructive hover:text-destructive"
								onclick={() => removeSelectedFile(file)}
							>
								<TrashIcon class="size-4" />
							</ShButton>
						</div>
					{/each}
				</div>
			{/if}
		</div>
		<ShDialogFooter>
			<ShButton variant="outline" onclick={() => (selectedFilesOpen = false)}>Fechar</ShButton>
		</ShDialogFooter>
	</ShDialogContent>
</ShDialog>

<!-- Queue Dialog -->
<ShDialog bind:open={queueOpen}>
	<ShDialogContent class="sm:max-w-3xl">
		<ShDialogHeader>
			<ShDialogTitle>Fila de Processamento</ShDialogTitle>
			<ShDialogDescription>Acompanhe o status dos arquivos na fila.</ShDialogDescription>
		</ShDialogHeader>
		<div class="max-h-[60vh] overflow-y-auto pr-4">
			<div class="flex flex-col gap-3">
				{#each $documentsStore.jobs as job (job.job_id)}
					<div class="flex flex-col border-b pb-2">
						<div class="flex items-center justify-between">
							<span class="truncate pr-4 text-sm font-medium">{job.filename}</span>
							<span class="flex shrink-0 items-center gap-1 text-xs">
								{QUEUE_ICONS[job.status] ?? '•'}
								{job.status}
							</span>
						</div>
						<div class="mt-1 text-xs text-muted-foreground">
							Job ID: <code>{job.job_id.slice(0, 8)}</code>
						</div>
						{#if job.error}
							<div class="mt-1 text-xs text-destructive">
								Erro: {job.error}
							</div>
						{/if}
					</div>
				{/each}
			</div>
		</div>
		<ShDialogFooter>
			<ShButton variant="outline" onclick={() => (queueOpen = false)}>Fechar</ShButton>
		</ShDialogFooter>
	</ShDialogContent>
</ShDialog>
