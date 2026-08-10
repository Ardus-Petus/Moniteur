# main_CESU.py
from Monitor.core.monitor import Monitor, Context  
from Cesu.metier_CESU import ExtractionMetier as application
from Cesu.gui_CESU import gui, gui_update
from Monitor.gui.presentation_horizontale import Presentation

context=Context()            

context.set_application(application)
context.set_gui(gui, gui_update)
context.set_presentation(Presentation, 'gauche', 'droite')

app = Monitor(context) 
app.run()          # Application
