import math as m
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import interp1d
from plotly.subplots import make_subplots
import os
from statistics import mean
import wx


###############################################################################
################################### INTERFACE #################################
###############################################################################

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size = (1100,800))
        self.panel = MyPanel(self)
        self.SetIcon(wx.Icon("images/icon.png", wx.BITMAP_TYPE_PNG))

        
class MyPanel(wx.Panel):
    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)
        
        # "Input"-"Output" 
        self.titleInput = wx.StaticText(self, label = "Input:", pos = (10,5)) 
        self.titleOutput = wx.StaticText(self, label = "Output:", pos = (330,5))                   
        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.titleInput.SetFont(font)
        self.titleOutput.SetFont(font)
        self.output_blank = wx.StaticBitmap(self, size=(700,700), pos = (330,25))
        self.output_blank.SetBitmap(wx.Bitmap('images/blank.png'))
        
        
        # temperature input
        self.T = wx.StaticText(self, label = "T", pos = (10,33))                                   
        self.T_input = wx.TextCtrl(self, size=(50,-1), pos = (25,30))
        self.T_unit = wx.StaticText(self, label="°C", pos = (80,33))  
        self.T_input.SetValue('900')     #default value
        
        # component combobox (Cl, X, Y)
        self.component = wx.StaticText(self, label = "Component", pos = (120, 33))                 
        component_choices = ['Cl', 'X', 'Y']
        self.component_combobox = wx.ComboBox(self, choices = component_choices, pos = (195, 30))
        self.component_combobox.SetValue('Cl')      #default value
        
        # upload button
        self.natural_data = wx.StaticText(self, label = "Natural data:", pos = (10,66))      
        self.naturaldata_button = wx.Button(self, label="Upload", pos=(100,63))
        self.naturaldata_button.Bind(wx.EVT_BUTTON, self.OnClickUpload)        
                
        # Plot button 
        self.plot_button = wx.Button(self, label = "Plot", pos = (100, 96))  
        self.plot_button.Bind(wx.EVT_BUTTON, self.OnClickPlot) 
        
        # initial C
        self.InitialC = wx.StaticText(self, label = "Initial C =", pos = (10, 132))                        
        self.InitialC_input = wx.TextCtrl(self, size=(50,-1), pos = (110, 129))
        self.wt_unit1 = wx.StaticText(self, label = "wt.%", pos = (165, 132))
        
        # left boundary
        self.LeftBoundary = wx.StaticText(self, label = "Left Boundary =", pos = (10, 165))                 
        self.left_boundary_input = wx.TextCtrl(self, size=(50,-1), pos = (110, 163))
        self.wt_unit2 = wx.StaticText(self, label = "wt.%", pos = (165, 165))
        
        # right boundary
        self.RightBoundary = wx.StaticText(self, label = "Right Boundary =", pos = (10, 195))              
        self.right_boundary_input = wx.TextCtrl(self, size=(50,-1), pos = (110, 193))
        self.wt_unit3 = wx.StaticText(self, label = "wt.%", pos = (165, 195))
        
        #------------- Static Line ----------------
        self.hline = wx.StaticText(self, label="__________________________________________________", pos=(10,250))
                
        
        #dx (distance step)
        self.dx = wx.StaticText(self, label = "dx", pos = (10,300))                         
        self.dx_input = wx.TextCtrl(self, size=(50,-1), pos = (30,297))
        self.dx_unit = wx.StaticText(self, label="µm", pos = (85,300))
        self.dx_input.SetValue('0.5')     #default value
        
        #dt (time step)
        self.dt = wx.StaticText(self, label = "dt", pos = (140,300))                         
        self.dt_input = wx.TextCtrl(self, size=(50,-1), pos = (160,297))
        self.dt_unit = wx.StaticText(self, label="s", pos = (215,300))   
        self.dt_input.SetValue('8000')      #default value
        
        # interation input
        self.iteration = wx.StaticText(self, label = "Iteration", pos = (10,333))           
        self.iteration_input = wx.TextCtrl(self, size=(50,-1), pos = (60,330))
        self.iteration_input.SetValue('250')     #default value
        
        ###### Run modeling and plot figure 2 button #####
        self.Run_button = wx.Button(self, label = "Run!", pos = (150, 329))
        self.Run_button.Bind(wx.EVT_BUTTON, self.OnClickRun)

    def OnClickUpload(self, event):   
        # OPEN EXCEL FILE FOR USERS TO TYPE IN
        path = 'Upload_data.csv'
        os.startfile(path)
    
    def OnClickPlot(self, event):       
        #GET INPUT VALUE FROM USER
        T = int(self.T_input.GetValue())             #temperature in celsius degree (for user)
        gamma = 17.7        #angle between c-axis and traverse
        alfa1 = m.degrees(m.acos(m.sin(gamma*m.pi/180)*m.cos((45/180)*m.pi)))      #angle between a-axis and traverse
        alfa2 = alfa1
        D_a1 = 1.3*(10**(-9))*(m.e**(-216000/(8.314*(T+273.15))))*(10**12)  #Diffusion Coefficient along a-axis(um2/s) from Brenan
        D_a2 = 1.3*(10**(-9))*(m.e**(-216000/(8.314*(T+273.15))))*(10**12)  #Diffusion Coefficient along b-axis(um2/s) from Brenan
        D_c = 5.1*(10**(-5))*(m.e**(-290000/(8.314*(T+273))))*(10**12)      #Diffusion Coefficient along c-axis(um2/s);our data
        D_tra = (m.cos(alfa1/180*m.pi)**2)*D_a1 + (m.cos(alfa2/180*m.pi)**2)*D_a2 + ((m.cos(gamma/180*m.pi))**2)*D_c #Diffusion coefficient along traverse
        print('D_a1 =',D_a1)
        print()
        
        #NATURAL PROFILE FROM MEASUREMENT
        with open('Upload_data.csv', 'r') as A:
            x_nat = []                          #Distance (um) as x-axis
            c_nat = []                          #concentration (wt.%) as y-axis
            for item in A.readlines()[1:]:
                item1 = item.split(',')
                x_nat.append(int(item1[0]))
                c_nat.append(float(item1[1].strip()))
            length_nat = x_nat[-1]              #Total length of the measured profile (um)
            real_i = len(x_nat)                 #Total points in real profile
            uncert = 0.02                       #uncertainty of data (+/-,wt.%; by user)
            err = [uncert]*len(c_nat)           #uncertainty list
            
        #SET VARIABLES (by user)
        try:
            delta_x = float(self.dx_input.GetValue())                        #Distance step (um)   0.5
            delta_t = int(self.dt_input.GetValue())                          #Time step            8000
            t_itr = int(self.iteration_input.GetValue())                     #Time iteration       250
        except:
            pass
        
        try:
            x_model = []                            #location of model points
            i = 1
            while i <= length_nat:
                x_model.append(i)
                i += delta_x
            x_i = len(x_model)                      #Total model points
            print('x_i =',x_i)
            print()
        except:
            pass
        
        #SET INITIAL CONDITIONS (BY USERS)
        try:
            c_ini = float(self.InitialC_input.GetValue())              # c_ini = 0.96
            c_ini_arr = [c_ini]*(x_i -1)
        except:
            pass
        
        #SET BOUNDARY CONDITIONS (BY USERS): in this case, the first and last number of c array have fixed values
        try:
            c_bl = float(self.left_boundary_input.GetValue())               # =max(c_nat)  =1.56822
            c_br = float(self.right_boundary_input.GetValue())              # =c_ini       =0.96
        except:
            pass
        
        ######################################################################
        ############### PLOT NATURAL PROFILE FOR USER TO CHECK ###############
        ######################################################################
        fig = make_subplots(rows=2, cols=1,
                            subplot_titles=('     ','     '))
        
        
        ########## FIGURE 1 ##########
        try:
            fig.add_trace(go.Scatter(x=[1,1,length_nat, length_nat],
                                 y=[c_bl,c_ini,c_ini, c_br],
                                 name='Initial & Boundary Conditions',
                                 line_shape='linear',
                                 line=(dict(color='blue', dash='dash'))),
                      row=1, col=1)      #Initial and Boundary Conditions line
        except:
            pass
        fig.add_trace(go.Scatter(x=list(range(1,length_nat+1)),
                                 y=c_nat,
                                 error_y=dict(array=err, visible=True),
                                 mode="lines+markers",
                                 name="Natural Profile", 
                                 line=dict(color="black",dash="dash")),
                      row=1, col=1)                                               #Natural Profile and Error Bar
        fig.update_layout(margin=dict(l=30, r=30, t=30, b=30))
        
        fig.update_yaxes(title_text=self.component_combobox.GetValue()+" in Ap (wt%)", row=1, col=1)
        fig.update_xaxes(title_text="Distance (µm)", row=1, col=1)
        fig['layout'].update(width=700, height=700, autosize=False)
        
        if not os.path.exists("images"):
            os.mkdir("images")
        fig.write_image("images/single_ele_diffusion.png")
        
        # fig.show()
        # plot(fig,show_link = False)

        
        # Display figure 1
        self.single_ele_diff_pic = wx.StaticBitmap(self, size=(500, 500), pos = (330,25))
        self.single_ele_diff_pic.SetBitmap(wx.Bitmap('images/single_ele_diffusion.png'))

    def OnClickRun(self, event):
        ######## SET UP PROGRESS BAR ###
        self.gauge = wx.Gauge(self, range=100, pos=(10,400), size=(250,25), style=wx.GA_HORIZONTAL)

        ######## CHECK STABILITY #######
        #GET INPUT VALUE FROM USER
        T = int(self.T_input.GetValue())             #temperature in celsius degree (for user)
        gamma = 17.7        #angle between c-axis and traverse
        alfa1 = m.degrees(m.acos(m.sin(gamma*m.pi/180)*m.cos((45/180)*m.pi)))      #angle between a-axis and traverse
        alfa2 = alfa1
        D_a1 = 1.3*(10**(-9))*(m.e**(-216000/(8.314*(T+273.15))))*(10**12)  #Diffusion Coefficient along a-axis(um2/s) from Brenan
        D_a2 = 1.3*(10**(-9))*(m.e**(-216000/(8.314*(T+273.15))))*(10**12)  #Diffusion Coefficient along b-axis(um2/s) from Brenan
        D_c = 5.1*(10**(-5))*(m.e**(-290000/(8.314*(T+273))))*(10**12)      #Diffusion Coefficient along c-axis(um2/s);our data
        D_tra = (m.cos(alfa1/180*m.pi)**2)*D_a1 + (m.cos(alfa2/180*m.pi)**2)*D_a2 + ((m.cos(gamma/180*m.pi))**2)*D_c #Diffusion coefficient along traverse
        print('D_a1 =',D_a1)
        print()
        
        #NATURAL PROFILE FROM MEASUREMENT
        with open('Upload_data.csv', 'r') as A:
            x_nat = []                          #Distance (um) as x-axis
            c_nat = []                          #concentration (wt.%) as y-axis
            for item in A.readlines()[1:]:
                item1 = item.split(',')
                x_nat.append(int(item1[0]))
                c_nat.append(float(item1[1].strip()))
            length_nat = x_nat[-1]              #Total length of the measured profile (um)
            real_i = len(x_nat)                 #Total points in real profile
            uncert = 0.02                       #uncertainty of data (+/-,wt.%; by user)
            err = [uncert]*len(c_nat)           #uncertainty list
            
        #SET VARIABLES (by user)
        delta_x = float(self.dx_input.GetValue())                        #Distance step (um)   0.5
        delta_t = int(self.dt_input.GetValue())                          #Time step            8000
        t_itr = int(self.iteration_input.GetValue())                     #Time iteration       250
        
        
        try:
            x_model = []                            #location of model points
            i = 1
            while i <= length_nat:
                x_model.append(i)
                i += delta_x
            x_i = len(x_model)                      #Total model points
            print('x_i =',x_i)
            print()
        except:
            pass
        
        #SET INITIAL CONDITIONS (BY USERS)
        try:
            c_ini = float(self.InitialC_input.GetValue())              # c_ini = 0.96
            c_ini_arr = [c_ini]*(x_i -1)
        except:
            pass
        
        #SET BOUNDARY CONDITIONS (BY USERS): in this case, the first and last number of c array have fixed values
        try:
            c_bl = float(self.left_boundary_input.GetValue())               # =max(c_nat)  =1.56822
            c_br = float(self.right_boundary_input.GetValue())              # =c_ini       =0.96
        except:
            pass
        
       
        Stability = (D_tra*delta_t)/(delta_x**2)
        if Stability > 0.5:
            self.MessageBox()
        
        ####### CHECK STABLITY: DONE #######
        else:
            fig = make_subplots(rows=2, cols=1, subplot_titles=('     ','     '))
            ########## PLOT FIG. 1 ##########
            try:
                fig.add_trace(go.Scatter(x=[1,1,length_nat,length_nat],
                                     y=[c_bl,c_ini,c_ini, c_br],
                                     name='Initial & Boundary Conditions',
                                     line_shape='linear',
                                     line=(dict(color='blue', dash='dash'))),
                          row=1, col=1)      #Initial and Boundary Conditions line
            except:
                pass
            fig.add_trace(go.Scatter(x=list(range(1,length_nat+1)),
                                     y=c_nat,
                                     error_y=dict(array=err, visible=True),
                                     mode="lines+markers",
                                     name="Natural Profile", 
                                     line=dict(color="black",dash="dash")),
                          row=1, col=1)                                               #Natural Profile and Error Bar
            fig.update_layout(margin=dict(l=30, r=30, t=30, b=30))
            
            fig.update_yaxes(title_text=self.component_combobox.GetValue()+" in Ap (wt%)", row=1, col=1)
            fig.update_xaxes(title_text="Distance (µm)", row=1, col=1)
            fig['layout'].update(width=700, height=700, autosize=False)
            
            ##### PLOT FIG. 2: START MODELLING AND DISPLAY MODELLED PROFILE
            c=np.ones((x_i, t_itr+1))      #initiate a matrix of c
            for j in range(t_itr):
                value = round(j/t_itr*100)
                self.gauge.SetValue(value)
                if j==t_itr-1:
                    self.gauge.Destroy()
                for i in range(1,x_i-1):
                    c[1:x_i,0] = c_ini_arr;
                    c[0,j] = c_bl          #constant c at left-side boundary
                    c[x_i-1,j] = c_br      #constant c at right-side boundary
                    c[i,j+1] = Stability * (c[i-1,j]+c[i+1,j] - 2*c[i,j]) + c[i,j]
                Ans = list(c[:,j])
                ### PLOT MODEL ###
                if j==0:
                    fig.add_trace(go.Scatter(x=x_model,
                                         y=Ans,
                                         mode='lines',
                                         name='Model',
                                         line=dict(color='red')),
                              row=1, col=1)
                    fig.update_layout(
                        annotations=[go.layout.Annotation(
                                        x=0.5,
                                        y=0.5,
                                        xref='paper',
                                        yref='paper',
                                        text="<b>Modelling process T=<b>"+str(T)+"<b>°C<b>",
                                        font=dict(size=18))])
                   # fig.show()
                   # plot(fig,show_link = False)

                else: 
                    fig.update_traces(go.Scatter(x=x_model,y=Ans),
                                      selector=dict(name='Model'))
                t = delta_t*j
                t_hour=t/3600
                x_ano = 3*len(x_nat)/4      #x_coordinate of annotations
                y_ano_1 = 11*c_nat[0]/12    #y_coordinate of annotation 1
                y_ano_2 = 7*c_nat[0]/8      #y_coordinate of annotation 2
                y_ano_3 = 3*c_nat[0]/4      #y_coordinate of annotation 3
                fig.update_layout(
                            annotations=[go.layout.Annotation(
                                    x=x_ano,
                                    y=y_ano_1,
                                    xref='x',
                                    yref='y',
                                    text="Total time = "+str(t)+"s",
                                    font=dict(size=18)),
                                         go.layout.Annotation(
                                    x=x_ano,
                                    y=y_ano_2,
                                    xref='x',
                                    yref='y',
                                    text="("+str(round(t_hour))+" hours) ",
                                    font=dict(size=18))])
                
              #  fig.show()
              #  plot(fig,show_link = False)

                
            ##### FIND THE BESTFIT #####
            num_errs = {}
            min_rms = 100            
            for j in range(t_itr):
                Ans = list(c[:,j])
                interp_funct=interp1d(x_model,Ans)
                new_Ans = list(interp_funct(x_nat))
                num_fit = 0
                ### FIND TE MAXIMUM POINTS OF 'FIT' WITHIN UNCERTAINTY ###
                for k in range(len(x_nat)):
                    if (new_Ans[k] < c_nat[k]+err[k]) and (new_Ans[k] > c_nat[k]-err[k]):
                        num_fit += 1
                        
                num_errs[j]=num_fit
                max_num = num_fit                                     #maximum fit points
                if max_num == 0:
                    self.rmsBox()
                    break
                rms = sum([(c_nat - new_Ans)**2 for (c_nat, new_Ans) in list(zip(c_nat, new_Ans))])/x_i    #minimize root-mean-square deviation to find bestfit timing
                
                if rms < min_rms:
                    min_rms = rms
                    best_j = j
                
                
            #### CALCULATE ERRORS IN THE RESULTS ####
            bestf_errs = num_errs[best_j]
            if best_j == t_itr:
                max_j = j
            else:
                max_j = t_itr
                for j in range(best_j, t_itr+1):
                    #try:
                    if bestf_errs != num_errs[j]:
                            max_j = j-1
                            # print(num_errs[j])
                            break
                    #except KeyError:
                        #self.rmsBox()
                        #break
                for j in range(best_j, 0, -1):
                    if bestf_errs != num_errs[j]:
                        min_j = j+1
                        break
                
            
            negat_errs = min_j - best_j         #negative value
            posit_errs = max_j - best_j         #positive value
            t_best_hour = delta_t*(best_j)/3600
            t_best_day = t_best_hour/24
            t_best_ners = delta_t*negat_errs/3600
            t_best_pers = delta_t*posit_errs/3600
            t_best_day_ners = t_best_ners/24
            t_best_day_pers = t_best_pers/24
            best_Ans = c[0:x_i,best_j-1]
            new_best_Ans = list(interp1d(x_model, best_Ans)(x_nat))
            Diff = []
            Diff_norm = []
            for N in range(real_i):
                Diff.append(abs(new_best_Ans[N]-c_nat[N]))
                Diff_norm.append(Diff[N]/c_nat[N])
            Discrepancy = mean(Diff_norm)
            
            ##### PLOT THE RESULTS #####
            fig.add_trace(go.Scatter(x=x_model,
                                     y=c[:,min_j],
                                     mode='lines',
                                     name='Uncertainty',
                                     line=(dict(color='green', dash='dash')),
                                     line_shape="spline"),                      
                              row=2, col=1)                                      #Uncertainty min
            fig.add_trace(go.Scatter(x=x_model,
                                     y=c[:,max_j],
                                     mode='lines',
                                     line=(dict(color='green', dash='dash')),
                                     line_shape="spline",
                                     showlegend=False), 
                              row=2, col=1)                                      #Uncertainty max
            fig.add_trace(go.Scatter(x=[1,length_nat],
                                 y=[c_bl,c_br],
                                 name='Initial & Boundary Conditions',         ##### NOTE: 3 numbers
                                 line_shape='vh',
                                 line=(dict(color='blue', dash='dash')),
                                 showlegend=False),
                      row=2, col=1)                                                #Initial and Boundary Conditions line
            fig.add_trace(go.Scatter(x=list(range(1,length_nat+1)),
                                 y=c_nat,
                                 error_y=dict(array=err, visible=True),
                                 mode="lines+markers",
                                 name="Natural Profile", 
                                 line=dict(color="black",dash="dash"),
                                 showlegend=False),
                      row=2, col=1)                                               #Natural Profile and Error Bar
            fig.add_trace(go.Scatter(x=x_model,
                                     y=c[:,best_j],
                                     mode='lines',
                                     name='Bestfit',
                                     line=dict(color='orange')),
                              row=2, col=1)                                       #Bestfit
        
            
            t_best_ers='Time = '+ str(round(t_best_hour)) + ' (+' + str(round(t_best_pers)) + '/' + str(round(t_best_ners*10)/10) +') hours'
            t_best_ers_day=str(round(t_best_day*10)/10)+' (+' + str(round(t_best_day_pers*10)/10) + '/' + str(round(t_best_day_ners*10)/10)+') days'
            corr_res='Discrepancy = ' + str(round(Discrepancy*100, 2)) + '%'
            
            fig.update_layout(
                        annotations=[go.layout.Annotation(
                                        x=0.5,
                                        y=0.5,
                                        xref='paper',
                                        yref='paper',
                                        text="<b>Modelling process T=<b>"+str(T)+"<b>°C<b>",
                                        font=dict(size=16)),
                                     go.layout.Annotation(
                                        x=0.5,
                                        y=0.4,
                                        xref='paper',
                                        yref='paper',
                                        text="<b>Results<b>",
                                        font=dict(size=16))])             #Titles of 2 graphs
               
            fig.add_trace(go.Scatter(x=[x_ano, x_ano, x_ano], y=[y_ano_1, y_ano_2, y_ano_3],
                                         mode="markers+text",
                                         text=[t_best_ers, t_best_ers_day, corr_res],
                                         textfont=dict(size=14),
                                         line=dict(color="white"),
                                         showlegend=False),    
                              row=2, col=1)                               #Annotations of graph 2
                
            text_total_time='Total time = '+str(t)+'s'
            text_total_time_hour='('+str(round(t_hour))+' hours)'
                
            fig.add_trace(go.Scatter(x=[x_ano, x_ano], y=[y_ano_1, y_ano_2],
                                         mode="markers+text",
                                         text=[text_total_time, text_total_time_hour],
                                         textfont=dict(size=14),
                                         line=dict(color="white"),
                                         showlegend=False),
                              row=1, col=1)                               #Annotations of graph 1  
                                       
            fig.update_yaxes(title_text=self.component_combobox.GetValue()+" in Ap (wt%)", row=2, col=1)
            fig.update_xaxes(title_text="Distance (µm)", row=2, col=1)
            fig['layout'].update(width=700, height=700, autosize=False)
            
            if not os.path.exists("images"):
                os.mkdir("images")
            fig.write_image("images/figure.png")
            
           # fig.show()
           #  plot(fig,show_link = False)

        
            # Display figure 2
            self.figure_pic = wx.StaticBitmap(self, size=(500,500), pos = (330,25))
            self.figure_pic.SetBitmap(wx.Bitmap('images/figure.png'))
        
    def MessageBox(self):
        wx.MessageBox("Stability < 0.5", "Dialog", wx.OK | wx.ICON_ERROR)
    
    def rmsBox(self):
        wx.MessageBox("Increase interation, OR change initial/boundary conditions", "Dialog", wx.OK|wx.ICON_ERROR)
        


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(parent=None, title="ApTimer")
        self.frame.Show()
        return True

    
app = MyApp()
app.MainLoop()

