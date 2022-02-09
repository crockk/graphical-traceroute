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
    // $tracerouteQueryResults = mockRouteData;

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

        if (maxTrcrtLength > curTrcrt.hops.length && curTtl >= (curTrcrt.hops.length - 2) ) {
          console.log("not enough hops")
          curTrcrt.hops.splice(-2,0,JSON.parse(JSON.stringify(curTrcrt.hops[curTrcrt.hops.length - 2])));
          curTrcrt.hops[curTrcrt.hops.length - 2].ttl = curTrcrt.hops[curTrcrt.hops.length - 2].ttl + 1;
          curTrcrt.hops[curTrcrt.hops.length - 2].placeHolder = true;
          curTrcrt.hops[curTrcrt.hops.length - 1].ttl = curTrcrt.hops[curTrcrt.hops.length - 1].ttl + 1;
        };

        // Base case for graphing. The newsest traceroute is plotted as a horizontal line
        if (trcrtIndex == 0) {
          if (!$tracerouteQueryResults[trcrtIndex].hops[curTtl].placeHolder) {
            circleList.push({
              cx: curTtl,
              cy: 0
            });
          };

          $tracerouteQueryResults[trcrtIndex].hops[curTtl].differs = false;
          $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel = 0;
          $tracerouteQueryResults[trcrtIndex].hops[curTtl].nodeVisitorNum = 0;

        // The case where the host of the node to be plotted differes from
        //    host of the node with the same ttl but in the previuos traceroute
      } else if (curHostDiffersFromPrevTrcrtSameTtl(curTrcrt, trcrtIndex, curTtl) && !$tracerouteQueryResults[trcrtIndex].hops[curTtl].placeHolder) {

          $tracerouteQueryResults[trcrtIndex].hops[curTtl].differs = true;

          if (!$tracerouteQueryResults[trcrtIndex].hops[curTtl - 1].differs) {
            // console.log("prev not differs", curTtl, trcrtIndex)

            $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel = $tracerouteQueryResults[trcrtIndex -1].hops[curTtl].yLevel + 1;
            $tracerouteQueryResults[trcrtIndex].hops[curTtl].nodeVisitorNum = 0;

          } else {
            // console.log("prev differs", curTtl, trcrtIndex)
            $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel = $tracerouteQueryResults[trcrtIndex].hops[curTtl - 1].yLevel;
            $tracerouteQueryResults[trcrtIndex].hops[curTtl].nodeVisitorNum = $tracerouteQueryResults[trcrtIndex].hops[curTtl - 1].nodeVisitorNum;

          };

          if (!$tracerouteQueryResults[trcrtIndex].hops[curTtl].placeHolder) {
            circleList.push({
              cx: curTtl,
              cy: $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel,
            });
          };
        // The case where the host of the node to be plotted does not differes from
        //    host of the node with the same ttl but in the previuos traceroute
        } else {
          if (!$tracerouteQueryResults[trcrtIndex].hops[curTtl].placeHolder) {
            $tracerouteQueryResults[trcrtIndex].hops[curTtl].differs = false;
            $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel = $tracerouteQueryResults[trcrtIndex - 1].hops[curTtl].yLevel;
            $tracerouteQueryResults[trcrtIndex].hops[curTtl].nodeVisitorNum = $tracerouteQueryResults[trcrtIndex - 1].hops[curTtl].nodeVisitorNum + 1;
          } else {
              $tracerouteQueryResults[trcrtIndex].hops[curTtl].differs = true;
              $tracerouteQueryResults[trcrtIndex].hops[curTtl].yLevel = $tracerouteQueryResults[trcrtIndex].hops[curTtl - 1].yLevel;
              $tracerouteQueryResults[trcrtIndex].hops[curTtl].nodeVisitorNum = $tracerouteQueryResults[trcrtIndex].hops[curTtl - 1].nodeVisitorNum;
          };
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
      endY = svgConfig.vInitDist + svgConfig.vNodeDist * 0.5;

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
