<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { marked } from 'marked';
	import { toast } from 'svelte-sonner';
	import { chatStore } from '$lib/hooks/store/use-chat.hook';
	import { settingsStore } from '$lib/hooks/store/use-settings.hook';
	import { PROVIDER_LABELS, PROVIDER_MODELS, type Provider } from '$lib/hooks/store/use-settings.hook';
	import ShButton from '$lib/components/sh-button/sh-button.svelte';
	import ShInput from '$lib/components/sh-input/sh-input.svelte';
	import ShSkeleton from '$lib/components/sh-skeleton/sh-skeleton.svelte';
	import ShSpinner from '$lib/components/sh-spinner/sh-spinner.svelte';
	import ShThemeToggle from '$lib/components/sh-theme-toggle/sh-theme-toggle.svelte';
	import SendIcon from '@lucide/svelte/icons/send';
	import BotIcon from '@lucide/svelte/icons/bot';
	import UserIcon from '@lucide/svelte/icons/user';
	import ChevronDownIcon from '@lucide/svelte/icons/chevron-down';

	let question = $state('');
	let messagesEl = $state<HTMLElement | null>(null);
	let modelMenuOpen = $state(false);

	onMount(async () => {
		await settingsStore.load();
	});

	async function scrollBottom() {
		await tick();
		if (messagesEl) messagesEl.scrollTop = messagesEl.scrollHeight;
	}

	async function submit() {
		const q = question.trim();
		if (!q || chatStore.loading) return;
		question = '';
		await chatStore.send(q);
		await scrollBottom();
		if (chatStore.error) toast.error(chatStore.error);
	}

	function onKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			submit();
		}
	}

	function selectModel(provider: Provider, model: string) {
		settingsStore.apply(provider, model);
		modelMenuOpen = false;
	}

	const renderedMessages = $derived(
		$chatStore.messages.map((m) => ({
			...m,
			html: m.role === 'assistant' ? marked.parse(m.content) : m.content
		}))
	);
</script>

<div class="flex h-full flex-col">
	<!-- Header -->
	<header
		class="border-border bg-background flex h-14 shrink-0 items-center justify-between border-b px-4"
		style="box-shadow: var(--shadow-header);"
	>
		<span class="text-foreground font-semibold">Chat</span>

		<div class="flex items-center gap-2">
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
						class="border-border bg-popover text-popover-foreground absolute right-0 top-full z-50 mt-1 w-60 rounded-lg border p-1 shadow-md"
					>
						{#each Object.entries(PROVIDER_MODELS) as [provider, models]}
							<p class="text-muted-foreground px-2 py-1 text-xs font-medium">
								{PROVIDER_LABELS[provider as Provider]}
							</p>
							{#each models as model}
								<button
									class="hover:bg-accent hover:text-accent-foreground w-full rounded px-2 py-1.5 text-left text-sm transition-colors
										{$settingsStore.model === model ? 'text-primary font-medium' : ''}"
									onclick={() => selectModel(provider as Provider, model)}
								>
									{model}
								</button>
							{/each}
						{/each}
					</div>
				{/if}
			</div>

			<ShThemeToggle />
		</div>
	</header>

	{#if !$settingsStore.configured && !$settingsStore.loading}
		<div class="border-b border-amber-200 bg-amber-50 px-4 py-2 text-sm text-amber-800 dark:border-amber-800/50 dark:bg-amber-950/40 dark:text-amber-300">
			⚠️ Modelo não configurado — API key não encontrada no <code>.env</code>
		</div>
	{/if}

	<!-- Messages -->
	<div bind:this={messagesEl} class="flex-1 overflow-y-auto py-6">
		<div class="mx-auto w-full max-w-[50%] min-w-80 px-4">
			{#if renderedMessages.length === 0}
				<div class="text-muted-foreground flex flex-col items-center justify-center gap-2 pt-20">
					<BotIcon class="size-10 opacity-30" />
					<p class="text-sm">Faça uma pergunta sobre a documentação.</p>
				</div>
			{/if}

			{#each renderedMessages as msg}
				<div class="mb-4 flex gap-3 {msg.role === 'user' ? 'flex-row-reverse' : ''}">
					<div class="bg-muted flex size-8 shrink-0 items-center justify-center rounded-full">
						{#if msg.role === 'user'}
							<UserIcon class="size-4" />
						{:else}
							<BotIcon class="size-4" />
						{/if}
					</div>
					<div
						class="max-w-[80%] rounded-xl px-4 py-2.5 text-sm
							{msg.role === 'user'
							? 'bg-primary text-primary-foreground'
							: 'bg-card text-card-foreground border border-border'}"
					>
						{#if msg.role === 'assistant' && msg.content === ''}
							<ShSkeleton class="h-4 w-32" />
						{:else if msg.role === 'assistant'}
							<!-- eslint-disable-next-line svelte/no-at-html-tags -->
							<div class="prose prose-sm max-w-none dark:prose-invert">{@html msg.html}</div>
						{:else}
							{msg.content}
						{/if}
					</div>
				</div>
			{/each}
		</div>
	</div>

	<!-- Input area -->
	<div class="border-border bg-background border-t py-3">
		<div class="mx-auto flex w-full max-w-[50%] min-w-80 gap-2 px-4">
			<ShInput
				class="flex-1"
				placeholder="Faça uma pergunta sobre a documentação…"
				bind:value={question}
				onkeydown={onKeydown}
				disabled={$chatStore.loading}
			/>
			<ShButton onclick={submit} disabled={$chatStore.loading || !question.trim()}>
				{#if $chatStore.loading}
					<ShSpinner class="size-4" />
				{:else}
					<SendIcon class="size-4" />
				{/if}
			</ShButton>
		</div>
	</div>
</div>
