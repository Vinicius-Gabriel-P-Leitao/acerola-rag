<script lang="ts">
	import { cn } from '$lib/utils';
	import ChevronDownIcon from '@lucide/svelte/icons/chevron-down';
	import type { Snippet } from 'svelte';

	let {
		children,
		threshold = 280,
		class: className = ''
	}: {
		children: Snippet;
		threshold?: number;
		class?: string;
	} = $props();

	let expanded = $state(false);
	let needsTruncation = $state(false);
	let contentEl = $state<HTMLElement | null>(null);

	$effect(() => {
		if (contentEl) {
			needsTruncation = contentEl.scrollHeight > threshold;
		}
	});
</script>

<div class={cn('relative', className)}>
	<div
		bind:this={contentEl}
		class="overflow-hidden"
		style={!expanded && needsTruncation ? `max-height: ${threshold}px` : ''}
	>
		{@render children()}
	</div>

	{#if needsTruncation && !expanded}
		<div
			class="pointer-events-none absolute bottom-6 left-0 right-0 h-10 bg-gradient-to-t from-card to-transparent"
		></div>
	{/if}

	{#if needsTruncation}
		<button
			class="mt-1.5 flex items-center gap-1 text-xs text-muted-foreground transition-colors hover:text-foreground"
			onclick={() => (expanded = !expanded)}
		>
			{expanded ? 'Ver menos' : 'Ver mais'}
			<ChevronDownIcon class={cn('size-3 transition-transform duration-200', expanded && 'rotate-180')} />
		</button>
	{/if}
</div>
