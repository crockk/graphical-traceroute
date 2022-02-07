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

  async function getMaxRoutes() {
    $maxRoutes = await axios.get($backendBaseURL + '/max-routes').then((x) => x.data.max_routes);
  };

  function updatePanelOpenList(index){
    panelOpenList[index] = !panelOpenList[index];
  };
  $: panelOpenList = new Array($maxRoutes).fill(false);

  onMount(() => {
    getMaxRoutes();
    // $tracerouteQueryResults = mockRouteData;
	});

  $: $tracerouteQueryResults ? refreshTracerouteGraph() : "$tracerouteQueryResults set to nullable val."

  const svgConfig = {
    width: 1200,
    aspectRatio: 9/16,
    hInitDist: 50, // horizontalInitialDistance
    vInitDist: 50, // verticalInitialDistance
    hNodeDist: 75, // horizontalNodeDistance
    vNodeDist: 75, // verticalNodeDistance
    nodeCircR: 10 // nodeCircleRadius
  }

  let parsedTraceroutes;
  $: console.log(parsedTraceroutes);

  function refreshTracerouteGraph() {
    console.log("refreshing traceroutes graph.")
    parsedTraceroutes = parseTraceroutes()
  }

  function parseTraceroutes() {
    let circleList = [];
    let pathList = [];

    let maxTrcrtLength = $tracerouteQueryResults.sort(hopLengthCompare)[0].hops.length;

    // TODO: sort tracerouteList by trcrtTime, newest to oldest.
    // TODO: sort each traceroute.hop list by ttl.
    //       Currently a bug where clicking the submit button multiple times makes everything out of order

    let trcrtPathEnded = Array($tracerouteQueryResults.length).fill(false);
    let endPath = false;

    for (let curTtl = 0; curTtl < maxTrcrtLength; curTtl++) {
      $tracerouteQueryResults.forEach(function (curTrcrt, trcrtIndex) {
        // console.dir(trcrtIndex);
        // console.dir(curTrcrt);

        if (trcrtIndex == 0) {

          circleList.push({
            cx: curTtl,
            cy: 0
          });
          $tracerouteQueryResults[trcrtIndex].hops[curTtl].differs = false;
          $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel = 0;

        } else if (curHostDiffersFromPrevTrcrtSameTtl(curTrcrt, trcrtIndex, curTtl)) {

          $tracerouteQueryResults[trcrtIndex].hops[curTtl].differs = true;

          if (!$tracerouteQueryResults[trcrtIndex].hops[curTtl - 1].differs) {
            // console.log("prev not differs", curTtl, trcrtIndex)

            $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel = $tracerouteQueryResults[trcrtIndex -1].hops[curTtl].yLevel + 1;

          } else {
            // console.log("prev differs", curTtl, trcrtIndex)

            $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel = $tracerouteQueryResults[trcrtIndex].hops[curTtl - 1].yLevel;

          };

          circleList.push({
            cx: curTtl,
            cy: $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel,
          });

        } else {
          $tracerouteQueryResults[trcrtIndex].hops[curTtl].differs = false;
          $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel = $tracerouteQueryResults[trcrtIndex - 1].hops[curTtl].yLevel;
        };

        if (curTtl > 0) {
          pathList.push({
            startYLevel: $tracerouteQueryResults[trcrtIndex].hops[curTtl - 1].yLevel,
            endYLevel: $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel,
            endTtl: curTtl
          });
        };
      });
    };

    return {
      circleList: circleList,
      pathList: pathList,
    };
  };

  function hopLengthCompare(a, b) {
    if ( a.hops.length < b.hops.length ) {
      return -1;
    };
    if ( a.hops.length > b.hops.length ) {
      return 1;
    };
    return 0;
  };

  function curHostDiffersFromPrevTrcrtSameTtl(curTrcrt, trcrtIndex, curTtl) {
    if (curTtl < curTrcrt.hops.length && curTtl > 0) {
      let curHost = curTrcrt.hops[curTtl].host;
      let prevHost = $tracerouteQueryResults[trcrtIndex - 1].hops[curTtl].host;
      // console.log(curHost, prevHost)
      return curHost != prevHost;
    };
    return false;
  };

  function pathInfoToSvgStr(pathInfo) {

    let lineStr;

    let moveX = svgConfig.hInitDist + svgConfig.hNodeDist * (pathInfo.endTtl - 1);
    let moveY = svgConfig.vInitDist + svgConfig.vNodeDist * (pathInfo.startYLevel);
    let moveToStr = "M " + moveX + "," + moveY;

    if (pathInfo.startYLevel == pathInfo.endYLevel) {
      lineStr = "h " + svgConfig.hNodeDist;
    } else {

      let controlX;
      let controlY;

      let endX;
      let endY;

      if (pathInfo.startYLevel < pathInfo.endYLevel) {

        moveX = svgConfig.hInitDist + svgConfig.hNodeDist * (pathInfo.endTtl - 0.5);
        moveY = svgConfig.vInitDist + svgConfig.vNodeDist * (pathInfo.startYLevel + 0.5);
        moveToStr = "M " + moveX + "," + moveY;

        controlX = 0;
        controlY = svgConfig.vNodeDist * (pathInfo.endYLevel - 0.5);

        endX = svgConfig.hNodeDist * 0.5;
        endY = svgConfig.vNodeDist * ( pathInfo.endYLevel - pathInfo.startYLevel - 0.5);

      } else {

        controlX = svgConfig.hNodeDist * 0.5;
        controlY = 0;

        endX = svgConfig.hNodeDist * 0.5;
        endY = svgConfig.vNodeDist * ( pathInfo.endYLevel - pathInfo.startYLevel + 0.5);

      };

      let controlPoint = controlX + "," + controlY;
      let endPoint = endX + "," + endY;

      lineStr = "q " + controlPoint + " " + endPoint + " " + pathComplimentSection(pathInfo);
    };
    return moveToStr + " " + lineStr
  };

  function pathComplimentSection(pathInfo) {

    let moveX = svgConfig.hInitDist + svgConfig.hNodeDist * (pathInfo.endTtl - 0.5);
    let moveY = svgConfig.vInitDist + svgConfig.vNodeDist * (pathInfo.endYLevel + 0.5);

    let controlX;
    let controlY;

    let endX;
    let endY;

    if (pathInfo.startYLevel < pathInfo.endYLevel) {

      moveX = svgConfig.hInitDist + svgConfig.hNodeDist * (pathInfo.endTtl - 1);
      moveY = svgConfig.vInitDist + svgConfig.vNodeDist * pathInfo.startYLevel;

      controlX = svgConfig.hNodeDist * 0.5;
      controlY = 0;

      endX = svgConfig.hNodeDist * 0.5;
      endY = svgConfig.vNodeDist * 0.5;

    } else {

      controlX = 0;
      controlY = svgConfig.vNodeDist * -0.5;

      endX = svgConfig.hNodeDist * 0.5;
      endY = svgConfig.vNodeDist * -0.5;
    };

    let moveToStr = "M " + moveX + "," + moveY;
    let controlPoint = controlX + "," + controlY;
    let endPoint = endX + "," + endY;

    let lineStr = "q " + controlPoint + " " + endPoint;

    return moveToStr + " " + lineStr
  };

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

      {#if parsedTraceroutes}
      <svg width="{ svgConfig.width }" height="{ svgConfig.width * svgConfig.aspectRatio }">

        {#each parsedTraceroutes.pathList as pathInfo}


          <path fill="none" stroke="red"
            d="
              {pathInfoToSvgStr(pathInfo)}
            "
          />

        {/each}
        {#each parsedTraceroutes.circleList as circleInfo}

          <circle
            cx="{ svgConfig.hInitDist + svgConfig.hNodeDist * circleInfo.cx }"
            cy="{ svgConfig.vInitDist + svgConfig.vNodeDist * circleInfo.cy }"
            r="{ svgConfig.nodeCircR }"
            stroke="green"
            stroke-width="4"
            fill="yellow"
          />
        {/each}

      </svg>
      {/if}

    </LayoutCell>

  </LayoutGrid>
{/if}
