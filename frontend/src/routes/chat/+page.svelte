<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { marked, type Token } from 'marked';
	import { toast } from 'svelte-sonner';
	import { chatStore } from '$lib/hooks/store/use-chat.hook';
	import { settingsStore } from '$lib/hooks/store/use-settings.hook';
	import {
		PROVIDER_LABELS,
		PROVIDER_MODELS,
		type Provider
	} from '$lib/hooks/store/use-settings.hook';
	import { useHeader } from '$lib/hooks/ui/use-header.svelte';
	import ShButton from '$lib/components/sh-button/sh-button.svelte';
	import ShTextarea from '$lib/components/sh-textarea/sh-textarea.svelte';
	import ShSkeleton from '$lib/components/sh-skeleton/sh-skeleton.svelte';
	import ShSpinner from '$lib/components/sh-spinner/sh-spinner.svelte';
	import ShCodeBlock from '$lib/components/sh-code-block/sh-code-block.svelte';
	import ShExpandable from '$lib/components/sh-expandable/sh-expandable.svelte';
	import SendIcon from '@lucide/svelte/icons/send';
	import BotIcon from '@lucide/svelte/icons/bot';
	import UserIcon from '@lucide/svelte/icons/user';
	import ChevronDownIcon from '@lucide/svelte/icons/chevron-down';
	import PaperclipIcon from '@lucide/svelte/icons/paperclip';
	import XIcon from '@lucide/svelte/icons/x';
	import FileTextIcon from '@lucide/svelte/icons/file-text';
	import BookOpenIcon from '@lucide/svelte/icons/book-open';
	import { AI_CONTRACT } from '$lib/contracts/ai.contract';

	type MessageBlock = {
		type: 'code' | 'html';
		content: string;
		lang?: string;
	};

	let question = $state('');
	let messagesEl = $state<HTMLElement | null>(null);
	let textareaEl = $state<HTMLTextAreaElement | null>(null);
	let fileInputEl = $state<HTMLInputElement | null>(null);
	let modelMenuOpen = $state(false);
	let sourcesOpen = $state(false);

	const headerStore = useHeader();
	headerStore.action = headerAction;
	headerStore.title = 'Chat';

	onMount(() => {
		settingsStore.load();
		return () => (headerStore.action = null);
	});

	function autoResizeTextarea() {
		if (!textareaEl) return;
		textareaEl.style.height = 'auto';
		textareaEl.style.height = `${textareaEl.scrollHeight}px`;
	}

	async function scrollBottom() {
		await tick();
		if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
	}

	async function submit() {
		const query = question.trim();
		if (!query || $chatStore.loading) return;
		question = '';

		await tick();
		if (textareaEl) textareaEl.style.height = 'auto';

		await chatStore.send(query);
		await scrollBottom();

		if ($chatStore.error) toast.error($chatStore.error);
	}

	function onKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey && !event.ctrlKey) {
			event.preventDefault();
			submit();
		}
	}

	function selectModel(provider: Provider, model: string) {
		settingsStore.apply(provider, model);
		modelMenuOpen = false;
	}

	function onFileChange(e: Event) {
		const files = (e.target as HTMLInputElement).files;
		if (!files) return;
		for (const file of Array.from(files)) {
			chatStore.attachFile(file);
		}
		if (fileInputEl) fileInputEl.value = '';
	}

	function extractAIResponse(content: string): string {
		const openTag = AI_CONTRACT.TAGS.CONTENT_RESPONSE_OPEN;
		const closeTag = AI_CONTRACT.TAGS.CONTENT_RESPONSE_CLOSE;
		const startIndex = content.indexOf(openTag);
		const endIndex = content.indexOf(closeTag);
		if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
			return content.substring(startIndex + openTag.length, endIndex).trim();
		}
		return content.trim();
	}

	function processMarkdown(markdown: string): MessageBlock[] {
		const tokens = marked.lexer(markdown);
		const blocks: MessageBlock[] = [];
		let accumulatedHtmlTokens: Token[] = [];

		function flushHtmlTokens() {
			if (accumulatedHtmlTokens.length > 0) {
				// @ts-expect-error - `tokens.links` is required by marked.parser
				accumulatedHtmlTokens.links = {};
				const htmlContent = marked.parser(accumulatedHtmlTokens);
				blocks.push({ type: 'html', content: htmlContent });
				accumulatedHtmlTokens = [];
			}
		}

		for (const token of tokens) {
			if (token.type === 'code') {
				flushHtmlTokens();
				blocks.push({ type: 'code', content: token.text, lang: token.lang });
			} else {
				accumulatedHtmlTokens.push(token);
			}
		}
		flushHtmlTokens();
		return blocks;
	}

	const renderedMessages = $derived(
		$chatStore.messages.map((message) => {
			if (message.role === 'assistant') {
				const extractedContent = extractAIResponse(message.content);
				return { ...message, blocks: processMarkdown(extractedContent) };
			}
			return { ...message, blocks: [] as MessageBlock[] };
		})
	);

	const hasMessages = $derived(renderedMessages.length > 0);

	function formatSize(bytes: number) {
		return bytes < 1024 ? `${bytes} B` : `${(bytes / 1024).toFixed(1)} KB`;
	}

	function greeting() {
		const h = new Date().getHours();
		if (h < 12) return 'Bom dia';
		if (h < 18) return 'Boa tarde';
		return 'Boa noite';
	}
</script>

{#snippet headerAction()}
	<div class="flex items-center gap-2">
		<!-- Fontes da conversa -->
		{#if $chatStore.sources.length > 0}
			<ShButton
				variant="outline"
				size="sm"
				class="gap-1.5 text-xs"
				onclick={() => (sourcesOpen = !sourcesOpen)}
			>
				<BookOpenIcon class="size-3.5" />
				{$chatStore.sources.length} fontes
			</ShButton>
		{/if}

		<!-- Model selector -->
		<div class="relative">
			<ShButton
				variant="outline"
				size="sm"
				class="gap-1.5 text-xs"
				onclick={() => (modelMenuOpen = !modelMenuOpen)}
			>
				<BotIcon class="size-3.5" />
				<span class="max-w-28 truncate">{$settingsStore.model}</span>
				<ChevronDownIcon class="size-3" />
			</ShButton>

			{#if modelMenuOpen}
				<div
					class="absolute top-full right-0 z-50 mt-1 w-60 rounded-lg border border-border bg-popover p-1 text-popover-foreground shadow-md"
				>
					{#each Object.entries(PROVIDER_MODELS) as [provider, models] (provider)}
						<p class="px-2 py-1 text-xs font-medium text-muted-foreground">
							{PROVIDER_LABELS[provider as Provider]}
						</p>
						{#each models as model (model)}
							<button
								class="w-full rounded px-2 py-1.5 text-left text-sm transition-colors hover:bg-accent hover:text-accent-foreground
									{$settingsStore.model === model ? 'font-medium text-primary' : ''}"
								onclick={() => selectModel(provider as Provider, model)}
							>
								{model}
							</button>
						{/each}
					{/each}
				</div>
			{/if}
		</div>
	</div>
{/snippet}

<div class="flex flex-1 overflow-hidden">
	<!-- Chat area -->
	<div class="flex min-w-0 flex-1 flex-col overflow-hidden">
		{#if !$settingsStore.configured && !$settingsStore.loading}
			<div
				class="border-b border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-800 dark:border-amber-800/50 dark:bg-amber-950/40 dark:text-amber-300"
			>
				⚠️ Modelo não configurado — API key não encontrada no <code>.env</code>
			</div>
		{/if}

		{#if !hasMessages}
			<!-- Home: input centralizado -->
			<div class="flex flex-1 flex-col items-center justify-center gap-6 px-4">
				<div class="text-center">
					<h1 class="text-2xl font-semibold text-foreground">{greeting()}, Vinicius</h1>
					<p class="mt-1 text-sm text-muted-foreground">Pergunte qualquer coisa sobre sua documentação.</p>
				</div>

				<div class="w-full max-w-xl">
					{@render inputArea()}
				</div>
			</div>
		{:else}
			<!-- Messages -->
			<div bind:this={messagesEl} class="flex-1 overflow-x-hidden overflow-y-auto py-6">
				<div class="mx-auto box-border w-full min-w-0 max-w-full px-4 md:max-w-[50%] md:min-w-80">
					{#each renderedMessages as msg, i (i)}
						<div class="mb-4 flex gap-3 {msg.role === 'user' ? 'flex-row-reverse' : ''}">
							<div class="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted">
								{#if msg.role === 'user'}
									<UserIcon class="size-4" />
								{:else}
									<BotIcon class="size-4" />
								{/if}
							</div>

							<div class="flex max-w-[80%] flex-col gap-1.5">
								<!-- Attached file cards (user messages) -->
								{#if msg.attached_files && msg.attached_files.length > 0}
									<div class="flex flex-wrap gap-1.5 {msg.role === 'user' ? 'justify-end' : ''}">
										{#each msg.attached_files as af (af.name)}
											<div
												class="flex items-center gap-1.5 rounded-lg border border-border bg-muted px-2.5 py-1.5 text-xs"
											>
												<FileTextIcon class="size-3.5 shrink-0 text-muted-foreground" />
												<span class="max-w-[120px] truncate font-medium">{af.name}</span>
												<span class="text-muted-foreground uppercase">{af.type}</span>
											</div>
										{/each}
									</div>
								{/if}

								<!-- Message bubble -->
								<div
									class="rounded-xl px-4 py-2.5 text-sm
										{msg.role === 'user'
										? 'bg-primary text-primary-foreground'
										: 'border border-border bg-card text-card-foreground'}"
								>
									{#if msg.role === 'assistant' && msg.content === ''}
										<ShSkeleton class="h-4 w-32" />
									{:else if msg.role === 'assistant'}
										<ShExpandable threshold={300}>
											<div class="prose prose-sm max-w-none dark:prose-invert">
												{#each msg.blocks as block (block.content)}
													{#if block.type === 'code'}
														<ShCodeBlock lang={block.lang} content={block.content} />
													{:else}
														{@html block.content}
													{/if}
												{/each}
											</div>
										</ShExpandable>
									{:else}
										{msg.content}
									{/if}
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>

			<!-- Input bottom -->
			<div class="shrink-0 border-t border-border bg-background py-3">
				<div class="mx-auto w-full min-w-0 max-w-full px-4 md:max-w-[50%] md:min-w-80">
					{@render inputArea()}
				</div>
			</div>
		{/if}
	</div>

	<!-- Fontes da conversa — painel lateral -->
	{#if sourcesOpen && $chatStore.sources.length > 0}
		<aside
			class="hidden w-72 shrink-0 flex-col border-l border-border bg-card md:flex"
		>
			<div class="flex items-center justify-between border-b border-border px-4 py-3">
				<p class="text-sm font-semibold">Fontes da conversa</p>
				<button
					class="text-muted-foreground hover:text-foreground"
					onclick={() => (sourcesOpen = false)}
				>
					<XIcon class="size-4" />
				</button>
			</div>
			<div class="flex-1 overflow-y-auto p-3">
				{#each $chatStore.sources as src, i (i)}
					<div class="mb-3 rounded-lg border border-border bg-background p-3 text-xs">
						<div class="mb-1 flex items-center justify-between gap-2">
							<span class="flex items-center gap-1 font-medium text-foreground">
								<FileTextIcon class="size-3 shrink-0 text-muted-foreground" />
								<span class="truncate">{src.source_file}</span>
							</span>
							<span class="shrink-0 text-muted-foreground">{(src.score * 100).toFixed(0)}%</span>
						</div>
						<p class="line-clamp-4 text-muted-foreground">{src.chunk_text}</p>
					</div>
				{/each}
			</div>
		</aside>
	{/if}
</div>

{#snippet inputArea()}
	<!-- Pending file chips -->
	{#if $chatStore.pendingFiles.length > 0}
		<div class="mb-2 flex flex-wrap gap-1.5">
			{#each $chatStore.pendingFiles as pf (pf.name)}
				<div
					class="flex items-center gap-1.5 rounded-full border border-border bg-muted px-2.5 py-1 text-xs"
				>
					<FileTextIcon class="size-3 shrink-0 text-muted-foreground" />
					<span class="max-w-[120px] truncate">{pf.name}</span>
					<span class="text-muted-foreground">{formatSize(pf.size_bytes)}</span>
					<button
						class="ml-0.5 text-muted-foreground hover:text-foreground"
						onclick={() => chatStore.removeFile(pf.name)}
					>
						<XIcon class="size-3" />
					</button>
				</div>
			{/each}
		</div>
	{/if}

	<div class="flex items-end gap-2">
		<!-- Hidden file input -->
		<input
			bind:this={fileInputEl}
			type="file"
			accept=".pdf,.docx,.doc,.txt,.md"
			multiple
			class="hidden"
			onchange={onFileChange}
		/>

		<!-- Attach button -->
		<ShButton
			variant="outline"
			size="icon"
			class="shrink-0 self-end"
			onclick={() => fileInputEl?.click()}
			disabled={$chatStore.pendingFiles.length >= 5}
			title="Anexar arquivo (máx. 5)"
		>
			<PaperclipIcon class="size-4" />
		</ShButton>

		<ShTextarea
			bind:element={textareaEl}
			class="max-h-[35vh] min-h-10 flex-1 resize-none"
			placeholder="Pergunte qualquer coisa…"
			bind:value={question}
			oninput={autoResizeTextarea}
			onkeydown={onKeydown}
			disabled={$chatStore.loading}
		/>

		<ShButton
			class="shrink-0 self-end"
			onclick={submit}
			disabled={$chatStore.loading || !question.trim()}
		>
			{#if $chatStore.loading}
				<ShSpinner class="size-4" />
			{:else}
				<SendIcon class="size-4" />
			{/if}
		</ShButton>
	</div>
{/snippet}
