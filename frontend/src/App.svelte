<script lang="ts">

  import Button from '@smui/button';
  import TopAppBar, {
		Row,
		Section,
		Title,
		AutoAdjust,
		TopAppBarComponentDev
	} from '@smui/top-app-bar';
  import { Label, Icon } from '@smui/common';

  import GraphTraceRoute from './graphical-traceroute/GraphTraceRoute.svelte'

  let lightTheme = typeof window === 'undefined' || window.matchMedia('(prefers-color-scheme: light)').matches;
  $: console.log((lightTheme ? "light" : "dark") + " theme activated")

  function switchTheme() {
    lightTheme = !lightTheme;
    let themeLink = document.head.querySelector<HTMLLinkElement>('#theme');
    if (!themeLink) {
      themeLink = document.createElement('link');
      themeLink.rel = 'stylesheet';
      themeLink.id = 'theme';
    }
    themeLink.href = `/static/smui${lightTheme ? '' : '-dark'}.css`;
    document.head.querySelector<HTMLLinkElement>('link[href="/static/smui-dark.css"]')
    ?.insertAdjacentElement('afterend', themeLink);


    let siteThemeLink = document.head.querySelector<HTMLLinkElement>('#site');
    if (!siteThemeLink) {
      siteThemeLink = document.createElement('link');
      siteThemeLink.rel = 'stylesheet';
      siteThemeLink.id = 'site';
    }
    siteThemeLink.href = `/static/site${lightTheme ? '' : '-dark'}.css`;
    document.head.querySelector<HTMLLinkElement>('link[href="/static/site-dark.css"]')
    ?.insertAdjacentElement('afterend', siteThemeLink);

  }

  let topAppBar: TopAppBarComponentDev;

</script>


<TopAppBar bind:this={topAppBar} class="demo-top-app-bar mdc-top-app-bar smui-top-app-bar--static" >
  <Row>

    <Section>
      <Title class="mdc-theme--primary" style="font-weight: bold">Graphical Trace Route</Title>
    </Section>

    <Section>
    <!--
      <TabBar tabs={webpages} let:tab bind:active={activeTab}>
        <Tab class="secondary"  {tab}>
          <Label>{tab.name}</Label>
        </Tab>
      </TabBar>
      -->
    </Section>

    <Section align="end" toolbar>
      <Button color='secondary' variant="raised" toggle on:click={switchTheme}>
        <Icon class="material-icons">{ lightTheme ? "light_mode" : "dark_mode" }</Icon>
        <Label>{lightTheme ? 'Lights off' : 'Lights on'}</Label>
      </Button>
    </Section>

  </Row>
</TopAppBar>

<AutoAdjust {topAppBar}>
</AutoAdjust>

<div>
  <GraphTraceRoute/>
</div>
