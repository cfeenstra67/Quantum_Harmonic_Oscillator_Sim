#!/usr/local/bin/python3

import wx
from wx.lib.scrolledpanel import ScrolledPanel

import matplotlib as mpl
import matplotlib.gridspec as gridspec
mpl.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib import animation

import numpy as np
from scipy.special import eval_hermite
from math import factorial as fact
from time import time



def e_lvl_func(n):
    psi_n=lambda y: (((2**n)*fact(n))**-.5)*(np.pi**-.25)*np.exp((-y**2)/2)*eval_hermite(n,y)
    return lambda y,t: psi_n(y)*np.exp(-1j*(n+.5)*t)  
    
def super_pos_func(state):
    def func(y,t):
        try: total=np.full(len(y),0,dtype=complex)
        except: total=0
        for lvl, coef in enumerate(state):
            total+=coef*e_lvl_func(lvl)(y,t)
        return total
    return func

class plot_panel(wx.Panel):
    def __init__(self, parent, dx=.01, state=[1,1,1,1], dt=np.pi*2/96, active_dict={'rl':True,'im':True,'parab':True,'e_n':True}):
        super().__init__(parent)
        self.e_lvls=len(state)
        self.state=state
        self.__active_dict=active_dict
        self.x_ran=self.e_lvls**.5
        self.x_ran=(-self.x_ran,self.x_ran)
        self.dx=dx
        self.dt=dt
        self.x=np.arange(*self.x_ran,self.dx)

        self.fig=Figure()
        self.canvas=FigureCanvas(self,-1,self.fig)
        gs=gridspec.GridSpec(3,1)
        self.ax=self.fig.add_subplot(gs[:2,0],xlim=self.x_ran,ylim=(0,self.e_lvls))
        self.parab, =self.ax.plot(self.x,self.x**2,'g')
        self.lvls=[]
        self.e_rl_plots=[]
        self.e_im_plots=[]
        for i in range(self.e_lvls):
            e_plot, =self.ax.plot(self.x,np.full(len(self.x),i+.5),'y',lw=1); self.lvls.append(e_plot)
            e_rl_plot, =self.ax.plot([],[],'b',lw=1); self.e_rl_plots.append(e_rl_plot)
            e_im_plot, =self.ax.plot([],[],'r',lw=1); self.e_im_plots.append(e_im_plot)
        self.super_ax=self.fig.add_subplot(gs[2,0],xlim=self.x_ran,ylim=(-2,2))
        self.super_pos_rl, =self.super_ax.plot([],[],'b')
        self.super_pos_im, =self.super_ax.plot([],[],'r')
        self.__active_lines=self.active_lines()
        
        sizer=wx.BoxSizer()
        sizer.Add(self.canvas,proportion=1,flag=wx.EXPAND)
        self.SetSizer(sizer)
    def start(self):
        t0=time()
        self.animate(0)
        t1=time()
        interval=1000*self.dt-(t1-t0)
        self.animate_init()
        self.ani=animation.FuncAnimation(self.fig,self.animate,frames=192,interval=interval,blit=True)
    def reset(self):
        self.ani.frame_seq=self.ani.new_frame_seq()
    def set_active(self,key,val):
        if self.__active_dict[key]!=val:
            self.__active_dict[key]=val
            def update_ani():
                self.canvas.draw()
                if self.ani:
                    self.ani._stop()
                    del(self.ani)
                    self.start()
            if key=='parab':
                self.parab.set_visible(val)
                update_ani()
            elif key=='e_n':
                for lvl, lvl_plot in enumerate(self.lvls):
                    lvl_plot.set_visible(val)
                update_ani()
            else:
                self.__active_lines=self.active_lines()
                self.reset()
    def get_active(self, key): return self.__active_dict[key]
    def active_lines(self):
        lines=[]
        if self.__active_dict['rl']:
            lines.extend(self.e_rl_plots)
            lines.append(self.super_pos_rl)
        if self.__active_dict['im']:
            lines.extend(self.e_im_plots)
            lines.append(self.super_pos_im)
        return lines
    def animate_init(self):
        full=self.__active_lines
        for some_plot in full: some_plot.set_data([],[])
        return full
    def animate(self, t):
        for lvl, (rl_plot, im_plot) in enumerate(zip(self.e_rl_plots,self.e_im_plots)):
            y=e_lvl_func(lvl)(self.x,t*self.dt)+(lvl+.5)*(1j+1)
            rl_plot.set_data(self.x,y.real)
            im_plot.set_data(self.x,y.imag)
        y_sup=super_pos_func(self.state)(self.x,t*self.dt)
        self.super_pos_rl.set_data(self.x,y_sup.real)
        self.super_pos_im.set_data(self.x,y_sup.imag)
        return self.__active_lines

class control_panel(ScrolledPanel):
    def __init__(self, parent, width=200):
        super().__init__(parent,size=(width,1000))
        self.border_w=5
        self.ctrl_w=width-15-self.border_w*2
        self.SetupScrolling(scroll_x=False,scroll_y=True)
        self.vbox=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.vbox)
        cb_dict={'im':'Imaginary','rl':'Real','parab':'Parabola','e_n':'Energy Levels'}
        def checkbox_fired(event):
            cb=event.EventObject
            key=next(k for k,v in cb_dict.items() if v==cb.GetLabel())
            parent.Parent.checkbox_changed(key,cb.GetValue())
        for val in cb_dict.values(): self.add_check(val,checkbox_fired)
            
    def add_check(self, label_text, action):
        new_cb=wx.CheckBox(self, wx.ID_ANY, label_text, size=(self.ctrl_w,20))
        new_cb.SetValue(True)
        new_cb.Bind(wx.EVT_CHECKBOX, action)
        self.add_control(new_cb)
    def add_control(self, ctrl):
        self.vbox.Add(ctrl,0,wx.TOP | wx.LEFT | wx.RIGHT,border=self.border_w)
        
class plot_editor(wx.Frame):
    def __init__(self):
        super().__init__(None,wx.ID_ANY,"QM Demo")
        self.bkg=wx.Panel(self)
        self.plot=plot_panel(self.bkg)
        self.controls=control_panel(self.bkg)
        hbox=wx.BoxSizer()
        hbox.Add(self.plot,proportion=1,flag=wx.EXPAND)
        hbox.Add(self.controls,proportion=0,flag=wx.LEFT)
        self.bkg.SetSizer(hbox)
    def checkbox_changed(self, key, checked):
        self.plot.set_active(key,checked)
        

if __name__ == '__main__':
    app=wx.App(redirect=False)
    win_size=(500,500)
    win=plot_editor()
    win.plot.start()
    win.Show(True)
    app.MainLoop()
        
        
        
        
        
        