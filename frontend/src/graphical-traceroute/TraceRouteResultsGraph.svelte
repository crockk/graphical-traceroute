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
    nodeCircR: 10, // nodeCircleRadius
    strokeWidth: 3, //strokeWidth
    lineOffset: 3  // lineOffset
  }

  const colorOptions = [
    "#008000",
    "#00FFFF",
    "#FF0000",
    "#0000FF",
    "#FF00FF",
    "#2F4F4F",
    "#FFFF00",
    "#FFA500",
  ];

  let parsedTraceroutes;
  $: console.log(parsedTraceroutes);

  function refreshTracerouteGraph() {
    console.log("refreshing traceroutes graph.")
    parsedTraceroutes = parseTraceroutes()
  }

  function parseTraceroutes() {
    // List of (cx:int, cy:int) which define the center point of each node to be graphed
    // center points are defined with unit increments, not pixels.
    let circleList = [];
    // List of information used define the path from the previos node to the current node
    // List elements: {startYLevel: int, endYLevel: int, endTtl: int, colorIndex: int, lineOffsetStart: int, lineOffsetEnd: int}
    // All list element propertiesare defined with unit increments, not pixels.
    let pathList = [];
    $tracerouteQueryResults = mockRouteData;

    let maxTrcrtLength = $tracerouteQueryResults.sort(hopLengthCompare)[0].hops.length;

    // Sort traceroute data from backend by trace_time, newest to oldest
    $tracerouteQueryResults.sort(tracerouteDateCompare);
    // Sort the list of hops for each traceroute by ttl, ascending order
    $tracerouteQueryResults.forEach(function (curTrcrt, trcrtIndex) { curTrcrt.hops.sort(hopCompare); });

    // Outer loop iterates over each possible ttl
    for (let curTtl = 0; curTtl < maxTrcrtLength; curTtl++) {
      // Inner loop iterates over each traceroute in order to access the current ttl
      $tracerouteQueryResults.forEach(function (curTrcrt, trcrtIndex) {
        // console.dir(trcrtIndex);
        // console.dir(curTrcrt);

      // Base case for graphing. If the current node is a placeholder, Do Nothing.
      // All required info is added when placegolders are created
      if ($tracerouteQueryResults[trcrtIndex].hops[curTtl].placeHolder) {
        ;

      // Base case for graphing. The newsest traceroute is plotted as a horizontal line
      } else if (trcrtIndex == 0) {
          circleList.push({
            cx: curTtl,
            cy: 0
          });

          $tracerouteQueryResults[trcrtIndex].hops[curTtl].differs = false;
          $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel = 0;
          $tracerouteQueryResults[trcrtIndex].hops[curTtl].nodeVisitorNum = 0;

      // The case where the host of the node to be plotted differes from
      //    host of the node with the same ttl but in the previuos traceroute
      } else if (curHostDiffersFromPrevTrcrtSameTtl(curTrcrt, trcrtIndex, curTtl)) {

          $tracerouteQueryResults[trcrtIndex].hops[curTtl].differs = true;

          // The case where the host of the previous ttl is not different than the host of the previous ttl and previous traceroute (relative to current node)
          // This is the case where the traceroute branch.
          if (!$tracerouteQueryResults[trcrtIndex].hops[curTtl - 1].differs) {
            // console.log("prev not differs", curTtl, trcrtIndex)

            $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel = $tracerouteQueryResults[trcrtIndex -1].hops[curTtl].yLevel + 1;
            $tracerouteQueryResults[trcrtIndex].hops[curTtl].nodeVisitorNum = 0;

          // The case where the host of the previous ttl is different than the host of the previous ttl and previous traceroute (relative to current node)
          // This is the case where a branched traceroute continues its branch.
          } else {
            // console.log("prev differs", curTtl, trcrtIndex)
            $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel = $tracerouteQueryResults[trcrtIndex].hops[curTtl - 1].yLevel;
            $tracerouteQueryResults[trcrtIndex].hops[curTtl].nodeVisitorNum = $tracerouteQueryResults[trcrtIndex].hops[curTtl - 1].nodeVisitorNum;

          };

          circleList.push({
            cx: curTtl,
            cy: $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel,
          });

        // The case where the host of the node to be plotted does not differes from
        //    host of the node with the same ttl but in the previuos traceroute
        // This is the case where a branched traceroute merges into the previous traceroute
        } else {
          $tracerouteQueryResults[trcrtIndex].hops[curTtl].differs = false;
          $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel = $tracerouteQueryResults[trcrtIndex - 1].hops[curTtl].yLevel;
          $tracerouteQueryResults[trcrtIndex].hops[curTtl].nodeVisitorNum = $tracerouteQueryResults[trcrtIndex - 1].hops[curTtl].nodeVisitorNum + 1;
        };

        // Paths are defined as going from the previous node to the current node
        // Nodes with ttl == 0 have no previous node so they are ommited
        if (curTtl > 0) {
          pathList.push({
            startYLevel: $tracerouteQueryResults[trcrtIndex].hops[curTtl - 1].yLevel,
            endYLevel: $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel,
            endTtl: curTtl,
            colorIndex: trcrtIndex,
            lineOffsetStart: $tracerouteQueryResults[trcrtIndex].hops[curTtl - 1].nodeVisitorNum,
            lineOffsetEnd: $tracerouteQueryResults[trcrtIndex].hops[curTtl].nodeVisitorNum
          });
        };

        // If the current traceroute has fewer hops then the traceroute with the most hops,
        //    then on the 2nd last hop of the shorter traceroute a placeholder node must be added before the the last item in the hop list
        // The new node must be added before the last node because the final node should be the same for all traceroutes
        //    ie. final node is the destination IP of the traceroute and should all traceroutes
        //    The goal is to extend the hop list until the final hop is in the same column as the rest of the traceroutes
        // This process is repeated until the shorter hop list is the same length as the longest one
        // If the final node is in fact different, it will still be plotted in the final column but on a different yLevel just like any other node.
        if (maxTrcrtLength > curTrcrt.hops.length && curTtl >= (curTrcrt.hops.length - 2) ) {
          console.log("not enough hops")

          let hopCopyIndex = curTrcrt.hops.length - 2;

          // Use JSON stringify and parse to create deep copy of the hop to be copied
          let hopDeepCopy = JSON.parse(JSON.stringify(curTrcrt.hops[hopCopyIndex]));

          // Insert the deep copy into the 2nd last position in the array
          curTrcrt.hops.splice(-2, 0, hopDeepCopy);

          // Increment hopCopyIndex AFTER the new item is added, this allows us to index the new item
          hopCopyIndex++

          // The ttl of the new hop is one more than the previous hop
          curTrcrt.hops[hopCopyIndex].ttl = curTrcrt.hops[hopCopyIndex].ttl + 1;
          // Add property stating this hop is a placeholder to extend the traceroute
          curTrcrt.hops[hopCopyIndex].placeHolder = true;
          // The ttl of the last hop should also be incremented
          curTrcrt.hops[curTrcrt.hops.length - 1].ttl = curTrcrt.hops[curTrcrt.hops.length - 1].ttl + 1;

        };
      });
    };

    return {
      circleList: circleList,
      pathList: pathList,
    };
  };

  function hopLengthCompare(a, b) {
    return b.hops.length - a.hops.length;
  };

  function hopCompare(a, b ) {
    return a.ttl - b.ttl;
  };

  function tracerouteDateCompare(a, b ) {
    let dateA = new Date(a.trace_time);
    let dateB = new Date(b.trace_time);
    return dateB - dateA;
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
    let moveY = svgConfig.vInitDist + svgConfig.vNodeDist * (pathInfo.startYLevel) + svgConfig.lineOffset * (pathInfo.lineOffsetStart);
    let moveToStr = "M " + moveX + "," + moveY;

    if (pathInfo.startYLevel == pathInfo.endYLevel) {
      lineStr = "h " + svgConfig.hNodeDist;
    } else {

      let controlX;
      let controlY;

      let endX;
      let endY;

      if (pathInfo.startYLevel < pathInfo.endYLevel) {

        moveX = svgConfig.hInitDist + svgConfig.hNodeDist * (pathInfo.endTtl - 0.5) - svgConfig.lineOffset * pathInfo.lineOffsetStart;
        moveY = svgConfig.vInitDist + svgConfig.vNodeDist * (pathInfo.startYLevel + 0.5);
        moveToStr = "M " + moveX + "," + moveY;

        controlX = svgConfig.hInitDist + svgConfig.hNodeDist * (pathInfo.endTtl - 0.5) - svgConfig.lineOffset * pathInfo.lineOffsetStart;
        controlY = svgConfig.vInitDist + svgConfig.vNodeDist * pathInfo.endYLevel + svgConfig.lineOffset * pathInfo.lineOffsetEnd;

        endX = svgConfig.hInitDist + svgConfig.hNodeDist * (pathInfo.endTtl);
        endY = svgConfig.vInitDist + svgConfig.vNodeDist * ( pathInfo.endYLevel)  + svgConfig.lineOffset * pathInfo.lineOffsetEnd;

      } else {

        controlX = svgConfig.hInitDist + svgConfig.hNodeDist * (pathInfo.endTtl - 0.5) + svgConfig.lineOffset * pathInfo.lineOffsetEnd;
        controlY = svgConfig.vInitDist + svgConfig.vNodeDist * pathInfo.startYLevel + svgConfig.lineOffset * pathInfo.lineOffsetStart;

        endX = svgConfig.hInitDist + svgConfig.hNodeDist * (pathInfo.endTtl - 0.5) + svgConfig.lineOffset * pathInfo.lineOffsetEnd;
        endY = svgConfig.vInitDist + svgConfig.vNodeDist * ( pathInfo.endYLevel + 0.5);

      };

      let controlPoint = controlX + "," + controlY;
      let endPoint = endX + "," + endY;

      lineStr = "Q " + controlPoint + " " + endPoint + " " + pathComplimentSection(pathInfo);
    };
    return moveToStr + " " + lineStr
  };

  function pathComplimentSection(pathInfo) {

    let moveX = svgConfig.hInitDist + svgConfig.hNodeDist * (pathInfo.endTtl - 0.5) + svgConfig.lineOffset * pathInfo.lineOffsetEnd;
    let moveY = svgConfig.vInitDist + svgConfig.vNodeDist * (pathInfo.endYLevel + 0.5);

    let controlX;
    let controlY;

    let endX;
    let endY;

    if (pathInfo.startYLevel < pathInfo.endYLevel) {

      moveX = svgConfig.hInitDist + svgConfig.hNodeDist * (pathInfo.endTtl - 1);
      moveY = svgConfig.vInitDist + svgConfig.vNodeDist * pathInfo.startYLevel + svgConfig.lineOffset * pathInfo.lineOffsetStart;

      controlX = svgConfig.hInitDist + svgConfig.hNodeDist * (pathInfo.endTtl - 0.5)- svgConfig.lineOffset * pathInfo.lineOffsetStart;
      controlY = svgConfig.vInitDist + svgConfig.vNodeDist * pathInfo.startYLevel + svgConfig.lineOffset * pathInfo.lineOffsetStart;

      endX = svgConfig.hInitDist + svgConfig.hNodeDist * (pathInfo.endTtl - 0.5) - svgConfig.lineOffset * pathInfo.lineOffsetStart;
      endY = svgConfig.vInitDist + svgConfig.vNodeDist * (pathInfo.startYLevel + 0.5);

    } else {

      controlX = svgConfig.hInitDist + svgConfig.hNodeDist * (pathInfo.endTtl - 0.5) + svgConfig.lineOffset * pathInfo.lineOffsetEnd;
      controlY = svgConfig.vInitDist + svgConfig.vNodeDist * pathInfo.endYLevel + svgConfig.lineOffset * pathInfo.lineOffsetEnd;

      endX = svgConfig.hInitDist + svgConfig.hNodeDist * ( pathInfo.endTtl);
      endY = svgConfig.vInitDist + svgConfig.vNodeDist * (pathInfo.endYLevel) + svgConfig.lineOffset * pathInfo.lineOffsetEnd;
    };

    let moveToStr = "M " + moveX + "," + moveY;
    let controlPoint = controlX + "," + controlY;
    let endPoint = endX + "," + endY;

    let lineStr = "Q " + controlPoint + " " + endPoint;

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


          <path fill="none" stroke="{ colorOptions[pathInfo.colorIndex] }" stroke-width="{ svgConfig.strokeWidth }"
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
