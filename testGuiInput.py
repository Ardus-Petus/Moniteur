from Monitor.core.monitor import Monitor, Context
from Monitor.gui.guiStandard import gui, gui_update
from progTestGUIInput import Program as application
    
ctx = Context()
ctx.set_gui(gui, gui_update)
ctx.set_application(application)
Monitor(ctx).run()