import wx

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size = (1200,800))
        self.panel = MyPanel(self)

     

class MyPanel(wx.Panel):
    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)
        
        # "Input"-"Output"
        self.titleInput = wx.StaticText(self, label = "Input:", pos = (10,5))                      
        self.titleOutput = wx.StaticText(self, label = "Output:", pos = (330,5))                   
        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.titleInput.SetFont(font)
        self.titleOutput.SetFont(font)
        
        # temperature input
        self.T = wx.StaticText(self, label = "T", pos = (10,33))                                   
        self.T_input = wx.TextCtrl(self, size=(50,-1), pos = (25,30))
        self.T_unit = wx.StaticText(self, label="°C", pos = (80,33))
        self.T_input.SetValue('900')
        
        # component combobox (Cl, X, Y)
        self.component = wx.StaticText(self, label = "Component", pos = (120, 33))                 
        self.component_choices = ['Cl', 'X', 'Y']
        self.component_combobox = wx.ComboBox(self, choices = self.component_choices, pos = (195, 30))
        #grey = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx)
        self.component_combobox.SetValue('Cl')
        
        # initial C
        self.InitialC = wx.StaticText(self, label = "Initial C =", pos = (10, 66))                        
        self.InitialC_input = wx.TextCtrl(self, size=(50,-1), pos = (110, 63))
        self.wt_unit1 = wx.StaticText(self, label = "wt.%", pos = (165, 66))
        
        # left boundary
        self.LeftBoundary = wx.StaticText(self, label = "Left Boundary =", pos = (10, 99))                 
        self.left_boundary_input = wx.TextCtrl(self, size=(50,-1), pos = (110, 96))
        self.wt_unit2 = wx.StaticText(self, label = "wt.%", pos = (165, 99))
        
        # right boundary
        self.RightBoundary = wx.StaticText(self, label = "Right Boundary =", pos = (10, 132))              
        self.right_boundary_input = wx.TextCtrl(self, size=(50,-1), pos = (110, 129))
        self.wt_unit3 = wx.StaticText(self, label = "wt.%", pos = (165, 132))
        
        # natural data upload button
        self.natural_data = wx.StaticText(self, label = "Natural data:", pos = (10,165))      
        self.naturaldata_button = wx.Button(self, label="Upload", pos=(100,162))
        
        ###### Plot fig. 1 button #####
        self.plot_button = wx.Button(self, label = "Plot", pos = (100, 195))  
        self.plot_button.Bind(wx.EVT_BUTTON, self.OnClickPlot)                 
        
        #dx (distance step)
        self.dx = wx.StaticText(self, label = "dx", pos = (10,240))                         
        self.dx_input = wx.TextCtrl(self, size=(50,-1), pos = (30,237))
        self.dx_unit = wx.StaticText(self, label="µm", pos = (85,240))
        
        #dt (time step)
        self.dt = wx.StaticText(self, label = "dt", pos = (140,240))                         
        self.dt_input = wx.TextCtrl(self, size=(50,-1), pos = (160,237))
        self.dt_unit = wx.StaticText(self, label="s", pos = (215,240))
        
        # interation input
        self.iteration = wx.StaticText(self, label = "Iteration", pos = (10,273))           
        self.iteration_input = wx.TextCtrl(self, size=(50,-1), pos = (60,270))
        
        ###### Run modeling and plot figure 2 button #####
        self.Run_button = wx.Button(self, label = "Run!", pos = (150, 269))
        self.Run_button.Bind(wx.EVT_BUTTON, self.OnClickRun)
        
        
        
        ###### TEST BUTTON                                                          #####
        self.test_button = wx.Button(self, label = "test button", pos = (10, 400))  #####
        self.test_button.Bind(wx.EVT_BUTTON, self.OnClickTest)                      #####
        

    def OnClickPlot(self, event):
        # Display figure 1
        self.single_ele_diff_pic = wx.StaticBitmap(self, size=(500,500), pos = (330,25))
        self.single_ele_diff_pic.SetBitmap(wx.Bitmap('images/single_ele_diffusion.png'))

    def OnClickRun(self, event):
        # Display figure 2
        self.figure_pic = wx.StaticBitmap(self, size=(500,500), pos = (330,25))
        self.figure_pic.SetBitmap(wx.Bitmap('images/figure.png'))
        
    def OnClickTest(self, event):                                                #####
        Ti = self.T_input.GetValue()                                             #####
        self.print_testvalue = wx.StaticText(self, label = Ti, pos = (10, 420))  #####


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(parent=None, title="ApTimer")
        self.frame.Show()
        return True
 
    
app = MyApp()
app.MainLoop()


