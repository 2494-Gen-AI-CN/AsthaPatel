from datetime import timedelta, timezone
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# 1. Load the csv file into a pandas DataFrame 
# Data is a 5-day OHLC data for NAS100 index for October 2026.
df = pd.read_csv("NAS100_oct_7th_2026.csv")
# define EST timezone
EST = timezone(timedelta(hours=-5), name='EST')
df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_convert(EST)
# set 'date' as index and sort in ascending order for proper resampling
df = df.set_index("date").sort_index() 

# define timeframes
TIMEFRAMES = {
    "1m" : "1min",
    "15m" : "15min",
    "30m" : "30min",
    "45m" : "45min",
    "1h" : "1h",
    "2h" : "2h",
    "4h" : "4h"
}

# 2. OHLC aggregation
def ohlc_agg(data, timeframe):
    # define the aggregation functions for each column
    agg_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    }

    # resample() traverses through the data and groups it into the specified timeframe
    # agg() applies the aggregation functions defined in agg_dict to each group
    return data.resample(timeframe).agg(agg_dict)

def make_figure(candles, label, show_all):
    # Plot EST wall-clock values so a browser's timezone cannot shift them.
    times = candles.index.tz_localize(None)
    step = pd.Timedelta(TIMEFRAMES[label])
    grid = pd.date_range(times[0], times[-1], freq=TIMEFRAMES[label])
    missing = grid.difference(times)
    figure = go.Figure(go.Candlestick(
        x=times, open=candles['open'], high=candles['high'],
        low=candles['low'], close=candles['close'],
        increasing=dict(line=dict(color='#35dfdf', width=1), fillcolor='#35dfdf'),
        decreasing=dict(line=dict(color='#f16ab6', width=1), fillcolor='#f16ab6'),
        name='NAS100',
    ))
    # All rows remain in the chart. Only its initial viewport is limited.
    first_visible = 0 if show_all else max(0, len(times) - 150)
    figure.update_layout(
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(13,18,48,0.76)',
        hoverlabel=dict(bgcolor='#211a40', bordercolor='#7060a0',
                        font=dict(color='#f0eaff', size=12)),
        height=540, margin=dict(l=12, r=68, t=22, b=10),
        font=dict(family='Arial, sans-serif', color='#cbd5e1'),
        showlegend=False, dragmode='pan', hovermode='closest',
        uirevision=f'{label}-{times[0]}-{times[-1]}-{show_all}',
        xaxis=dict(
            type='date',
            range=[times[first_visible] - step / 2, times[-1] + step],
            rangeslider=dict(visible=True, thickness=0.055, bgcolor='#171630',
                             bordercolor='#39315b', borderwidth=1),
            rangebreaks=[dict(values=missing.to_pydatetime().tolist(),
                              dvalue=step.total_seconds() * 1000)],
            tickformat='%I:%M %p<br>%b %-d',
            hoverformat='%b %-d, %Y · %I:%M %p', gridcolor='rgba(145,151,215,0.10)',
            tickfont=dict(size=11, color='#abb3d5'), zeroline=False,
        ),
        yaxis=dict(title='Price (USD)', side='right', tickformat=',.2f',
                   gridcolor='rgba(145,151,215,0.10)', fixedrange=False,
                   tickfont=dict(size=11, color='#abb3d5'), zeroline=False),
    )
    figure.add_annotation(
        text='NAS100', x=0.5, y=0.55, xref='paper', yref='paper',
        showarrow=False, font=dict(size=100, color='rgba(182,153,243,0.085)'),
        textangle=0,
    )
    figure.add_hline(y=float(candles.close.iloc[-1]), line_width=1,
                     line_dash='dot', line_color='rgba(53,223,223,0.40)')
    return figure


def select_timeframe(value):
    st.session_state.active_timeframe = value


def select_view(value):
    st.session_state.full_day_view = value


def main():
    st.set_page_config(page_title='NAS100 | Market Terminal', page_icon='📈', layout='wide',
                       initial_sidebar_state='collapsed')
    st.markdown('''<style>
      .stApp {background:radial-gradient(ellipse at 12% 0%,#233765 0%,transparent 48%),
        radial-gradient(ellipse at 92% 80%,#281344 0%,transparent 55%),#10152c;color:#e7e4ff;}
      header[data-testid="stHeader"] {display:none;}
      .block-container {padding:8px 22px 0;max-width:none;}
      div[data-testid="stVerticalBlock"] {gap:0.2rem;}
      .st-key-chart_toolbar {
        padding:10px 12px;background:linear-gradient(110deg,#1d2b4eaa,#251c4099);
        border:1px solid #7263a333;border-radius:12px;
        box-shadow:0 5px 18px #080a191f;margin:4px 0 6px;
      }
      .st-key-chart_toolbar div[data-testid="stHorizontalBlock"] {gap:6px;}
      .st-key-chart_toolbar button {
        min-height:36px;border-radius:8px;font-size:12px;font-weight:600;
        transition:background 160ms,border-color 160ms,box-shadow 160ms;
      }
      .st-key-chart_toolbar button p {font-size:12px;letter-spacing:.3px;}
      .st-key-chart_toolbar button[data-testid="stBaseButton-secondary"] {
        color:#b9b9d8;background:#12172b66;border:1px solid transparent;
      }
      .st-key-chart_toolbar button[data-testid="stBaseButton-secondary"]:hover {
        color:#f0eaff;background:#5d4d8033;border-color:#8c73ba66;
      }
      .st-key-chart_toolbar button[data-testid="stBaseButton-primary"] {
        color:#fff;background:linear-gradient(120deg,#516bc4,#8b55b8);
        border:1px solid #b59bef88;box-shadow:0 2px 12px #7855bd33;
      }
      .st-key-chart_toolbar button:focus-visible {outline:2px solid #66dedc;outline-offset:2px;}
      .terminal-header {display:flex;align-items:center;justify-content:space-between;
        padding:8px 0 10px;border-bottom:1px solid #57508055;gap:18px;}
      .brand {font:600 9px Arial;letter-spacing:2px;color:#aaa2cc;margin-bottom:5px;}
      .symbol {font:700 25px Arial;letter-spacing:-.6px;color:#f1f5f9;}
      .sub {font:11px Arial;color:#a4a9cd;margin-left:12px;}
      .footer {display:flex;justify-content:space-between;gap:12px;
        border-top:1px solid #57508055;padding-top:4px;font:9px Arial;color:#9d97bb;}
      iframe {border-radius:8px;}
      @media(max-width:700px) {
        .block-container {padding:8px 10px 0;}
        .sub {display:block;margin:5px 0 0;}
        .symbol {font-size:20px;}
        .footer {flex-wrap:wrap;}
      }
    </style>''', unsafe_allow_html=True)
    components.html(TICKER_HTML, height=36, scrolling=False)
    st.markdown(f'''<div class="terminal-header">
      <div><div class="brand">MARKET TERMINAL / HISTORICAL</div>
      <span class="symbol">NAS100</span><span class="sub">Candlestick chart · 07 OCT 2026 · EST / UTC−5</span></div>
      </div>''', unsafe_allow_html=True)

    st.session_state.setdefault('active_timeframe', '1m')
    st.session_state.setdefault('full_day_view', False)
    with st.container(key='chart_toolbar'):
        intervals, view = st.columns([5, 1.7], gap='large')
        with intervals:
            buttons = st.columns(len(TIMEFRAMES))
            for column, option in zip(buttons, TIMEFRAMES):
                column.button(
                    option, key=f'tf_{option}', width='stretch',
                    type='primary' if st.session_state.active_timeframe == option else 'secondary',
                    on_click=select_timeframe, args=(option,),
                    help=f'Show {option} candles',
                )
        with view:
            recent, full = st.columns(2)
            recent.button('Recent', key='view_recent', width='stretch',
                          type='secondary' if st.session_state.full_day_view else 'primary',
                          on_click=select_view, args=(False,),
                          help='Start with the latest 150 candles; pan back for earlier data')
            full.button('Full day', key='view_full', width='stretch',
                        type='primary' if st.session_state.full_day_view else 'secondary',
                        on_click=select_view, args=(True,), help='Fit all available candles')

    label = st.session_state.active_timeframe
    show_all = st.session_state.full_day_view

    candles = ohlc_agg(df, TIMEFRAMES[label]).dropna()
    figure = make_figure(candles, label, show_all)
    chart_html = figure.to_html(
        full_html=True, include_plotlyjs=True,
        config={'scrollZoom': True, 'displaylogo': False, 'responsive': True,
                'modeBarButtonsToRemove': ['select2d', 'lasso2d']},
    )
    # Fit the Plotly canvas to the available browser height. Inform Streamlit
    # of the same iframe height so the page has no unnecessary chart scrollbar.
    resize_script = '''<style>html,body{margin:0;overflow:hidden;
      background:linear-gradient(125deg,#142140,#17142f 60%,#211435);}
      .modebar{background:transparent!important;}
      </style>
    <script>
    let previousHeight=0;
    function fitChart(){
      let viewport=window.screen.availHeight-130,top=180;
      try{
        viewport=window.parent.innerHeight;
        if(window.frameElement){top=window.frameElement.getBoundingClientRect().top;}
      }catch(e){}
      const height=500;
      const chart=document.querySelector('.plotly-graph-div');
      if(chart&&window.Plotly&&height!==previousHeight){
        previousHeight=height;
        Plotly.relayout(chart,{height:height});
        if(window.frameElement){
          window.frameElement.style.height=height+'px';
          const host=window.frameElement.closest('[data-testid="stElementContainer"]');
          if(host){host.style.height=height+'px';host.style.minHeight='0';}
        }
        window.parent.postMessage({isStreamlitMessage:true,type:'streamlit:setFrameHeight',height:height},'*');
      }
    }
    window.addEventListener('load',fitChart);
    window.addEventListener('resize',fitChart);
    try{window.parent.addEventListener('resize',fitChart);}catch(e){}
    setTimeout(fitChart,150);
    setTimeout(fitChart,650);
    </script>'''
    components.html(chart_html.replace('</body>', resize_script+'</body>'), height=540, scrolling=False)
    st.markdown(f'''<div class="footer"><span> Data: 07 OCT 2026</span>
      <span>Drag to pan · Scroll to zoom · Bottom navigator for earlier candles</span>
      <span>EST · Source gap 4:15–5:59 PM</span></div>''', unsafe_allow_html=True)


# Real ticker symbols with simulated prices, independent of the NAS100 chart.
# It runs in the browser and does not need an API, connection, or Python refresh.
TICKER_HTML = '''<!doctype html><html><head><style>
html,body{margin:0;background:transparent;font:11px Arial;color:#f0e9ff;overflow:hidden;}
.bar{height:34px;display:flex;align-items:center;border:1px solid #60538b66;border-radius:6px;
 background:linear-gradient(100deg,#243c64,#292044 60%,#342044);}
.clip{overflow:hidden;flex:1;}.track{display:flex;width:max-content;animation:slide 55s linear infinite;}
.item{display:inline-flex;align-items:center;gap:12px;padding:0 26px;border-right:1px solid #8d7dae33;}
.name{color:#d2bff3;letter-spacing:.8px;font-weight:700;width:44px;}
.price{font-variant-numeric:tabular-nums;display:inline-block;min-width:66px;}
.change{font-variant-numeric:tabular-nums;display:inline-block;min-width:60px;}
.up{color:#50e4df;}.down{color:#f783bf;}
.clip:hover .track{animation-play-state:paused;}
@keyframes slide{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media(prefers-reduced-motion:reduce){.track{animation:none;}}
</style></head><body><div class="bar">
<div class="clip"><div class="track" id="track"></div></div></div><script>
// Illustrative values only; no live quote service is connected.
const quotes=[['AAPL',231.84],['MSFT',427.18],['NVDA',182.64],['AMZN',224.91],
 ['GOOGL',198.45],['META',618.28],['TSLA',351.06],['AVGO',287.32],
 ['AMD',176.42],['NFLX',112.76]];
const base=quotes.map((q,i)=>q[1]/(1+(i%2===0?1:-1)*(0.003+i*0.0005)));
function render(){
 const html=quotes.map((q,i)=>{
  const change=(q[1]/base[i]-1)*100;
  return `<span class="item"><span class="name">${q[0]}</span><span class="price">$${q[1].toFixed(2)}</span>
   <span class="change ${change>=0?'up':'down'}">${change>=0?'+':''}${change.toFixed(2)}%</span></span>`;
 }).join('');
 document.getElementById('track').innerHTML=html+html;
}
render();setInterval(()=>{quotes.forEach(q=>q[1]*=1+(Math.random()-.5)*.001);render();},1800);
</script></body></html>'''


if __name__ == '__main__':
    main()
