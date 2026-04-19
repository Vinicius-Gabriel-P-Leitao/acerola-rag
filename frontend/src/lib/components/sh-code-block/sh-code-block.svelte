<script lang="ts">
	import hljs from 'highlight.js';
	import 'highlight.js/styles/github-dark.css';
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import ShButton from '$lib/components/sh-button/sh-button.svelte';
	import CopyIcon from '@lucide/svelte/icons/copy';
	import CheckIcon from '@lucide/svelte/icons/check';

	let { lang = 'text', content = '' } = $props();

	let codeEl: HTMLElement;
	let copied = $state(false);

	onMount(() => {
		if (codeEl) {
			hljs.highlightElement(codeEl);
		}
	});

	function copyToClipboard() {
		navigator.clipboard
			.writeText(content)
			.then(() => {
				copied = true;
				setTimeout(() => (copied = false), 2000);
			})
			.catch(() => {
				toast.error('Falha ao copiar o código');
			});
	}

	function getLanguageLabel(lang: string) {
		if (!lang || lang === 'text') return '';
		const detected = hljs.getLanguage(lang);
		return detected ? detected.name : lang;
	}
</script>

<div class="code-block group relative rounded-lg bg-muted/30">
	<div
		class="flex items-center justify-between rounded-t-lg border-b border-border bg-muted/50 px-4 py-1.5 text-xs"
	>
		<span class="font-semibold text-muted-foreground">{getLanguageLabel(lang)}</span>

		<ShButton
			variant="ghost"
			size="sm"
			class="h-auto gap-1.5 px-2 py-1 opacity-0 transition-opacity group-hover:opacity-100"
			onclick={copyToClipboard}
		>
			{#if copied}
				<CheckIcon class="size-3.5" />
				<span class="text-xs">Copiado!</span>
			{:else}
				<CopyIcon class="size-3.5" />
				<span class="text-xs">Copiar</span>
			{/if}
		</ShButton>
	</div>

	<pre class="overflow-x-auto p-4 text-sm"><code bind:this={codeEl} class="language-{lang}">{content}</code></pre>
</div>
