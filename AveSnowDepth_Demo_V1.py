####################################################################################
####################################################################################
####################################################################################
## Single Location Fuction
####################################################################################
####################################################################################
####################################################################################

def main_muti():
    from multiprocess import Process
    from multiprocess.pool import Pool
    from itertools import starmap
    import numpy as np
    import netCDF4
    import pandas as pd
    import os
    import csv
    from time import perf_counter

    ####################################################################################
    ####################################################################################
    ## Find Closest point fuction
    ####################################################################################
    ####################################################################################
    def geo_idx_fuction(dd, dd_array):

        """
         search for nearest decimal degree in an array of decimal degrees and return the index.
         np.argmin returns the indices of minium value along an axis.
        """
        geo_idx = (np.abs(dd_array - dd)).argmin()
        return geo_idx

    ####################################################################################
    ####################################################################################
    ## Find alternative closest point fuction(only the closest point data is empty)
    ####################################################################################
    ####################################################################################
    def geo_idx_alternative_closest_fuction(dd, dd_array, k):
        """
         search for alternative closest decimal degree in an array of decimal degrees and return the index.
         np.argpartition returns an array of indices of the same shape as a that index data along the given axis in partitioned order.
         subtract dd from all values in dd_array, take absolute value and find index of alternative closest point.
        """
        geo_idx_alternative_closest_fuction = np.argpartition(np.abs(dd_array - dd), k)[k]
        return geo_idx_alternative_closest_fuction

    ####################################################################################
    ####################################################################################
    ## Write the data to csv function
    ####################################################################################
    ####################################################################################
    def write_data_to_csv(filename_NSRDB, filename_NSRDB_Snow, Snow_depth_hourly):
        l = []
        i = 0

        ####################################################################################
        ## Remove exist file
        ####################################################################################
        try:
            os.remove(filename_NSRDB_Snow)
        except:
            pass

        ####################################################################################
        ## Write the data
        ####################################################################################
        finally:
            with open(filename_NSRDB,'rt') as f:
                cr = csv.reader(f)
                for row in cr:
                    if i == 0 or i == 1:
                        #print(row)
                        l.append(row)
                    elif i == 2:
                        row.append(np.ndarray.item(np.array(['Snow depth'])))
                        l.append(row)
                    else:
                        row.append(np.ndarray.item(np.array(Snow_depth_hourly[i-3])))
                        l.append(row)
                    i = i + 1
            with open(filename_NSRDB_Snow, 'wt', newline='') as f2:
                writer = csv.writer(f2)
                for rowdict in l:
                    writer.writerow(rowdict)

    ####################################################################################
    ####################################################################################
    ## Compute the snow depth Fuction
    ####################################################################################
    ####################################################################################
    def get_snowDepth(end_year,year,county,in_lat,in_lon):
        # Int, Int, pandas dataframe
        path_NSIDC = '/Snow_Depth_data'
        #path_NSRDB = 'F:/SAGES/NSRDB_SOLAR/'
        Depth_martix = np.zeros((365,year))

        ####################################################################################
        ## Iter to compute the ave snow depth
        ####################################################################################
        for i in range(year):
            nci = netCDF4.Dataset(path_NSIDC + '4km_SWE_Depth_WY' + str(end_year-i) + '_v01.nc')
            lats = nci.variables['lat'][:]
            lons = nci.variables['lon'][:]
            Depths = nci.variables['DEPTH'][:]
            lat_idx = geo_idx_fuction(in_lat, lats)
            lon_idx = geo_idx_fuction(in_lon, lons)
            Depth = Depths[:,lat_idx,lon_idx]/float(10)
            if str(Depth[32]) == '--':
                k = 1
                while str(Depth[32]) == '--':
                    lat_idx = geo_idx_alternative_closest_fuction(in_lat, lats, k)
                    lon_idx = geo_idx_alternative_closest_fuction(in_lon, lons, k)
                    k = k + 1
                    Depth = Depths[:,lat_idx,lon_idx]
                Depth = Depths[:,lat_idx,lon_idx]/float(10)

            if len(Depth)==366:
                Depth_martix[:,i] =  np.concatenate((Depth[0:151],Depth[152:366]))
            else:
                Depth_martix[:,i] = Depth[0:365]

        Snow_depth_start_OCT = np.average(Depth_martix,axis = 1)
        Snow_depth = np.concatenate((Snow_depth_start_OCT[92:366],Snow_depth_start_OCT[0:92]))

        Snow_depth_hourly = np.zeros((8760,1))#[0]*8760
        for i in range(0,len(Snow_depth)):
            for ii in range(0,24):
                Snow_depth_hourly[(i*24+ii),0] = Snow_depth[i];
        #print(Snow_depth_hourly)
        filename_NSRDB = path_NSRDB + county + '.csv'
        filename_NSRDB_Snow = path_NSRDB + county + '_snow.csv'
        write_data_to_csv(filename_NSRDB, filename_NSRDB_Snow, Snow_depth_hourly)
        #print(f'Finish write the {county} file ')
        return Snow_depth

    year = 10
    end_year = 2021
    location_data_excel = pd.read_excel('F:/SAGES/NSIDC/Location_test.xlsx')
    location_datas = pd.DataFrame(location_data_excel, columns=['County', 'BA',
                                                               'Longitude','Latitude','Fixed_tilt_30','1_axis_tracking','Fixed_tilt_45','Fixed_tilt_20'])
    i = 0;
    pd.options.mode.chained_assignment = None #close the warning information
    for (County) in location_datas['County']:
        location_datas['County'][i] = County.replace(" ", "")
        i = i + 1;
    print('Total location:', len(location_datas))
    with Pool(7) as pool:
        items = []
        for i in range(len(location_datas)):
            county = location_datas['County'][i]
            in_lat = location_datas['Latitude'][i]
            in_lon = location_datas['Longitude'][i]
            items.append((end_year,year,county,in_lat,in_lon))

        results = pool.starmap_async(get_snowDepth, items).get()
        #print(f'Got result: {result}', flush=True)

####################################################################################
####################################################################################
####################################################################################
## Single Location Fuction
####################################################################################
####################################################################################
####################################################################################

def main_single():
    ####################################################################################
    ####################################################################################
    ## Import package
    ####################################################################################
    ####################################################################################
    import numpy as np
    import netCDF4
    import pandas as pd
    import os

    ####################################################################################
    ####################################################################################
    ## Get the input value
    ####################################################################################
    ####################################################################################
    in_lon = float(e2.get())
    in_lat = float(e1.get())
    end_year = int(e3.get())
    year = int(e4.get())

    ####################################################################################
    ####################################################################################
    ## Find Closest point fuction
    ####################################################################################
    ####################################################################################
    def geo_idx_fuction(dd, dd_array):

        """
         search for nearest decimal degree in an array of decimal degrees and return the index.
         np.argmin returns the indices of minium value along an axis.
        """
        geo_idx = (np.abs(dd_array - dd)).argmin()
        return geo_idx

    ####################################################################################
    ####################################################################################
    ## Find alternative closest point fuction(only the closest point data is empty)
    ####################################################################################
    ####################################################################################
    def geo_idx_alternative_closest_fuction(dd, dd_array, k):

        """
         search for alternative closest decimal degree in an array of decimal degrees and return the index.
         np.argpartition returns an array of indices of the same shape as a that index data along the given axis in partitioned order.
         subtract dd from all values in dd_array, take absolute value and find index of alternative closest point.
        """

        geo_idx_alternative_closest_fuction = np.argpartition(np.abs(dd_array - dd), k)[k]
        return geo_idx_alternative_closest_fuction

    ####################################################################################
    ####################################################################################
    ## Compute the snow depth Fuction
    ####################################################################################
    ####################################################################################
    def get_snowDepth(end_year,year,in_lat,in_lon):
        # Int, Int, pandas dataframe
        path_NSIDC = '/Snow_Depth_data/'
        #path_NSRDB = 'F:/SAGES/NSRDB_SOLAR/'
        Depth_martix = np.zeros((365,year))

        ####################################################################################
        ## Iter to compute the ave snow depth
        ####################################################################################
        for i in range(year):
            nci = netCDF4.Dataset(current_path + path_NSIDC + '4km_SWE_Depth_WY' + str(end_year-i) + '_v01.nc')
            lats = nci.variables['lat'][:]
            lons = nci.variables['lon'][:]
            Depths = nci.variables['DEPTH'][:]
            lat_idx = geo_idx_fuction(in_lat, lats)
            lon_idx = geo_idx_fuction(in_lon, lons)
            Depth = Depths[:,lat_idx,lon_idx]/float(10)
            if str(Depth[32]) == '--':
                k = 1
                while str(Depth[32]) == '--':
                    lat_idx = geo_idx_alternative_closest_fuction(in_lat, lats, k)
                    lon_idx = geo_idx_alternative_closest_fuction(in_lon, lons, k)
                    k = k + 1
                    Depth = Depths[:,lat_idx,lon_idx]
                Depth = Depths[:,lat_idx,lon_idx]/float(10)

            if len(Depth)==366:
                Depth_martix[:,i] =  np.concatenate((Depth[0:151],Depth[152:366]))
            else:
                Depth_martix[:,i] = Depth[0:365]

        Snow_depth_start_OCT = np.average(Depth_martix,axis = 1)
        Snow_depth = np.concatenate((Snow_depth_start_OCT[92:366],Snow_depth_start_OCT[0:92])).reshape(365,1)

        Snow_depth_hourly = np.zeros((8760,1))#[0]*8760
        return Snow_depth,Snow_depth_hourly


    Snow_depth,Snow_depth_hourly = get_snowDepth(end_year,year,in_lat,in_lon)
    #print(Snow_depth)

    ####################################################################################
    ####################################################################################
    ## Refresh the window
    ####################################################################################
    ####################################################################################
    location_verification(Snow_depth)

####################################################################################
####################################################################################
####################################################################################
## Main
####################################################################################
####################################################################################
####################################################################################

if __name__ == "__main__":
    ####################################################################################
    ####################################################################################
    ## Import package
    ####################################################################################
    ####################################################################################
    import time
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import tkinter as tk
    import webbrowser
    import pathlib
    from functools import partial
    import mpl_toolkits.basemap
    from mpl_toolkits.basemap import Basemap
    from pyproj import _datadir, datadir
    from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
    from matplotlib.patches import Polygon
    from tkinter import *
    from tkinter import ttk

    ####################################################################################
    ####################################################################################
    ## Change the Path name Fuction
    ####################################################################################
    ####################################################################################
    def dict_to_string(dict_name):
        dict_name_str = (dict_name).replace("\\","/")
        return dict_name_str

    ####################################################################################
    ####################################################################################
    ## INSERT Link Fuction
    ####################################################################################
    ####################################################################################
    def personal_website(url):
        webbrowser.open_new_tab(url)

    ####################################################################################
    ####################################################################################
    ## Copy the data to clipboard Fuction
    ####################################################################################
    ####################################################################################
    def copy2clipboard(SnowDepth_np_array):
        group1.clipboard_clear()
        df_clipboard = pd.DataFrame(SnowDepth_np_array)
        df_clipboard.columns = ['Snow_Depth']
        df_clipboard.to_clipboard(index=False,header=False)

    ####################################################################################
    ####################################################################################
    ## Pop developing message Fuction
    ####################################################################################
    ####################################################################################
    def pop_developing_message():
        #Toplevel for the developing message
        Dev_message = Toplevel(root)
        Dev_message.title("Message")

        # sets the geometry of toplevel
        Dev_message.geometry("200x200")

        # A Label widget to show in toplevel
        Label(Dev_message,text ="This feature under developing!").pack()

    ####################################################################################
    ####################################################################################
    ## location Verification Fuction
    ####################################################################################
    ####################################################################################
    def location_verification(Snow_depth):
        # Map (long, lat) to (x, y) for plotting
        long = e2.get()#long, lati
        lati = e1.get()#long, lati

        ####################################################################################
        ## Group 2 Location Map
        ####################################################################################
        group2 = LabelFrame(root, text='Location Map', padx=10, pady=5)
        group2.grid(row=0, column=0, padx=10, pady=5,sticky = 'n')
        fig = plt.figure(figsize=(5.75, 4.3125))
        m = Basemap(projection='lcc', resolution=None,llcrnrlon=-119,llcrnrlat=22,urcrnrlon=-64,urcrnrlat=49,
            width=8E6, height=8E6,
            lat_1=33,lat_2=45,lon_0=-95)
        m.etopo(scale=0.5, alpha=0.5)
        x, y = m(e2.get(), e1.get())
        plt.plot(x, y, 'ok', markersize=5)
        plt.text(x, y, ' Point', fontsize=12)
        canvas = FigureCanvasTkAgg(fig, master=group2)
        canvas.get_tk_widget().grid(row=0,column=4,columnspan=3,rowspan=20)

        ####################################################################################
        ## Group 3 Average Snow Depth Plot
        ####################################################################################
        day = []
        for iiii in range(365):
            day.append(iiii+1)

        group3 = LabelFrame(root, text='Average Snow Depth Plot', padx=10, pady=5)
        group3.grid(row=1, column=0, padx=10, pady=5,sticky = 's')
        fig2 = plt.figure(figsize=(5.75, 4.3125))
        plt.plot(day, Snow_depth, color ='tab:blue', markersize=5)
        plt.xlabel('Day')
        plt.ylabel('Average Snow Depth (cm)')
        #plt.title('Average Snow Depth Plot')
        canvas2 = FigureCanvasTkAgg(fig2, master=group3);
        canvas2.get_tk_widget().grid(row=30,column=0,columnspan=3,rowspan=20);

        ####################################################################################
        ## Group 4 Data Table
        ####################################################################################
        group4 = LabelFrame(root, text='Average Snow Depth Data', padx=10, pady=5)
        group4.grid(row=0, rowspan=2, column=1, sticky='n',padx=10, pady=5)
        month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        month_name = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        data_array = np.zeros((365,4))
        day_th = 0
        for month_th in range(12):
            for month_day_th in range(month_days[month_th]):
                data_array[day_th,0] = int(day_th+1)
                data_array[day_th,1] = int(month_th + 1)
                data_array[day_th,2] = int(month_day_th + 1)
                data_array[day_th,3] = (Snow_depth[day_th,0])
                day_th = day_th + 1
        df = pd.DataFrame(data_array)
        df.columns = ['Days_Order', 'Month', 'Day', 'Snow_Depth']
        n_rows = 365
        n_cols = 4
        column_names = df.columns

        table1_frame = Frame(group4)
        table1_frame.pack()
        table1_scroll = Scrollbar(table1_frame)
        table1_scroll.pack(side= RIGHT,fill=Y)

        table1 = ttk.Treeview(table1_frame,yscrollcommand=table1_scroll.set, xscrollcommand =table1_scroll.set,height=45)
        table1.pack()

        # Scroll bar
        table1_scroll.config(command=table1.yview)
        table1_scroll.config(command=table1.xview)

        #Define column
        table1['columns'] = ('Day_Order','Month','Day', 'Snow_Depth')

        #Format column
        table1.column("#0", width=0,  stretch=NO)
        table1.column('Day_Order',anchor=CENTER, width=80)
        table1.column('Month',anchor=CENTER,width=120)
        table1.column('Day',anchor=CENTER, width=80)
        table1.column('Snow_Depth',anchor=CENTER,width=120)

        #Create Headings
        table1.heading("#0",text="",anchor=CENTER)
        table1.heading('Day_Order',text="Day Id",anchor=CENTER)
        table1.heading("Month",text="Month",anchor=CENTER)
        table1.heading('Day',text="Day",anchor=CENTER)
        table1.heading("Snow_Depth",text="Snow Depth(cm)",anchor=CENTER)

        #Add data
        for iiiI in range(365):
            table1.insert(parent='',index='end',iid=iiiI,text='',values=(int(data_array[iiiI,0]),int(data_array[iiiI,1]),int(data_array[iiiI,2]),round(data_array[iiiI,3], 2)))
        table1.pack()

    ####################################################################################
    ####################################################################################
    ## Intial Set for the main window
    ####################################################################################
    ####################################################################################

    ####################################################################################
    ## Intial Set for snow depth in [cm]
    ####################################################################################
    Snow_depth = np.array([[
     11.21,10.86,10.69,10.49,10.16, 9.46,10.19,10.47,10.59, 9.67,10.86,10.21,
     10.73,10.83,11.76,11.5 ,11.53,12.54,12.33,11.81,12.32,12.2 ,13.11,13.3 ,
     13.34,13.35,12.98,13.93,13.63,13.65,14.21,14.59,14.58,15.34,16.25,15.78,
     16.05,15.4 ,16.37,16.32,16.93,18.18,18.17,18.4 ,18.14,17.6 ,17.87,17.73,
     18.31,17.33,17.93,20.52,21.53,20.95,21.17,21.74,21.48,21.32,20.27,21.43,
     21.23,21.39,21.39,22.72,21.8 ,21.5 ,19.91,18.36,17.56,16.24,15.66,16.12,
     14.65,14.11,14.86,14.92,14.23,14.68,13.35,13.27,12.43,12.56,12.03,10.81,
     10.52, 9.9 , 8.9 , 8.51, 8.  , 7.54, 7.39, 7.25, 7.46, 8.6 , 8.06, 7.36,
      5.63, 4.98, 4.88, 4.52, 5.22, 5.2 , 5.1 , 5.02, 6.36, 6.23, 6.31, 6.04,
      6.13, 4.9 , 4.46, 3.45, 2.75, 1.59, 1.2 , 0.95, 0.23, 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ,
      0.  , 0.  , 0.  , 0.  , 0.03, 0.58, 0.49, 0.6 , 0.65, 0.62, 0.72, 0.64,
      0.9 , 0.65, 0.52, 0.4 , 0.28, 0.28, 0.11, 0.26, 0.09, 0.28, 0.22, 0.21,
      0.27, 0.8 , 2.32, 1.95, 2.07, 1.84, 1.88, 1.7 , 1.69, 1.59, 1.41, 1.35,
      1.06, 1.15, 1.37, 0.98, 0.89, 1.01, 1.16, 1.  , 1.34, 1.46, 2.27, 2.48,
      2.47, 3.33, 4.42, 3.45, 3.58, 3.55, 4.4 , 6.67, 7.97, 6.84, 6.09, 6.63,
      6.02, 6.14, 8.18, 6.37, 6.38, 6.14, 5.9 , 5.73, 5.85, 6.85, 6.67, 6.79,
      8.69,10.37,11.04,10.49,11.2 ]]).reshape(365, 1)


    ####################################################################################
    ## Get current path as str
    ####################################################################################
    current_path = dict_to_string(str(pathlib.Path(__file__).parent.resolve()))

    ####################################################################################
    ## Intial the main window
    ####################################################################################
    root = Tk()
    root.iconbitmap("snowflake-52-512.ico")
    root.title('AveSnowDepth V1.0')
    root.geometry("1600x1000")

    ####################################################################################
    ## Group 1
    ####################################################################################

    ## Creat new window
    group1 = LabelFrame(root, text='Input', padx=10, pady=5)
    group1.pack(padx=10, pady=10)
    group1.grid(row=0, column=2, padx=10, pady=5,sticky='n')

    ## Creat new sub window
    sub_group = LabelFrame(group1, text='Processing Method', padx=10, pady=5)
    sub_group.pack(padx=10, pady=10)
    sub_group.grid(row=0, column=0, sticky='ew',padx=10, pady=5)
    LANGS = [('Single', 1),
                ('Multiple (Under Developing)', 2)]
    v = IntVar()
    v.set(1)
    for lang, num in LANGS:
        b = Radiobutton(sub_group, text=lang, variable=v, value=num)
        b.pack(anchor=W)

    ## Creat new sub window
    sub_group2 = LabelFrame(group1, text='Input Values', padx=10, pady=5,height=1, width=5)
    sub_group2.grid(row=1, column=0,columnspan=2, sticky='ew', padx=10, pady=5)
    Label(sub_group2, text='Latitude:').grid(row=2, column=0)
    Label(sub_group2, text='Longitude:').grid(row=3, column=0)
    Label(sub_group2, text='End Year:').grid(row=4, column=0)
    Label(sub_group2, text='Time distance:').grid(row=5, column=0)

    lat = StringVar()
    lon = StringVar()
    end_year = StringVar()
    time_length = StringVar()

    #lat.set(45.00457083)
    #lon.set(-93.47681168)
    #end_year.set(2021)
    #time_length.set(10)

    e1 = Entry(sub_group2, textvariable=lat)#, textvariable=lat
    e2 = Entry(sub_group2, textvariable=lon)#, textvariable=lon
    e3 = Entry(sub_group2, textvariable=end_year)#, textvariable=end_year
    e4 = Entry(sub_group2, textvariable=time_length)#, textvariable=time_length

    e1.insert(0, 45.00457083)
    e2.insert(0, -93.47681168)
    e3.insert(0, 2021)
    e4.insert(0, 10)

    e1.grid(row=2, column=1, padx=10, pady=5)
    e2.grid(row=3, column=1, padx=10, pady=5)
    e3.grid(row=4, column=1, padx=10, pady=5)
    e4.grid(row=5, column=1, padx=10, pady=5)

    sub_group3 = LabelFrame(group1, text='Single Location Option', padx=10, pady=5,height=1, width=5)
    sub_group3.grid(row=6, column=0, sticky='ew',padx=10, pady=5)
    b1 = Button(sub_group3, text='Verify location', height=1, width=20,command=partial(location_verification, Snow_depth)).grid(row=0, column=0, sticky=N,padx=10, pady=5)
    b2 = Button(sub_group3, text='Single location', height=1, width=20, command=main_single).grid(row=1, column=0,sticky=N, padx=10, pady=5)
    b3 = Button(sub_group3, text='Copy Data to Clipboard', height=1, width=20,command=partial(copy2clipboard, Snow_depth)).grid(row=2, column=0,sticky=N, padx=10, pady=5)
    #root.window_create(INSERT, window=b1),(e2.get()), (e1.get())

    sub_group4 = LabelFrame(group1, text='Mult-location Option(Under Dev)', padx=10, pady=5,height=1, width=5)
    sub_group4.grid(row=6, column=1, sticky='ew',padx=10, pady=5)
    b4 = Button(sub_group4, text='Location file explore',height=1, width=20, command=pop_developing_message).grid(row=0, column=0, sticky=E, padx=10, pady=5)
    b5 = Button(sub_group4, text='Multiple location',height=1, width=20, command= pop_developing_message).grid(row=1, column=0, sticky=E, padx=10, pady=5)
    b6 = Button(sub_group4, text='Open Results Folder',height=1, width=20, command= pop_developing_message).grid(row=2, column=0, sticky=E, padx=10, pady=5)

    ####################################################################################
    ## Group 2 Location Map
    ####################################################################################

    ## Creat new window
    group2 = LabelFrame(root, text='Location Map', padx=10, pady=5)
    group2.grid(row=0, column=0, padx=10, pady=5,sticky='n')
    fig = plt.figure(figsize=(5.75, 4.3125))
    m = Basemap(llcrnrlon=-119,llcrnrlat=22,urcrnrlon=-64,urcrnrlat=49,projection='lcc', resolution=None,
            width=8E6, height=8E6, lat_1=33,lat_2=45,lon_0=-95)
    m.etopo(scale=0.5, alpha=0.5)
    long = e2.get()
    lati = e1.get()
    x, y = m(e2.get(), e1.get())
    plt.plot(x, y, 'ok', markersize=5)
    plt.text(x, y, ' Point', fontsize=12);
    canvas = FigureCanvasTkAgg(fig, master=group2);
    canvas.get_tk_widget().grid(row=0,column=0,columnspan=3,rowspan=20);

    ####################################################################################
    ## Group 3 Average Snow Depth Plot
    ####################################################################################
    day = []
    for iiii in range(365):
        day.append(iiii+1)

    ## Creat new window
    group3 = LabelFrame(root, text='Average Snow Depth Plot', padx=10, pady=5)
    group3.grid(row=1, column=0, padx=10, pady=5,sticky = 's')
    fig2 = plt.figure(figsize=(5.75, 4.3125))
    plt.plot(day, Snow_depth, color ='tab:blue', markersize=5)
    plt.xlabel('Day')
    plt.ylabel('Average Snow Depth (cm)')
    #plt.title('Average Snow Depth Plot')
    canvas2 = FigureCanvasTkAgg(fig2, master=group3);
    canvas2.get_tk_widget().grid(row=30,column=0,columnspan=3,rowspan=20);

    ####################################################################################
    ## Group 4 Data Table
    ####################################################################################

    ## Creat new window
    group4 = LabelFrame(root, text='Average Snow Depth Data', padx=10, pady=5)
    group4.grid(row=0, rowspan=2, column=1, sticky='n',padx=10, pady=5)

    ## Month and Days info
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    month_name = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    data_array = np.zeros((365,4))
    day_th = 0
    for month_th in range(12):
        for month_day_th in range(month_days[month_th]):
            data_array[day_th,0] = int(day_th+1)
            data_array[day_th,1] = int(month_th + 1)
            data_array[day_th,2] = int(month_day_th + 1)
            data_array[day_th,3] = (Snow_depth[day_th,0])
            day_th = day_th + 1
    df = pd.DataFrame(data_array)
    df.columns = ['Days_Order', 'Month', 'Day', 'Snow_Depth']
    n_rows = 365
    n_cols = 4
    column_names = df.columns

    ## Creat new table
    table1_frame = Frame(group4)
    table1_frame.pack()
    table1_scroll = Scrollbar(table1_frame)
    table1_scroll.pack(side= RIGHT,fill=Y)

    table1 = ttk.Treeview(table1_frame,yscrollcommand=table1_scroll.set, xscrollcommand =table1_scroll.set,height=45)
    table1.pack()

    ## Scrollbar
    table1_scroll.config(command=table1.yview)
    table1_scroll.config(command=table1.xview)

    #define column
    table1['columns'] = ('Day_Order','Month','Day', 'Snow_Depth')
    # format column
    table1.column("#0", width=0,  stretch=NO)
    table1.column('Day_Order',anchor=CENTER, width=80)
    table1.column('Month',anchor=CENTER,width=120)
    table1.column('Day',anchor=CENTER, width=80)
    table1.column('Snow_Depth',anchor=CENTER,width=120)
    #Create Headings
    table1.heading("#0",text="",anchor=CENTER)
    table1.heading('Day_Order',text="Day Id",anchor=CENTER)
    table1.heading("Month",text="Month",anchor=CENTER)
    table1.heading('Day',text="Day",anchor=CENTER)
    table1.heading("Snow_Depth",text="Snow Depth(cm)",anchor=CENTER)
    #add data
    for iiiI in range(365):
        table1.insert(parent='',index='end',iid=iiiI,text='',values=(int(data_array[iiiI,0]),int(data_array[iiiI,1]),int(data_array[iiiI,2]),round(data_array[iiiI,3], 2)))
    table1.pack()

    ####################################################################################
    ## Group 5 information
    ####################################################################################
    group5 = LabelFrame(root, text='Information', padx=10, pady=5)
    group5.grid(row=1,  column=2, sticky='sw',padx=10, pady=5)

    sub_group_4_group5_1 = LabelFrame(group5, text='Single Location Option', padx=10, pady=5)
    sub_group_4_group5_1.grid(row=0, column=0,columnspan=2, padx=10, pady=5)#sticky='nw',

    text_single_location = Text(sub_group_4_group5_1, height=15, width = 52,borderwidth=1, relief="solid")
    text_single_location.pack()

    ####################################################################################
    ## Text Information
    Availble_data_info = '''The dataset comes from NASA EarthData's [Daily 4 km Gridded SWE and Snow Depth from Assimilated In-Situ and Modeled Data over the Conterminous US]. This dataset contains snowfall data for the continental United States from 1982 to 2021. So, the software only supports calculating the average snow depth data from 1983 to 2021.\n'''
    Verify_Location_Info = '''\nVerify Location option is used to check whether the input longitude & latitude location is in the US.\n'''
    Single_Location_Info = '''\nSingle Location option is used to compute the average snow depth through the given location in the US.\n'''
    Copy_Info = '''\nCopy data to Clipboard option used to copy the average snow depth data to the clipboard for the given location in the US.\n'''
    General_info = '''\nThe Location Map is used to check whether the input latitude and longitude are in the continental United States.
                    \nThe Average Snow Depth Plot shows the average snowfall from the first day of the year to the 365th day of the year (the calculation process ignores the snowfall data of February 29 in leap years).
                    \nThe Average Snow Depth Data Table shows the average snowfall data for each day of the month.'''

    ## Instert Text Information
    text_single_location.insert(tk.END, Availble_data_info)
    text_single_location.insert(tk.END, Verify_Location_Info)
    text_single_location.insert(tk.END, Single_Location_Info)
    text_single_location.insert(tk.END, Copy_Info)
    text_single_location.insert(tk.END, General_info)
    text_single_location.configure(state='disabled')

    ## Copyright Information
    sub_group_4_group5_2 = LabelFrame(group5, text='Copyright Information', padx=10, pady=5)
    sub_group_4_group5_2.grid(row=1, column=0, columnspan=2, padx=10, pady=5)#sticky='nw',

    text_Copyright = Text(sub_group_4_group5_2, height=2, width = 52,borderwidth=1, relief="solid")
    text_Copyright.pack()
    Copyright_Info = '''Jiaqun Wang wrote this software. The author reserves all copyrights.\n'''
    text_Copyright.insert(tk.END, Copyright_Info)
    text_Copyright.configure(state='disabled')

    ####################################################################################
    ## Link Information

    ## Creat new window
    sub_group_4_group5_3 = LabelFrame(group5, text='Contact Information', padx=10, pady=5)
    sub_group_4_group5_3.grid(row=2, column=0, padx=10, pady=5, sticky='nw')

    ## Linkedin
    linkedin = Label(sub_group_4_group5_3, text="Linkedin",font=('Helveticabold', 15), fg="blue", cursor="hand2")
    linkedin .pack()
    linkedin .bind("<Button-1>", lambda e: personal_website("https://www.linkedin.com/in/jiaqun-wang/"))

    ## Creat new window
    sub_group_4_group5_4 = LabelFrame(group5, text='Data Source', padx=10, pady=5)
    sub_group_4_group5_4.grid(row=2, column=1, padx=10, pady=5, sticky='ne')

    ## Source Link
    link_Earth_Data = Label(sub_group_4_group5_4, text="EarthData",font=('Helveticabold', 15), fg="blue", cursor="hand2")
    link_Earth_Data.pack()
    link_Earth_Data.bind("<Button-1>", lambda e: personal_website("https://nsidc.org/data/nsidc-0719/versions/1"))


    mainloop()

    #start_time = time.perf_counter()
    #end_time = time.perf_counter()
    #print(f'It took {end_time- start_time :0.2f} second(s) to complete.')
