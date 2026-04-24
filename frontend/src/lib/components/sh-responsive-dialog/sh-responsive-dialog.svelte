<script lang="ts">
	import type { Snippet } from 'svelte';
	import { cn } from '$lib/utils';
	import { mobileStore } from '$lib/hooks/ui/use-mobile.hook';

	import ShDialog from '$lib/components/sh-dialog/sh-dialog.svelte';
	import ShDialogContent from '$lib/components/sh-dialog/sh-dialog-content.svelte';
	import ShDialogHeader from '$lib/components/sh-dialog/sh-dialog-header.svelte';
	import ShDialogTitle from '$lib/components/sh-dialog/sh-dialog-title.svelte';
	import ShDialogDescription from '$lib/components/sh-dialog/sh-dialog-description.svelte';
	import ShDialogFooter from '$lib/components/sh-dialog/sh-dialog-footer.svelte';

	import ShDrawer from '$lib/components/sh-drawer/sh-drawer.svelte';
	import ShDrawerContent from '$lib/components/sh-drawer/sh-drawer-content.svelte';
	import ShDrawerHeader from '$lib/components/sh-drawer/sh-drawer-header.svelte';
	import ShDrawerTitle from '$lib/components/sh-drawer/sh-drawer-title.svelte';
	import ShDrawerDescription from '$lib/components/sh-drawer/sh-drawer-description.svelte';
	import ShDrawerFooter from '$lib/components/sh-drawer/sh-drawer-footer.svelte';

	let {
		open = $bindable(false),
		title,
		description,
		children,
		footer,
		class: className,
		contentClass
	}: {
		open: boolean;
		title?: Snippet;
		description?: Snippet;
		children?: Snippet;
		footer?: Snippet;
		class?: string;
		contentClass?: string;
	} = $props();
</script>

{#if $mobileStore}
	<ShDrawer bind:open>
		<ShDrawerContent class={className}>
			{#if title || description}
				<ShDrawerHeader>
					{#if title}<ShDrawerTitle>{@render title()}</ShDrawerTitle>{/if}
					{#if description}<ShDrawerDescription>{@render description()}</ShDrawerDescription>{/if}
				</ShDrawerHeader>
			{/if}

			{#if children}
				<div class={cn('min-h-0 flex-1 overflow-auto px-4 pb-2', contentClass)}>
					{@render children()}
				</div>
			{/if}

			{#if footer}
				<ShDrawerFooter>{@render footer()}</ShDrawerFooter>
			{/if}
		</ShDrawerContent>
	</ShDrawer>
{:else}
	<ShDialog bind:open>
		<ShDialogContent class={className}>
			{#if title || description}
				<ShDialogHeader>
					{#if title}<ShDialogTitle>{@render title()}</ShDialogTitle>{/if}
					{#if description}<ShDialogDescription>{@render description()}</ShDialogDescription>{/if}
				</ShDialogHeader>
			{/if}

			{#if children}
				<div class={contentClass}>
					{@render children()}
				</div>
			{/if}

			{#if footer}
				<ShDialogFooter>{@render footer()}</ShDialogFooter>
			{/if}
		</ShDialogContent>
	</ShDialog>
{/if}
