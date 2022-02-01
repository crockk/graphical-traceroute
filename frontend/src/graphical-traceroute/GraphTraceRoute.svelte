<script>

  import TraceRouteParams from './TraceRouteParams.svelte'
  let srcNode;
  let destNode;
  let numRoutes;
  let searchDuration;
  let selectedDate;

</script>

<TraceRouteParams
  bind:srcNode={srcNode}
  bind:destNode={destNode}
  bind:numRoutes={numRoutes}
  bind:searchDuration={searchDuration}
  bind:selectedDate={selectedDate}
/>



{srcNode}
{destNode}
{numRoutes}
{searchDuration}
{selectedDate}
