<script lang="ts">
	import PaginationEllipsis from '$lib/components/ui/pagination/pagination-ellipsis.svelte';
	import { cn } from '$lib/utils';
	import type { ComponentProps } from 'svelte';

	let { class: className, ...restProps }: ComponentProps<typeof PaginationEllipsis> = $props();
</script>

<PaginationEllipsis class={cn(className)} {...restProps} />
