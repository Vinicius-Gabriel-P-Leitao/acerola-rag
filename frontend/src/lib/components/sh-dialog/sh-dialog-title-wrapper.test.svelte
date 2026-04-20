<script lang="ts">
	import ShDialog from './sh-dialog.svelte';
	import ShDialogTitle from './sh-dialog-title.svelte';
	import type { ComponentProps } from 'svelte';

	let { ...restProps }: ComponentProps<typeof ShDialogTitle> = $props();
</script>

<ShDialog>
	<ShDialogTitle {...restProps} />
</ShDialog>
