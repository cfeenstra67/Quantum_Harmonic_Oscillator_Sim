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
from functools import partial
from collections import OrderedDict as odict
from sympy import *


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
    def __init__(self, parent, dx=.01, state=[1,1,1,1], dt=np.pi*2/96, active_dict={'rl':True,'im':True,'parab':True,'e_n':True}, e_lvls=-1):
        super().__init__(parent)
        
        
        self.__e_lvls=e_lvls if e_lvls!=-1 else len(state)
        self.state=state
        self.__supyb=2
        self.__xprop=2
        self.__active_dict=active_dict
        self.dx=dx
        self.dt=dt
        
        self.fig=Figure()
        self.canvas=FigureCanvas(self,-1,self.fig)
        gs=gridspec.GridSpec(3,1)
        self.ax=self.fig.add_subplot(gs[:2,0])
        self.super_ax=self.fig.add_subplot(gs[2,0])
        self.super_pos_rl, =self.super_ax.plot([],[],'b')
        self.super_pos_im, =self.super_ax.plot([],[],'r')
        
        self.e_lvls=self.__e_lvls
        self.supyb=self.__supyb

        sizer=wx.BoxSizer()
        sizer.Add(self.canvas,proportion=1,flag=wx.EXPAND)
        self.SetSizer(sizer)
    
    def get_e_lvls(self): return self.__e_lvls
    def set_e_lvls(self, val):
        self.ax.clear()
        self.__e_lvls=val
        self.x_ran=(self.e_lvls**.5)*self.xprop
        self.x_ran=(-self.x_ran,self.x_ran)
        self.ax.set_xlim(*self.x_ran)
        self.ax.set_ylim(0,self.e_lvls)
        self.super_ax.set_xlim(*self.x_ran)
        self.x=np.arange(*self.x_ran,step=self.dx)
        
        self.lvls=[]
        self.e_rl_plots=[]
        self.e_im_plots=[]
        for i in range(self.e_lvls):
            e_plot, =self.ax.plot(self.x,np.full(len(self.x),i+.5),'y',lw=1); self.lvls.append(e_plot)
            e_rl_plot, =self.ax.plot([],[],'b',lw=1); self.e_rl_plots.append(e_rl_plot)
            e_im_plot, =self.ax.plot([],[],'r',lw=1); self.e_im_plots.append(e_im_plot)
        self.parab, =self.ax.plot(self.x,self.x**2,'g')
        self.__active_lines=self.active_lines()
    e_lvls=property(get_e_lvls,set_e_lvls)
    
    def get_supyb(self): return self.__supyb
    def set_supyb(self, val):
        self.__supyb=val
        self.super_ax.set_ylim(-val,val)
    supyb=property(get_supyb,set_supyb)
    
    def get_xprop(self): return self.__xprop
    def set_xprop(self, val):
        self.__xprop=val
        self.e_lvls=self.e_lvls
    xprop=property(get_xprop,set_xprop)
    
    def start(self):
        t0=time()
        self.animate(0)
        t1=time()
        interval=1000*self.dt-(t1-t0)
        self.animate_init()
        self.ani=animation.FuncAnimation(self.fig,self.animate,frames=192,interval=interval,blit=True)
    def reset(self):
        self.ani.frame_seq=self.ani.new_frame_seq()
    def hard_reset(self):
        self.canvas.draw()
        if self.ani:
            self.ani._stop()
            del(self.ani)
            self.start()
    def set_active(self,key,val):
        if self.__active_dict[key]!=val:
            self.__active_dict[key]=val
            if key=='parab':
                self.parab.set_visible(val)
                self.hard_reset()
            elif key=='e_n':
                for lvl, lvl_plot in enumerate(self.lvls):
                    lvl_plot.set_visible(val)
                self.hard_reset()
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
        cb_dict=odict((('im','Imaginary'),('rl','Real'),('parab','Parabola'),('e_n','Energy Levels')))
        def checkbox_fired(event):
            cb=event.EventObject
            key=next(k for k,v in cb_dict.items() if v==cb.GetLabel())
            parent.Parent.checkbox_changed(key,cb.GetValue())
        for val in cb_dict.values(): self.add_check(val,checkbox_fired)
        tc_dict=odict((('e_lvls',('# Energy Levels:',str(parent.Parent.plot.e_lvls))),('state',('Superposition:',",".join([str(num) for num in parent.Parent.plot.state])))))
        def textctrl_fired(event, key):
            tc=event.EventObject
            parent.Parent.textctrl_changed(key,tc)
        self.tctrl_dict={}
        for key,(val,initial) in tc_dict.items(): self.tctrl_dict[key]=self.add_textctrl(val,partial(textctrl_fired,key=key),initial)
        def edit_superp(event):
            editor=spfn_editor(parent.Parent)
            editor.Show()
        self.add_button('Generate w/ Fn',edit_superp)
        self.add_textctrl('Superposition Y Bound:',partial(textctrl_fired,key='super_y'),str(parent.Parent.plot.supyb))
        self.add_textctrl('X Proportion:',partial(textctrl_fired,key='xprop'),str(parent.Parent.plot.xprop))
        spacer=wx.Panel(self, size=(self.ctrl_w,20))
        self.add_control(spacer)
    def add_check(self, label_text, action):
        new_cb=wx.CheckBox(self, wx.ID_ANY, label_text, size=(self.ctrl_w,20))
        new_cb.SetValue(True)
        new_cb.Bind(wx.EVT_CHECKBOX, action)
        self.add_control(new_cb)
    def add_textctrl(self, label_text, ret_action, initial=''):
        h=20
        bg=wx.Panel(self,size=(self.ctrl_w,h*2+self.border_w))
        txt=wx.StaticText(bg, label=label_text, size=(self.ctrl_w,h))
        txt_ctrl=wx.TextCtrl(bg, style=wx.TE_PROCESS_ENTER,size=(self.ctrl_w,h),pos=(0,h+self.border_w))
        txt_ctrl.Bind(wx.EVT_TEXT_ENTER, ret_action)
        txt_ctrl.SetValue(initial)
        self.add_control(bg)
        return txt_ctrl
    def add_button(self, label_text, action):
        new_b=wx.Button(self, size=(self.ctrl_w,20), label=label_text)
        new_b.Bind(wx.EVT_BUTTON,action)
        self.add_control(new_b)
    def add_control(self, ctrl):
        self.vbox.Add(ctrl,0,wx.TOP | wx.LEFT | wx.RIGHT,border=self.border_w)
        
class plot_editor(wx.Frame):
    def __init__(self,size=(500,500)):
        super().__init__(None,wx.ID_ANY,"QM Demo",size=size)
        self.bkg=wx.Panel(self,size=size)
        self.plot=plot_panel(self.bkg)
        self.controls=control_panel(self.bkg)
        hbox=wx.BoxSizer()
        hbox.Add(self.plot,proportion=1,flag=wx.EXPAND)
        hbox.Add(self.controls,proportion=0,flag=wx.LEFT)
        self.bkg.SetSizer(hbox)
    def checkbox_changed(self, key, checked):
        self.plot.set_active(key,checked)
    def textctrl_changed(self, key, textctrl):
        text=textctrl.GetValue()
        if key=='e_lvls':
            try:
                self.plot.e_lvls=int(text)
                self.plot.hard_reset()
            except:
                textctrl.SetValue(str(self.plot.e_lvls))
        elif key=='state':
            try:
                self.plot.state=[float(txt) for txt in text.split(",")]
                self.plot.reset()
            except:
                textctrl.SetValue(",".join([str(num) for num in self.plot.state]))
        elif key=='super_y':
            try:
                self.plot.supyb=float(text)
                self.plot.hard_reset()
            except:
                textctrl.SetValue(str(self.plot.supyb))
        elif key=='xprop':
            try:
                self.plot.xprop=float(text)
                self.plot.hard_reset()
            except:
                textctrl.SetValue(str(self.plot.xprop))
    def state_generated(self, new_state):
        key='state'
        tc=self.controls.tctrl_dict[key]
        tc.SetValue(",".join([str(num) for num in new_state]))
        self.plot.state=new_state
        self.plot.reset()

class spfn_editor(wx.Frame):
    def __init__(self, controller=None, size=(300,150)):
        super().__init__(None, wx.ID_ANY, "Superposition Editor", size=size, style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
        self.cont=controller
        w,h=size
        self.border_w=5
        self.line_w=w-self.border_w*2
        self.bkg=wx.Panel(self)
        box=wx.BoxSizer()
        box.Add(self.bkg)
        self.SetSizer(box)
        self.vbox=wx.BoxSizer(wx.VERTICAL)
        self.bkg.SetSizer(self.vbox)
        fields=('Fn:','For:','From:','To:')
        self.ctrl_dict={}
        for field in fields: self.ctrl_dict[field]=self.add_line(field)
        go=wx.Button(self.bkg,size=(self.line_w,20),label='Go')
        go.Bind(wx.EVT_BUTTON,self.pressed_go)
        self.vbox.Add(go,0,wx.ALL,border=self.border_w)
        self.Fit()
    def add_line(self, text):
        prop=.3
        h=20
        pn=wx.Panel(self.bkg,size=(self.line_w,h))
        hbox=wx.BoxSizer()
        txt=wx.StaticText(pn,label=text,size=(self.line_w*prop,h))
        ctrl=wx.TextCtrl(pn,size=(self.line_w*(1-prop),h),pos=(self.line_w*prop,0))
        hbox.Add(txt)
        hbox.Add(ctrl)
        pn.SetSizer(hbox)
        self.vbox.Add(pn,0,wx.TOP | wx.LEFT | wx.RIGHT, border=self.border_w)
        return ctrl
    def pressed_go(self, event=None):
        try:
            fn=self.ctrl_dict['Fn:'].GetValue()
            var=Symbol(self.ctrl_dict['For:'].GetValue())
            start=int(self.ctrl_dict['From:'].GetValue())
            end=int(self.ctrl_dict['To:'].GetValue())
            seq=[float(sympify(fn).evalf(subs={var:i})) for i in range(start,end+1)]
            self.cont.state_generated(seq)
        except: pass
    

if __name__ == '__main__':
    app=wx.App(redirect=False)
    win_size=(600,400)
    win=plot_editor(size=win_size)
    win.plot.start()
    win.Show(True)
    app.MainLoop()