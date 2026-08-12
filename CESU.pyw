# main_CESU.py
from Monitor.core.monitor import Monitor, Context  
from Monitor.gui.presentation_horizontale import Presentation
from Cesu.metier_CESU import ExtractionMetier as application
from Cesu.gui_CESU import gui

context=Context()            

context.set_application(application)
context.set_gui(gui)
context.set_presentation(Presentation, 'gauche', 'droite')

app = Monitor(context)
app.run()          # Application
