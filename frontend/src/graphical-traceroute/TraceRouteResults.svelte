<script lang="ts">
  import Paper, { Title, Content } from '@smui/paper';
  import Tab, { Label } from '@smui/tab';
  import TabBar from '@smui/tab-bar';
  import LayoutGrid, { Cell } from '@smui/layout-grid';

  import TraceRouteResultsText from './TraceRouteResultsText.svelte'
  import TraceRouteResultsGraph from './TraceRouteResultsGraph.svelte'

  const resultPages = [
    { id: 1,
      component: TraceRouteResultsText,
      title: "Text Results",
    },
    { id: 2,
      component: TraceRouteResultsGraph,
      title: "Graph Results",
    }
  ];

  let activeTabItem = resultPages[0];

</script>

<Paper color="primary" variant="outlined" class="mdc-theme--primary">

  <Title>
    <LayoutGrid>

      <Cell span="3">
        Trace Route Results
      </Cell>

      <Cell span="9">

        <TabBar tabs={resultPages} let:tab bind:active={activeTabItem}>
          <Tab {tab}>
            <Label>{tab.title}</Label>
          </Tab>
        </TabBar>

      </Cell>

    </LayoutGrid>
  </Title>

  <Content>
    <svelte:component this={activeTabItem.component} />
  </Content>

</Paper>
