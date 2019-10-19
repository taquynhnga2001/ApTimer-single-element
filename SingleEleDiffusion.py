import math as m
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import interp1d
from plotly.subplots import make_subplots
import os
from statistics import mean

####################################################################
############################## SET UP ##############################
####################################################################

#INPUTS FROM USER
T = 900             #temperature in celsius degree (for user)
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
with open('Cl_Apa.txt', 'r') as A:
    x_nat = []                          #Distance (um) as x-axis
    c_nat = []                          #concentration (wt.%) as y-axis
    for item in A.readlines():
        item1 = item.split('\t')
        x_nat.append(int(item1[0]))
        c_nat.append(float(item1[1].strip()))
    length_nat = x_nat[-1]              #Total length of the measured profile (um)
    real_i = len(x_nat)                 #Total points in real profile
    uncert = 0.02                       #uncertainty of data (+/-,wt.%; by user)
    err = [uncert]*len(c_nat)           #uncertainty list

#SET VARIABLES (by user)
delta_x = 0.5                           #Distance step (um)
delta_t = 8000                          #Time step
t_itr = 250                             #Time iteration

x_model = []                            #location of model points
i = 1
while i <= length_nat:
    x_model.append(i)
    i += delta_x
x_i = len(x_model)                      #Total model points
print('x_i =',x_i)
print()

#SET INITIAL CONDITIONS (BY USERS)
c_ini = 0.96
c_ini_arr = [c_ini]*(x_i -1)

#SET BOUNDARY CONDITIONS (BY USERS): in this case, the first and last number of c array have fixed values
c_bl = max(c_nat)
c_br = c_ini 


######################################################################
############### PLOT NATURAL PROFILE FOR USER TO CHECK ###############
######################################################################
fig = make_subplots(rows=2, cols=1,
                    subplot_titles=('     ','     '))


########## FIGURE 1 ##########
fig.add_trace(go.Scatter(x=[1,1,length_nat],
                         y=[c_bl,c_ini,c_br],
                         name='Initial & Boundary Conditions',
                         line_shape='linear',
                         line=(dict(color='blue', dash='dash'))),
              row=1, col=1)                                                #Initial and Boundary Conditions line
fig.add_trace(go.Scatter(x=list(range(1,length_nat+1)),
                         y=c_nat,
                         error_y=dict(array=err, visible=True),
                         mode="lines+markers",
                         name="Natural Profile", 
                         line=dict(color="black",dash="dash")),
              row=1, col=1)                                               #Natural Profile and Error Bar
fig.update_layout(margin=dict(l=30, r=30, t=30, b=30))

fig.update_yaxes(title_text="Cl in Ap (wt%)", row=1, col=1)
fig.update_xaxes(title_text="Distance (µm)", row=1, col=1)
fig['layout'].update(width=700, height=700, autosize=False)

if not os.path.exists("images"):
    os.mkdir("images")
fig.write_image("images/single_ele_diffusion.png")

fig.show()



########## FIGURE 2 ##########
### CHECK STABABILITY
Stability = (D_tra*delta_t)/(delta_x**2)
print('Stability=', Stability)
if Stability > 0.5:
    print('stability >0.5, check')
else:    
    press=input('Proceed with computation?[y-YES;n-NO] : ')          #input "y" to continue this program
    
if press == 'y' or press == 'Y':
    ##### PLOT FIG. 2: START MODELLING AND DISPLAY MODELLED PROFILE
    c=np.ones((x_i, t_itr+1))      #initiate a matrix of c
    for j in range(t_itr):
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
            fig.show()
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
        
        fig.show()
        
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
        max_num = num_fit                                                                          #maximum fit points
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
            if bestf_errs != num_errs[j]:
                max_j = j-1
                break
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
    best_Ans = c[0:x_i, best_j-1]
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
    fig.add_trace(go.Scatter(x=[1,1,length_nat],
                         y=[c_bl,c_ini,c_br],
                         name='Initial & Boundary Conditions',
                         line_shape='linear',
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
                             line=dict(color='red')),
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
                               
    fig.update_yaxes(title_text="Cl in Ap (wt%)", row=2, col=1)
    fig.update_xaxes(title_text="Distance (µm)", row=2, col=1)
    fig['layout'].update(width=700, height=700, autosize=False)
    
    if not os.path.exists("images"):
        os.mkdir("images")
    fig.write_image("images/figure.png")
    
    fig.show()
