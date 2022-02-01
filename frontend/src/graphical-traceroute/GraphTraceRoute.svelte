<script>

  import TraceRouteParams from './TraceRouteParams.svelte'
  let srcNode;
  let destNode;
  let numRoutes;

</script>

<TraceRouteParams
  bind:srcNode={srcNode}
  bind:destNode={destNode}
  bind:numRoutes={numRoutes}
/>



{srcNode}
{destNode}
{numRoutes}
