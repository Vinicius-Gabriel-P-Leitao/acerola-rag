<script lang="ts">
	import ShDialog from './sh-dialog.svelte';
	import ShDialogDescription from './sh-dialog-description.svelte';
	import type { ComponentProps } from 'svelte';

	let { ...restProps }: ComponentProps<typeof ShDialogDescription> = $props();
</script>

<ShDialog>
	<ShDialogDescription {...restProps} />
</ShDialog>
