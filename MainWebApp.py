# IMPORTING THE LIBRARIES
import pandas as pd
import dash
# import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output
# import dash_core_components as dcc
from dash import dcc
import webbrowser
import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as pyo
import dash_bootstrap_components as dbc
# import dash_table as dt
from dash import dash_table as dt

# DECLARING GLOBAL VARIABLES
project_name=None
app=dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])




# DEFINING MY FUNCTIONS
def load_data():
	# It loads the data from the csv files
	print("My function load_data started")
	
	call_dataset_name= "Call_data.csv"
	service_dataset_name= "Service_data.csv"
	device_dataset_name= "Device_data.csv"
	
	global call_data
	call_data=pd.read_csv(call_dataset_name)
	
	global service_data
	service_data=pd.read_csv(service_dataset_name)
	
	global device_data
	device_data=pd.read_csv(device_dataset_name)
	
	
	# [{'label': '2019-06-20', 'value': '2019-06-20'} ]
	temp_list=sorted(call_data['date'].dropna().unique().tolist())
	
	global start_date_list
	start_date_list=[{'label': str(i) , 'value': str(i)} for i in temp_list]
	
	
	global end_date_list
	end_date_list= [{'label': str(i) , 'value': str(i)} for i in temp_list]
	
	
	temp_list=['Hourly', 'Daywise', 'Weekly']
	
	global report_type_list
	report_type_list=[{'label': str(i) , 'value': str(i)} for i in temp_list]
	
	
	print("End of the load_data function")

def open_browser():
	#This opens our webbrowser automatically
	webbrowser.open_new('http://127.0.0.1:8050/')


def create_app_ui():
	#Creating the WebApp UI of our project
	main_layout=html.Div(
		children=[ 
				html.Div(id="Main_Heading" , children=[
					html.H1(id="heading", children="CDR Analysis with Insights", style={'text-align': 'center', 'color': 'white'})],
					style={'background': 'black', 'padding': 10}),
				html.Br(),
				dcc.Tabs(id="Tabs", value="Call Analytics tool",children=[
					
					dcc.Tab(label="Call Analytics tool", id="Call Analytics tool", value="Call Analytics tool",
							children=[		
									dcc.Dropdown(id="start-date-dropdown",
															placeholder="Select Starting Date Here",
															value="2019-06-20",
															options=start_date_list),
									dcc.Dropdown(id="end-date-dropdown",
															placeholder="Select Ending Date Here",
															options=end_date_list,
															value="2019-06-25"),
									dcc.Dropdown(id="group-dropdown",
															placeholder="Select Group Here",
															multi=True),
									dcc.Dropdown(id="report-type-dropdown",
															placeholder="Select Report Type",
															options=report_type_list),
									html.Br(),
										
									dcc.Loading(
											html.Div(id="visualizattion-object" , children="Graph, Card, Datatable"))
								]),
					dcc.Tab(label="Device Analytics tool",id="Device Analytics tool",value="Device Analytics tool",
							children =[
									dcc.Dropdown(id="Device_Analytics_Dropdown" , 
															options=start_date_list,
															placeholder="Select Date"),
									html.Br(),
									dcc.Loading(
											html.Div(id = 'Device-Piechart', style={'marginLeft': '16%'})
									)
							]),
					dcc.Tab(label="Service Analytics tool",id="Service Analytics tool",value="Service Analytics tool",
						children=[
								dcc.Dropdown(id="Service-Analytics-Dropdown",
														options=start_date_list,
														placeholder="Select date"),
								html.Br(),
								dcc.Loading(
										html.Div(id = 'Service-Piechart', style={'marginLeft': '10%'})	
								)
						])]
				)					
		],style={'padding':35})
	
	return main_layout

@app.callback(
		Output("group-dropdown", "options"),
		[
			Input("start-date-dropdown" , "value"),
			Input("end-date-dropdown" , "value")
		]
	)
def update_groups(start_date,end_date):
	#Calling this function automatically using callback on selection of start date and end date
	print(f"Data type : {type(start_date)}")
	print(f"Data type : {type(end_date)}")
	print(f"Start date : {start_date}")
	print(f"End date : {end_date}")
	
	reformed_data=call_data[(call_data["date"] >= start_date) & (call_data["date"] <= end_date)]
	group_list=reformed_data["Group"].unique().tolist()
	print(group_list)
	
	group_list=[{"label": m  , "value": m} for m in group_list]
	
	return group_list
	
def create_card(title,content,color):
	# Creating the Cards
	card=dbc.Card(
		dbc.CardBody(
			[
				html.H4(title),
				html.Br(),
				html.Br(),
				html.H2(content),
				html.Br(),
			]
		),
		color=color,inverse=True
	)
	return (card)
	
	
@app.callback(
		Output('Service-Piechart', 'children'),
		[
			Input('Service-Analytics-Dropdown', 'value')
		]
	)
def update_service_piechart(date):
	#Creating the Service_Analytics_tool Piechart
	print(f"Service Date : {date}")
	
	new_data=service_data.groupby('FeatureEventDate')['FeatureName'].value_counts().reset_index(name="count")
	pie_data = new_data[new_data['FeatureEventDate']==date]
	labels = [i for i in pie_data['FeatureName']]
	values = [int(i) for i in pie_data['count']]
	
	figure = {'data' : [go.Pie(labels=labels, values=values)],
					'layout': go.Layout(height=850,width=850, autosize= False)}
	
	return dcc.Graph(figure = figure)
	

	
	

@app.callback(
		Output("Device-Piechart" , "children"),
		[
			Input("Device_Analytics_Dropdown" , "value")
		]
	)
def update_device_piechart(date):
	#Creating the Device_Analytics_tool Piechart
	print(f"Device Date :  {date}")
	
	dd_data = device_data.replace(to_replace = r'^Polycom(.*$)', value = 'Polycom', regex = True)
	dd_data = dd_data.replace(to_replace = r'(.*)Windows(.*$)', value = 'Windows', regex = True)
	dd_data = dd_data.replace(to_replace = r'^Yealink(.*$)', value = 'Yealink', regex = True)
	dd_data = dd_data.replace(to_replace = r'(.*)Android(.*$)', value = 'Android', regex = True)
	dd_data = dd_data.replace(to_replace = r'(.*)iPhone(.*$)', value = 'iPhone', regex = True)
	dd_data = dd_data.replace(to_replace = r'(.*)Aastra(.*$)', value = 'Aastra', regex = True)
	dd_data = dd_data.replace(to_replace = r'(.*)Mac(.*$)', value = 'Mac', regex = True)
	dd_data = dd_data.replace(to_replace = r'^Algo(.*$)', value = 'Algo', regex = True)
	dd_data = dd_data.replace(to_replace = r'^Linksys(.*$)', value = 'Linksys', regex = True)
	dd_data = dd_data.replace(to_replace = r'^CS2000(.*$)', value = 'CS2000 NGSS', regex = True)
	new_data = dd_data.groupby('DeviceEventDate')['UserDeviceType'].value_counts().reset_index(name="count")
	
	pie_data = new_data[new_data['DeviceEventDate'] == date]
	labels = [i for i in pie_data['UserDeviceType']]
	values = [int(i) for i in pie_data['count']]
	
	figure = {'data' : [go.Pie(labels=labels, values=values, hole =.3)],
				'layout' : go.Layout(height=800, width = 800, autosize = False)	
				}
	
	return dcc.Graph(figure = figure)
	

@app.callback(
		Output("visualizattion-object" , "children"),
		[
			Input("start-date-dropdown" , "value"),
			Input("end-date-dropdown" , "value"),
			Input("group-dropdown" , "value"),
			Input("report-type-dropdown" , "value")
		]
	)
def update_app_ui(start_date,end_date,group,report):
			# Creating the Graph , Cards , Datatable
			print(f"Data Type : {type(start_date)}")
			print(f"Start Date : {start_date}")
			
			print(f"Data Type : {type(end_date)}")
			print(f"End Date : {end_date}")
			
			print(f"Data Type : {type(group)}")
			print(f"Group : {group}")
			
			print(f"Data Type : {type(report)}")
			print(f"Report : {report}")
			
			# Filter the data as per the dropdowns
			
			call_analytics_data = call_data[(call_data["date"] >= start_date) & (call_data["date"] <= end_date)]
			
			if (group == [] or group is None):
				pass
			else:
				call_analytics_data = call_analytics_data[call_analytics_data["Group"].isin(group)]
			
			graph_data=call_analytics_data
			
			#Group the data based on dropdown
			if report=="Hourly":
				graph_data = graph_data.groupby("hourly_range")["Call_Direction"].value_counts().reset_index(name = "count")
				x="hourly_range"
				
				content=call_analytics_data["hourly_range"].value_counts().idxmax()
				title="Busiest Hour"
				
			elif report=="Daywise":
				graph_data = graph_data.groupby("date")["Call_Direction"].value_counts().reset_index(name = "count")
				x="date"
				
				content=call_analytics_data["date"].value_counts().idxmax()
				title="Busiest day"
			else:
				graph_data = graph_data.groupby("weekly_range")["Call_Direction"].value_counts().reset_index(name = "count")
				x="weekly_range"
				
				content=call_analytics_data["weekly_range"].value_counts().idxmax()
				title="Busiest Weekday"
				
			#Graph Section
			figure = px.area(
				graph_data,
				x=x,
				y="count",
				color = "Call_Direction",
				hover_data = ["Call_Direction" , "count"],
				template = "plotly_dark")
			
			figure.update_traces(mode = "lines+markers")
			
			#Card section
			total_calls=call_analytics_data["Call_Direction"].count()
			card_1=create_card("Total Calls",total_calls,"success")
			
			incoming_calls=call_analytics_data["Call_Direction"][call_analytics_data["Call_Direction"]=="Incoming"].count()
			card_2=create_card("Incoming Calls",incoming_calls,"primary")
			
			outgoing_calls=call_analytics_data["Call_Direction"][call_analytics_data["Call_Direction"]=="Outgoing"].count()
			card_3=create_card("Outgoing Calls",outgoing_calls,"primary")
			
			missed_calls=call_analytics_data["Missed Calls"][call_analytics_data["Missed Calls"]==3].count()
			card_4=create_card("Missed Calls",missed_calls,"danger")
			
			max_duration=call_analytics_data["duration"].max()
			card_5=create_card("Max Duration",f"{max_duration} min","dark")
			
			card_6=create_card(title,content,"primary")
			
			
			
			graphRow0=dbc.Row([dbc.Col(md=2),dbc.Col(id='card1', children=[card_1] , md=4) , dbc.Col(id='card2', children=[card_2] , md=4)])
			graphRow1=dbc.Row([dbc.Col(md=2),dbc.Col(id='card3', children=[card_3] , md=4) , dbc.Col(id='card4', children=[card_4] , md=4)])
			graphRow2=dbc.Row([dbc.Col(md=2),dbc.Col(id='card5', children=[card_5] , md=4) , dbc.Col(id='card6', children=[card_6] , md=4)])
			
			
			cardDiv = html.Div([graphRow0,html.Br(),graphRow1,html.Br(),graphRow2],
				style={'marginTop': 30, 'marginBottom': 30})
			
			#Datatable Section
			
			datatable_data=call_analytics_data.groupby(["Group", "UserID", "UserDeviceType"])["Call_Direction"].value_counts().unstack(fill_value=0).reset_index()
			
			if call_analytics_data["Missed Calls"][call_analytics_data["Missed Calls"] == 19].count() != 0:
				datatable_data["Missed Calls"] = call_analytics_data.groupby(["Group", "UserID", "UserDeviceType"])["Missed Calls"].value_counts().unstack()[3]
			else:
				datatable_data["Missed Calls"] = 0
			
			datatable_data["Total_call_duration"] = call_analytics_data.groupby(["Group", "UserID", "UserDeviceType"])["duration"].sum().tolist()
			
			
			datatable = dt.DataTable(
				id="table",
				columns=[{"name": i, "id": i} for i in datatable_data.columns],
				data=datatable_data.to_dict('records'),
        		page_current=0,
        		page_size=20,
        		page_action='native',
        		style_header={'backgroundColor': 'rgb(30, 30, 30)'},
				style_cell={'backgroundColor': 'rgb(50, 50, 50)','color': 'white'}
			)
				
				
			return [
				dcc.Graph(figure=figure),
				html.Br(),
				cardDiv,
				html.Br(),
				datatable
			
			]
			
			
# MAIN FUNCTION
def main():
	# Calling all the functions here
	print("Start of the main function")
	
	load_data()
	
	open_browser()
	
	global project_name
	project_name = "CDR Analysis with Insights"
	
	global app
	app.layout=create_app_ui()
	app.run_server() #Infinite loop
	
	
	print("End of the Main Function")
	
	
	global call_data , service_data , device_data 
	call_data=None
	device_data=None
	service_data=None
	project_name=None
	app=None
	
if __name__=='__main__':
	main()
	
	



