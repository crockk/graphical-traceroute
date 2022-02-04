<script lang="ts">

  import DataTable, { Head, Body, Row, Cell as DataCell } from '@smui/data-table';
  import Paper, { Title, Content } from '@smui/paper';
  import LayoutGrid, { Cell as LayoutCell, InnerGrid } from '@smui/layout-grid';
  import Button, { Label } from '@smui/button';
  import Accordion, { Panel, Header, Content } from '@smui-extra/accordion';
  import IconButton, { Icon } from '@smui/icon-button';
  import axios from "axios";
  import {
    backendBaseURL,
    tracerouteQueryResults,
    maxRoutes
  } from '../store.js'
  import { onMount } from 'svelte';

  import mockRouteData from './mockRouteData.js'

  function hopCompare( a, b ) {
    if ( a.ttl < b.ttl ){
      return -1;
    }
    if ( a.ttl > b.ttl ){
      return 1;
    }
    return 0;
  }

  async function getMaxRoutes() {
    $maxRoutes = await axios.get($backendBaseURL + '/max-routes').then((x) => x.data.max_routes);
  };

  function updatePanelOpenList(index){
    panelOpenList[index] = !panelOpenList[index];
  }

  $: console.dir($tracerouteQueryResults ? $tracerouteQueryResults[0].hops.sort( hopCompare ) : undefined)

  $: panelOpenList = new Array($maxRoutes).fill(false);

  onMount(() => {
    getMaxRoutes();
    $tracerouteQueryResults = mockRouteData;
	});

  $: console.log(mockRouteData);
  let circleY;
  let pathY;

  const svgConfig = {
    width: 1200,
    aspectRatio: 9/16,
    hInitDist: 50, // horizontalInitialDistance
    vInitDist: 50, // verticalInitialDistance
    hNodeDist: 75, // horizontalNodeDistance
    vNodeDist: 75, // verticalNodeDistance
    nodeCircR: 10 // nodeCircleRadius
  }

  function traceRouteHost(curIndex, curTtl) {
    let host = "";
    if (curIndex < $tracerouteQueryResults.length) {
      let rt = $tracerouteQueryResults[curIndex]
      if (curTtl <= rt.hops.length) {
        host = rt.hops.sort( hopCompare )[curTtl - 1].host;
      }
    };
    console.log("trctr host: " + host);
    return host;
  };

  function previosTraceRouteHost(curIndex, curTtl) {
    if(curIndex >= 1){
      return traceRouteHost(curIndex - 1, curTtl);
    };
    console.log("previosTraceRouteHost default");
    return "";
  };

  function nextTraceRouteHost(curIndex, curTtl) {
    if(curIndex < $tracerouteQueryResults.length){
      console.log("here");
      return traceRouteHost(curIndex + 1, curTtl);
    };
    console.log("nextTraceRouteHost default");
    console.log($tracerouteQueryResults.length)
    console.log(curIndex)

    return "";
  };

  function previousHopDiffers(curIndex, curTtl) {
    if(curTtl >= (1 + 1)){
      console.log("here")
      return previosTraceRouteHost(curIndex, curTtl - 1) == previosTraceRouteHost(curIndex + 1, curTtl -1);
    };
    console.log("previousHopDiffers default");

    console.log(curIndex >= 2)
    console.log(curTtl>= 2)

    return false;
  }
  function nextHopDiffers(curIndex, curTtl) {
    return traceRouteHost(curIndex, curTtl + 1) != previosTraceRouteHost(curIndex, curTtl + 1)
  }
</script>

{#if (! $tracerouteQueryResults)}
  <LayoutGrid>

    <!-- ROW -->
    <LayoutCell span="1">
    </LayoutCell>

    <LayoutCell span="4">
      No traceroutes found
    </LayoutCell>

    <LayoutCell span="7">
    </LayoutCell>
  </LayoutGrid>
{:else}
  <LayoutGrid>

    <!-- ROW -->
    <LayoutCell span="1">
    </LayoutCell>

    <LayoutCell span="11">

      <svg width="{ svgConfig.width }" height="{ svgConfig.width * svgConfig.aspectRatio }">

        {#each $tracerouteQueryResults as traceroute, index}
          {#each traceroute.hops.sort( hopCompare ) as hop}

            {#if index != 0 && hop.host != previosTraceRouteHost(index, hop.ttl)}

              { circleY = svgConfig.vNodeDist + svgConfig.vInitDist }


              { pathY = svgConfig.vNodeDist + svgConfig.vInitDist }

            {:else}
              { pathY = svgConfig.vInitDist }

              { circleY = svgConfig.vInitDist }

            {/if}

            <!-- {#if previousHopDiffers(index, hop.ttl)}

              { pathY = svgConfig.vNodeDist + svgConfig.vInitDist }

            {:else}

              { pathY = svgConfig.vInitDist }

            {/if} -->

            {#if hop.ttl < traceroute.hops.length }
              <path fill="none" stroke="red"
                d="
                  M { svgConfig.hInitDist + svgConfig.hNodeDist * hop.ttl },{ pathY }
                  h { svgConfig.hNodeDist }
                "
              />
            {/if}


            <circle
              cx="{ svgConfig.hInitDist + svgConfig.hNodeDist * hop.ttl }"
              cy="{ circleY }"
              r="{ svgConfig.nodeCircR }"
              stroke="green"
              stroke-width="4"
              fill="yellow"
            />

          {/each}
        {/each}

      </svg>

    </LayoutCell>

  </LayoutGrid>
{/if}
