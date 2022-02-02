<script>

  import DataTable, { Head, Body, Row, Cell } from '@smui/data-table';
  import TraceRouteParams from './TraceRouteParams.svelte'
  import TraceRouteSubmit from './TraceRouteSubmit.svelte'
  import Paper, { Title, Content } from '@smui/paper';
  import {
    srcNode,
    destNode,
    numRoutes,
    searchDuration,
    selectedDate
  } from '../store.js'

</script>

<TraceRouteParams/>

<br>

<TraceRouteSubmit/>
