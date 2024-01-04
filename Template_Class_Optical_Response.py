from plotly import graph_objs as go
from plotly import express as px
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
import pandas as pd
import pywt.data
from scipy import*
from datetime import datetime
from plotly.express.colors import sample_colorscale
from sklearn.preprocessing import minmax_scale
from sklearn.metrics import mean_absolute_percentage_error


pd.options.plotting.backend = "plotly"

#from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.signal import savgol_filter

class Optical_data_processing:
    def __init__(self, file_names: list, 
                 time_cycle: float,
                 res_time: float,
                 rec_time: float, 
                 parameter: list):
        
        self.file_names = file_names
        self.time_cycle = time_cycle
        self.res_time = res_time
        self.rec_time = rec_time
        self.parameter = parameter
    
    # Function for cleaning
    def PM100D_data(self) -> pd.DataFrame:
        dt = pd.DataFrame()
        for name, index in zip(self.file_names, np.arange(1, len(self.file_names)+1)):
            data_optic_response = pd.read_excel(f'{name}', header = None)
            data_optic_response['Timestamp'] = pd.to_timedelta(data_optic_response.iloc[15:, 2]).dt.total_seconds()
            data_optic_response['Timestamp'] = data_optic_response['Timestamp'] - data_optic_response.iloc[15, 5]
            dt[f'optic_response_{index}_Time_s'] = data_optic_response.iloc[15:, 5]
            dt[f'optic_response_{index}_Power_W'] = data_optic_response.iloc[15:, 3]
        dt = dt.reset_index().drop(['index'], axis=1)
        return dt

    # Function for cleaning
    def PM320_data(self) -> pd.DataFrame:
        dt = pd.DataFrame()
        for name, index in zip(self.file_names, np.arange(1, len(self.file_names)+1)):
            data_optic_response = pd.read_table(f'{name}', header = None, sep = r"\s+")
            dt[f'data_optic_response_{index}_Time'] = data_optic_response.index.values
            dt[f'data_optic_response_{index}_Power_dshape'] = data_optic_response.drop([0, 1, 2, 3, 4, 5, 7, 8], axis=1).rename(columns={6: 'Power_dshape'})
            #dt[f'data_optic_response_{index}_Power_ASE'] = data_optic_response.drop([0, 1, 2, 4, 5, 6, 7, 8], axis=1).rename(columns={3: 'Power_ASE'})
        return dt

    # Function for cleaning
    def old_PM100D_data(self) -> pd.DataFrame:
        dt = pd.DataFrame()
        for name, index in zip(self.file_names, np.arange(1, len(self.file_names)+1)):
            data_optic_response = pd.read_excel(f'{name}', header = None)
            data_optic_response = data_optic_response.iloc[23:, 0:2].rename(columns={0: 'Time_ms', 1: 'Power_W'}).reset_index().drop(['index'], axis=1)
            dt[f'optic_response_{index}_Time_ms'] = data_optic_response.iloc[:, 0]
            dt[f'optic_response_{index}_Power_W'] = data_optic_response.iloc[:, 1]
        return dt


    # Function for creating transmittance data PM100D
    def Transmittance_create_data(self, data: pd.DataFrame):
        Transmittance_norm = pd.DataFrame()
        for n, count in zip(np.arange(0, len(data.columns), 2), np.arange(1, len(data.columns)+1, 1)):
            Transmittance_norm[f'data_optic_response_{count}_Transmit'] = (data.iloc[:, n+1] - data.iloc[0, n+1]) / data.iloc[0, n+1]
        return Transmittance_norm

    # Function for creating time data
    def Time_create_data(self, data: pd.DataFrame):
        Time = pd.DataFrame()
        for n, count in zip(np.arange(0, len(data.columns), 2), np.arange(1, len(data.columns)+1, 1)):
            Time[f'{count}_Time'] = data.iloc[:, n]
        return Time
    

    ## QUICK PLOT
    def quick_plot_T(self, data: pd.DataFrame, Time_data) -> None:
        fig = go.Figure()
        
        # Making colour for each data
        color_dict = dict(zip(self.parameter[1:], sample_colorscale('Portland', minmax_scale(self.parameter[1:]))))

        # Creating line plots from data
        for param, count in zip(self.parameter[1:], np.arange(0, len(data.columns.values), 1)):
            fig.add_trace(go.Scattergl(x = Time_data.iloc[:, count].values / 60,  # minutes
                                        y = data.iloc[:, count], 
                                        name = str(f'{param} {self.parameter[0]}'),
                                        line_color = color_dict[param]))

        # Creating vertical rectangles
        for i in np.arange(self.rec_time +0.15, max(Time_data.max())/60, (self.res_time+self.rec_time)):
            fig.add_vrect(x0=i,
                        x1=i + self.res_time,
                        line_width=0,
                        fillcolor='grey',
                        opacity=0.1,
                        annotation_text='<i>NO<sub>2</sub></i>',
                        annotation_font_size=20,
                        annotation_textangle=270,
                        annotation_position='top',)

        # Updating layout data
        fig.update_layout(font_size = 15,
                        title = f"CNT film T=80%, S11=1.5 \u03BCm.  date: 15.11.23 <br>Mixture: Air (100 sccm) <--> 50 ppm NO<sub>2</sub> (50 sccm) + Air (50 sccm).",
                        title_x = 0.5,
                        legend_title = "Measurement<br>parameters",
                        legend_font_size = 15,
                        xaxis_title = "Time, min",
                        yaxis_title = "Transmittance, \u0394T / T<sub>0</sub></i>",
                        #yaxis_type = 'log',
                        plot_bgcolor = 'rgba(250,250,250,1)',
                        width = 1000,
                        height = 650,
                        )
        fig.add_shape(type="rect",
                    xref="paper",
                    yref="paper",
                    x0=0,
                    y0=0,
                    x1=1.0,
                    y1=1.0,
                line=dict(
                    color="black",
                    width=1,))    
        fig.show()