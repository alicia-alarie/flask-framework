
from flask import Flask, render_template, request, redirect
import requests
import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.models import Legend, LegendItem
from bokeh.models import DatetimeTickFormatter

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/graph', methods=['POST'])
def graph():
    projectpath = request.form
    monthselection= str(request.form.get("month"))
    print(monthselection)
    
    symbol=projectpath.get('stockname')
    print(projectpath)

    adjdata=requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol='+symbol+'&outputsize=full&apikey=MWDL9XVGUTMSSPDP')
    adjdata=adjdata.json()
    
    AdjTimeSeries=pd.DataFrame(adjdata.get('Time Series (Daily)'))
    AdjTimeSeries=AdjTimeSeries.transpose()
    
    # 
    Dates=pd.DataFrame()
    Dates=AdjTimeSeries.index
    Dates=pd.to_datetime(Dates)
    
    #Filter for the month of June to present
    if monthselection == 'April':
        start_date="2020-04-01 00:00:00"
        end_date="2020-04-30 00:00:00"
    elif monthselection == 'May':
        start_date="2020-05-01 00:00:00"
        end_date="2020-05-29 00:00:00"
    elif monthselection == 'June':
        start_date="2020-06-01 00:00:00"
        end_date="2020-06-30 00:00:00"
    
    LastMonthDates=Dates[Dates>=start_date]
    LastMonthDates=LastMonthDates[LastMonthDates<=end_date]

    LastMonthTS=AdjTimeSeries[AdjTimeSeries.index>=start_date]
    LastMonthTS=LastMonthTS[LastMonthTS.index<=end_date]

    plottitle=monthselection+' 2020 Market Summary, NASDAQ:'+symbol
    p = figure(title=plottitle, plot_width=800,y_range=(0, LastMonthTS.max()[0]*1.5), tools=["xpan","ypan"],#plot_height=300
            x_axis_type="datetime", x_axis_location="below") #x_range
    
    prices=[]
    dates=[]
    label=[]
    colors=[]
    for key in projectpath.keys():
        if projectpath.get(key) == 'Closingpr':
            p.line(LastMonthDates.tolist(), LastMonthTS.get('4. close').tolist(), line_color='red',alpha=.4,line_width=2,legend_label="Closing Price")
            #prices.append(LastMonthTS.get('4. close').tolist())
            # dates.append(LastMonthDates.tolist())
            # label.append('Closing Price')
            # colors.append('red')
        elif projectpath.get(key) == 'AdjClosingpr':
            p.line(LastMonthDates.tolist(), LastMonthTS.get('5. adjusted close').tolist(), line_color='green',alpha=.4,line_width=2,legend_label="Adjusted Closing Price")
            # prices.append(LastMonthTS.get('5. adjusted close').tolist())
            # dates.append(LastMonthDates.tolist())
            # label.append('Adjusted Closing Price')
            # colors.append('blue')
        elif projectpath.get(key) == 'Openpr':
            p.line(LastMonthDates.tolist(), LastMonthTS.get('1. open').tolist(), line_color='blue',alpha=.4,line_width=2,legend_label="Opening Price")
            # prices.append(LastMonthTS.get('1. open').tolist())
            # dates.append(LastMonthDates.tolist())
            # label.append('Opening Price')
            # colors.append('green')
    
    # p.multi_line(xs=dates,ys=prices,color=colors, alpha=.5)
    # legend = Legend(items=[LegendItem(label="Closing Price", index=0),LegendItem(label="Adjusted Closing Price", index=1),LegendItem(label="Opening Price", index=2)])
        
    # p.add_layout(legend)
    p.yaxis.axis_label = 'Price (USD)'
    p.xaxis.axis_label = 'Date'
    p.xaxis.formatter=DatetimeTickFormatter(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],
    )
    script, div = components(p)
    return render_template('graph.html', script=script, div=div)
    
if __name__ == '__main__':
  app.run(port=5000, debug=True)